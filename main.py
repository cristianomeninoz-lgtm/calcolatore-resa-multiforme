#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcolatore Resa Prodotti — Cooperativa Multiforme di Soave (VR)
Versione Android (Kivy / KivyMD)
=================================================================

Stessa logica di calcolo del programma desktop (PyQt5), riadattata
con un'interfaccia pensata per smartphone: navigazione in basso,
campi numerici con tastierino, schede scorrevoli.

Licenza: MIT — Software libero e open source.
Realizzato da Ninoz Sistem per la Cooperativa Multiforme di Soave (VR).
"""

import os
import json
import math
import traceback
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog

APP_TITLE = "Calcolatore Resa"
APP_SUBTITLE = "Marmellate, Confetture & Passata di Pomodoro"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
ICON_PATH = os.path.join(BASE_DIR, "assets", "icon.png")

# ---------------------------------------------------------------------------
# Dati di default (identici alla versione desktop)
# ---------------------------------------------------------------------------

DEFAULT_DATA = {
    "jam_density_kg_per_l": 1.30,
    "tomato_density_kg_per_l": 1.03,
    "fruits": [
        {"name": "Mela", "loss": 15},
        {"name": "Pera", "loss": 15},
        {"name": "Albicocca", "loss": 18},
        {"name": "Pesca", "loss": 17},
        {"name": "Prugna", "loss": 16},
        {"name": "Fragola", "loss": 20},
        {"name": "Ciliegia", "loss": 18},
        {"name": "Uva", "loss": 16},
        {"name": "Agrumi (arancia/limone)", "loss": 14},
        {"name": "Mirtillo / Frutti di bosco", "loss": 19},
        {"name": "Kiwi", "loss": 17},
        {"name": "Fico", "loss": 16},
        {"name": "Melone", "loss": 22},
        {"name": "Zucca", "loss": 20},
        {"name": "Rabarbaro", "loss": 24},
        {"name": "Ananas", "loss": 25},
        {"name": "Mela cotogna", "loss": 20},
        {"name": "Melograno", "loss": 30},
        {"name": "Ribes", "loss": 15},
        {"name": "Lampone", "loss": 12},
        {"name": "Mora", "loss": 14},
        {"name": "Susina", "loss": 16},
    ],
    "product_types": [
        {"name": "Confettura Extra (65 frutta : 35 zucchero)", "ratio": 0.35},
        {"name": "Confettura (60 frutta : 40 zucchero)", "ratio": 0.40},
        {"name": "Marmellata classica (50 : 50)", "ratio": 0.50},
        {"name": "Composta / poco zucchero (75 : 25)", "ratio": 0.25},
        {"name": "Senza zucchero aggiunto (solo dolcificante, ~5%)", "ratio": 0.05},
    ],
    "jam_jar_sizes_ml": [106, 212, 314, 370, 500, 720, 1000],
    "tomato_varieties": [
        {"name": "San Marzano / Roma", "yield": 65},
        {"name": "Cuore di bue", "yield": 62},
        {"name": "Perino / Datterino", "yield": 68},
        {"name": "Ramato", "yield": 66},
        {"name": "Ciliegino", "yield": 60},
        {"name": "Misto orto", "yield": 65},
    ],
    "tomato_jar_sizes_ml": [250, 500, 750, 1000, 1500],
}


def get_data_path():
    """Su Android i file dell'app vanno salvati nella cartella dati
    privata e persistente dell'app (user_data_dir), non nella cartella
    di installazione che è di sola lettura."""
    app = App.get_running_app()
    if app is not None:
        return os.path.join(app.user_data_dir, "recipes.json")
    return os.path.join(BASE_DIR, "recipes.json")


def load_data():
    path = get_data_path()
    if not os.path.exists(path):
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    path = get_data_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Logica di calcolo (identica, parola per parola, alla versione desktop)
# ---------------------------------------------------------------------------

def calc_jam_forward(fruit_kg, ratio, loss_pct, pectin_rate, jar_ml, density):
    sugar_kg = fruit_kg * (ratio / (1 - ratio))
    return _jam_from_fruit_and_sugar(fruit_kg, sugar_kg, loss_pct, pectin_rate, jar_ml, density, manual_sugar=False)


def calc_jam_forward_manual_sugar(fruit_kg, sugar_kg, loss_pct, pectin_rate, jar_ml, density):
    return _jam_from_fruit_and_sugar(fruit_kg, sugar_kg, loss_pct, pectin_rate, jar_ml, density, manual_sugar=True)


def _jam_from_fruit_and_sugar(fruit_kg, sugar_kg, loss_pct, pectin_rate, jar_ml, density, manual_sugar):
    total_raw = fruit_kg + sugar_kg
    final_kg = total_raw * (1 - loss_pct / 100)
    pectin_g = pectin_rate * fruit_kg
    liters = final_kg / density
    jars = math.floor((liters * 1000) / jar_ml) if jar_ml > 0 else 0
    return {
        "fruit_kg": fruit_kg, "sugar_kg": sugar_kg, "pectin_g": pectin_g,
        "total_raw_kg": total_raw, "final_kg": final_kg, "liters": liters,
        "jars": jars, "jar_ml": jar_ml, "loss_pct": loss_pct,
        "manual_sugar": manual_sugar,
    }


def calc_jam_reverse(jars_wanted, jar_ml, ratio, loss_pct, pectin_rate, density):
    final_kg = jars_wanted * (jar_ml / 1000) * density
    total_raw = final_kg / (1 - loss_pct / 100)
    fruit_kg = total_raw * (1 - ratio)
    sugar_kg = total_raw * ratio
    pectin_g = pectin_rate * fruit_kg
    liters = final_kg / density
    return {
        "fruit_kg": fruit_kg, "sugar_kg": sugar_kg, "pectin_g": pectin_g,
        "total_raw_kg": total_raw, "final_kg": final_kg, "liters": liters,
        "jars": jars_wanted, "jar_ml": jar_ml, "loss_pct": loss_pct,
        "manual_sugar": False,
    }


def calc_tom_forward(tom_kg, yield_pct, salt_per_l, basil_per_l, bottle_ml, density):
    passata_kg = tom_kg * (yield_pct / 100)
    liters = passata_kg / density
    salt_g = liters * salt_per_l
    basil = round(liters * basil_per_l)
    bottles = math.floor((liters * 1000) / bottle_ml) if bottle_ml > 0 else 0
    return {
        "tom_kg": tom_kg, "passata_kg": passata_kg, "liters": liters,
        "salt_g": salt_g, "basil": basil, "bottles": bottles,
        "bottle_ml": bottle_ml, "yield_pct": yield_pct,
    }


def calc_tom_reverse(bottles_wanted, bottle_ml, yield_pct, salt_per_l, basil_per_l, density):
    liters = bottles_wanted * (bottle_ml / 1000)
    passata_kg = liters * density
    tom_kg = passata_kg / (yield_pct / 100)
    salt_g = liters * salt_per_l
    basil = round(liters * basil_per_l)
    return {
        "tom_kg": tom_kg, "passata_kg": passata_kg, "liters": liters,
        "salt_g": salt_g, "basil": basil, "bottles": bottles_wanted,
        "bottle_ml": bottle_ml, "yield_pct": yield_pct,
    }


def fmt(n, dec=2):
    return f"{n:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def parse_float(text, default=0.0):
    if not text:
        return default
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return default


def parse_int(text, default=0):
    try:
        return int(float(text.replace(",", ".")))
    except (ValueError, AttributeError):
        return default


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def decimal_filter(substring, from_undo):
    """Filtro per i campi numerici: accetta cifre, virgola e punto (in
    Italia il separatore decimale è la virgola, ma accettiamo entrambi)."""
    return "".join(ch for ch in substring if ch in "0123456789.,")


# ---------------------------------------------------------------------------
# Palette colori — coerente con il logo della cooperativa, professionale
# ---------------------------------------------------------------------------

COLOR_BG = (0.97, 0.96, 0.93, 1)          # crema chiaro
COLOR_CARD = (1, 1, 1, 1)                 # bianco
COLOR_PRIMARY = (0.16, 0.38, 0.32, 1)     # verde bosco (freschezza / natura)
COLOR_PRIMARY_DARK = (0.10, 0.27, 0.22, 1)
COLOR_ACCENT = (0.80, 0.55, 0.18, 1)      # ambra / miele
COLOR_TEXT = (0.18, 0.16, 0.13, 1)
COLOR_MUTED = (0.45, 0.43, 0.40, 1)


# ---------------------------------------------------------------------------
# Widget riutilizzabili
# ---------------------------------------------------------------------------

class Card(MDCard):
    """Scheda con ombra leggera, coerente in tutta l'app (MDCard include
    già il comportamento di elevazione/ombra)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding", dp(16))
        kwargs.setdefault("spacing", dp(10))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("elevation", 1)
        kwargs.setdefault("radius", [dp(14)] * 4)
        kwargs.setdefault("md_bg_color", COLOR_CARD)
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter("height"))


