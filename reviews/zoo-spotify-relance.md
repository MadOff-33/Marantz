# Relecture — zoo/spotify-relance (commit 66e567c, base master)

**Verdict : CHANGEMENTS REQUIS (ko)**

Périmètre du diff : conforme (9 fichiers de la mission, aucun fichier de l'arbre `zoo/marantz-sante`). Cible unique `raspotify` : conforme (aucune action HA, OpenClaw, gmediarender, Docker). Aucun secret.
Tests et recette non rejoués (journal #20 : pytest 34 passed, recette exit 0). Les défauts ci-dessous ne sont pas couverts par les tests, qui injectent le journal et l'état par fixtures.

## Défauts bloquants

1. **`systemd/spotify-relance.service:16` — l'état est effacé à chaque passage, le watchdog ne relance jamais.**
   `RuntimeDirectory=spotify-relance` sans `RuntimeDirectoryPreserve=yes` : systemd supprime `/run/spotify-relance` à chaque arrêt de l'unité, donc à la fin de chaque passage oneshot. `fault.state` n'existe donc jamais au passage suivant. Le script entre toujours dans la branche « première observation » (`scripts/spotify-relance.sh:175-181`) et sort avec le code 0. La grâce n'expire jamais et aucune relance n'a lieu. `attempt.state` (cooldown) est perdu de la même façon. Cela contredit la spec (« Runtime privé conservé entre passages ») et les critères C1 et C2 en conditions réelles. Le test `units` vérifie seulement la présence textuelle de `RuntimeDirectory=` (`tests/test_spotify_relance.py:372`).
   Correction : ajouter `RuntimeDirectoryPreserve=yes` et un test qui l'exige.

2. **`scripts/spotify-relance.sh:86` et `:234` — journal non limité à l'invocation courante : faux positif au démarrage et relance en boucle.**
   `journalctl -u raspotify -b` lit tout le boot. La spec (l. 7) exige un journal « limité au boot et à cette invocation ». Après une relance par le watchdog ou un redémarrage manuel, l'ancienne signature de défaut reste la dernière ligne non résolue tant que la nouvelle instance n'a pas écrit « Authenticated as ». Or, en mode zeroconf, cette ligne n'apparaît qu'à la connexion d'un client. Le nouvel InvocationID réinitialise l'état sans effacer le défaut hérité : nouvelle grâce de 120 s, puis nouvelle relance. Une fois le défaut 1 corrigé, on obtient une relance toutes les 600 s indéfiniment sur une instance saine et inactive.
   Correction : `journalctl -b _SYSTEMD_INVOCATION_ID="$INVOCATION" --no-pager --output=cat`, à appliquer aux deux lectures (pour la relecture, utiliser `$INVOCATION2`, qui est égal à `$INVOCATION`). Ajouter un test sur l'ancien défaut d'une autre invocation, au niveau de la commande ou par une fixture de journal filtrée.

## Défauts non bloquants (à corriger dans le même lot)

3. **`scripts/spotify-relance.sh:158-159` — verrou orphelin possible une fois le défaut 1 corrigé.**
   Le trap est `EXIT` seulement. Si systemd tue le script après `TimeoutStartSec=90` (service.l.12) ou sur SIGTERM, le répertoire `lock` peut rester. Avec `RuntimeDirectoryPreserve=yes`, `mkdir` échoue ensuite à chaque passage et le script sort avec le code 0 en silence : watchdog désactivé jusqu'au reboot. Correction : `trap … EXIT INT TERM`, ou bien supprimer le verrou, devenu redondant puisqu'une unité oneshot ne s'exécute pas deux fois en parallèle. Sinon, retirer tout verrou plus ancien que `TimeoutStartSec`.
4. **`systemd/spotify-relance.service:8-17` — aucun durcissement pour un service root.**
   Ajouter au minimum `NoNewPrivileges=yes`, `ProtectSystem=strict`, `ProtectHome=yes`, `PrivateTmp=yes`, `ProtectKernelTunables=yes`, `ProtectControlGroups=yes` et `RestrictAddressFamilies=AF_UNIX`. Ces options restent compatibles avec `systemctl restart` (D-Bus via socket unix) et `journalctl`. `RuntimeDirectoryMode=0755` (l. 17) contredit « runtime privé » : utiliser `0700`.
5. **`docs/runbooks/spotify-relance.md:38-43` — installation non idempotente.**
   La garde refuse tout fichier existant. La spec (l. 18) demande de refuser seulement les collisions **différentes**, et un second passage du bloc échoue. Correction : `[ -e "$f" ] && ! cmp -s <source> "$f"` en associant chaque source à sa cible. De plus, `exit 1` (l. 35, 42, 63), collé dans un shell interactif, ferme la session de l'humain. Envelopper chaque bloc dans `sh -c '…'` ou dans un sous-shell `( … )`.

## Conforme
- Détection en deux passes (dernier « Authenticated as », puis premier défaut postérieur), à la granularité de la ligne : correcte.
- Grâce de 120 s, cooldown de 600 s écrit avant l'action, détection du recul d'horloge, revérification de l'état, de l'invocation et du journal avant l'action, unité inactive ou en échec laissée en l'état : logique correcte (sous réserve des défauts 1 et 2).
- Le timer (`OnBootSec=120s`, `OnUnitActiveSec=60s`, non persistant) n'empêche rien d'autre, et le service ne tire pas raspotify.
- Désinstallation : ordre correct (timer, service, fichiers, état, daemon-reload), raspotify intact, `rm -f` rejouable.
