# Come trasformare questo progetto in un file .apk installabile

## 🔧 Novità di questa revisione

- **Causa reale del terzo errore trovata (grazie al log completo che hai
  condiviso)**: Buildozer era impostato per compilare per **due
  architetture insieme** (`arm64-v8a` e `armeabi-v7a`). Un bug recente
  e documentato di python-for-android (corretto a monte solo a fine
  luglio 2026) fa sì che, compilando due architetture di seguito nella
  stessa esecuzione, la seconda trovi un'installazione di `pip`
  corrotta lasciata dalla prima — questo è ciò che causava sia
  l'errore `BuildDependencyInstallError` sia la cascata di tentativi
  con decine di versioni diverse di `kivymd` che si vedeva nel log
  (non era affatto un problema di quale versione di KivyMD fosse
  scelta). **Corretto compilando per una sola architettura,
  `arm64-v8a`** — quella di tutti gli smartphone Android recenti — che
  evita del tutto quel percorso di codice difettoso.
- **Dipendenze rese più affidabili** (dalla revisione precedente):
  rimosso il pin `kivy==2.3.0` (bug noto di compilazione su Kivy 2.2+)
  e rimosso `pillow` dai requisiti Android (inutilizzato e causa nota
  di errori). `kivymd` resta fissato a `1.2.0`: dalla versione 2.0 in
  poi l'interfaccia interna è cambiata radicalmente e il codice di
  questa app non sarebbe più compatibile.
- **Secondo errore di build trovato e corretto** (revisione precedente):
  nel primo tentativo di passare all'immagine Docker ufficiale avevo
  forzato un comando manuale (`chown`) sovrascrivendo l'avvio interno
  dell'immagine — proprio quell'avvio interno serve ad allineare i
  permessi della cartella di progetto, quindi bypassandolo il comando
  manuale falliva. Ora il workflow chiama l'immagine `kivy/buildozer`
  esattamente come documentato ufficialmente, senza forzature.
- **Causa del primo errore di build**: il workflow usava un'azione di
  terze parti (`ArtemSBulgakov/buildozer-action`) il cui Dockerfile
  interno ha smesso di funzionare per un problema esterno (prova ad
  aggiungere un repository Java non ancora compatibile con l'ultima
  immagine Ubuntu pubblicata su Docker Hub — lo stesso problema che il
  team ufficiale di Kivy aveva già risolto in passato nella propria
  immagine). Il workflow ora usa **direttamente l'immagine Docker
  ufficiale di Buildozer** (`kivy/buildozer`, mantenuta dal team Kivy),
  eliminando la dipendenza da quell'azione di terze parti, che la
  stessa documentazione di Kivy segnala come potenzialmente obsoleta.
- **Pulizia codice**: rimossa una funzione di validazione rimasta
  inutilizzata da una revisione precedente.
- **Layout**: risolti gli spazi vuoti che comparivano quando si
  nascondevano dei campi (es. cambio modalità di calcolo).
- **Pulsanti risultato**: "Copia" e "Condividi" ora fanno davvero due
  cose diverse (prima erano identici per errore); "Copia" conferma con
  un breve "✅ Copiato!".
- **Validazione**: i campi con un valore mancante o a zero ora si
  colorano di rosso con un messaggio, invece di fallire in silenzio.
- **Nuovo pulsante "ℹ️ Informazioni"** in alto, con licenza e crediti
  (mancava nella versione mobile).
- **Risultato più leggibile**: ora è in un riquadro colorato ben
  visibile invece di semplice testo.
- **Più tipi di marmellata**: aggiunte "Confettura (60:40)" e "Senza
  zucchero aggiunto (dolcificante)"; aggiunti 12 nuovi frutti (kiwi,
  fico, melone, zucca, rabarbaro, ananas, mela cotogna, melograno,
  ribes, lampone, mora, susina) e 2 varietà di pomodoro in più (ramato,
  ciliegino), più il formato bottiglia da 1500 ml.

---


Questa cartella contiene l'app **Calcolatore Resa** già pronta, scritta in
Python con Kivy/KivyMD (l'equivalente di PyQt5 ma per smartphone). Manca
solo l'ultimo passaggio — la **compilazione** — che richiede strumenti
Android (SDK/NDK) molto pesanti da installare. Qui sotto trovi due modi
per ottenere il file `.apk`, dal più semplice al più avanzato.

---

## ✅ Metodo consigliato: GitHub Actions (gratuito, nessuna installazione)

Questo metodo compila l'APK "nel cloud": tu carichi solo il codice,
GitHub fa il lavoro pesante e ti restituisce il file pronto.

1. **Crea un account gratuito** su [github.com](https://github.com) se non
   lo hai già.
2. Crea un **nuovo repository** (può essere privato), ad esempio chiamato
   `calcolatore-resa-multiforme`.
3. **Carica tutto il contenuto di questa cartella** nel repository
   (trascina i file dalla pagina del repository su GitHub, oppure usa
   Git se lo conosci). Assicurati che la cartella `.github/workflows/`
   con dentro `build-apk.yml` venga caricata correttamente (su alcuni
   sistemi le cartelle che iniziano con il punto sono nascoste: verifica
   di vederla anche tu prima di caricare).
4. Vai sulla scheda **"Actions"** in alto nel repository. Dovrebbe
   partire automaticamente una compilazione chiamata "Build APK
   Android" (la prima volta può impiegare 15-25 minuti: scarica e
   prepara tutti gli strumenti Android).
5. Quando il pallino diventa verde ✅, apri quella esecuzione e in
   basso troverai un file scaricabile chiamato
   **"calcolatore-resa-apk"**: dentro c'è il tuo `.apk`.
6. Scarica lo zip, estrai l'APK e installalo sul telefono (vedi sotto
   "Installare l'APK sul telefono").

