# Spotify relance — cadrage S

**Besoin.** Relancer seulement raspotify sur Lenovo 48sab si la session meurt sans arrêt du processus. GO acquis ; cadrage documentaire sans commande. Diagnostic du 01/11 : **fait fourni par l'humain**, à ne pas refaire ; [rapport](../rapports/spotify-relance.md).

## Mécanisme retenu

Watchdog Bash, oneshot root et timer toutes les 60 s, première vérification après 120 s. Cible constante : raspotify, jamais paramétrable. Lire état et identifiant d'invocation ; journal chronologique horodaté limité au boot et à cette invocation, sans fenêtre récente excluant l'erreur du 15/10.

Détecter les signatures librespot session « Connection to server closed. » et dealer « Websocket peer does not respond. ». Sans « Authenticated as » ultérieur, relancer après 120 s depuis le premier défaut non résolu ; les erreurs répétées ne repoussent pas la grâce. Silence, absence d'audio et zeroconf seuls ne déclenchent rien ; unité inactive laissée inactive.

Revérifier état, invocation et journal avant action ; abandon si récupération/changement. Verrou exclusif ; minimum 600 s entre **tentatives**, même échouées, par uptime, horodatage atomique écrit avant action. Runtime privé conservé entre passages, effacé au reboot. Observation impossible, outil absent ou état invalide : aucune relance, code non nul. Commandes bornées, une tentative/passage, aucune identité ni journal brut en sortie.

## Plan de fichiers et tests

- [Script](../../scripts/spotify-relance.sh) : mode test explicite, journal fichier/horloges/état/exécutable factice injectés ensemble ; fixture manquante = refus, jamais systemd réel, jamais chaîne évaluée.
- [Service](../../systemd/spotify-relance.service) et [timer](../../systemd/spotify-relance.timer) : runtime privé conservé, oneshot borné, timer non persistant ; aucun drop-in ni dépendance démarrant raspotify.
- [Tests](../../tests/test_spotify_relance.py) : groupes detection, guards, units, scope ; fixtures dans tests/tmp, PATH isolé ; inspiration [socle existant](../../tests/marantz_common.py:13), sans modification. Matrice au rapport.
- [Runbook](../runbooks/spotify-relance.md) : blocs exacts installation/désinstallation sudo, humain local sur 48sab ; script sous /usr/local/sbin, unités sous /etc/systemd/system. Garde hostname, refus des collisions différentes. Désinstallation : arrêter/désactiver timer puis watchdog, retirer seulement leurs fichiers/état, recharger systemd ; laisser raspotify intact.
- [Recette](../recette/spotify-relance.json) : cinq critères locaux ; validateur Zoo à lancer au mode code. Toute étape Lenovo ajoutée porte le marqueur GO humain.

## Préconditions, hors périmètre et risques

**Git.** Arbre zoo/marantz-sante : milliers de modifications humaines, à ne toucher/embarquer sous aucun prétexte. Résoudre les worktrees puis ajouter zoo/spotify-relance depuis master sous [.zoo-work/wt-spotify-relance](../../.zoo-work/wt-spotify-relance) ; commande au rapport. Si collision, inspecter sans écraser. Recopier seulement les trois documents, aucun script/test voisin. Vérifier venv/pytest, outils et recette ; aucune dépendance nouvelle prévue.

**Exclusions :** Home Assistant, OpenClaw, DLNA/gmediarender, Docker, ALSA, secrets, diagnostic distant, déploiement automatique. **Risques :** faux positif interrompant l'audio ; panne sans signature, messages modifiés ou journal purgé non détectés. Suite distincte : tests rouges, implémentation ciblée, une revue indépendante finale, recette locale ; sudo humain uniquement.