def section_title(text):
    return MDLabel(
        text=text, bold=True, font_style="Subtitle1",
        theme_text_color="Custom", text_color=COLOR_PRIMARY_DARK,
        size_hint_y=None, height=dp(28),
    )


def field_label(text):
    return MDLabel(
        text=text, theme_text_color="Custom", text_color=COLOR_MUTED,
        font_style="Caption", size_hint_y=None, height=dp(18),
    )


def section_title_row(text, on_reset=None):
    """Titolo di sezione con, opzionalmente, un piccolo pulsante
    'Reimposta' allineato a destra — utile per tornare rapidamente ai
    valori di partenza dopo aver fatto più calcoli di fila."""
    row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
    row.add_widget(section_title(text))
    if on_reset:
        reset_btn = MDIconButton(
            icon="restore", theme_text_color="Custom", text_color=COLOR_MUTED,
            size_hint=(None, None), size=(dp(28), dp(28)),
        )
        reset_btn.bind(on_release=lambda *_: on_reset())
        row.add_widget(reset_btn)
    return row


def focus_select_all(text_field):
    """Seleziona tutto il testo quando si tocca un campo numerico, così
    per correggere un valore basta scrivere subito il nuovo, senza
    dover prima cancellare a mano quello vecchio."""
    def on_focus(instance, has_focus):
        if has_focus:
            instance.select_all()
    text_field.bind(focus=on_focus)
    return text_field


def styled_spinner(values, initial, on_select):
    sp = Spinner(
        text=initial, values=values, size_hint_y=None, height=dp(46),
        background_normal="", background_color=COLOR_PRIMARY,
        color=(1, 1, 1, 1), font_size="15sp",
    )
    sp.bind(text=lambda inst, val: on_select(val))
    return sp


