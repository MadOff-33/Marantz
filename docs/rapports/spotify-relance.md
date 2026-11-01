# Rapport consolidé — spotify-relance

## Objectif et mandat

TAILLE S ; GO humain déjà donné. Cadrage documentaire seulement : [spec courte](../specs/spotify-relance.md), [recette locale](../recette/spotify-relance.json), présent rapport. Aucun code, test, commande Git, sudo, SSH ou action Lenovo dans cette phase. Le runbook et les exécutables sont des livrables de l'implémentation future, pas du cadrage.

## Fait fourni par l'humain — 2026-11-01

Sur lenovo-openclaw, hostname 48sab, raspotify/librespot reste actif pour systemd alors que la session Spotify est morte depuis le 15/10. Derniers messages : « ERROR librespot_core::session] Connection to server closed. », puis « WARN librespot_core::dealer] Websocket peer does not respond. », puis silence. Le redémarrage manuel de raspotify répare : « Authenticated as … », puis « Published zeroconf service ». La politique de redémarrage sur échec est inopérante puisque le processus ne termine pas. Diagnostic acquis, non reproduit. Aucune identité Spotify collectée.

Autre **fait fourni par l'humain** : branche courante zoo/marantz-sante avec milliers de modifications non commitées, à préserver intégralement ; mission future sur zoo/spotify-relance depuis master, worktree isolé [.zoo-work/wt-spotify-relance](../../.zoo-work/wt-spotify-relance). Métadonnées de session cohérentes avec ce fait ; aucune vérification Git exécutée.

## Chronologie

| Date | Mode | Résultat |
| --- | --- | --- |
| 2026-11-01 | architect | Lecture ciblée du workflow, du routeur, des consignes et des exemples ; diagnostic humain conservé sans nouvelle investigation. |
| 2026-11-01 | architect | Cadrage : watchdog journal par invocation, grâce 120 s, timer 60 s, anti-boucle 600 s ; plan et matrice ci-dessous. |
| 2026-11-01 | code, sous-tâche documentaire | Création de la recette JSON uniquement, cinq critères locaux ; aucune commande ni implémentation. |
| 2026-11-01 | architect | Relecture de la recette : correspondance C1–C5, champs repris de l'exemple, aucun accès distant ; validation exécutable différée. |

## Sources vérifiées par lecture

- [Workflow](../../.workflow/workflow-system/WORKFLOW.md:7) et [préflight](../../.workflow/workflow-system/procedures/00-session-preflight.md:5) : isolation avant contexte métier ; commandes différées, car hors capacités et mandat de cette phase. Aucun autre worktree n'est déclaré résolu. Pas de lecture du contexte métier ni de l'état d'une autre mission.
- [Routeur](../../.workflow/workflow-system/ROUTER.md:3) : phase documentaire R0 ; mission corrective future R5, diagnostic déjà acquis. Skill writing-plans chargé ; livrables courts et emplacement imposés par la demande, sans plan concurrent ni nouvelle spec longue.
- [Consignes](../../CLAUDE.md:17), [recette existante](../recette/marantz-sante.json:6) : champs mission, criteres, etapes ; étapes locales avec commande, code_attendu, sortie_contient, sortie_absente, timeout, go_humain.
- [Santé](../../scripts/marantz-sante.sh:35), [tests](../../tests/test_marantz_sante.py:79), [socle de fixtures](../../tests/marantz_common.py:13) : injection de binaires factices, environnement isolé et données temporaires dans le dépôt. Références consultées uniquement, sans modification ni copie transversale.

## Décisions techniques et matrice d'acceptation

Pas d'ADR pour cette mission S. Bash et outils système usuels, sans sonde réseau, sans dépendance Spotify externe. Le watchdog ne garantit que la détection des deux signatures connues de session interrompue ; aucune preuve de lecture audio n'est prétendue.

Les cinq critères de la [recette](../recette/spotify-relance.json) doivent appeler les tests ciblés suivants ; chaque groupe doit contenir des assertions réelles, sans tests ignorés ou succès sur exception :

| Critère | Sélecteur ou contrôle | Assertions obligatoires |
| --- | --- | --- |
| C1 | detection | Chacune des deux erreurs anciennes non résolues entraîne exactement une relance de raspotify ; authentification postérieure annule ; erreur après authentification relance ; ligne sans rapport après erreur ne l'efface pas ; journal ancien de plusieurs jours traité ; autre invocation/boot exclus ; silence, journal vide et zeroconf seul sans relance. |
| C2 | guards | Grâce avant/à 120 s ; erreurs répétées sans report infini ; cooldown avant/à 600 s, y compris échec de restart ; verrou/concurrence ; unité inactive ; récupération et changement d'invocation avant action ; lecture refusée, timeout, fixture manquante, outil absent, état corrompu et recul d'horloge : aucune action réelle. Vérifier code non nul sur défaut d'observation et échec de relance. |
| C3 | syntaxe | Syntaxe Bash valide ; shellcheck obligatoire si disponible, absence explicitement signalée sinon. |
| C4 | units | Contrôle textuel systématique service/timer : oneshot, chemins exacts, bornes, intervalle, runtime privé conservé, pas de dépendance sur un service tiers. Si systemd-analyze est disponible : verify obligatoire sur copie temporaire des unités avec seul chemin de l'exécutable remplacé par le script local existant ; toute erreur est conservée, jamais transformée en succès ou repli textuel. Sinon absence annoncée et contrôle textuel seul. Aucun manager systemd lancé. |
| C5 | scope | Traces des binaires factices : seule mutation cible raspotify.service ; unité non paramétrable, aucun eval. Inspection statique des exécutables/unités et de tous les blocs exécutables du runbook : aucune action sur les services protégés, Docker ou audio. Valider blocs installation/désinstallation complets, garde hostname, collisions, droits root et nettoyage limité aux fichiers propres. Les mentions explicatives hors blocs ne sont pas des actions. |

