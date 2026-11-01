# Runbook spotify-relance — déploiement sur lenovo-openclaw (48sab)

Watchdog de relance de `raspotify` après perte de session librespot.
Mission `spotify-relance`, taille S. Contexte, mécanisme et limites :
[spec](../specs/spotify-relance.md), [rapport](../rapports/spotify-relance.md).

Périmètre strict : ce watchdog n'agit que sur l'unité `raspotify.service`.
Il ne touche jamais Home Assistant, OpenClaw, gmediarender, Docker, ALSA ni
aucun secret. Le diagnostic (session librespot morte, processus vivant) est
un fait fourni par l'humain, déjà acquis.

Toutes les commandes des blocs ci-dessous sont à exécuter **localement sur
lenovo-openclaw, en root (sudo)**, par l'humain. Elles ne sont jamais
exécutées par les agents.

## Préparation ( lecture seule)

Depuis la racine du dépôt Marantz, après fusion de la branche
`zoo/spotify-relance` :

```sh
hostname        # doit afficher 48sab : sinon STOP, mauvaise machine
git rev-parse --show-toplevel
ls scripts/spotify-relance.sh systemd/spotify-relance.service systemd/spotify-relance.timer
bash -n scripts/spotify-relance.sh && echo SYNTAXE_OK
```

Si le hostname n'est pas `48sab`, ne rien faire et vérifier la cible.

## Installation (sudo, sur 48sab)

```sh
# depuis la racine du dépôt Marantz sur lenovo-openclaw
# garde : mauvaise machine -> STOP avant toute écriture
[ "$(hostname)" = "48sab" ] || { echo "hostname inattendu: $(hostname)"; exit 1; }

# garde : collisions -> STOP avant d'écraser un fichier existant différent
for f in /usr/local/sbin/spotify-relance.sh \
         /etc/systemd/system/spotify-relance.service \
         /etc/systemd/system/spotify-relance.timer \
         /usr/local/share/doc/spotify-relance-runbook.md; do
  [ -e "$f" ] && { echo "collision: $f existe deja"; exit 1; }
done

sudo install -m 0755 scripts/spotify-relance.sh /usr/local/sbin/spotify-relance.sh
sudo install -d -m 0755 /usr/local/share/doc
sudo install -m 0644 docs/runbooks/spotify-relance.md /usr/local/share/doc/spotify-relance-runbook.md
sudo install -m 0644 systemd/spotify-relance.service /etc/systemd/system/spotify-relance.service
sudo install -m 0644 systemd/spotify-relance.timer /etc/systemd/system/spotify-relance.timer
sudo systemctl daemon-reload
sudo systemctl enable --now spotify-relance.timer
systemctl status spotify-relance.timer --no-pager
```

Première vérification 120 s après le boot du timer, puis toutes les 60 s.
Vérifier le journal : `sudo journalctl -u spotify-relance.service -b --no-pager`.

## Désinstallation (sudo, sur 48sab)

```sh
# depuis la racine du dépôt Marantz sur lenovo-openclaw
# garde : mauvaise machine -> STOP
[ "$(hostname)" = "48sab" ] || { echo "hostname inattendu: $(hostname)"; exit 1; }

sudo systemctl disable --now spotify-relance.timer
sudo systemctl stop spotify-relance.service
sudo rm -f /etc/systemd/system/spotify-relance.timer
sudo rm -f /etc/systemd/system/spotify-relance.service
sudo rm -f /usr/local/sbin/spotify-relance.sh
sudo rm -f /usr/local/share/doc/spotify-relance-runbook.md
# etat runtime du watchdog (efface de toute facon au reboot)
sudo rm -rf /run/spotify-relance
sudo systemctl daemon-reload
# raspotify reste intact : aucune action sur lui ici
systemctl status raspotify --no-pager
```

## Comportement et limites

- Détection : « Connection to server closed. » puis « Websocket peer does
  not respond. » sans « Authenticated as » ultérieur dans le journal du
  boot courant de l'invocation courante → relance après une grâce de 120 s
  depuis la première observation.
- Anti-boucle : minimum 600 s entre tentatives, même échouées ; horodatage
  écrit avant l'action ; verrou exclusif par passage.
- Silence, absence d'audio, zeroconf seul : aucune action. Unité inactive :
  laissée inactive. Observation impossible ou état invalide : aucune
  relance, code non nul dans le journal.
- Risques connus : panne sans signature, messages modifiés ou journal purgé
  non détectés. Le watchdog ne garantit que les deux signatures connues.
