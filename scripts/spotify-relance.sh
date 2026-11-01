#!/bin/bash
# spotify-relance — watchdog de relance de raspotify (mission spotify-relance).
#
# Relance uniquement l'unite raspotify quand la session librespot est morte
# sans arret du processus : signatures librespot session « Connection to
# server closed. » et dealer « Websocket peer does not respond. » sans
# « Authenticated as » ulterieur dans le journal du boot courant limite a
# l'invocation en cours de l'unite. Grace de
# 120 s depuis la premiere observation du defaut non resolu ; minimum 600 s
# entre tentatives (memes echouees), horodatage par uptime ecrit avant
# action. Unite inactive laissee inactive. Observation impossible ou etat
# invalide : aucune action, code de sortie non nul.
#
# Mode test : `spotify-relance.sh test` exige les sept fixtures ensemble —
# SPOTIFY_JOURNAL_FILE, SPOTIFY_ACTIVE_FILE, SPOTIFY_INVOCATION_FILE,
# SPOTIFY_BOOT_ID_FILE, SPOTIFY_UPTIME_FILE, SPOTIFY_STATE_DIR,
# SPOTIFY_RESTART (chemin d'executable appele avec « restart raspotify »,
# jamais une chaine passee au shell). Toute fixture absente : refus immediat.
# Le mode test n'appelle jamais systemctl ni journalctl.

set -u

export LC_ALL=C  # parsing numérique indépendant de la locale (fr_FR : virgule décimale)
UNIT=raspotify
GRACE=120
COOLDOWN=600
SIG_SESSION='Connection to server closed.'
SIG_DEALER='Websocket peer does not respond.'
SIG_AUTH='Authenticated as'

MODE=${1:-}

fail() {
  printf 'spotify-relance: %s\n' "$1" >&2
  exit "${2:-3}"
}

TEST=0
if [ "$MODE" = "test" ]; then
  TEST=1
fi

# --- Sources d'observation -------------------------------------------------

JOURNAL=''
ACTIVE=''
INVOCATION=''
BOOT=''
UP=''

if [ "$TEST" = 1 ]; then
  [ -n "${SPOTIFY_JOURNAL_FILE:-}" ]    || fail 'fixture manquante: SPOTIFY_JOURNAL_FILE' 2
  [ -n "${SPOTIFY_ACTIVE_FILE:-}" ]     || fail 'fixture manquante: SPOTIFY_ACTIVE_FILE' 2
  [ -n "${SPOTIFY_INVOCATION_FILE:-}" ] || fail 'fixture manquante: SPOTIFY_INVOCATION_FILE' 2
  [ -n "${SPOTIFY_BOOT_ID_FILE:-}" ]    || fail 'fixture manquante: SPOTIFY_BOOT_ID_FILE' 2
  [ -n "${SPOTIFY_UPTIME_FILE:-}" ]     || fail 'fixture manquante: SPOTIFY_UPTIME_FILE' 2
  [ -n "${SPOTIFY_STATE_DIR:-}" ]       || fail 'fixture manquante: SPOTIFY_STATE_DIR' 2
  [ -n "${SPOTIFY_RESTART:-}" ]         || fail 'fixture manquante: SPOTIFY_RESTART' 2
  [ -f "$SPOTIFY_JOURNAL_FILE" ]        || fail 'fixture introuvable: journal' 2
  [ -f "$SPOTIFY_ACTIVE_FILE" ]         || fail 'fixture introuvable: etat actif' 2
  [ -f "$SPOTIFY_INVOCATION_FILE" ]     || fail 'fixture introuvable: invocation' 2
  [ -f "$SPOTIFY_BOOT_ID_FILE" ]        || fail 'fixture introuvable: boot' 2
  [ -f "$SPOTIFY_UPTIME_FILE" ]         || fail 'fixture introuvable: uptime' 2
  [ -d "$SPOTIFY_STATE_DIR" ]           || fail 'fixture introuvable: repertoire d etat' 2
  [ -x "$SPOTIFY_RESTART" ]             || fail 'fixture introuvable: executable de relance' 2
  JOURNAL=$(cat "$SPOTIFY_JOURNAL_FILE")    || fail 'lecture journal impossible' 3
  ACTIVE=$(cat "$SPOTIFY_ACTIVE_FILE")      || fail 'lecture etat actif impossible' 3
  INVOCATION=$(cat "$SPOTIFY_INVOCATION_FILE") || fail 'lecture invocation impossible' 3
  BOOT=$(cat "$SPOTIFY_BOOT_ID_FILE")       || fail 'lecture boot impossible' 3
  UP=''
  read -r UP _ < "$SPOTIFY_UPTIME_FILE"     || fail 'lecture uptime impossible' 3
