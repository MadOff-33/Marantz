"""Tests pytest de spotify-relance — groupes detection, guards, units, scope.

Mode test uniquement du script : journal, etat, invocation, boot, uptime,
repertoire d'etat et executable de relance factices injectes ensemble.
Fixtures sous tests/tmp/ (tmp_path de pytest est configure dessus via
conftest local si absent : ici tmp_path natif est redirige manuellement).
Aucun systemd reel, aucun sudo, aucune chaine evaluee.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "spotify-relance.sh"
SERVICE = REPO / "systemd" / "spotify-relance.service"
TIMER = REPO / "systemd" / "spotify-relance.timer"
RUNBOOK = REPO / "docs" / "runbooks" / "spotify-relance.md"

SIG_SESSION = "ERROR librespot_core::session] Connection to server closed."
SIG_DEALER = "WARN librespot_core::dealer] Websocket peer does not respond."
SIG_AUTH = 'INFO librespot_core::session] Authenticated as "user" !'
SIG_ZEROCONF = "INFO librespot_core::zeroconf] Published zeroconf service"

PATH_MIN = "/usr/bin:/bin"


class Fx:
    """Fixtures d'un passage du watchdog en mode test."""

    def __init__(self, base, restart_exit=0):
        self.base = base
        self.journal = base / "journal.txt"
        self.active = base / "active.txt"
        self.invoc = base / "invoc.txt"
        self.boot = base / "boot.txt"
        self.upt = base / "uptime.txt"
        self.state = base / "state"
        self.trace = base / "trace.txt"
        self.journal.write_text("")
        self.active.write_text("active\n")
        self.invoc.write_text("inv1\n")
        self.boot.write_text("boot1\n")
        self.set_uptime(1000)
        self.state.mkdir()
        self.trace.write_text("")
        self.restart = base / "restart"
        self.restart.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"{trace}\"\n"
            "exit {code}\n".format(trace=self.trace, code=restart_exit))
        self.restart.chmod(0o755)

    def set_uptime(self, seconds):
        self.upt.write_text("{0}.00 99999.00\n".format(seconds))

    def set_journal(self, lines):
        self.journal.write_text("".join(l + "\n" for l in lines))

    def env(self, omit=()):
        values = {
            "SPOTIFY_JOURNAL_FILE": str(self.journal),
            "SPOTIFY_ACTIVE_FILE": str(self.active),
            "SPOTIFY_INVOCATION_FILE": str(self.invoc),
            "SPOTIFY_BOOT_ID_FILE": str(self.boot),
            "SPOTIFY_UPTIME_FILE": str(self.upt),
            "SPOTIFY_STATE_DIR": str(self.state),
            "SPOTIFY_RESTART": str(self.restart),
        }
        for key in omit:
            values.pop(key, None)
        env = {"PATH": PATH_MIN, "LC_ALL": "C"}
        env.update(values)
        return env

    def run(self, omit=()):
        bash = shutil.which("bash")
        assert bash is not None
        return subprocess.run(
            [bash, str(SCRIPT), "test"],
            cwd=str(REPO), env=self.env(omit=omit),
            capture_output=True, text=True, timeout=60)

    def restarts(self):
        try:
            return self.trace.read_text().splitlines()
        except OSError:
            return []


@pytest.fixture
def fx(tmp_path):
    return Fx(tmp_path)


@pytest.fixture
def fx_fail(tmp_path):
    return Fx(tmp_path, restart_exit=1)


# ---------------------------------------------------------------- detection

def test_detection_session_closed_relance_une_fois(fx):
    fx.set_journal([SIG_SESSION, SIG_DEALER])
    r1 = fx.run()
    assert r1.returncode == 0
    assert fx.restarts() == []
    fx.set_uptime(1300)
    r2 = fx.run()
    assert r2.returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_dealer_seul_relance(fx):
    fx.set_journal([SIG_DEALER])
    fx.run()
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_auth_posterieure_annule(fx):
    fx.set_journal([SIG_SESSION, SIG_DEALER, SIG_AUTH])
    fx.run()
    fx.set_uptime(5000)
    fx.run()
    assert fx.restarts() == []
    assert not (fx.state / "fault.state").exists()