Nom du futur module : [tests/test_spotify_relance.py](../../tests/test_spotify_relance.py). Tests compatibles pytest, sans modifier les tests existants ; isoler tous les processus système par doubles stricts. Le mode test n'autorise jamais une commande réelle par défaut : journal, identifiants, état, horloges et exécutable de restart factice requis ensemble. La commande injectée est un chemin d'exécutable appelé avec les arguments constants de restart et d'unité, pas une chaîne évaluée. L'installation n'active jamais ce mode.

### Lots futurs et gates

Après résolution des worktrees, commande de création prévue, **non exécutée**, depuis la racine du dépôt ; une commande Git par appel, seulement si branche et destination sont absentes :

```sh
git worktree add -b zoo/spotify-relance ".zoo-work/wt-spotify-relance" master
```

- [ ] Résoudre worktrees et baseline ; lire la gouvernance du checkout retenu ; créer/réutiliser sans écrasement le worktree dédié depuis master ; y recopier uniquement les trois documents de cette mission ; lire le journal partagé de mission.
- [ ] Vérifier le format de la recette par l'outil Zoo ; ne pas changer les critères après GO pour masquer un échec. Vérifier venv/pytest et outils locaux ; aucun paquet global ni commande sur le Lenovo.
- [ ] Lot logique : [script](../../scripts/spotify-relance.sh) et [tests](../../tests/test_spotify_relance.py), critères C1/C2/C3/C5 ; écrire les régressions rouges, constater leur échec, implémenter, conserver les sorties.
- [ ] Lot intégration : [service](../../systemd/spotify-relance.service), [timer](../../systemd/spotify-relance.timer), [runbook](../runbooks/spotify-relance.md), critères C4/C5. Fournir commandes exactes sudo locales et contrôle des collisions ; ne pas les exécuter.
- [ ] Une revue indépendante finale du diff complet et des cinq critères, puis recette locale par l'intégrateur avant fusion. Aucun déploiement, commit ou push autorisé par le seul présent cadrage. L'humain exécute ensuite les blocs Lenovo.

## Commandes et preuves

Aucune commande exécutée : codes de sortie non disponibles. Lecture et écriture documentaires uniquement ; pas de preuve de tests verts, de conformité du validateur Zoo ou d'état distant. Le format a été repris de la recette existante ; sa validation effective incombe au mode code. Les étapes de la recette sont toutes locales et sans GO humain requis ; toute future étape visant le Lenovo devra porter le marqueur de GO humain, même si elle ne fait que lire.

## Écarts, état et prochaine étape

Le préflight Git/runtime et la lecture du journal nécessitent un terminal : reportés, pas supposés réussis. La création du worktree est reportée à l'exécution ; les documents préparés dans le checkout courant ne doivent jamais justifier d'y travailler sur le code. La restriction architecte autorise seulement Markdown : transcription du JSON déléguée à un mode autorisé, mandat limité à ce seul document, sans commande ni implémentation.

État : trois livrables documentaires créés ; cohérence contrôlée par lecture, format de recette non validé par exécution, aucun déploiement effectué. Prochaine étape distincte : reprendre les trois livrables dans le worktree dédié, valider la recette puis appliquer les lots ci-dessus sous le GO déjà acquis ; ne pas redemander confirmation ni refaire le diagnostic humain.

## Entrée journal à transmettre au prochain mode avec terminal

Paramètres : --mission spotify-relance --lot cadrage --role architect --type spec --statut ok

Résumé : cadrage documentaire S ; diagnostic humain acquis ; détection journal par invocation, grâce 120 s, cooldown 600 s ; cinq critères locaux ; code et déploiement non exécutés. Critères : C1 C2 C3 C4 C5. Fichiers : les trois documents indexés ci-dessous. Lire les entrées existantes avant ajout et éviter un doublon. Aucun ajout au journal réalisé dans cette phase.

## Index des livrables

- [Spec et plan de fichiers](../specs/spotify-relance.md)
- [Recette exécutable locale — cinq critères, validation différée](../recette/spotify-relance.json)
- [Rapport consolidé](spotify-relance.md)
