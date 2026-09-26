[app]

# --- Informazioni generali dell'app ---
title = Calcolatore Resa Multiforme
package.name = calcolatoreresamultiforme
package.domain = org.ninozsistem

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf

version = 1.0.0

# --- Dipendenze Python ---
# Non fissiamo la versione esatta di kivy: farlo può causare errori di
# compilazione Android con alcune versioni (documentato dagli stessi
# sviluppatori di Buildozer) — lasciamo che scelga da sola la versione
# che sa già compilare correttamente.
# kivymd invece VA fissato a 1.2.0: dalla versione 2.0 in poi KivyMD ha
# cambiato profondamente le proprie funzioni interne (non è più
# compatibile con il codice di questa app).
# "pillow" non serve: l'app non lo usa (serviva solo in fase di
# preparazione delle immagini sul computer).
requirements = python3,kivy,kivymd==1.2.0,plyer

# --- Icona e schermata di avvio ---
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #F7F3EC

# --- Orientamento e comportamento ---
orientation = portrait
fullscreen = 0

# --- Permessi Android ---
# Nessun permesso speciale necessario: il pulsante "Condividi" usa il
# selettore di sistema (ACTION_SEND) che non richiede permessi extra.
android.permissions =

# --- Configurazione Android ---
android.api = 34
android.minapi = 21
android.ndk = 25b
# Una sola architettura (arm64-v8a, quella di tutti gli smartphone
# Android recenti): compilare per due architetture insieme attiva un
# bug noto e recente di python-for-android che corrompe l'installazione
# di pip a metà build, causando errori di dipendenze (tra cui proprio
# quello con le tante versioni di kivymd). Se in futuro serve supportare
# anche dispositivi molto vecchi (pre-2018 circa), si può aggiungere
# ", armeabi-v7a" una volta che quel bug sarà risolto a monte.
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

# Icona adattiva (opzionale, migliora l'aspetto sui launcher moderni)
# android.adaptive_icon_foreground = %(source.dir)s/assets/icon.png
# android.adaptive_icon_background = #F7F3EC

[buildozer]
log_level = 2
warn_on_root = 1
