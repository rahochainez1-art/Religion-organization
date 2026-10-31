# Pipeline hebdomadaire · cours de l'Institut Al Ihsan → carnet

Lis tout ce fichier avant de commencer. Règles absolues :
- **Sources religieuses fiables uniquement.** Tout texte arabe (verset, hadith) affiché doit être recopié depuis une source vérifiée
  (Coran : github.com/semarketir/quranjson, hadiths : github.com/AhmedBaset/hadith-json, versions sunnah.com) et comparé lettre par lettre
  (normalisation : sans voyelles, alif/hamza unifiés, ى→ي, ة→ه, sans « صلى الله عليه وسلم »). Jamais depuis la transcription automatique.
  Si un texte ne peut pas être vérifié, ne l'affiche pas en arabe et signale-le dans le rapport.
- **Rien d'inventé.** Les explications viennent du professeur (repère ⏱ mm:ss). Tout ajout est marqué « complément ».
- **Le contenu des cours ne doit jamais apparaître en clair dans ce dépôt public** : il va uniquement dans `espace.js` (chiffré) et
  dans la bibliothèque Claude privée. Ne commite aucun fichier de travail (audio, transcription, JSON de cours, fiches).

## 1. Choisir les cours de cette exécution
`outils/etat.json` : `faits` (déjà traités) et `rattrapage` (file d'attente). À chaque exécution :
1. le **nouveau cours** de la matière du jour (vendredi → Sîra, lundi → Tawhid + Fiqh), s'il est sur la plateforme et pas dans `faits` ;
2. **plus 1 cours** pris en tête de `rattrapage` (s'il n'est pas déjà fait).

## 2. Récupérer l'audio (navigateur intégré de l'ordinateur de Chacha)
- Sîra : https://etudiant.institutalihsan.fr/espaceetudiant/submenu/option_1ere%20ann%C3%A9e_Sira
- Tawhid + Fiqh : https://etudiant.institutalihsan.fr/espaceetudiant/submenu/maliki_1ere%20ann%C3%A9e
- Si la page de connexion s'affiche, arrête-toi et préviens Chacha (ne tape jamais de mot de passe).
- La liste « Liste des cours » contient des lignes « NN - Titre - JJ/MM/AAAA ». Clique la ligne (par JS : l'élément feuille dont le texte
  commence par « NN - »), attends ~2 s, puis lis `document.querySelector('audio').currentSrc` (lien S3 signé, valable 6 h).
- Télécharge-le dans le conteneur avec `curl -o cours.m4a "<lien>"` (le domaine s3.eu-west-par.io.cloud.ovh.net est autorisé).

## 3. Transcrire
`pip install sherpa-onnx numpy --break-system-packages` ; modèle :
`https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2` (extraire, puis
`WHISPER_DIR=<dossier>/ NT=$(nproc) python3 outils/transcribe.py cours.m4a transcript.txt`). Lance-le en arrière-plan (≈30 min / heure d'audio).
La transcription déforme l'arabe : lis-la pour le sens, puis reconstruis.

## 4. Fiches carnet (HTML, 8 à 9 pages A4)
Pars de `outils/fiche-head.html` (styles + symboles, ouvre `<main class="book">` toi-même) et écris les pages :
`<section class="page" id="pN"><div class="content">…</div><div class="foot">…</div></section>`.
Composants : `.runhead`, `h1.lettering.xl` / `h2.lettering.l`, `.kicker`, `.intro`, `.flow > .step + .arrow`, `.box` (+ `.soft`, `.dash`)
avec `<span class="tape">titre</span><span class="when">⏱ mm:ss</span>`, `.row` (`.r3`, `.r-12`, `.r-21`), `.verse` (`.ar`, `.fr`, `.ref`),
`.quote`, `table.recap`, `ul.dots`, `ol.nums`, `.hl` (surligné), `.add` (complément), schémas SVG (couleurs #E88DA9, #F7CCD9, #FFF0F5, #49332F).
Structure : page de titre + plan + schéma → pages de contenu (une idée forte par encadré, toujours le ⏱) → « À retenir » (10 points),
« Vérifier ma compréhension », « Mon lexique » → « Quiz » (12 QCM + réponses). Termine par ce script de zoom :
`<script>(function(){var b=document.querySelector('.book');function f(){var s=Math.min(1,b.clientWidth/793.7);document.querySelectorAll('.page').forEach(function(p){p.style.zoom=s})}f();addEventListener('resize',f);addEventListener('beforeprint',function(){document.querySelectorAll('.page').forEach(function(p){p.style.zoom=1})})})();</script>`
Vérifie avec Playwright qu'aucune page ne déborde (`.content` scrollHeight ≤ clientHeight) et regarde une planche des pages.
Export PDF : `page.pdf(format='A4', print_background=True)` après `emulate_media(media='print')`.

## 5. Leçons (3 niveaux) et données
Dossier de travail `cours/<id>/` (hors du dépôt) :
- `cours.json` : `{"id":"sira-03","matiere":"sira","numero":3,"titre":"…","court":"…","date":"AAAA-MM-JJ","duree":"54 min","pages":9,"statut":"fiches-pretes","resume":"…"}`
  (Tawhid + Fiqh : deux cours, `tawhid-NN` et `fiqh-NN`, chacun avec sa partie.)
- `lecons/<id>-lK.json` (4 à 6 leçons) : `{"id":"sira-03-l1","cours":"sira-03","ordre":1,"titre":"…","cartes":[{"titre":"…","arabe":"(facultatif, vérifié)","texte":"… (⏱ mm:ss)"}],"quiz":[…4 QCM…],"quiz2":[…4…],"quiz3":[…4…]}`
  QCM : `{"q":"…","choix":["bonne réponse","…","…"],"bonne":0,"explication":"(facultatif)"}` (la bonne réponse en premier, l'appli mélange).
  quiz2 (Approfondi, 4 choix, pièges) : peut contenir `{"type":"associer","q":"…","paires":[["A","a"],…]}` et `{"type":"ordre","q":"…","items":[…dans l'ordre…]}`.
  quiz3 (Expert) : textes arabes à compléter `{"q":"Complète …","ar":"… …… …","choixAr":true,"choix":["mot juste",…],"bonne":0}` (texte vérifié !)
  et une question `{"type":"redige","q":"…","modele":"…","points":["…"]}`.
- `lexique/<id>.json` : `{"id":"…","mot":"…","arabe":"…","sens":"…","matiere":"sira","source":"Sîra · cours 3"}`
- `textes/<id>.json` : `{"id":"…","type":"verset|hadith|parole","matiere":"…","ordre":N,"arabe":"…","fr":"…","ref":"… · Sîra cours 3"}`
- `fiches.html` : les fiches.

## 6. Publier
1. Espace chiffré : `CARNET_MDP=<mot de passe> python3 outils/espace.py ajouter cours/<id>/` (une fois par cours), puis
   `python3 outils/espace.py verifier`.
2. Bibliothèque Claude privée (artifact https://claude.ai/artifact/ASgJs6veUCYeaUiSx71MdU) : écrire dans sa base les mêmes documents
   (collections `cours`, `lecons`, `lexique`, `textes`, sans le champ "id" dans les données) et les passages de transcription dans `sources`
   (`{"cours":id,"matiere":…,"t":"mm:ss","texte":…}`, blocs d'environ 75 s, id `<cours>-tMMSS`). Publier les fiches comme artifact privé
   et mettre son lien dans le champ `fiches` du cours de la bibliothèque.
3. PDF dans le dossier de Chacha : `~/Desktop/RELIGION/SIRAH/COURS_NN_TITRE_fiches.pdf` (Sîra) ou `~/Desktop/RELIGION/TAWHID-FIQH/…`
   (via les outils de l'ordinateur ; dossier relié : ~/Desktop/RELIGION).
4. Mettre à jour `outils/etat.json` (ajouter à `faits`, retirer de `rattrapage`), puis `git add espace.js index.html outils/etat.json`,
   commit (auteur « Chacha » <rahochainez1@gmail.com>) et push sur main. Vérifier qu'aucun texte de cours n'est en clair dans le dépôt.

## 7. Rapport à Chacha (en français, court)
Cours traités, nombre de pages et de questions, sources vérifiées (et celles écartées), où trouver le PDF, ce qui a échoué.