else
  SHOW_OUT=''
  SHOW_OUT=$(timeout 30 systemctl show "$UNIT" -p ActiveState -p InvocationID 2>/dev/null) \
    || fail 'observation systemctl impossible' 3
  while IFS= read -r line; do
    case "$line" in
      ActiveState=*)   ACTIVE=${line#ActiveState=} ;;
      InvocationID=*)  INVOCATION=${line#InvocationID=} ;;
    esac
  done <<EOF_SHOW
$SHOW_OUT
EOF_SHOW
  [ -n "${ACTIVE:-}" ]      || fail 'etat actif illisible' 3
  [ -n "${INVOCATION:-}" ]  || fail 'invocation illisible' 3
  BOOT=$(cat /proc/sys/kernel/random/boot_id 2>/dev/null) || fail 'boot id illisible' 3
  read -r UP _ < /proc/uptime || fail 'uptime illisible' 3
  # Journal limite au boot ET a l'invocation courante : un defaut d'une
  # invocation anterieure (avant relance) ne doit plus etre vu.
  JOURNAL=$(timeout 30 journalctl -u "$UNIT" -b _SYSTEMD_INVOCATION_ID="$INVOCATION" --no-pager --output=cat 2>/dev/null) \
    || fail 'lecture journal impossible' 3
fi

[ -n "$UP" ] || fail 'uptime illisible' 3
NOW=$(printf '%.0f' "$UP" 2>/dev/null) || fail 'uptime invalide' 3

case "$ACTIVE" in
  active) ;;
  inactive|failed)
    # Unite arretee : laissee inactive, aucune action.
    exit 0
    ;;
  *)
    fail 'etat inattendu' 3
    ;;
esac

# --- Detection : premier defaut non resolu depuis la derniere authentification
# Deux passes : position de la derniere authentification, puis premiere
# signature de defaut situee apres elle. Un defaut suivi d'une
# authentification ulterieure est resolu et ne compte pas.

FAULT_AT=-1

scan_journal() {
  # $1 = journal complet ; positionne FAULT_AT (numero de ligne du premier
  # defaut non resolu, -1 si aucun).
  FAULT_AT=-1
  last_auth=-1
  line_no=0
  while IFS= read -r scan_line; do
    case "$scan_line" in
      *"$SIG_AUTH"*) last_auth=$line_no ;;
    esac
    line_no=$((line_no + 1))
  done <<EOF_SCAN_AUTH
$1
EOF_SCAN_AUTH
  line_no=0
  while IFS= read -r scan_line; do
    case "$scan_line" in
      *"$SIG_SESSION"*|*"$SIG_DEALER"*)
        if [ "$line_no" -gt "$last_auth" ] && [ "$FAULT_AT" -lt 0 ]; then
          FAULT_AT=$line_no
        fi
        ;;
    esac
    line_no=$((line_no + 1))
  done <<EOF_SCAN_FAULT
$1
EOF_SCAN_FAULT
}

scan_journal "$JOURNAL"

if [ "$TEST" = 1 ]; then
  STATE_DIR=$SPOTIFY_STATE_DIR
else
  STATE_DIR=/run/spotify-relance
fi
FAULT_STATE="$STATE_DIR/fault.state"
ATTEMPT_STATE="$STATE_DIR/attempt.state"
LOCK_DIR="$STATE_DIR/lock"

if [ "$FAULT_AT" -lt 0 ]; then
  rm -f "$FAULT_STATE"
  exit 0
fi

# --- Verrou exclusif --------------------------------------------------------

mkdir "$LOCK_DIR" 2>/dev/null || exit 0
# Liberation meme sur signal (systemd TimeoutStartSec, SIGTERM) : sinon le
# verrou orphelin bloquerait silencieusement tous les passages suivants.
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT
trap 'exit 0' INT TERM HUP

# --- Grille d'etat : invocation/boot differente => defaut perime ------------

SEEN=''
if [ -f "$FAULT_STATE" ]; then
  SBOOT=''; SINV=''; SSEEN=''
  read -r SBOOT SINV SSEEN < "$FAULT_STATE" || SBOOT=''
  if [ -n "$SBOOT" ] && [ -n "$SINV" ] && [ -n "$SSEEN" ] \
     && [ "$SBOOT" = "$BOOT" ] && [ "$SINV" = "$INVOCATION" ]; then
    SEEN=$SSEEN
  else
    rm -f "$FAULT_STATE"
  fi