def number_field(hint, value="", suffix=""):
    tf = MDTextField(
        hint_text=hint + (f" ({suffix})" if suffix else ""),
        text=str(value),
        input_filter=decimal_filter,
        input_type="number",
        size_hint_y=None,
        height=dp(48),
    )
    return focus_select_all(tf)


class SegmentedControl(MDBoxLayout):
    """Selettore a due opzioni (come uno switch iOS/Android) per scegliere
    la direzione del calcolo: diretto oppure inverso."""

    def __init__(self, left_text, right_text, on_change, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(44),
                          spacing=dp(4), **kwargs)
        self.on_change = on_change
        self.left_btn = MDFlatButton(
            text=left_text, size_hint_x=0.5,
            md_bg_color=COLOR_PRIMARY, theme_text_color="Custom", text_color=(1, 1, 1, 1),
        )
        self.right_btn = MDFlatButton(
            text=right_text, size_hint_x=0.5,
            md_bg_color=(0.90, 0.89, 0.86, 1), theme_text_color="Custom", text_color=COLOR_TEXT,
        )
        self.left_btn.bind(on_release=lambda *_: self._select(True))
        self.right_btn.bind(on_release=lambda *_: self._select(False))
        self.add_widget(self.left_btn)
        self.add_widget(self.right_btn)
        self.is_left = True

    def _select(self, left):
        self.is_left = left
        self.left_btn.md_bg_color = COLOR_PRIMARY if left else (0.90, 0.89, 0.86, 1)
        self.left_btn.text_color = (1, 1, 1, 1) if left else COLOR_TEXT
        self.right_btn.md_bg_color = (0.90, 0.89, 0.86, 1) if left else COLOR_PRIMARY
        self.right_btn.text_color = COLOR_TEXT if left else (1, 1, 1, 1)
        self.on_change(left)


class WeightField(MDBoxLayout):
    """Campo peso con pulsante kg/g accanto, come nella versione desktop.
    Mantiene internamente il valore sempre in kg."""

    def __init__(self, hint, kg_value=1.0, on_change=None, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(48),
                          spacing=dp(6), **kwargs)
        self._unit = "kg"
        self._on_change = on_change
        self.input = MDTextField(
            hint_text=f"{hint} (kg)", text=fmt(kg_value), input_filter=decimal_filter,
            input_type="number", size_hint_x=1,
        )
        focus_select_all(self.input)
        self.input.bind(text=lambda *_: self._changed())
        self.unit_btn = MDRaisedButton(
            text="kg", size_hint=(None, None), width=dp(56), height=dp(40),
            md_bg_color=COLOR_ACCENT,
        )
        self.unit_btn.bind(on_release=lambda *_: self._toggle_unit())
        self.add_widget(self.input)
        self.add_widget(self.unit_btn)
        self._hint = hint

    def _toggle_unit(self):
        current_kg = self.get_kg()
        self._unit = "g" if self._unit == "kg" else "kg"
        self.unit_btn.text = self._unit
        self.input.hint_text = f"{self._hint} ({self._unit})"
        self.set_kg(current_kg)

    def _changed(self):
        if self._on_change:
            self._on_change()

    def get_kg(self):
        v = parse_float(self.input.text, 0.0)
        return v if self._unit == "kg" else v / 1000.0

    def set_kg(self, kg_value):
        v = kg_value if self._unit == "kg" else kg_value * 1000.0
        self.input.text = fmt(v, 2 if self._unit == "kg" else 0)


class ResultBanner(MDBoxLayout):
    """Riquadro colorato ed evidente per il risultato principale
    (es. '🫙 12 vasetti da 500 ml'), più leggibile di una semplice etichetta."""

    text = StringProperty("—")

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(56))
        kwargs.setdefault("padding", (dp(12), dp(4)))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_PRIMARY)
            self._rect = RoundedRectangle(radius=[dp(14)] * 4, pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.label = MDLabel(
            text=self.text, halign="center", bold=True, font_style="H5",
            theme_text_color="Custom", text_color=(1, 1, 1, 1),
        )
        self.add_widget(self.label)
        self.bind(text=lambda inst, val: setattr(self.label, "text", val))

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


def make_result_rows(container, rows):
    container.clear_widgets()
    for k, v in rows:
        row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
        left = MDLabel(text=k, theme_text_color="Custom", text_color=COLOR_MUTED,
                        font_style="Body2")
        right = MDLabel(text=v, theme_text_color="Custom", text_color=COLOR_TEXT,
                         font_style="Body2", halign="right", bold=True)
        right.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        row.add_widget(left)
        row.add_widget(right)
        container.add_widget(row)


def add_jar_size_popup(existing_sizes, on_add, title="Nuovo formato"):
    box = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16),
                       size_hint_y=None, height=dp(140))
    tf = MDTextField(hint_text="Capacità in ml", input_filter="int", input_type="number")
    box.add_widget(MDLabel(text=title, bold=True, size_hint_y=None, height=dp(24)))
    box.add_widget(tf)
    btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(44))
    popup = Popup(title="", content=box, size_hint=(0.85, None), height=dp(220),
                   separator_height=0)

    def confirm(*_):
        ml = parse_int(tf.text, 0)
        if ml > 0:
            on_add(ml)
        popup.dismiss()

    ok_btn = MDRaisedButton(text="Aggiungi", md_bg_color=COLOR_PRIMARY)
    ok_btn.bind(on_release=confirm)
    cancel_btn = MDFlatButton(text="Annulla")
    cancel_btn.bind(on_release=lambda *_: popup.dismiss())
    btn_row.add_widget(cancel_btn)
    btn_row.add_widget(ok_btn)
    box.add_widget(btn_row)
    popup.open()


