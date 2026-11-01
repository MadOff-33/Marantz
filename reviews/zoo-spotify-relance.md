# Relecture — zoo/spotify-relance

## Contre-relecture 3a99db4 (diff 66e567c..3a99db4)

**Verdict : APPROUVÉ (ok)**

Seul le diff des corrections a été relu. Tests et recette n'ont pas été rejoués : selon le journal du mode code, pytest donne 38 passed et la recette C1–C5 sort avec le code 0.

| # | Défaut du verdict #21 | État |
|---|---|---|
| 1 | État effacé à chaque passage | **Levé.** `RuntimeDirectoryPreserve=yes` et `RuntimeDirectoryMode=0700` (`systemd/spotify-relance.service`). L'état reste en tmpfs, il est donc purgé au reboot comme la spec l'exige. Un test exige les deux directives. |
| 2 | Journal non limité à l'invocation | **Levé.** Les deux lectures (`scripts/spotify-relance.sh:89` et `:240`) utilisent `journalctl -u "$UNIT" -b _SYSTEMD_INVOCATION_ID="$INVOCATION"`. Le match de champ s'ajoute en conjonction aux matches de `-u`. La relecture qui utilise `$INVOCATION` reste correcte : si `INVOCATION2` diffère, l'invocation est déjà écartée (l. 247). Un test statique (2 occurrences, aucune forme non filtrée) et un scénario « nouvelle invocation saine, aucune relance » ont été ajoutés. |
| 3 | Verrou orphelin | **Levé.** `trap 'exit 0' INT TERM HUP` déclenche le trap EXIT, qui exécute `rmdir`. Bash diffère le trap jusqu'à la fin de l'enfant `timeout 30`, soit 30 s au plus, sous `TimeoutStopSec` : pas de SIGKILL attendu. |
| 4 | Durcissement absent | **Levé.** Ajout de `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `ProtectKernelTunables`, `ProtectControlGroups`, `RestrictAddressFamilies=AF_UNIX` et `ReadWritePaths=/run/spotify-relance`. Ces options restent compatibles avec `systemctl restart raspotify` : le service tourne en root, passe par le socket unix privé de systemd ou par D-Bus en AF_UNIX, sans polkit ni setuid, donc `NoNewPrivileges` ne bloque pas, et aucune écriture hors de l'état n'a lieu. `journalctl` n'a besoin que d'une lecture, autorisée sous `strict`. |
| 5 | Runbook non idempotent / `exit` | **Levé.** Les blocs sont en sous-shells `( … ) \|\| echo`. La collision n'est refusée que si `cmp -s` source/cible diffère. La désinstallation peut être rejouée. |

### Remarques non bloquantes
- Une mise à jour du script installé (contenu différent) passe par une désinstallation puis une réinstallation. Ce comportement est conforme à la spec (« refus des collisions différentes »).
- `docs/recette/spotify-relance.resultats.json` est un artefact de recette commité. Il est sans effet.

### Journal
L'entrée du mode code (impl-corr, n° #4) **est absente du journal principal** `/mnt/d/REPO CLONES/Marantz/.zoo/journal.db`, qui ne contient que #19–#21 avant cette relecture. Elle a été écrite dans `.zoo/` du worktree, non suivi. L'intégrateur doit la reporter dans le journal principal.

---

## Relecture initiale 66e567c (base master) — verdict ko, journal #21

Défauts : (1) `RuntimeDirectory` sans `RuntimeDirectoryPreserve=yes` ; (2) `journalctl -b` non filtré par `_SYSTEMD_INVOCATION_ID` ; (3) trap EXIT seul ; (4) aucun durcissement, mode 0755 ; (5) installation non idempotente, `exit` dans un shell interactif. Tous sont levés en 3a99db4 (ci-dessus).