fi

if [ -z "$SEEN" ]; then
  TMP_STATE="$STATE_DIR/.fault.$$"
  printf '%s %s %s\n' "$BOOT" "$INVOCATION" "$NOW" > "$TMP_STATE" \
    || fail 'ecriture etat impossible' 3
  mv -f "$TMP_STATE" "$FAULT_STATE" || fail 'ecriture etat impossible' 3
  exit 0
fi

# --- Recul d'horloge : observation invalide, aucune action -------------------

SEEN_NOW=$(printf '%.0f' "$SEEN" 2>/dev/null) || fail 'horodatage stocke invalide' 3
if [ "$NOW" -lt "$SEEN_NOW" ]; then
  fail 'recul d horloge' 3
fi

# --- Grace 120 s depuis le premier defaut non resolu -------------------------

if [ $((NOW - SEEN_NOW)) -lt "$GRACE" ]; then
  exit 0
fi

# --- Cooldown 600 s entre tentatives, memes echouees -------------------------

if [ -f "$ATTEMPT_STATE" ]; then
  ASEEEN=''
  read -r ASEEEN _ < "$ATTEMPT_STATE" || ASEEEN=''
  if [ -n "$ASEEEN" ]; then
    ASEEEN_NOW=$(printf '%.0f' "$ASEEEN" 2>/dev/null) || fail 'horodatage tentative invalide' 3
    if [ "$NOW" -lt "$ASEEEN_NOW" ]; then
      fail 'recul d horloge tentative' 3
    fi
    if [ $((NOW - ASEEEN_NOW)) -lt "$COOLDOWN" ]; then
      exit 0
    fi
  fi
fi

# --- Revérification : etat, invocation et journal avant action ---------------

if [ "$TEST" = 1 ]; then
  ACTIVE2=$(cat "$SPOTIFY_ACTIVE_FILE")      || fail 'relecture etat impossible' 3
  INVOCATION2=$(cat "$SPOTIFY_INVOCATION_FILE") || fail 'relecture invocation impossible' 3
  JOURNAL2=$(cat "$SPOTIFY_JOURNAL_FILE")    || fail 'relecture journal impossible' 3
else
  SHOW_OUT2=''
  SHOW_OUT2=$(timeout 30 systemctl show "$UNIT" -p ActiveState -p InvocationID 2>/dev/null) \
    || fail 'relecture systemctl impossible' 3
  ACTIVE2=''
  INVOCATION2=''
  while IFS= read -r line2; do
    case "$line2" in
      ActiveState=*)   ACTIVE2=${line2#ActiveState=} ;;
      InvocationID=*)  INVOCATION2=${line2#InvocationID=} ;;
    esac
  done <<EOF_SHOW2
$SHOW_OUT2
EOF_SHOW2
  [ -n "$ACTIVE2" ]     || fail 'relecture etat impossible' 3
  [ -n "$INVOCATION2" ] || fail 'relecture invocation impossible' 3
  JOURNAL2=$(timeout 30 journalctl -u "$UNIT" -b _SYSTEMD_INVOCATION_ID="$INVOCATION" --no-pager --output=cat 2>/dev/null) \
    || fail 'relecture journal impossible' 3
fi

if [ "$ACTIVE2" != active ]; then
  exit 0
fi
if [ "$INVOCATION2" != "$INVOCATION" ]; then
  exit 0
fi

scan_journal "$JOURNAL2"
FAULT_AT2=$FAULT_AT

if [ "$FAULT_AT2" -lt 0 ]; then
  rm -f "$FAULT_STATE"
  exit 0
fi

# --- Horodatage de tentative ecrit AVANT l'action ---------------------------

TMP_ATTEMPT="$STATE_DIR/.attempt.$$"
printf '%s\n' "$NOW" > "$TMP_ATTEMPT" || fail 'ecriture tentative impossible' 3
mv -f "$TMP_ATTEMPT" "$ATTEMPT_STATE" || fail 'ecriture tentative impossible' 3

# --- Action : uniquement raspotify -------------------------------------------

if [ "$TEST" = 1 ]; then
  "$SPOTIFY_RESTART" restart "$UNIT" >/dev/null 2>&1 \
    || fail 'relance echouee' 4
else
  timeout 30 systemctl restart "$UNIT" >/dev/null 2>&1 \
    || fail 'relance echouee' 4
fi

rm -f "$FAULT_STATE"
printf 'spotify-relance: raspotify relance\n'
exit 0