def copy_text(text):
    """Copia il testo negli appunti del telefono (sempre disponibile)."""
    Clipboard.copy(text)


def share_text(text):
    """Apre il selettore di condivisione di Android (WhatsApp, email,
    ecc.). Se non è disponibile (es. su desktop durante un test), copia
    il testo negli appunti come ripiego."""
    if platform == "android":
        try:
            from plyer import share
            share.share(text=text)
            return
        except Exception:
            pass
    copy_text(text)


def mark_invalid(text_field, invalid, message="Inserisci un valore maggiore di zero"):
    """Segnala visivamente un campo non valido (bordo ed etichetta
    rossi), al posto di un popup di errore invasivo su mobile."""
    text_field.helper_text_mode = "on_error"
    text_field.helper_text = message
    text_field.error = invalid


def flash_feedback(btn, temp_text):
    """Cambia per un istante il testo di un pulsante per confermare
    all'utente che l'azione è andata a buon fine (es. 'Copiato!')."""
    original = btn.text
    btn.text = temp_text
    btn.disabled = True

    def restore(*_):
        btn.text = original
        btn.disabled = False

    Clock.schedule_once(restore, 1.2)


# ---------------------------------------------------------------------------
# Scheda "Marmellate / Confetture"
# ---------------------------------------------------------------------------