Ogni volta che modifichi il codice e lo ricarichi su GitHub, una nuova
compilazione partirà da sola.

---

## 🖥️ Metodo alternativo: compilare da un computer Linux (o WSL su Windows)

Se preferisci compilare da un tuo computer Linux (buildozer **non
funziona su Windows nativo**, serve Linux oppure WSL):

```bash
# 1. Installa le dipendenze di sistema (esempio per Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip build-essential git python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    openjdk-17-jdk unzip

# 2. Installa buildozer
pip3 install --user buildozer cython

# 3. Entra nella cartella del progetto e compila
cd calcolatore_resa_android
buildozer android debug
```

Il file `.apk` verrà creato dentro la cartella `bin/` al termine della
compilazione (la prima volta scarica automaticamente Android SDK/NDK,
quindi serve una connessione internet buona e un po' di pazienza: 20-40
minuti).

---

## 📲 Installare l'APK sul telefono

1. Copia il file `.apk` sul telefono Android (via cavo USB, email a te
   stesso, Google Drive, WhatsApp, ecc.).
2. Apri il file dal telefono: Android chiederà il permesso di
   **"installare app da fonti sconosciute"** — è normale, capita per
   qualsiasi app non scaricata dal Play Store. Concedi il permesso
   all'app che stai usando per aprire il file (es. "File" o "Gmail").
3. Segui la procedura di installazione guidata: comparirà l'icona
   scelta e il nome "Calcolatore Resa Multiforme".

L'app funziona su qualunque telefono Android **5.0 o successivo**
(praticamente tutti i telefoni in uso oggi).

---

## 🧪 Provare l'app anche su PC (facoltativo, prima di compilare)

Se vuoi vederla funzionare subito sul computer, senza aspettare la
compilazione Android:

```bash
pip install -r requirements.txt
python main.py
```

Si aprirà una finestra che mostra esattamente la stessa interfaccia che
poi vedrai sul telefono — utile per controllare i calcoli prima di
generare l'APK.

---

## 🔄 Aggiornare i dati (frutti, formati vasetto, ecc.)

Come nella versione desktop, i valori di partenza sono nel codice
(`main.py`, dizionario `DEFAULT_DATA`). Le modifiche fatte dall'app
stessa (es. "Nuovo formato vasetto") vengono salvate automaticamente
nella cartella privata dei dati dell'app sul telefono, e restano anche
dopo aver chiuso l'app.

---

## 🆘 Se la build fallisce ancora

Con le correzioni di questa revisione la build dovrebbe completarsi.
Se dovesse fallire lo stesso, il modo più veloce per risolvere è
**copiare il testo esatto dell'errore** (non solo una foto):

1. Apri la scheda "Actions" del repository, poi l'esecuzione fallita.
2. Clicca sullo step segnato con la ✗ rossa per espanderlo.
3. Cerca l'icona a forma di ingranaggio ⚙️ in alto a destra del riquadro
   dei log → "Copy log" (oppure seleziona e copia a mano le ultime
   20-30 righe, quelle appena sopra "Error").
4. Incolla quel testo (non serve tradurlo, va bene anche in inglese).

Una foto dello schermo va bene comunque, ma il testo copiato è più
preciso: evita problemi di leggibilità e, soprattutto, eventuali
traduzioni automatiche del browser che possono alterare nomi tecnici
(è già successo con "user" tradotto in "utente" dentro un comando).

## ℹ️ Note

- Il file `buildozer.spec` è già configurato con nome, icona, schermata
  di avvio (presplash) e permessi minimi necessari.
- **Compatibilità telefoni**: l'app è compilata solo per architettura
  `arm64-v8a` (64 bit), quella di tutti gli smartphone Android venduti
  da diversi anni a questa parte. Non si installerà su telefoni molto
  vecchi (indicativamente pre-2018, solo 32 bit) — una platea ormai
  molto ridotta.
- Non è richiesto nessun permesso invasivo: l'app non accede a
  contatti, posizione, fotocamera, ecc.
- Se in futuro vuoi pubblicare l'app sul Google Play Store, serve in
  aggiunta un account sviluppatore Google (a pagamento, una tantum) e
  generare un APK/AAB "firmato" — un passaggio successivo, non
  necessario per usare l'app internamente in cooperativa.