def test_detection_erreur_apres_auth_relance(fx):
    fx.set_journal([SIG_AUTH, SIG_SESSION])
    fx.run()
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_ligne_sans_rapport_nefface_pas(fx):
    fx.set_journal([SIG_SESSION, "INFO librespot_core::mercury] unrelated"])
    fx.run()
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_journal_ancien_plusieurs_jours(fx):
    fx.set_journal([SIG_SESSION])
    fx.set_uptime(900000)
    fx.run()
    fx.set_uptime(900200)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_autre_invocation_exclue(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    # invocation differente : defaut stocke perime, nouveau cycle sans action
    fx.invoc.write_text("inv2\n")
    fx.set_uptime(5000)
    assert fx.run().returncode == 0
    assert fx.restarts() == []
    # apres grace de la nouvelle observation, relance
    fx.set_uptime(5200)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_autre_boot_exclu(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.boot.write_text("boot2\n")
    fx.set_uptime(5000)
    assert fx.run().returncode == 0
    assert fx.restarts() == []
    # l'etat perime est purged puis re-ancre sur le boot courant : aucun
    # heritage de la grace de l'observation precedente
    fx.set_uptime(5200)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_detection_silence_sans_relance(fx):
    fx.set_journal(["INFO librespot_core::session] nothing to see"])
    fx.run()
    fx.set_uptime(5000)
    fx.run()
    assert fx.restarts() == []


def test_detection_journal_vide_sans_relance(fx):
    fx.run()
    fx.set_uptime(5000)
    fx.run()
    assert fx.restarts() == []


def test_detection_zeroconf_seul_sans_relance(fx):
    fx.set_journal([SIG_ZEROCONF])
    fx.run()
    fx.set_uptime(5000)
    fx.run()
    assert fx.restarts() == []


# ------------------------------------------------------------------- guards

def test_guards_grace_avant_120s(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.set_uptime(1119)
    assert fx.run().returncode == 0
    assert fx.restarts() == []


def test_guards_grace_a_120s(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.set_uptime(1120)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_guards_erreurs_repetees_ne_reportent_pas(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    # erreur repetee plus tard : la grace reste ancrée sur la premiere vue
    fx.set_journal([SIG_SESSION, SIG_SESSION, SIG_DEALER])
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_guards_cooldown_600s_apres_relance(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    # nouveau defaut juste apres la relance
    fx.set_journal([SIG_SESSION])
    fx.set_uptime(1310)
    fx.run()
    fx.set_uptime(1500)  # grace passee, cooldown non
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]
    fx.set_uptime(1905)  # 605 s apres la tentative : cooldown passe
    assert fx.run().returncode == 0
    assert len(fx.restarts()) == 2


def test_guards_cooldown_memes_echecs(fx_fail):
    fx_fail.set_journal([SIG_SESSION])
    fx_fail.run()
    fx_fail.set_uptime(1300)
    r = fx_fail.run()
    assert r.returncode != 0
    assert fx_fail.restarts() == ["restart raspotify"]
    # nouvelle tentative de refus avant 600 s : aucune action
    fx_fail.set_journal([SIG_SESSION])
    fx_fail.set_uptime(1500)
    assert fx_fail.run().returncode == 0
    assert fx_fail.restarts() == ["restart raspotify"]


def test_guards_verrou_exclusif(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.set_uptime(1300)
    (fx.state / "lock").mkdir()
    assert fx.run().returncode == 0
    assert fx.restarts() == []


def test_guards_unite_inactive_laissee_inactive(fx):
    fx.set_journal([SIG_SESSION])
    fx.active.write_text("inactive\n")
    assert fx.run().returncode == 0
    fx.set_uptime(5000)
    assert fx.run().returncode == 0
    assert fx.restarts() == []
    assert not (fx.state / "fault.state").exists()


def test_guards_recuperation_avant_action(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    # authentification apparue avant le passage decisif
    fx.set_journal([SIG_SESSION, SIG_AUTH])
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    assert fx.restarts() == []
    assert not (fx.state / "fault.state").exists()


def test_guards_lecture_refusee(fx):
    fx.set_journal([SIG_SESSION])
    fx.journal.chmod(0o000)
    r = fx.run()
    fx.journal.chmod(0o644)
    assert r.returncode != 0
    assert fx.restarts() == []


def test_guards_fixture_manquante(fx):
    fx.set_journal([SIG_SESSION])
    for var in ("SPOTIFY_JOURNAL_FILE", "SPOTIFY_ACTIVE_FILE",
                "SPOTIFY_INVOCATION_FILE", "SPOTIFY_BOOT_ID_FILE",
                "SPOTIFY_UPTIME_FILE", "SPOTIFY_STATE_DIR",
                "SPOTIFY_RESTART"):
        r = fx.run(omit=(var,))
        assert r.returncode == 2, var
    assert fx.restarts() == []


def test_guards_outil_absent_non_executable(fx):
    fx.set_journal([SIG_SESSION])
    fx.restart.chmod(0o644)
    r = fx.run()
    assert r.returncode == 2
    assert fx.restarts() == []


def test_guards_etat_corrompu_sans_action(fx):
    fx.set_journal([SIG_SESSION])
    fx.upt.write_text("pas-un-nombre\n")
    r = fx.run()
    assert r.returncode != 0
    assert fx.restarts() == []


def test_guards_etat_stocke_corrompu_nouveau_cycle(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    (fx.state / "fault.state").write_text("garbage\n")
    fx.set_uptime(5000)
    assert fx.run().returncode == 0
    assert fx.restarts() == []
    fx.set_uptime(5200)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]


def test_guards_recul_horloge(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.set_uptime(900)  # horloge avant la premiere observation
    r = fx.run()
    assert r.returncode != 0
    assert fx.restarts() == []


def test_guards_echec_relance_code_non_nul(fx_fail):
    fx_fail.set_journal([SIG_SESSION])
    fx_fail.run()
    fx_fail.set_uptime(1300)
    r = fx_fail.run()
    assert r.returncode == 4
    # la tentative echouee compte pour le cooldown
    assert (fx_fail.state / "attempt.state").exists()


# -------------------------------------------------------------------- units

def test_units_service_texte():
    text = SERVICE.read_text()
    assert "Type=oneshot" in text
    assert "ExecStart=/usr/local/sbin/spotify-relance.sh" in text
    assert "TimeoutStartSec=90" in text
    assert "RuntimeDirectory=spotify-relance" in text
    # aucune dependance demarrant raspotify
    for banned in ("Requires=", "Wants=", "BindsTo=", "PartOf=", "Upholds="):
        assert banned not in text, banned
    assert "Restart=" not in text


def test_units_timer_texte():
    text = TIMER.read_text()
    assert "OnBootSec=120s" in text
    assert "OnUnitActiveSec=60s" in text
    assert "Persistent=true" not in text
    assert "WantedBy=timers.target" in text


def test_units_verify_systemd_analyze(tmp_path):
    analyze = shutil.which("systemd-analyze")
    copies = tmp_path / "units"
    copies.mkdir()
    # le chemin du depot contient une espace : ExecStart le refuserait ;
    # copie du script reel (contenu identique) sous un chemin sans espace
    local_script = copies / "spotify-relance.sh"
    shutil.copy2(SCRIPT, local_script)
    local_script.chmod(0o755)
    svc = copies / "spotify-relance.service"
    svc.write_text(SERVICE.read_text().replace(
        "/usr/local/sbin/spotify-relance.sh", str(local_script)))
    (copies / "spotify-relance.timer").write_text(TIMER.read_text())
    if analyze is None:
        pytest.skip("systemd-analyze indisponible : controle textuel seul")
    result = subprocess.run(
        [analyze, "verify", str(svc), str(copies / "spotify-relance.timer")],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


# -------------------------------------------------------------------- scope

PROTECTED = ("gmediarender", "homeassistant", "home-assistant",
             "openclaw", "docker", "alsactl", "amixer")


def test_scope_trace_unique_cible(fx):
    fx.set_journal([SIG_SESSION])
    fx.run()
    fx.set_uptime(1300)
    assert fx.run().returncode == 0
    assert fx.restarts() == ["restart raspotify"]
    # apres relance, defaut resolu : plus aucune action meme a long terme
    fx.set_uptime(50000)
    fx.run()
    assert fx.restarts() == ["restart raspotify"]


def test_scope_script_statique():
    text = SCRIPT.read_text()
    assert "UNIT=raspotify" in text
    # cible constante, jamais parametrable ni passee au shell
    assert "eval" not in text
    assert '"$UNIT"' in text
    for banned in PROTECTED:
        assert banned not in text.lower(), banned


def sh_blocks():
    """Tous les blocs de code sh du runbook : les seules commandes reelles."""
    blocks = []
    current = []
    in_block = False
    for line in RUNBOOK.read_text().splitlines():
        stripped = line.strip()
        if stripped == "```sh":
            in_block = True
            current = []
            continue
        if in_block and stripped == "```":
            blocks.append(current)
            in_block = False
            continue
        if in_block:
            current.append(line)
    return blocks


def test_scope_runbook_installation():
    blocks = sh_blocks()
    assert blocks, "aucun bloc sh dans le runbook"
    all_lines = [l for b in blocks for l in b]
    assert any("install -m 0755 scripts/spotify-relance.sh /usr/local/sbin/spotify-relance.sh" in l
               for l in all_lines)
    assert any("install -m 0644 systemd/spotify-relance.service /etc/systemd/system/spotify-relance.service" in l
               for l in all_lines)
    assert any("install -m 0644 systemd/spotify-relance.timer /etc/systemd/system/spotify-relance.timer" in l
               for l in all_lines)
    assert any("daemon-reload" in l for l in all_lines)
    assert any("enable --now spotify-relance.timer" in l for l in all_lines)
    # garde hostname et collisions presentes dans les blocs
    assert any('$(hostname)" = "48sab"' in l for l in all_lines)
    assert any("collision" in l for l in all_lines)


def test_scope_runbook_desinstallation():
    blocks = sh_blocks()
    all_lines = [l for b in blocks for l in b]
    assert any("disable --now spotify-relance.timer" in l for l in all_lines)
    assert any("rm -f /etc/systemd/system/spotify-relance.timer" in l for l in all_lines)
    assert any("rm -f /etc/systemd/system/spotify-relance.service" in l for l in all_lines)
    assert any("rm -f /usr/local/sbin/spotify-relance.sh" in l for l in all_lines)
    assert any("rm -rf /run/spotify-relance" in l for l in all_lines)
    assert any("daemon-reload" in l for l in all_lines)
    # desinstallation limitee aux fichiers propres
    for line in all_lines:
        if "rm " in line:
            assert "spotify-relance" in line, line


def test_scope_runbook_aucune_action_protegee():
    # seules les lignes de commande des blocs sh sont des actions ; les
    # mentions explicatives du texte ne comptent pas
    blocks = sh_blocks()
    all_lines = [l for b in blocks for l in b]
    for banned in PROTECTED:
        for line in all_lines:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            assert banned not in line.lower(), (banned, line)
    # raspotify intact : aucune commande de gestion de raspotify dans les blocs
    for line in all_lines:
        if "raspotify" in line:
            assert "systemctl" not in line or "status" in line, line