class JamContent(ScrollView):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.mode_forward = True
        self.manual_sugar = False
        self.last_result_text = ""
        self._ready = False
        self._build_ui()
        self._ready = True
        self.calculate()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical", spacing=dp(14), padding=dp(14),
                            size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))
        self.add_widget(root)

        # --- Ricetta ---
        recipe = Card()
        recipe.add_widget(section_title("🍓  Ricetta"))

        recipe.add_widget(field_label("Frutto"))
        fruit_names = [f["name"] for f in self.data["fruits"]]
        self.fruit_spinner = styled_spinner(fruit_names, fruit_names[0], self._on_fruit_changed)
        recipe.add_widget(self.fruit_spinner)

        recipe.add_widget(field_label("Tipo di prodotto"))
        type_names = [t["name"] for t in self.data["product_types"]]
        self.type_spinner = styled_spinner(type_names, type_names[0], lambda v: self.calculate())
        recipe.add_widget(self.type_spinner)

        self.loss_field = number_field("Perdita in cottura", 15, "%")
        self.loss_field.bind(text=lambda *_: self.calculate())
        recipe.add_widget(self.loss_field)

        self.pectin_field = number_field("Pectina aggiunta", 0, "g/kg frutta")
        self.pectin_field.bind(text=lambda *_: self.calculate())
        recipe.add_widget(self.pectin_field)

        root.add_widget(recipe)

        # --- Calcolo ---
        calc = Card()
        calc.add_widget(section_title_row("⚖️  Calcolo", on_reset=self._reset_calc))
        calc.add_widget(MDLabel(
            text="Scegli il verso del calcolo:", font_style="Caption",
            theme_text_color="Custom", text_color=COLOR_MUTED,
            size_hint_y=None, height=dp(18)))
        self.mode_switch = SegmentedControl(
            "Da peso frutta", "Da n. vasetti", self._on_mode_changed)
        calc.add_widget(self.mode_switch)

        # Contenitore dinamico: mostra solo i campi pertinenti alla
        # direzione di calcolo scelta, senza lasciare spazi vuoti.
        self.weight_field = WeightField("Peso frutta netta", 10, self.calculate)

        self.sugar_toggle_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        self.sugar_toggle_row.add_widget(MDLabel(text="Specificare io lo zucchero", font_style="Body2"))
        self.manual_sugar_switch = MDSwitch()
        self.manual_sugar_switch.bind(active=self._on_manual_sugar_toggled)
        self.sugar_toggle_row.add_widget(self.manual_sugar_switch)

        self.sugar_field = WeightField("Zucchero da aggiungere", 5, self.calculate)

        self.jars_wanted_field = number_field("Vasetti desiderati", 100)
        self.jars_wanted_field.bind(text=lambda *_: self.calculate())

        self.dynamic_box = MDBoxLayout(orientation="vertical", spacing=dp(10),
                                        size_hint_y=None)
        self.dynamic_box.bind(minimum_height=self.dynamic_box.setter("height"))
        calc.add_widget(self.dynamic_box)
        self._refresh_dynamic_fields()

        calc.add_widget(field_label("Formato vasetto"))
        jar_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(46))
        jar_values = [f"{ml} ml" for ml in self.data["jam_jar_sizes_ml"]]
        self.jar_spinner = styled_spinner(jar_values, jar_values[0], lambda v: self.calculate())
        jar_row.add_widget(self.jar_spinner)
        add_btn = MDIconButton(icon="plus-circle", theme_text_color="Custom", text_color=COLOR_ACCENT)
        add_btn.bind(on_release=lambda *_: self._add_jar_size())
        jar_row.add_widget(add_btn)
        calc.add_widget(jar_row)

        root.add_widget(calc)

        # --- Risultato ---
        result = Card()
        result.add_widget(section_title("📊  Risultato"))
        self.big_result = ResultBanner()
        result.add_widget(self.big_result)
        self.result_rows = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.result_rows.bind(minimum_height=self.result_rows.setter("height"))
        result.add_widget(self.result_rows)

        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(44))
        self.copy_btn = MDFlatButton(text="📋  Copia", on_release=lambda *_: self._copy())
        self.share_btn = MDRaisedButton(text="📤  Condividi", md_bg_color=COLOR_ACCENT,
                                         on_release=lambda *_: self._share())
        btn_row.add_widget(self.copy_btn)
        btn_row.add_widget(self.share_btn)
        result.add_widget(btn_row)

        root.add_widget(result)

    def _on_fruit_changed(self, name):
        for f in self.data["fruits"]:
            if f["name"] == name:
                self.loss_field.text = fmt(float(f["loss"]), 0)
                break
        self.calculate()

    def _refresh_dynamic_fields(self):
        """Ricostruisce il contenitore dinamico con solo i campi utili
        alla modalità corrente, senza lasciare spazi vuoti nel layout."""
        self.dynamic_box.clear_widgets()
        if self.mode_forward:
            self.dynamic_box.add_widget(self.weight_field)
            self.dynamic_box.add_widget(self.sugar_toggle_row)
            if self.manual_sugar:
                self.dynamic_box.add_widget(self.sugar_field)
        else:
            self.dynamic_box.add_widget(self.jars_wanted_field)

        # Il "tipo di prodotto" (rapporto frutta/zucchero) non serve
        # quando lo zucchero viene inserito a mano: lo disabilitiamo per
        # evitare di far credere che influenzi ancora il risultato.
        manual_forward = self.mode_forward and self.manual_sugar
        self.type_spinner.disabled = manual_forward
        self.type_spinner.background_color = (0.78, 0.77, 0.74, 1) if manual_forward else COLOR_PRIMARY
        self.type_spinner.color = (0.55, 0.53, 0.50, 1) if manual_forward else (1, 1, 1, 1)

    def _on_mode_changed(self, is_forward):
        self.mode_forward = is_forward
        self._refresh_dynamic_fields()
        self.calculate()

    def _reset_calc(self):
        """Riporta la sezione 'Calcolo' ai valori di partenza, comodo
        dopo aver fatto più simulazioni di fila."""
        if not self.mode_forward:
            self.mode_switch._select(True)
        self.manual_sugar_switch.active = False
        self.weight_field.set_kg(10)
        self.jars_wanted_field.text = "100"
        self.sugar_field.set_kg(5)
        self.calculate()

    def _on_manual_sugar_toggled(self, instance, active):
        self.manual_sugar = active
        self._refresh_dynamic_fields()
        self.calculate()

    def _add_jar_size(self):
        def on_add(ml):
            if ml not in self.data["jam_jar_sizes_ml"]:
                self.data["jam_jar_sizes_ml"].append(ml)
                self.data["jam_jar_sizes_ml"].sort()
                save_data(self.data)
            values = [f"{m} ml" for m in self.data["jam_jar_sizes_ml"]]
            self.jar_spinner.values = values
            self.jar_spinner.text = f"{ml} ml"
        add_jar_size_popup(self.data["jam_jar_sizes_ml"], on_add, "Nuovo formato vasetto")

    def _current_ratio(self):
        name = self.type_spinner.text
        for t in self.data["product_types"]:
            if t["name"] == name:
                return t["ratio"]
        return 0.5

    def _current_jar_ml(self):
        try:
            return int(self.jar_spinner.text.replace(" ml", ""))
        except ValueError:
            return self.data["jam_jar_sizes_ml"][0]

    def calculate(self, *args):
        if not self._ready:
            return
        ratio = self._current_ratio()
        loss_pct = clamp(parse_float(self.loss_field.text, 15), 0.0, 60.0)
        pectin_rate = clamp(parse_float(self.pectin_field.text, 0), 0.0, 50.0)
        jar_ml = self._current_jar_ml()
        density = self.data.get("jam_density_kg_per_l", 1.30)
        fruit_name = self.fruit_spinner.text

        if self.mode_forward:
            fruit_kg = self.weight_field.get_kg()
            if fruit_kg <= 0:
                mark_invalid(self.weight_field.input, True)
                self.big_result.text = "—"
                make_result_rows(self.result_rows, [])
                return
            mark_invalid(self.weight_field.input, False)
            if self.manual_sugar:
                sugar_kg = self.sugar_field.get_kg()
                r = calc_jam_forward_manual_sugar(fruit_kg, sugar_kg, loss_pct, pectin_rate, jar_ml, density)
            else:
                r = calc_jam_forward(fruit_kg, ratio, loss_pct, pectin_rate, jar_ml, density)
        else:
            jars_wanted = parse_int(self.jars_wanted_field.text, 100)
            r = calc_jam_reverse(jars_wanted, jar_ml, ratio, loss_pct, pectin_rate, density)

        self.big_result.text = f"🫙  {r['jars']} vasetti da {r['jar_ml']} ml"
        sugar_label = "Zucchero (inserito a mano)" if r.get("manual_sugar") else "Zucchero necessario"
        rows = [
            ("Frutto", fruit_name),
            ("Frutta necessaria", f"{fmt(r['fruit_kg'])} kg"),
            (sugar_label, f"{fmt(r['sugar_kg'])} kg"),
        ]
        if r["pectin_g"] > 0:
            rows.append(("Pectina", f"{fmt(r['pectin_g'])} g"))
        rows.append(("Resa finale (prodotto cotto)", f"{fmt(r['final_kg'])} kg"))
        make_result_rows(self.result_rows, rows)

        lines = [
            f"MARMELLATA / CONFETTURA — {fruit_name}",
            "Cooperativa Multiforme di Soave (VR)",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "-" * 40,
            f"RISULTATO: {r['jars']} vasetti da {r['jar_ml']} ml",
            "-" * 40,
        ] + [f"{k}: {v}" for k, v in rows]
        self.last_result_text = "\n".join(lines)

    def _copy(self):
        if self.last_result_text:
            copy_text(self.last_result_text)
            flash_feedback(self.copy_btn, "✅  Copiato!")

    def _share(self):
        if self.last_result_text:
            share_text(self.last_result_text)


# ---------------------------------------------------------------------------
# Scheda "Passata di Pomodoro"
# ---------------------------------------------------------------------------

class TomatoContent(ScrollView):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.mode_forward = True
        self.last_result_text = ""
        self._ready = False
        self._build_ui()
        self._ready = True
        self.calculate()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical", spacing=dp(14), padding=dp(14),
                            size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))
        self.add_widget(root)

        recipe = Card()
        recipe.add_widget(section_title("🍅  Ricetta"))

        recipe.add_widget(field_label("Varietà pomodoro"))
        variety_names = [v["name"] for v in self.data["tomato_varieties"]]
        self.variety_spinner = styled_spinner(variety_names, variety_names[0], self._on_variety_changed)
        recipe.add_widget(self.variety_spinner)

        self.yield_field = number_field("Resa stimata", 65, "%")
        self.yield_field.bind(text=lambda *_: self.calculate())
        recipe.add_widget(self.yield_field)

        self.salt_field = number_field("Sale", 8, "g/litro")
        self.salt_field.bind(text=lambda *_: self.calculate())
        recipe.add_widget(self.salt_field)

        self.basil_field = number_field("Basilico", 2, "foglie/litro")
        self.basil_field.bind(text=lambda *_: self.calculate())
        recipe.add_widget(self.basil_field)

        root.add_widget(recipe)

        calc = Card()
        calc.add_widget(section_title_row("⚖️  Calcolo", on_reset=self._reset_calc))
        calc.add_widget(MDLabel(
            text="Scegli il verso del calcolo:", font_style="Caption",
            theme_text_color="Custom", text_color=COLOR_MUTED,
            size_hint_y=None, height=dp(18)))
        self.mode_switch = SegmentedControl(
            "Da peso pomodoro", "Da n. bottiglie", self._on_mode_changed)
        calc.add_widget(self.mode_switch)

        self.weight_field = WeightField("Peso pomodoro fresco", 20, self.calculate)

        self.bottles_wanted_field = number_field("Bottiglie desiderate", 50)
        self.bottles_wanted_field.bind(text=lambda *_: self.calculate())

        self.dynamic_box = MDBoxLayout(orientation="vertical", spacing=dp(10),
                                        size_hint_y=None)
        self.dynamic_box.bind(minimum_height=self.dynamic_box.setter("height"))
        calc.add_widget(self.dynamic_box)
        self._refresh_dynamic_fields()

        calc.add_widget(field_label("Formato bottiglia"))
        jar_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(46))
        jar_values = [f"{ml} ml" for ml in self.data["tomato_jar_sizes_ml"]]
        self.jar_spinner = styled_spinner(jar_values, jar_values[0], lambda v: self.calculate())
        jar_row.add_widget(self.jar_spinner)
        add_btn = MDIconButton(icon="plus-circle", theme_text_color="Custom", text_color=COLOR_ACCENT)
        add_btn.bind(on_release=lambda *_: self._add_jar_size())
        jar_row.add_widget(add_btn)
        calc.add_widget(jar_row)

        root.add_widget(calc)

        result = Card()
        result.add_widget(section_title("📊  Risultato"))
        self.big_result = ResultBanner()
        result.add_widget(self.big_result)
        self.result_rows = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(2))
        self.result_rows.bind(minimum_height=self.result_rows.setter("height"))
        result.add_widget(self.result_rows)

        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(44))
        self.copy_btn = MDFlatButton(text="📋  Copia", on_release=lambda *_: self._copy())
        self.share_btn = MDRaisedButton(text="📤  Condividi", md_bg_color=COLOR_ACCENT,
                                         on_release=lambda *_: self._share())
        btn_row.add_widget(self.copy_btn)
        btn_row.add_widget(self.share_btn)
        result.add_widget(btn_row)

        root.add_widget(result)

    def _on_variety_changed(self, name):
        for v in self.data["tomato_varieties"]:
            if v["name"] == name:
                self.yield_field.text = fmt(float(v["yield"]), 0)
                break
        self.calculate()

    def _refresh_dynamic_fields(self):
        self.dynamic_box.clear_widgets()
        if self.mode_forward:
            self.dynamic_box.add_widget(self.weight_field)
        else:
            self.dynamic_box.add_widget(self.bottles_wanted_field)

    def _on_mode_changed(self, is_forward):
        self.mode_forward = is_forward
        self._refresh_dynamic_fields()
        self.calculate()

    def _reset_calc(self):
        """Riporta la sezione 'Calcolo' ai valori di partenza."""
        if not self.mode_forward:
            self.mode_switch._select(True)
        self.weight_field.set_kg(20)
        self.bottles_wanted_field.text = "50"
        self.calculate()

    def _add_jar_size(self):
        def on_add(ml):
            if ml not in self.data["tomato_jar_sizes_ml"]:
                self.data["tomato_jar_sizes_ml"].append(ml)
                self.data["tomato_jar_sizes_ml"].sort()
                save_data(self.data)
            values = [f"{m} ml" for m in self.data["tomato_jar_sizes_ml"]]
            self.jar_spinner.values = values
            self.jar_spinner.text = f"{ml} ml"
        add_jar_size_popup(self.data["tomato_jar_sizes_ml"], on_add, "Nuovo formato bottiglia")

    def _current_bottle_ml(self):
        try:
            return int(self.jar_spinner.text.replace(" ml", ""))
        except ValueError:
            return self.data["tomato_jar_sizes_ml"][0]

    def calculate(self, *args):
        if not self._ready:
            return
        yield_pct = clamp(parse_float(self.yield_field.text, 65), 1.0, 100.0)
        salt_per_l = clamp(parse_float(self.salt_field.text, 8), 0.0, 50.0)
        basil_per_l = clamp(parse_float(self.basil_field.text, 2), 0.0, 20.0)
        bottle_ml = self._current_bottle_ml()
        density = self.data.get("tomato_density_kg_per_l", 1.03)
        variety_name = self.variety_spinner.text

        if yield_pct <= 0:
            mark_invalid(self.yield_field, True, "La resa deve essere maggiore di zero")
            self.big_result.text = "—"
            make_result_rows(self.result_rows, [])
            return
        mark_invalid(self.yield_field, False)
        yield_pct = min(yield_pct, 100.0)

        if self.mode_forward:
            tom_kg = self.weight_field.get_kg()
            if tom_kg <= 0:
                mark_invalid(self.weight_field.input, True)
                self.big_result.text = "—"
                make_result_rows(self.result_rows, [])
                return
            mark_invalid(self.weight_field.input, False)
            r = calc_tom_forward(tom_kg, yield_pct, salt_per_l, basil_per_l, bottle_ml, density)
        else:
            bottles_wanted = parse_int(self.bottles_wanted_field.text, 50)
            r = calc_tom_reverse(bottles_wanted, bottle_ml, yield_pct, salt_per_l, basil_per_l, density)

        self.big_result.text = f"🍶  {r['bottles']} bottiglie da {r['bottle_ml']} ml"
        rows = [
            ("Varietà", variety_name),
            ("Pomodoro necessario", f"{fmt(r['tom_kg'])} kg"),
            ("Passata ottenuta (peso)", f"{fmt(r['passata_kg'])} kg"),
            ("Passata ottenuta (volume)", f"{fmt(r['liters'])} litri"),
            ("Sale necessario", f"{fmt(r['salt_g'])} g"),
        ]
        if r["basil"] > 0:
            rows.append(("Foglie di basilico", f"{r['basil']}"))
        make_result_rows(self.result_rows, rows)

        lines = [
            f"PASSATA DI POMODORO — {variety_name}",
            "Cooperativa Multiforme di Soave (VR)",
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "-" * 40,
            f"RISULTATO: {r['bottles']} bottiglie da {r['bottle_ml']} ml",
            "-" * 40,
        ] + [f"{k}: {v}" for k, v in rows]
        self.last_result_text = "\n".join(lines)

    def _copy(self):
        if self.last_result_text:
            copy_text(self.last_result_text)
            flash_feedback(self.copy_btn, "✅  Copiato!")

    def _share(self):
        if self.last_result_text:
            share_text(self.last_result_text)


# ---------------------------------------------------------------------------
# App principale
# ---------------------------------------------------------------------------

class CalcolatoreApp(MDApp):
    def build(self):
        # Se qualcosa va storto nella costruzione della schermata,
        # mostriamo l'errore a schermo (con un modo per condividerlo)
        # invece di chiudere l'app di colpo senza alcuna spiegazione.
        try:
            return self._build_ui()
        except Exception:
            return self._build_error_screen(traceback.format_exc())

    def _build_ui(self):
        self.title = APP_TITLE
        self.icon = ICON_PATH if os.path.exists(ICON_PATH) else None
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Orange"
        Window.clearcolor = COLOR_BG

        self.data = load_data()

        root = MDBoxLayout(orientation="vertical", md_bg_color=COLOR_BG)

        # Header con il logo reale della cooperativa
        header = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(72),
            padding=(dp(16), dp(10)), spacing=dp(12), md_bg_color=(1, 1, 1, 1),
        )
        from kivy.uix.image import Image as KvImage
        if os.path.exists(LOGO_PATH):
            logo_img = KvImage(source=LOGO_PATH, size_hint=(None, None),
                                height=dp(34), width=dp(34 * 4.87))
            header.add_widget(logo_img)
        title_box = MDBoxLayout(orientation="vertical")
        title_box.add_widget(MDLabel(
            text="🍯 " + APP_TITLE, bold=True, font_style="Subtitle1",
            theme_text_color="Custom", text_color=COLOR_PRIMARY_DARK))
        title_box.add_widget(MDLabel(
            text=APP_SUBTITLE, font_style="Caption",
            theme_text_color="Custom", text_color=COLOR_MUTED))
        header.add_widget(title_box)

        info_btn = MDIconButton(icon="information-outline", theme_text_color="Custom",
                                 text_color=COLOR_MUTED)
        info_btn.bind(on_release=lambda *_: self._show_about())
        header.add_widget(info_btn)

        root.add_widget(header)

        # Navigazione in basso (equivalente mobile della sidebar desktop).
        # Le proprietà di colore extra vengono impostate DOPO la
        # creazione, una per una e in modo protetto: se una di queste
        # non esistesse in questa versione di KivyMD, l'app userebbe
        # semplicemente lo stile di default invece di bloccarsi.
        nav = MDBottomNavigation()
        for attr, val in (
            ("panel_color", (1, 1, 1, 1)),
            ("text_color_normal", COLOR_MUTED),
            ("text_color_active", COLOR_PRIMARY),
        ):
            try:
                setattr(nav, attr, val)
            except Exception:
                pass

        jam_tab = MDBottomNavigationItem(name="jam", text="Marmellate", icon="food-apple")
        jam_tab.add_widget(JamContent(self.data))
        nav.add_widget(jam_tab)

        tom_tab = MDBottomNavigationItem(name="tomato", text="Passata", icon="cup")
        tom_tab.add_widget(TomatoContent(self.data))
        nav.add_widget(tom_tab)

        root.add_widget(nav)
        return root

    def _build_error_screen(self, tb_text):
        """Schermata di emergenza: se l'avvio normale fallisce, mostra
        l'errore invece di chiudere l'app senza spiegazioni, e permette
        di salvarlo/condividerlo per poterlo correggere."""
        try:
            log_path = os.path.join(self.user_data_dir, "ultimo_errore.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(tb_text)
        except Exception:
            log_path = None

        box = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12),
                           md_bg_color=(1, 1, 1, 1))
        box.add_widget(MDLabel(
            text="⚠️ Si è verificato un errore all'avvio",
            bold=True, font_style="H6", theme_text_color="Custom",
            text_color=(0.7, 0.15, 0.1, 1), size_hint_y=None, height=dp(40),
        ))
        box.add_widget(MDLabel(
            text="Copia o condividi il testo qui sotto e inviamelo: mi serve per correggere il problema.",
            font_style="Body2", theme_text_color="Custom", text_color=COLOR_MUTED,
            size_hint_y=None, height=dp(48),
        ))

        scroll = ScrollView()
        err_label = MDLabel(
            text=tb_text, theme_text_color="Custom", text_color=(0.3, 0.05, 0.05, 1),
            font_style="Caption", size_hint_y=None, halign="left", valign="top",
        )
        err_label.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1]),
        )
        scroll.add_widget(err_label)
        box.add_widget(scroll)

        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(10),
                               size_hint_y=None, height=dp(46))
        copy_btn = MDFlatButton(text="📋 Copia", on_release=lambda *_: copy_text(tb_text))
        share_btn = MDRaisedButton(text="📤 Condividi", md_bg_color=COLOR_ACCENT,
                                    on_release=lambda *_: share_text(tb_text))
        btn_row.add_widget(copy_btn)
        btn_row.add_widget(share_btn)
        box.add_widget(btn_row)

        return box

    def _show_about(self):
        dialog = MDDialog(
            title="ℹ️ Informazioni",
            text=(
                f"{APP_TITLE}\n"
                "Cooperativa Multiforme di Soave (VR)\n\n"
                "Software libero e open source (licenza MIT). Calcola quanti "
                "vasetti o bottiglie risulteranno da una certa quantità di "
                "ingredienti, o viceversa quanti ingredienti servono per un "
                "numero desiderato di unità.\n\n"
                "I valori proposti sono medie standard, modificabili nella "
                "scheda di ogni ricetta.\n\n"
                "Realizzato da Ninoz Sistem."
            ),
            buttons=[MDFlatButton(text="Chiudi", on_release=lambda *_: dialog.dismiss())],
        )
        dialog.open()


if __name__ == "__main__":
    try:
        CalcolatoreApp().run()
    except Exception:
        # Ultima rete di sicurezza: se anche l'avvio di KivyMD fallisce
        # (non solo la costruzione della schermata, già gestita sopra),
        # mostriamo l'errore con Kivy "puro", che non dipende da KivyMD,
        # invece di lasciare che l'app si chiuda senza spiegazioni.
        tb_text = traceback.format_exc()
        try:
            with open(os.path.join(BASE_DIR, "ultimo_errore.txt"), "w", encoding="utf-8") as f:
                f.write(tb_text)
        except Exception:
            pass

        from kivy.app import App as _KivyApp
        from kivy.uix.scrollview import ScrollView as _SV
        from kivy.uix.label import Label as _Label

        class _CrashApp(_KivyApp):
            def build(self):
                sv = _SV()
                lbl = _Label(
                    text="ERRORE ALL'AVVIO — foto/copia questa schermata:\n\n" + tb_text,
                    size_hint_y=None, halign="left", valign="top",
                )
                lbl.bind(
                    width=lambda i, w: setattr(i, "text_size", (w, None)),
                    texture_size=lambda i, ts: setattr(i, "height", ts[1]),
                )
                sv.add_widget(lbl)
                return sv

        _CrashApp().run()
