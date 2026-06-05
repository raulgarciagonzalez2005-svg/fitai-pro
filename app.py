import streamlit as st
import json, os, re, base64, io, hashlib, uuid
from datetime import date, datetime
from PIL import Image

# ── Supabase (optional – graceful fallback to local JSON if not configured) ──
try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FitAI Pro",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM  ·  White & Green  ·  Clean, editorial, human
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --white:   #ffffff;
  --bg:      #f7f8f4;
  --bg2:     #eef1ea;
  --surface: #ffffff;
  --border:  #e2e8d9;
  --border2: #c8d4bc;
  --green:   #2d6a4f;
  --green2:  #40916c;
  --green3:  #74c69d;
  --green4:  #b7e4c7;
  --green5:  #d8f3dc;
  --dark:    #1b2e22;
  --text:    #1e2d1f;
  --text2:   #4a6352;
  --text3:   #8aab94;
  --red:     #c0392b;
  --amber:   #e67e22;
  --blue:    #2471a3;
  --r:       14px;
  --rsm:     8px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
  max-width: 760px !important;
  padding: 0 1.25rem 7rem !important;
  margin: 0 auto !important;
}

/* ── HERO ── */
.hero {
  padding: 2.8rem 0 2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.hero-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: .6rem;
  color: var(--green2);
  letter-spacing: .18em;
  text-transform: uppercase;
  margin-bottom: .9rem;
  display: flex;
  align-items: center;
  gap: .5rem;
}
.hero-dot {
  width: 6px; height: 6px;
  background: var(--green2);
  border-radius: 50%;
  animation: pulse 2.4s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity: 1; transform: scale(1); }
  50%      { opacity: .4; transform: scale(.7); }
}
.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.6rem, 8vw, 4.8rem);
  font-weight: 400;
  line-height: .92;
  letter-spacing: -.02em;
  color: var(--dark);
  margin-bottom: .8rem;
}
.hero-title em { font-style: italic; color: var(--green); }
.hero-sub {
  font-size: .78rem;
  color: var(--text3);
  display: flex;
  align-items: center;
  gap: .5rem;
  flex-wrap: wrap;
}
.hero-sep { color: var(--border2); }

/* ── CARDS ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.2rem 1.35rem;
  margin-bottom: .8rem;
  box-shadow: 0 1px 3px rgba(45,106,79,.04), 0 4px 12px rgba(45,106,79,.04);
  transition: box-shadow .2s;
}
.card:hover { box-shadow: 0 2px 6px rgba(45,106,79,.07), 0 8px 24px rgba(45,106,79,.07); }
.card.accent {
  background: linear-gradient(135deg, var(--green) 0%, var(--green2) 100%);
  border-color: var(--green);
  color: #fff;
}
.card.accent .lbl, .card.accent p { color: rgba(255,255,255,.75); }
.card.accent .big, .card.accent .mv { color: #fff; }

.lbl {
  font-family: 'JetBrains Mono', monospace;
  font-size: .58rem;
  color: var(--text3);
  letter-spacing: .14em;
  text-transform: uppercase;
  margin-bottom: .6rem;
}

.big {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  font-weight: 400;
  line-height: 1;
  letter-spacing: -.02em;
  color: var(--dark);
}
.big-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: .56rem;
  color: var(--text3);
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-top: .25rem;
}

/* ── PROGRESS BAR ── */
.pb { background: var(--bg2); border-radius: 999px; height: 4px; overflow: hidden; margin-top: .5rem; }
.pb-f { height: 100%; border-radius: 999px; transition: width .6s cubic-bezier(.4,0,.2,1); }

/* ── MACRO GRID ── */
.mgrid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.mv {
  font-family: 'Playfair Display', serif;
  font-size: 1.75rem;
  font-weight: 400;
  line-height: 1;
  color: var(--dark);
}
.ms { font-size: .6rem; color: var(--text3); font-family: 'JetBrains Mono', monospace; margin-top: .1rem; }

/* ── STAT GRID ── */
.sgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.sv {
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem;
  font-weight: 400;
  color: var(--dark);
  line-height: 1;
}

/* ── BADGES ── */
.badge {
  display: inline-flex;
  align-items: center;
  padding: .18rem .55rem;
  border-radius: var(--rsm);
  font-size: .65rem;
  font-weight: 500;
  margin: .1rem .06rem 0 0;
  font-family: 'JetBrains Mono', monospace;
  border: 1px solid transparent;
}
.bk  { background: var(--green5); color: var(--green); border-color: var(--green4); }
.bp  { background: #e8f8f0; color: #1a7a4a; border-color: #b7e4c7; }
.bc  { background: #eaf2fb; color: var(--blue); border-color: #aed6f1; }
.bf  { background: #fef9e7; color: var(--amber); border-color: #fad7a0; }
.bn  { background: var(--bg); color: var(--text2); border-color: var(--border); }
.bw  { background: #fdedec; color: var(--red); border-color: #f5b7b1; }
.bg2 { background: var(--green5); color: var(--green); border-color: var(--green4); }

/* ── ROWS ── */
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .35rem 0;
  border-bottom: 1px solid var(--border);
  font-size: .8rem;
}
.row:last-child { border-bottom: none; }
.rl { color: var(--text2); }
.rr { color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: .7rem; }

/* ── SEPARATOR ── */
.sep {
  display: flex;
  align-items: center;
  gap: .65rem;
  margin: 1.5rem 0 .9rem;
}
.sep-l { flex: 1; height: 1px; background: var(--border); }
.sep-t {
  font-family: 'JetBrains Mono', monospace;
  font-size: .57rem;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .14em;
  white-space: nowrap;
}

/* ── TYPE BADGE ── */
.typebadge {
  font-family: 'JetBrains Mono', monospace;
  font-size: .55rem;
  font-weight: 500;
  padding: .15rem .45rem;
  border-radius: var(--rsm);
  letter-spacing: .06em;
  text-transform: uppercase;
  border: 1px solid;
}

/* ── BUTTONS ── */
div.stButton > button {
  background: var(--green) !important;
  color: #fff !important;
  font-family: 'Inter', sans-serif !important;
  font-size: .82rem !important;
  font-weight: 600 !important;
  border: none !important;
  border-radius: var(--rsm) !important;
  padding: .6rem 1.2rem !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: background .15s, transform .1s !important;
  letter-spacing: .01em !important;
}
div.stButton > button:hover {
  background: var(--green2) !important;
  transform: translateY(-1px) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

/* ── INPUTS ── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stNumberInput input {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: .83rem !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(45,106,79,.12) !important;
}
div[data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  color: var(--text) !important;
}
label { color: var(--text2) !important; font-size: .78rem !important; font-family: 'Inter', sans-serif !important; }

/* ── TABS ── */
[data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--rsm) !important;
  padding: 3px !important;
  gap: 2px !important;
  box-shadow: 0 1px 3px rgba(45,106,79,.04) !important;
}
[data-baseweb="tab"] {
  color: var(--text3) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .73rem !important;
  border-radius: 6px !important;
  padding: .37rem .9rem !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: var(--green) !important;
  color: #fff !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  border: 1.5px dashed var(--border2) !important;
  border-radius: var(--r) !important;
  background: var(--bg) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
  background: var(--green5) !important;
  border: 1px solid var(--green4) !important;
  border-radius: var(--rsm) !important;
  font-size: .8rem !important;
  color: var(--green) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--rsm) !important;
}
[data-testid="stExpander"] summary { color: var(--text2) !important; font-size: .8rem !important; }

/* ── LOGIN CARD ── */
.login-wrap {
  max-width: 420px;
  margin: 3rem auto 0;
}
.login-logo {
  text-align: center;
  margin-bottom: 2rem;
}
.login-logo .big { font-size: 2.8rem; color: var(--green); }

/* ── FOOD VISUAL GRID ── */
.food-pill {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: .22rem .65rem;
  font-size: .72rem;
  color: var(--text2);
  margin: .1rem;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 999px; }

/* ── MOBILE ── */
@media (max-width: 520px) {
  .hero-title { font-size: 2.6rem; }
  .big { font-size: 2.4rem; }
  .block-container { padding: 0 .8rem 6rem !important; }
  .mgrid { gap: .6rem; }
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════════
DATA_FILE = "fitai_data.json"
USERS_FILE = "fitai_users.json"

FOOD_ICONS = {
    "Pollo": "🍗", "pavo": "🦃", "Atun": "🐟", "Salmon": "🐠", "Merluza": "🐟",
    "Ternera": "🥩", "Cerdo": "🥩", "Huevo": "🥚", "Claras": "🥚",
    "Queso": "🧀", "Yogur": "🥛", "Leche": "🥛", "Whey": "💪", "Caseina": "💪",
    "Avena": "🌾", "Arroz": "🍚", "Pasta": "🍝", "Pan": "🍞",
    "Boniato": "🍠", "Patata": "🥔", "Quinoa": "🌿", "Lentejas": "🫘",
    "Garbanzos": "🫘", "Alubias": "🫘", "Aguacate": "🥑", "Aceite": "🫒",
    "Almendras": "🌰", "Nueces": "🌰", "Platano": "🍌", "Manzana": "🍎",
    "Naranja": "🍊", "Fresas": "🍓", "Arandanos": "🫐",
    "Brocoli": "🥦", "Espinacas": "🥬", "Tomate": "🍅", "Pepino": "🥒",
    "Lechuga": "🥬", "Zanahoria": "🥕", "Pimiento": "🫑", "Calabacin": "🥒",
    "Tofu": "🧆", "Tempeh": "🧆", "Aceitunas": "🫒", "Hummus": "🫘",
}

ALIMENTOS_DB = {
    "Pollo a la plancha (100g)":    {"cal":165,"prot":31.0,"carb":0.0,"grasa":3.6},
    "Pechuga de pavo (100g)":       {"cal":135,"prot":30.0,"carb":0.0,"grasa":1.0},
    "Atun en agua (100g)":          {"cal":116,"prot":26.0,"carb":0.0,"grasa":1.0},
    "Salmon (100g)":                {"cal":208,"prot":20.0,"carb":0.0,"grasa":13.0},
    "Merluza (100g)":               {"cal":86, "prot":17.0,"carb":0.0,"grasa":1.5},
    "Ternera magra (100g)":         {"cal":170,"prot":26.0,"carb":0.0,"grasa":7.0},
    "Cerdo magro (100g)":           {"cal":143,"prot":22.0,"carb":0.0,"grasa":5.9},
    "Huevo entero (1 ud ~60g)":     {"cal":86, "prot":7.5, "carb":0.6,"grasa":6.0},
    "Claras de huevo (100g)":       {"cal":52, "prot":11.0,"carb":0.7,"grasa":0.2},
    "Queso fresco 0% (100g)":       {"cal":62, "prot":11.0,"carb":3.3,"grasa":0.4},
    "Queso cottage (100g)":         {"cal":98, "prot":11.2,"carb":3.4,"grasa":4.3},
    "Yogur griego natural (100g)":  {"cal":97, "prot":9.0, "carb":3.6,"grasa":5.0},
    "Yogur griego 0% (100g)":       {"cal":59, "prot":10.0,"carb":3.5,"grasa":0.4},
    "Leche semidesnatada (100ml)":  {"cal":46, "prot":3.3, "carb":4.7,"grasa":1.6},
    "Whey protein (30g)":           {"cal":114,"prot":24.0,"carb":3.0,"grasa":1.5},
    "Caseina (30g)":                {"cal":110,"prot":24.0,"carb":2.5,"grasa":1.0},
    "Avena (100g)":                 {"cal":389,"prot":17.0,"carb":66.0,"grasa":7.0},
    "Arroz blanco cocido (100g)":   {"cal":130,"prot":2.7, "carb":28.0,"grasa":0.3},
    "Arroz integral cocido (100g)": {"cal":122,"prot":2.6, "carb":25.0,"grasa":0.9},
    "Pasta integral cocida (100g)": {"cal":124,"prot":5.0, "carb":25.0,"grasa":1.0},
    "Pan integral (35g/rebanada)":  {"cal":80, "prot":3.5, "carb":14.0,"grasa":1.0},
    "Boniato cocido (100g)":        {"cal":90, "prot":2.0, "carb":21.0,"grasa":0.1},
    "Patata cocida (100g)":         {"cal":77, "prot":2.0, "carb":17.0,"grasa":0.1},
    "Quinoa cocida (100g)":         {"cal":120,"prot":4.4, "carb":22.0,"grasa":1.9},
    "Lentejas cocidas (100g)":      {"cal":116,"prot":9.0, "carb":20.0,"grasa":0.4},
    "Garbanzos cocidos (100g)":     {"cal":164,"prot":8.9, "carb":27.0,"grasa":2.6},
    "Alubias negras cocidas (100g)":{"cal":132,"prot":8.9, "carb":24.0,"grasa":0.5},
    "Aguacate (100g)":              {"cal":160,"prot":2.0, "carb":9.0, "grasa":15.0},
    "Aceite de oliva (10ml)":       {"cal":90, "prot":0.0, "carb":0.0, "grasa":10.0},
    "Almendras (30g)":              {"cal":174,"prot":6.0, "carb":6.0, "grasa":15.0},
    "Nueces (30g)":                 {"cal":196,"prot":4.6, "carb":4.1, "grasa":19.5},
    "Platano mediano (120g)":       {"cal":107,"prot":1.3, "carb":27.0,"grasa":0.4},
    "Manzana mediana (150g)":       {"cal":78, "prot":0.4, "carb":21.0,"grasa":0.2},
    "Naranja (150g)":               {"cal":70, "prot":1.3, "carb":17.0,"grasa":0.2},
    "Fresas (100g)":                {"cal":32, "prot":0.7, "carb":7.7, "grasa":0.3},
    "Arandanos (100g)":             {"cal":57, "prot":0.7, "carb":14.5,"grasa":0.3},
    "Brocoli (100g)":               {"cal":34, "prot":2.8, "carb":7.0, "grasa":0.4},
    "Espinacas (100g)":             {"cal":23, "prot":2.9, "carb":3.6, "grasa":0.4},
    "Tomate (100g)":                {"cal":18, "prot":0.9, "carb":3.9, "grasa":0.2},
    "Pepino (100g)":                {"cal":15, "prot":0.7, "carb":3.6, "grasa":0.1},
    "Lechuga (100g)":               {"cal":15, "prot":1.4, "carb":2.9, "grasa":0.2},
    "Zanahoria (100g)":             {"cal":41, "prot":0.9, "carb":10.0,"grasa":0.2},
    "Pimiento rojo (100g)":         {"cal":31, "prot":1.0, "carb":6.0, "grasa":0.3},
    "Calabacin (100g)":             {"cal":17, "prot":1.2, "carb":3.1, "grasa":0.3},
    "Tofu firme (100g)":            {"cal":144,"prot":17.0,"carb":2.8, "grasa":8.7},
    "Tempeh (100g)":                {"cal":195,"prot":20.3,"carb":9.4, "grasa":10.8},
    "Aceitunas (30g)":              {"cal":43, "prot":0.3, "carb":2.3, "grasa":3.9},
    "Hummus (100g)":                {"cal":166,"prot":7.9, "carb":14.3,"grasa":9.6},
}

DIETAS_TEMPLATE = {
    "Volumen limpio (2800 kcal)": {
        "objetivo": "Ganar masa muscular con minima acumulacion de grasa",
        "macros": {"prot":175,"carb":350,"grasa":75},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Avena 80g + Whey 30g + Platano + Leche 200ml","cal":580,"prot":42,"carb":82,"grasa":10},
            {"nombre":"Media manana","alimentos":"Yogur griego 200g + Almendras 30g + Manzana","cal":330,"prot":22,"carb":30,"grasa":16},
            {"nombre":"Almuerzo","alimentos":"Arroz integral 150g + Pollo 200g + Brocoli + AOVE 10ml","cal":720,"prot":72,"carb":85,"grasa":14},
            {"nombre":"Merienda","alimentos":"Pan integral 70g + Atun 100g + Tomate","cal":290,"prot":36,"carb":28,"grasa":3},
            {"nombre":"Cena","alimentos":"Salmon 200g + Boniato 200g + Espinacas salteadas","cal":580,"prot":45,"carb":48,"grasa":28},
            {"nombre":"Antes de dormir","alimentos":"Claras 200g + Queso fresco 0% 150g","cal":220,"prot":34,"carb":7,"grasa":3},
        ],
    },
    "Definicion (1900 kcal)": {
        "objetivo": "Reducir grasa corporal conservando la masa muscular",
        "macros": {"prot":180,"carb":160,"grasa":60},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Claras 4 uds + 1 huevo + Avena 50g","cal":380,"prot":38,"carb":35,"grasa":9},
            {"nombre":"Media manana","alimentos":"Yogur griego 0% 200g + Caseina 30g","cal":250,"prot":35,"carb":10,"grasa":3},
            {"nombre":"Almuerzo","alimentos":"Pechuga pavo 200g + Patata 150g + Verduras","cal":430,"prot":62,"carb":35,"grasa":5},
            {"nombre":"Merienda","alimentos":"Atun 100g + Pan integral 35g + Pepino","cal":230,"prot":30,"carb":18,"grasa":2},
            {"nombre":"Cena","alimentos":"Merluza 200g + Brocoli + Espinacas + AOVE 5ml","cal":380,"prot":48,"carb":12,"grasa":14},
            {"nombre":"Antes de dormir","alimentos":"Queso fresco 0% 150g","cal":93,"prot":17,"carb":5,"grasa":0.6},
        ],
    },
    "Mantenimiento (2300 kcal)": {
        "objetivo": "Mantener composicion corporal y rendimiento",
        "macros": {"prot":155,"carb":260,"grasa":70},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Avena 60g + Leche 200ml + 2 Huevos + Fruta","cal":490,"prot":28,"carb":62,"grasa":14},
            {"nombre":"Media manana","alimentos":"Fruta + Almendras 25g + Queso fresco","cal":270,"prot":14,"carb":25,"grasa":13},
            {"nombre":"Almuerzo","alimentos":"Arroz 120g + Ternera magra 150g + Ensalada + AOVE","cal":600,"prot":45,"carb":60,"grasa":18},
            {"nombre":"Merienda","alimentos":"Platano + Pan integral + Pavo 80g","cal":310,"prot":26,"carb":42,"grasa":4},
            {"nombre":"Cena","alimentos":"Salmon 150g + Garbanzos 100g + Verduras a la plancha","cal":540,"prot":40,"carb":42,"grasa":21},
        ],
    },
    "Vegana alta proteina (2200 kcal)": {
        "objetivo": "Dieta plant-based con aporte proteico suficiente",
        "macros": {"prot":140,"carb":280,"grasa":65},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Avena 80g + Proteina vegana 30g + Platano","cal":520,"prot":35,"carb":80,"grasa":10},
            {"nombre":"Media manana","alimentos":"Hummus 100g + Pan integral + Tomate","cal":290,"prot":12,"carb":35,"grasa":10},
            {"nombre":"Almuerzo","alimentos":"Lentejas 200g + Arroz 100g + Verduras + AOVE","cal":590,"prot":28,"carb":95,"grasa":12},
            {"nombre":"Merienda","alimentos":"Aguacate + Pan integral + Batido espinacas","cal":350,"prot":10,"carb":30,"grasa":22},
            {"nombre":"Cena","alimentos":"Tofu 200g + Garbanzos 100g + Brocoli + AOVE","cal":470,"prot":38,"carb":35,"grasa":20},
        ],
    },
    "Recomposicion (2100 kcal)": {
        "objetivo": "Ganar musculo y perder grasa al mismo tiempo",
        "macros": {"prot":200,"carb":200,"grasa":65},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Claras 5 uds + 1 huevo + Avena 40g + Arandanos","cal":380,"prot":40,"carb":38,"grasa":8},
            {"nombre":"Pre-entreno","alimentos":"Platano + Whey 30g","cal":240,"prot":25,"carb":30,"grasa":2},
            {"nombre":"Almuerzo","alimentos":"Pollo 200g + Quinoa 100g + Pimiento + Zanahoria","cal":490,"prot":55,"carb":45,"grasa":9},
            {"nombre":"Merienda","alimentos":"Queso cottage 200g + Nueces 20g","cal":270,"prot":26,"carb":7,"grasa":15},
            {"nombre":"Cena","alimentos":"Salmon 180g + Espinacas + Tomate + AOVE 8ml","cal":440,"prot":38,"carb":8,"grasa":28},
            {"nombre":"Antes de dormir","alimentos":"Caseina 30g","cal":110,"prot":24,"carb":3,"grasa":1},
        ],
    },
}

EJERCICIOS_GYM = {
    "Pecho": [
        {"nombre":"Press banca plano","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-12","descanso":"90s","notas":"Escapulas retraidas, toque suave al pecho"},
        {"nombre":"Press banca inclinado","tipo":"Hipertrofia","equipo":"Barra o Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Angulo 30-45 grados"},
        {"nombre":"Aperturas con mancuernas","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados"},
        {"nombre":"Fondos en paralelas","tipo":"Peso corporal","equipo":"Paralelas","series_rec":"3-4","reps_rec":"Max","descanso":"90s","notas":"Torso inclinado hacia adelante"},
        {"nombre":"Crossover en polea","tipo":"Aislamiento","equipo":"Poleas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Estiramiento completo arriba"},
    ],
    "Espalda": [
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3 min","notas":"Espalda neutra, barra pegada al cuerpo"},
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra fija","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo, sin balanceo"},
        {"nombre":"Jalon al pecho","tipo":"Hipertrofia","equipo":"Polea alta","series_rec":"4","reps_rec":"10-15","descanso":"75s","notas":"Codos hacia abajo y atras"},
        {"nombre":"Remo con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Torso a 45 grados"},
        {"nombre":"Face pulls","tipo":"Prevencion","equipo":"Polea alta","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Esencial para el manguito rotador"},
    ],
    "Pierna": [
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3 min","notas":"Rodillas en la direccion de los pies"},
        {"nombre":"Prensa de piernas","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos isquios, pies bajos cuadriceps"},
        {"nombre":"Femoral tumbado","tipo":"Aislamiento","equipo":"Maquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Aisla isquiotibiales"},
        {"nombre":"Hip Thrust","tipo":"Gluteos","equipo":"Barra o Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Contraccion maxima arriba"},
        {"nombre":"Peso muerto rumano","tipo":"Hipertrofia","equipo":"Barra","series_rec":"3-4","reps_rec":"10-12","descanso":"90s","notas":"Bisagra de cadera perfecta"},
        {"nombre":"Elevacion de gemelos","tipo":"Aislamiento","equipo":"Maquina","series_rec":"4","reps_rec":"15-25","descanso":"45s","notas":"Rango completo"},
    ],
    "Hombros": [
        {"nombre":"Press militar con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2 min","notas":"Core activado"},
        {"nombre":"Elevaciones laterales","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Hasta la horizontal"},
        {"nombre":"Press Arnold","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Rotacion completa"},
        {"nombre":"Pajaro posterior","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Torso a 90 grados"},
    ],
    "Biceps": [
        {"nombre":"Curl con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"75s","notas":"Codos fijos a los costados"},
        {"nombre":"Curl con mancuernas alterno","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-14/brazo","descanso":"60s","notas":"Supinacion al subir"},
        {"nombre":"Curl martillo","tipo":"Braquial","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Agarre neutro"},
        {"nombre":"Curl predicador","tipo":"Aislamiento","equipo":"Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"No extender completamente"},
    ],
    "Triceps": [
        {"nombre":"Press banca agarre cerrado","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Codos pegados al tronco"},
        {"nombre":"Pushdown en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"3-4","reps_rec":"15-20","descanso":"45s","notas":"Extension completa abajo"},
        {"nombre":"Extension sobre la cabeza","tipo":"Hipertrofia","equipo":"Mancuerna","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Estiramiento maximo abajo"},
        {"nombre":"Press frances","tipo":"Hipertrofia","equipo":"Barra EZ","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Baja a la frente controlado"},
    ],
    "Core": [
        {"nombre":"Plancha frontal","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3-4","reps_rec":"45-90s","descanso":"45s","notas":"Cuerpo completamente recto"},
        {"nombre":"Rueda abdominal","tipo":"Fuerza","equipo":"Rueda ab","series_rec":"3","reps_rec":"8-15","descanso":"60s","notas":"Empezar de rodillas"},
        {"nombre":"Crunch en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Flexion de columna, no de caderas"},
        {"nombre":"Elevacion de piernas colgado","tipo":"Fuerza","equipo":"Barra fija","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Retroversion pelvica al subir"},
        {"nombre":"Dead bug","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"8-12/lado","descanso":"45s","notas":"Espalda baja pegada al suelo"},
    ],
    "Cardio": [
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint / 30s caminar","descanso":"—","notas":"FC al 85-90% del maximo"},
        {"nombre":"Tabata en bicicleta","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s / 10s pausa","descanso":"—","notas":"4 minutos totales por ronda"},
        {"nombre":"Zona 2 en eliptica","tipo":"Cardio","equipo":"Eliptica","series_rec":"1","reps_rec":"30-45 min","descanso":"—","notas":"FC 120-140 ppm"},
        {"nombre":"Remo en ergometro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500 m","descanso":"2 min","notas":"Combo cardio + espalda + piernas"},
    ],
    "Calistenia": [
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Progresion: australianas, negativas, completas"},
        {"nombre":"Fondos en paralelas","tipo":"Fuerza","equipo":"Paralelas","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo"},
        {"nombre":"Flexiones","tipo":"Peso corporal","equipo":"Suelo","series_rec":"4","reps_rec":"Max","descanso":"60s","notas":"Variantes: inclinadas, diamante, arqueras"},
        {"nombre":"Pistol squat","tipo":"Fuerza","equipo":"Peso corporal","series_rec":"3","reps_rec":"5-10/pierna","descanso":"90s","notas":"Gran activacion unilateral"},
    ],
}

RUTINAS_DEFAULT = {
    "PPL — Empuje": {"desc":"Pecho, hombros y triceps","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Press Arnold","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Extension sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
    ]},
    "PPL — Tiron": {"desc":"Espalda y biceps","ejercicios":[
        {"ejercicio":"Dominadas","series":4,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
    ]},
    "PPL — Piernas": {"desc":"Cuadriceps, isquios, gluteos y gemelos","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-8","peso":"","descanso":"2-3 min","notas":""},
        {"ejercicio":"Prensa de piernas","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Peso muerto rumano","series":3,"reps":"10-12","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Hip Thrust","series":4,"reps":"12-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Elevacion de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
    ]},
    "Full Body — Principiantes": {"desc":"3 dias por semana","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca plano","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Peso muerto convencional","series":3,"reps":"6-8","peso":"","descanso":"2 min","notas":""},
        {"ejercicio":"Press militar","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Dominadas","series":3,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"45s","notas":""},
    ]},
    "Upper — Tren superior": {"desc":"Pecho, espalda, hombros y brazos","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"60s","notas":""},
    ]},
    "Lower — Tren inferior": {"desc":"Cuadriceps, isquios, gluteos y core","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-10","peso":"","descanso":"2 min","notas":""},
        {"ejercicio":"Peso muerto rumano","series":4,"reps":"8-12","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Prensa de piernas","series":3,"reps":"12-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Hip Thrust","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Elevacion de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
    ]},
    "HIIT + Core": {"desc":"Alta intensidad + trabajo abdominal, aprox 35 min","ejercicios":[
        {"ejercicio":"Burpees","series":5,"reps":"30s / 15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Mountain climbers","series":5,"reps":"30s / 15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""},
    ]},
}

TIPO_COLOR = {
    "Fuerza":        ("#2d6a4f","rgba(45,106,79,.1)"),
    "Hipertrofia":   ("#2471a3","rgba(36,113,163,.1)"),
    "Aislamiento":   ("#7d3c98","rgba(125,60,152,.1)"),
    "Peso corporal": ("#1a7a4a","rgba(26,122,74,.1)"),
    "Cardio":        ("#e67e22","rgba(230,126,34,.1)"),
    "Estabilidad":   ("#1a7a4a","rgba(26,122,74,.1)"),
    "Gluteos":       ("#c0392b","rgba(192,57,43,.1)"),
    "Prevencion":    ("#1a7a4a","rgba(26,122,74,.1)"),
    "Braquial":      ("#7d3c98","rgba(125,60,152,.1)"),
}

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH & PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def load_users() -> dict:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_users(users: dict):
    try:
        with open(USERS_FILE,"w",encoding="utf-8") as f:
            json.dump(users,f,ensure_ascii=False,indent=2)
    except Exception as e:
        st.warning(f"Error guardando usuarios: {e}")

def get_user_file(uid: str) -> str:
    return f"fitai_user_{uid[:8]}.json"

def load_user_data(uid: str) -> dict:
    path = get_user_file(uid)
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "historial_calorias":{},"historial_macros":{},
        "diario_comidas":{},"rutinas_custom":{},
        "dietas_custom":{},"perfil":{},"registro_entreno":{},
    }

def save_user_data(uid: str, data: dict):
    try:
        with open(get_user_file(uid),"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception as e:
        st.warning(f"Error guardando datos: {e}")

# ── Supabase helpers ──────────────────────────────────────────────────────────
def get_supabase() -> "SupabaseClient | None":
    if not SUPABASE_AVAILABLE:
        return None
    url = st.secrets.get("SUPABASE_URL","")
    key = st.secrets.get("SUPABASE_KEY","")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

def sb_register(email: str, pw: str) -> tuple[bool,str]:
    sb = get_supabase()
    if sb:
        try:
            r = sb.auth.sign_up({"email":email,"password":pw})
            if r.user:
                return True, r.user.id
            return False, "Error al registrar en Supabase"
        except Exception as e:
            return False, str(e)
    # Local fallback
    users = load_users()
    if email in users:
        return False, "El correo ya esta registrado"
    uid = str(uuid.uuid4())
    users[email] = {"uid":uid,"pw_hash":hash_pw(pw),"created":str(datetime.now())}
    save_users(users)
    return True, uid

def sb_login(email: str, pw: str) -> tuple[bool,str,str]:
    sb = get_supabase()
    if sb:
        try:
            r = sb.auth.sign_in_with_password({"email":email,"password":pw})
            if r.user:
                return True, r.user.id, email
            return False, "", "Credenciales incorrectas"
        except Exception as e:
            return False, "", str(e)
    # Local fallback
    users = load_users()
    if email not in users:
        return False, "", "Correo no registrado"
    if users[email]["pw_hash"] != hash_pw(pw):
        return False, "", "Contrasena incorrecta"
    return True, users[email]["uid"], email

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def _ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_ss("logged_in", False)
_ss("user_id", "")
_ss("user_email", "")
_ss("datos", {})
_ss("gemini_key", "")
_ss("groq_key", "")
_ss("proveedor_ia", "Groq (recomendado)")
_ss("scan_res", None)
_ss("ia_dieta_res", None)
_ss("ej_temp", [])
_ss("sets_temp", [])
_ss("comidas_dc_temp", [])
_ss("auth_mode", "login")  # "login" or "register"

# ── Restore API keys from secrets if available ────────────────────────────────
if not st.session_state.gemini_key:
    try:
        st.session_state.gemini_key = st.secrets.get("GEMINI_KEY","")
    except Exception:
        pass
if not st.session_state.groq_key:
    try:
        st.session_state.groq_key = st.secrets.get("GROQ_KEY","")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def hoy(): return str(date.today())
def get_perfil(): return st.session_state.datos.get("perfil",{})
def get_obj_cal(): return int(get_perfil().get("objetivo_cal",2000))
def cal_hoy(): return st.session_state.datos.get("historial_calorias",{}).get(hoy(),0)
def macros_hoy(): return st.session_state.datos.get("historial_macros",{}).get(hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0})

def save_datos():
    save_user_data(st.session_state.user_id, st.session_state.datos)

def registrar_alimento(nombre,cal,prot,carb,grasa,comida):
    d = st.session_state.datos
    d.setdefault("historial_calorias",{})[hoy()] = cal_hoy() + cal
    hm = d.setdefault("historial_macros",{})
    dm = hm.setdefault(hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0})
    dm["prot"]  = round(dm["prot"]  + prot, 1)
    dm["carb"]  = round(dm["carb"]  + carb, 1)
    dm["grasa"] = round(dm["grasa"] + grasa,1)
    d.setdefault("diario_comidas",{}).setdefault(hoy(),[]).append({
        "comida":comida,"alimento":nombre,"cal":cal,
        "prot":prot,"carb":carb,"grasa":grasa,
        "hora":datetime.now().strftime("%H:%M"),
    })
    save_datos()

def calcular_tdee(peso,altura,edad,sexo,actividad):
    bmr = (88.36+13.4*peso+4.8*altura-5.7*edad) if sexo=="Hombre" \
          else (447.6+9.2*peso+3.1*altura-4.3*edad)
    f = {"Sedentario (sin ejercicio)":1.2,"Ligero (1-2 dias/semana)":1.375,
         "Moderado (3-4 dias/semana)":1.55,"Activo (5-6 dias/semana)":1.725,
         "Muy activo (2 veces/dia)":1.9}
    return int(bmr * f.get(actividad,1.55))

def pb(val,mx,color):
    pct = min(val/mx*100,100) if mx>0 else 0
    return f'<div class="pb"><div class="pb-f" style="width:{pct}%;background:{color}"></div></div>'

def ia_call(prompt,img_bytes=None):
    prov = st.session_state.proveedor_ia
    if "Groq" in prov:
        key = st.session_state.groq_key.strip()
        if not key: return "ERROR_NO_KEY"
        try:
            import requests
            headers = {"Authorization":f"Bearer {key}","Content-Type":"application/json"}
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode()
                try:
                    ext = Image.open(io.BytesIO(img_bytes)).format.lower().replace("jpg","jpeg")
                except Exception:
                    ext = "jpeg"
                msgs = [{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:image/{ext};base64,{b64}"}},
                    {"type":"text","text":prompt}
                ]}]
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
            else:
                msgs = [{"role":"user","content":prompt}]
                model = "llama-3.3-70b-versatile"
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers=headers, json={"model":model,"messages":msgs,"max_tokens":1200,"temperature":0.4},
                timeout=30)
            if r.status_code==401: return "API Key de Groq invalida. Verifica en console.groq.com/keys"
            if r.status_code==429: return "Limite de Groq alcanzado. Espera un minuto."
            if r.status_code!=200: return f"Error Groq {r.status_code}"
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error de conexion: {str(e)[:150]}"
    else:
        key = st.session_state.gemini_key.strip()
        if not key: return "ERROR_NO_KEY"
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            if img_bytes:
                img_pil = Image.open(io.BytesIO(img_bytes))
                return model.generate_content([prompt, img_pil]).text
            return model.generate_content(prompt).text
        except Exception as e:
            err = str(e)
            if "QUOTA" in err.upper() or "429" in err:
                return "Cuota de Gemini agotada. Cambia a Groq en Config."
            return f"Error Gemini: {err[:150]}"

def extraer_kcal(txt):
    try:
        m = re.search(r"TOTAL.*?(\d{2,4})\s*kcal",txt,re.IGNORECASE)
        if m: return int(m.group(1))
        m2 = re.search(r"(\d{3,4})\s*kcal",txt,re.IGNORECASE)
        if m2: return int(m2.group(1))
    except Exception: pass
    return 0

def sdiv(label):
    st.markdown(f'<div class="sep"><div class="sep-l"></div>'
                f'<span class="sep-t">{label}</span>'
                f'<div class="sep-l"></div></div>',unsafe_allow_html=True)

def card(content, accent=False):
    cls = "card accent" if accent else "card"
    return f'<div class="{cls}">{content}</div>'

def food_icon(name: str) -> str:
    for k,v in FOOD_ICONS.items():
        if k.lower() in name.lower():
            return v
    return "🥗"

# ═══════════════════════════════════════════════════════════════════════════════
# ── LOGIN / REGISTER SCREEN ──────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div style="padding:3rem 0 1.5rem; text-align:center; border-bottom:1px solid var(--border); margin-bottom:2rem">
      <div style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:var(--green2);
                  letter-spacing:.18em;text-transform:uppercase;margin-bottom:.8rem">Tu asistente de nutricion</div>
      <div style="font-family:'Playfair Display',serif;font-size:3.2rem;font-weight:400;
                  line-height:.9;color:var(--dark);letter-spacing:-.02em">
        Fit<em style="font-style:italic;color:var(--green)">AI</em> Pro
      </div>
      <div style="font-size:.75rem;color:var(--text3);margin-top:.6rem">Nutricion · Dietas · Gimnasio · Inteligencia Artificial</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1,2,1])
    with col_c:
        mode = st.session_state.auth_mode

        st.markdown(f'<div style="text-align:center;margin-bottom:1.2rem">'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:.65rem;'
                    f'color:var(--text3);letter-spacing:.1em;text-transform:uppercase">'
                    f'{"Iniciar sesion" if mode=="login" else "Crear cuenta"}</span></div>',
                    unsafe_allow_html=True)

        auth_email = st.text_input("Correo electronico", placeholder="hola@ejemplo.com", key="auth_email")
        auth_pw    = st.text_input("Contrasena", type="password", placeholder="Minimo 6 caracteres", key="auth_pw")

        if mode == "register":
            auth_nombre = st.text_input("Tu nombre (opcional)", placeholder="Carlos", key="auth_nombre")

        st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)

        if mode == "login":
            if st.button("Entrar", key="btn_login"):
                if not auth_email or not auth_pw:
                    st.warning("Rellena correo y contrasena.")
                else:
                    ok, uid, err_or_email = sb_login(auth_email.strip().lower(), auth_pw)
                    if ok:
                        st.session_state.logged_in   = True
                        st.session_state.user_id     = uid
                        st.session_state.user_email  = auth_email.strip().lower()
                        st.session_state.datos       = load_user_data(uid)
                        # Restore keys from profile
                        pf = st.session_state.datos.get("perfil",{})
                        if pf.get("groq_key")   and not st.session_state.groq_key:
                            st.session_state.groq_key   = pf["groq_key"]
                        if pf.get("gemini_key") and not st.session_state.gemini_key:
                            st.session_state.gemini_key = pf["gemini_key"]
                        st.rerun()
                    else:
                        st.error(err_or_email)

            st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
            st.markdown(
                '<div style="text-align:center;font-size:.77rem;color:var(--text3)">'
                'Sin cuenta? <a href="#" style="color:var(--green);text-decoration:none;font-weight:600" '
                'onclick="void(0)">Regístrate abajo</a></div>',
                unsafe_allow_html=True)
            if st.button("Crear cuenta nueva", key="btn_go_reg"):
                st.session_state.auth_mode = "register"
                st.rerun()

        else:  # register
            if st.button("Registrarme", key="btn_register"):
                if not auth_email or not auth_pw:
                    st.warning("Rellena correo y contrasena.")
                elif len(auth_pw) < 6:
                    st.warning("La contrasena debe tener al menos 6 caracteres.")
                else:
                    ok, uid_or_err = sb_register(auth_email.strip().lower(), auth_pw)
                    if ok:
                        uid = uid_or_err
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = uid
                        st.session_state.user_email = auth_email.strip().lower()
                        nombre_r = st.session_state.get("auth_nombre","")
                        st.session_state.datos = {
                            "historial_calorias":{},"historial_macros":{},
                            "diario_comidas":{},"rutinas_custom":{},
                            "dietas_custom":{},"registro_entreno":{},
                            "perfil":{"nombre":nombre_r,"objetivo_cal":2000,
                                      "obj_prot":150,"obj_carb":220,"obj_grasa":60},
                        }
                        save_datos()
                        st.success("Cuenta creada. Bienvenido/a!")
                        st.rerun()
                    else:
                        st.error(uid_or_err)

            st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
            if st.button("Ya tengo cuenta", key="btn_go_login"):
                st.session_state.auth_mode = "login"
                st.rerun()

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ── MAIN APP (logged in) ─────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
nombre_u = get_perfil().get("nombre","") or st.session_state.user_email.split("@")[0]

st.markdown(
    f'<div class="hero">'
    f'<div class="hero-eyebrow"><div class="hero-dot"></div>Hola, {nombre_u}</div>'
    f'<div class="hero-title">Fit<em>AI</em><br>Pro</div>'
    f'<div class="hero-sub">'
    f'<span>Nutricion</span><span class="hero-sep">·</span>'
    f'<span>Dietas</span><span class="hero-sep">·</span>'
    f'<span>Gimnasio</span><span class="hero-sep">·</span>'
    f'<span>IA</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)

t_nut, t_diet, t_gym, t_hist, t_cfg = st.tabs([
    "Nutricion", "Dietas", "Gimnasio", "Historial", "Config"
])

# ══════════════════════════════════════════════════════════════════════════════
# NUTRICION
# ══════════════════════════════════════════════════════════════════════════════
with t_nut:
    c_hoy_v  = cal_hoy()
    obj_c    = get_obj_cal()
    m_hoy    = macros_hoy()
    pf       = get_perfil()
    obj_p    = int(pf.get("obj_prot",  150))
    obj_cb   = int(pf.get("obj_carb",  220))
    obj_g    = int(pf.get("obj_grasa",  60))
    restante = max(obj_c - c_hoy_v, 0)
    exceso   = max(c_hoy_v - obj_c, 0)
    ok       = c_hoy_v <= obj_c

    c1,c2 = st.columns([3,2])
    with c1:
        nc = "var(--green)" if ok else "var(--red)"
        st.markdown(card(
            f'<div class="lbl">Calorias de hoy</div>'
            f'<div class="big" style="color:{nc}">{c_hoy_v}</div>'
            f'<div class="big-sub">de {obj_c} kcal objetivo · {str(date.today())}</div>'
            f'{pb(c_hoy_v,obj_c,"var(--green)" if ok else "var(--red)")}'),
            unsafe_allow_html=True)
    with c2:
        sv = f'<span style="color:var(--green);font-family:Playfair Display,serif;font-size:2rem;font-weight:400">{restante}</span>' if ok \
             else f'<span style="color:var(--red);font-family:Playfair Display,serif;font-size:2rem;font-weight:400">{exceso}</span>'
        sl = "kcal disponibles" if ok else "kcal excedido"
        st.markdown(card(
            f'<div style="text-align:center;padding:.5rem 0">'
            f'<div class="lbl">Estado del dia</div>'
            f'{sv}<br>'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:.58rem;color:var(--text3);text-transform:uppercase;letter-spacing:.1em">{sl}</span>'
            f'</div>'),unsafe_allow_html=True)

    pct_p  = int(min(m_hoy["prot"] /obj_p *100,100)) if obj_p  else 0
    pct_cb = int(min(m_hoy["carb"] /obj_cb*100,100)) if obj_cb else 0
    pct_g  = int(min(m_hoy["grasa"]/obj_g *100,100)) if obj_g  else 0
    st.markdown(card(
        f'<div class="lbl">Macronutrientes del dia</div>'
        f'<div class="mgrid">'
        f'<div><div class="lbl">Proteina</div>'
        f'<div class="mv" style="color:var(--green)">{m_hoy["prot"]}g</div>'
        f'<div class="ms">/{obj_p}g &middot; {pct_p}%</div>{pb(m_hoy["prot"],obj_p,"var(--green)")}</div>'
        f'<div><div class="lbl">Carbohidratos</div>'
        f'<div class="mv" style="color:var(--blue)">{m_hoy["carb"]}g</div>'
        f'<div class="ms">/{obj_cb}g &middot; {pct_cb}%</div>{pb(m_hoy["carb"],obj_cb,"var(--blue)")}</div>'
        f'<div><div class="lbl">Grasas</div>'
        f'<div class="mv" style="color:var(--amber)">{m_hoy["grasa"]}g</div>'
        f'<div class="ms">/{obj_g}g &middot; {pct_g}%</div>{pb(m_hoy["grasa"],obj_g,"var(--amber)")}</div>'
        f'</div>'),unsafe_allow_html=True)

    # Scanner IA
    sdiv("Scanner con inteligencia artificial")
    prov = st.session_state.proveedor_ia
    key_act = st.session_state.groq_key if "Groq" in prov else st.session_state.gemini_key
    if not key_act.strip():
        st.info(f"Configura tu API Key en la pestana Config para activar el scanner de IA (proveedor: {prov}).")
    else:
        img_up = st.file_uploader("Sube una foto del plato o alimento",
            type=["jpg","jpeg","png","webp"],key="up_scan")
        if img_up:
            st.image(img_up,use_container_width=True)
            sc1,sc2 = st.columns(2)
            with sc1:
                comida_scan = st.selectbox("Tipo de comida",
                    ["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="sc_com")
            with sc2:
                if st.button("Analizar con IA",key="btn_scan"):
                    with st.spinner("Analizando imagen..."):
                        prompt_s = (
                            "Eres un nutricionista experto. Analiza esta imagen en espanol "
                            "con este formato exacto:\n\n"
                            "Alimentos detectados:\n"
                            "- [alimento] — [X] kcal · P:[Xg] C:[Xg] G:[Xg]\n\n"
                            "TOTAL: [NNN] kcal | P:[Xg] C:[Xg] G:[Xg]\n\n"
                            "Valoracion: [una frase sobre el equilibrio nutricional]\n\n"
                            "Si no hay comida, indicalo."
                        )
                        res = ia_call(prompt_s,img_up.read())
                        if res=="ERROR_NO_KEY": st.warning("Configura tu API Key en Config.")
                        else: st.session_state.scan_res = res

        if st.session_state.scan_res:
            st.markdown(card(
                f'<div class="lbl">Resultado del analisis</div>'
                f'<p style="white-space:pre-wrap;color:var(--text2);font-size:.82rem;line-height:1.8">'
                f'{st.session_state.scan_res}</p>'),
                unsafe_allow_html=True)
            kd = extraer_kcal(st.session_state.scan_res)
            if kd>0:
                r1,r2 = st.columns(2)
                with r1:
                    if st.button(f"Registrar {kd} kcal",key="btn_reg_scan"):
                        registrar_alimento("Foto analizada por IA",kd,0,0,0,
                                           st.session_state.get("sc_com","Extra"))
                        st.session_state.scan_res = None
                        st.success("Registrado correctamente.")
                        st.rerun()
                with r2:
                    if st.button("Descartar",key="btn_disc"):
                        st.session_state.scan_res = None
                        st.rerun()

    # Registrar alimento
    sdiv("Registrar alimento")
    ra1,ra2 = st.columns([3,1])
    with ra1:
        alim = st.selectbox("Alimento",list(ALIMENTOS_DB.keys()),
                            key="sel_alim",label_visibility="collapsed")
    with ra2:
        cant = st.number_input("g",1,2000,100,key="cant",label_visibility="collapsed")
    ad  = ALIMENTOS_DB[alim]
    fac = cant/100
    cav = round(ad["cal"]*fac); prv = round(ad["prot"]*fac,1)
    cbv = round(ad["carb"]*fac,1); grv = round(ad["grasa"]*fac,1)
    ico = food_icon(alim)
    st.markdown(card(
        f'<div style="display:flex;align-items:center;gap:.65rem">'
        f'<div style="font-size:1.8rem;line-height:1">{ico}</div>'
        f'<div>'
        f'<div style="font-size:.84rem;font-weight:600;color:var(--text);margin-bottom:.3rem">{alim} — {cant}g</div>'
        f'<span class="badge bk">{cav} kcal</span>'
        f'<span class="badge bp">P {prv}g</span>'
        f'<span class="badge bc">C {cbv}g</span>'
        f'<span class="badge bf">G {grv}g</span>'
        f'</div></div>'),unsafe_allow_html=True)
    ra3,ra4 = st.columns([2,1])
    with ra3:
        com_db = st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="com_db")
    with ra4:
        if st.button("Anadir",key="btn_add_db"):
            registrar_alimento(f"{alim} ({cant}g)",cav,prv,cbv,grv,com_db)
            st.success(f"{cav} kcal registradas")
            st.rerun()

    # Registro manual
    sdiv("Registro manual libre")
    m1,m2,m3,m4 = st.columns([3,1,1,1])
    with m1: nm = st.text_input("Nombre",placeholder="Plato casero",key="nm",label_visibility="collapsed")
    with m2: km = st.number_input("kcal",0,5000,0,5,key="km",label_visibility="collapsed")
    with m3: pm = st.number_input("P(g)",0.0,300.0,0.0,.5,key="pm",label_visibility="collapsed")
    with m4: cbm= st.number_input("C(g)",0.0,500.0,0.0,.5,key="cbm",label_visibility="collapsed")
    m5,m6 = st.columns([2,1])
    with m5: comm=st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="comm")
    with m6:
        if st.button("Anadir",key="btn_man"):
            if km>0:
                registrar_alimento(nm or "Alimento libre",km,pm,cbm,0.0,comm)
                st.success(f"{km} kcal anadidas")
                st.rerun()
            else: st.warning("Introduce kcal mayor que 0")

    # Diario
    sdiv("Diario de hoy")
    diario = st.session_state.datos.get("diario_comidas",{}).get(hoy(),[])
    if not diario:
        st.markdown(card('<div style="text-align:center;padding:1rem 0">'
            '<div class="lbl" style="text-align:center">Sin registros todavia</div>'
            '<p style="color:var(--text3);font-size:.77rem;margin:0">Empieza anadiendo alimentos arriba</p>'
            '</div>'),unsafe_allow_html=True)
    else:
        grupos = {}
        for item in diario: grupos.setdefault(item["comida"],[]).append(item)
        for nc2,items in grupos.items():
            tc  = sum(i["cal"] for i in items)
            filas = "".join(
                f'<div class="row">'
                f'<span class="rl">'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:var(--text3)">{i["hora"]}</span>'
                f'&nbsp;&nbsp;{food_icon(i["alimento"])}&nbsp;{i["alimento"]}</span>'
                f'<span class="rr">{i["cal"]} kcal</span></div>'
                for i in items)
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">'
                f'<span style="font-weight:600;color:var(--dark);font-size:.85rem">{nc2}</span>'
                f'<span class="badge bk">{tc} kcal</span></div>{filas}'),
                unsafe_allow_html=True)

    if st.button("Resetear diario de hoy",key="btn_reset"):
        d = st.session_state.datos
        d.setdefault("historial_calorias",{})[hoy()] = 0
        d.setdefault("historial_macros",{})[hoy()] = {"prot":0.0,"carb":0.0,"grasa":0.0}
        d.setdefault("diario_comidas",{})[hoy()] = []
        save_datos()
        st.success("Diario reseteado.")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DIETAS
# ══════════════════════════════════════════════════════════════════════════════
with t_diet:
    dt1,dt2,dt3,dt4 = st.tabs(["Planes","Calculadora","IA Dietista","Mis dietas"])

    with dt1:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        plan_k = st.selectbox("Plan nutricional",list(DIETAS_TEMPLATE.keys()),key="plan_k")
        plan   = DIETAS_TEMPLATE[plan_k]
        tc_p   = sum(c["cal"]   for c in plan["comidas"])
        tp_p   = sum(c["prot"]  for c in plan["comidas"])
        tcb_p  = sum(c["carb"]  for c in plan["comidas"])
        tg_p   = sum(c["grasa"] for c in plan["comidas"])
        st.markdown(card(
            f'<div class="lbl">Objetivo del plan</div>'
            f'<div style="font-size:.92rem;font-weight:600;color:var(--dark);margin-bottom:.6rem">{plan["objetivo"]}</div>'
            f'<span class="badge bk">{tc_p} kcal totales</span>'
            f'<span class="badge bp">P {tp_p}g</span>'
            f'<span class="badge bc">C {tcb_p}g</span>'
            f'<span class="badge bf">G {tg_p}g</span>',accent=True),
            unsafe_allow_html=True)
        for c in plan["comidas"]:
            ico_c = food_icon(c["alimentos"])
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">'
                f'<div style="display:flex;align-items:center;gap:.5rem">'
                f'<span style="font-size:1.4rem">{ico_c}</span>'
                f'<span style="font-weight:600;font-size:.86rem;color:var(--dark)">{c["nombre"]}</span></div>'
                f'<span class="badge bk">{c["cal"]} kcal</span></div>'
                f'<p style="margin:0 0 .4rem;font-size:.78rem;color:var(--text2)">{c["alimentos"]}</p>'
                f'<span class="badge bp">P {c["prot"]}g</span>'
                f'<span class="badge bc">C {c["carb"]}g</span>'
                f'<span class="badge bf">G {c["grasa"]}g</span>'),
                unsafe_allow_html=True)
        if st.button("Usar como mi objetivo diario",key="btn_usar"):
            st.session_state.datos.setdefault("perfil",{}).update({
                "objetivo_cal":tc_p,"obj_prot":tp_p,"obj_carb":tcb_p,"obj_grasa":tg_p})
            save_datos()
            st.success(f"Objetivo actualizado: {tc_p} kcal/dia")
            st.rerun()

    with dt2:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        pf2 = get_perfil()
        d1,d2 = st.columns(2)
        with d1:
            dp = st.number_input("Peso (kg)",  30.0,250.0,float(pf2.get("peso",75)),.5,key="dp")
            da = st.number_input("Altura (cm)",100,250,int(pf2.get("altura",175)),key="da")
        with d2:
            de = st.number_input("Edad",10,100,int(pf2.get("edad",25)),key="de")
            dsx= st.selectbox("Sexo biologico",["Hombre","Mujer"],key="dsx")
        dact = st.selectbox("Nivel de actividad",[
            "Sedentario (sin ejercicio)","Ligero (1-2 dias/semana)",
            "Moderado (3-4 dias/semana)","Activo (5-6 dias/semana)","Muy activo (2 veces/dia)"],
            index=2,key="dact")
        dobj = st.selectbox("Objetivo",[
            "Perdida de grasa (-300 kcal)","Perdida agresiva (-500 kcal)",
            "Mantenimiento","Volumen limpio (+200 kcal)","Volumen (+400 kcal)"],key="dobj")
        if st.button("Calcular mi TDEE y macros",key="btn_calc"):
            tdee   = calcular_tdee(dp,da,de,dsx,dact)
            delta  = {"Perdida de grasa (-300 kcal)":-300,"Perdida agresiva (-500 kcal)":-500,
                      "Mantenimiento":0,"Volumen limpio (+200 kcal)":200,"Volumen (+400 kcal)":400}[dobj]
            cobj_k = tdee + delta
            perd   = "Perdida" in dobj
            prot_g = round(dp*(2.2 if perd else 1.9))
            gras_g = round(dp*(1.0 if perd else 1.1))
            carb_g = max(round((cobj_k-prot_g*4-gras_g*9)/4),50)
            imc    = round(dp/((da/100)**2),1)
            cat    = ("Bajo peso" if imc<18.5 else "Normopeso" if imc<25
                      else "Sobrepeso" if imc<30 else "Obesidad")
            st.markdown(card(
                f'<div class="lbl">Resultado del calculo</div>'
                f'<div class="sgrid" style="margin-bottom:.7rem">'
                f'<div><div class="lbl">Mantenimiento</div>'
                f'<div class="sv">{tdee}</div><div class="ms">kcal/dia</div></div>'
                f'<div><div class="lbl">Tu objetivo</div>'
                f'<div class="sv" style="color:var(--green)">{cobj_k}</div>'
                f'<div class="ms">kcal/dia</div></div></div>'
                f'<p style="font-size:.8rem;margin-bottom:.5rem">IMC: <b>{imc}</b> — {cat}</p>'
                f'<span class="badge bp">Proteina {prot_g}g</span>'
                f'<span class="badge bc">Carbos {carb_g}g</span>'
                f'<span class="badge bf">Grasas {gras_g}g</span>',accent=True),
                unsafe_allow_html=True)
            if st.button("Guardar estos objetivos",key="btn_sc"):
                st.session_state.datos.setdefault("perfil",{}).update({
                    "peso":dp,"altura":da,"edad":de,
                    "objetivo_cal":cobj_k,"obj_prot":prot_g,"obj_carb":carb_g,"obj_grasa":gras_g})
                save_datos()
                st.success("Objetivos guardados.")
                st.rerun()

    with dt3:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        key_a = st.session_state.groq_key if "Groq" in st.session_state.proveedor_ia else st.session_state.gemini_key
        if not key_a.strip():
            st.info(f"Configura tu API Key en Config para usar la IA Dietista.")
        else:
            pf3 = get_perfil()
            d1,d2 = st.columns(2)
            with d1:
                iap = st.number_input("Peso (kg)",  30.0,250.0,float(pf3.get("peso",75)),.5,key="iap")
                iaa = st.number_input("Altura (cm)",100,250,int(pf3.get("altura",175)),key="iaa")
                iae = st.number_input("Edad",10,100,int(pf3.get("edad",25)),key="iae")
            with d2:
                iasx= st.selectbox("Sexo",["Hombre","Mujer"],key="iasx")
                iaob= st.selectbox("Objetivo",[
                    "Perder grasa","Ganar musculo","Mantenimiento",
                    "Mejorar rendimiento","Salud general"],key="iaob")
                iaac= st.selectbox("Actividad",
                    ["Sedentario","Ligero","Moderado","Activo","Muy activo"],key="iaac")
            iarest = st.multiselect("Restricciones y preferencias",[
                "Sin gluten","Sin lactosa","Vegetariano","Vegano",
                "Sin cerdo","Sin mariscos","Bajo en sodio","Bajo en azucar"],key="iarest")
            iaext  = st.text_area("Contexto adicional",
                placeholder="Alergias, horarios, patologias...",height=65,key="iaext")
            if st.button("Generar mi plan con IA",key="btn_ia"):
                rest_s = ", ".join(iarest) if iarest else "ninguna"
                pr = (f"Eres un dietista-nutricionista experto. Crea un plan completo en espanol para:\n"
                      f"- Perfil: {iasx}, {iae} anios, {iap}kg, {iaa}cm\n"
                      f"- Objetivo: {iaob} | Actividad: {iaac} | Restricciones: {rest_s}\n"
                      f"- Info extra: {iaext or 'ninguna'}\n\n"
                      f"Incluye:\n1. Calorias y macros en gramos\n"
                      f"2. Plan de 5-6 comidas con alimentos concretos y cantidades\n"
                      f"3. Timing nutricional pre/post entreno\n"
                      f"4. Lista de la compra semanal\n5. 3 consejos clave\n\n"
                      f"Se muy especifico con cantidades.")
                with st.spinner("Generando tu plan personalizado..."):
                    res = ia_call(pr)
                    if res=="ERROR_NO_KEY": st.warning("Configura tu API Key en Config.")
                    else: st.session_state.ia_dieta_res = res
            if st.session_state.ia_dieta_res:
                st.markdown(card(
                    f'<div class="lbl">Plan generado</div>'
                    f'<p style="white-space:pre-wrap;color:var(--text2);font-size:.81rem;line-height:1.85">'
                    f'{st.session_state.ia_dieta_res}</p>'),
                    unsafe_allow_html=True)
                if st.button("Nuevo plan",key="btn_ia_r"):
                    st.session_state.ia_dieta_res = None
                    st.rerun()

    with dt4:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        dc_all = st.session_state.datos.get("dietas_custom",{})
        if dc_all:
            dc_sel = st.selectbox("Mis dietas",["— Nueva —"]+list(dc_all.keys()),key="dc_sel")
            if dc_sel!="— Nueva —":
                dc = dc_all[dc_sel]
                if dc.get("notas"):
                    st.markdown(card(f'<p style="font-size:.8rem;color:var(--text2)">{dc["notas"]}</p>'),unsafe_allow_html=True)
                for c in dc.get("comidas",[]):
                    st.markdown(card(
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:.3rem">'
                        f'<span style="font-weight:600;font-size:.84rem;color:var(--dark)">{food_icon(c.get("alimentos",""))} {c["nombre"]}</span>'
                        f'<span class="badge bk">{c.get("cal",0)} kcal</span></div>'
                        f'<p style="margin:0 0 .4rem;font-size:.78rem;color:var(--text2)">{c.get("alimentos","")}</p>'
                        f'<span class="badge bp">P {c.get("prot",0)}g</span>'
                        f'<span class="badge bc">C {c.get("carb",0)}g</span>'
                        f'<span class="badge bf">G {c.get("grasa",0)}g</span>'),
                        unsafe_allow_html=True)
                if st.button("Eliminar esta dieta",key="btn_del_dc"):
                    del st.session_state.datos["dietas_custom"][dc_sel]
                    save_datos()
                    st.success("Dieta eliminada.")
                    st.rerun()
        sdiv("Crear nueva dieta personalizada")
        nc_nom = st.text_input("Nombre de la dieta",placeholder="Mi dieta de verano",key="nc_nom")
        nc_not = st.text_area("Descripcion y notas",placeholder="Objetivo, duracion...",height=55,key="nc_not")
        sdiv("Anadir comidas al plan")
        dc1,dc2 = st.columns([2,1])
        with dc1:
            nc_cn = st.text_input("Nombre de la comida",placeholder="Almuerzo",key="nc_cn")
            nc_al = st.text_area("Alimentos y cantidades",placeholder="Pollo 150g, Arroz 100g",height=50,key="nc_al")
        with dc2:
            nc_cal = st.number_input("kcal",0,3000,0,10,key="nc_cal")
            nc_pr  = st.number_input("P (g)",0.0,200.0,0.0,.5,key="nc_pr")
            nc_cb2 = st.number_input("C (g)",0.0,500.0,0.0,.5,key="nc_cb2")
            nc_gr  = st.number_input("G (g)",0.0,200.0,0.0,.5,key="nc_gr")
        if st.button("Anadir comida",key="btn_add_nc"):
            if nc_cn:
                st.session_state.comidas_dc_temp.append({
                    "nombre":nc_cn,"alimentos":nc_al,
                    "cal":nc_cal,"prot":nc_pr,"carb":nc_cb2,"grasa":nc_gr})
                st.success(f"'{nc_cn}' anadida.")
            else: st.warning("Escribe el nombre de la comida.")
        if st.session_state.comidas_dc_temp:
            tot_dc = sum(c["cal"] for c in st.session_state.comidas_dc_temp)
            filas_dc = "".join(
                f'<div class="row"><span class="rl">{i+1}. {food_icon(c.get("alimentos",""))} {c["nombre"]}</span>'
                f'<span class="rr">{c["cal"]} kcal</span></div>'
                for i,c in enumerate(st.session_state.comidas_dc_temp))
            st.markdown(card(f'{filas_dc}'
                f'<div style="text-align:right;margin-top:.4rem">'
                f'<span class="badge bk">Total: {tot_dc} kcal</span></div>'),
                unsafe_allow_html=True)
        if st.button("Guardar dieta",key="btn_save_dc"):
            if not nc_nom: st.warning("Dale un nombre a la dieta.")
            elif not st.session_state.comidas_dc_temp: st.warning("Anade al menos una comida.")
            else:
                st.session_state.datos.setdefault("dietas_custom",{})[nc_nom] = {
                    "notas":nc_not,"comidas":st.session_state.comidas_dc_temp.copy()}
                save_datos()
                st.session_state.comidas_dc_temp = []
                st.success(f"Dieta '{nc_nom}' guardada.")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# GIMNASIO
# ══════════════════════════════════════════════════════════════════════════════
with t_gym:
    g1,g2,g3 = st.tabs(["Ejercicios","Rutinas","Registro"])

    with g1:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        grupo = st.selectbox("Grupo muscular",list(EJERCICIOS_GYM.keys()),key="grupo")
        for ej in EJERCICIOS_GYM[grupo]:
            tc,tbg = TIPO_COLOR.get(ej["tipo"],("#4a6352","rgba(74,99,82,.1)"))
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:.4rem;flex-wrap:wrap;margin-bottom:.4rem">'
                f'<span style="font-weight:600;font-size:.86rem;color:var(--dark)">{ej["nombre"]}</span>'
                f'<span class="typebadge" style="color:{tc};background:{tbg};border-color:{tc}55">{ej["tipo"]}</span></div>'
                f'<div style="font-size:.7rem;color:var(--text3);margin-bottom:.3rem">{ej["equipo"]}</div>'
                f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;font-size:.77rem;color:var(--text2);margin-bottom:.3rem">'
                f'<span>{ej["series_rec"]} series</span><span style="color:var(--border2)">·</span>'
                f'<span>{ej["reps_rec"]} reps</span><span style="color:var(--border2)">·</span>'
                f'<span>{ej["descanso"]}</span></div>'
                f'<p style="font-size:.72rem;color:var(--text3);font-style:italic;margin:0">{ej["notas"]}</p>'),
                unsafe_allow_html=True)

    with g2:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        todas = {**RUTINAS_DEFAULT,**st.session_state.datos.get("rutinas_custom",{})}
        rut_k = st.selectbox("Rutina",list(todas.keys()),key="rut_k")
        rut   = todas[rut_k]
        desc  = rut.get("desc","") if isinstance(rut,dict) else ""
        ejs   = rut.get("ejercicios",rut) if isinstance(rut,dict) else rut
        if desc:
            st.markdown(f'<div style="font-size:.75rem;color:var(--text3);margin-bottom:.75rem">{desc}</div>',unsafe_allow_html=True)
        for idx,ej in enumerate(ejs):
            p_s = f" · {ej['peso']}" if ej.get("peso") else ""
            n_s = (f'<p style="font-size:.7rem;color:var(--text3);font-style:italic;margin-top:.2rem">{ej["notas"]}</p>'
                   if ej.get("notas") else "")
            st.markdown(card(
                f'<div style="display:flex;align-items:flex-start;gap:.65rem">'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:.58rem;color:var(--text3);padding-top:.15rem;min-width:18px">'
                f'{idx+1:02d}</div>'
                f'<div style="flex:1"><div style="font-weight:600;font-size:.84rem;color:var(--dark);margin-bottom:.25rem">{ej["ejercicio"]}</div>'
                f'<div style="display:flex;gap:.35rem;flex-wrap:wrap;font-size:.76rem;color:var(--text2)">'
                f'<span>{ej["series"]} series</span><span style="color:var(--border2)">·</span>'
                f'<span>{ej["reps"]} reps</span><span style="color:var(--border2)">·</span>'
                f'<span>{ej["descanso"]}{p_s}</span></div>{n_s}</div></div>'),
                unsafe_allow_html=True)
        sdiv("Crear rutina personalizada")
        with st.expander("Nueva rutina"):
            nr_n = st.text_input("Nombre",placeholder="Mi rutina de lunes",key="nr_n")
            nr_d = st.text_input("Descripcion",placeholder="Pecho y triceps",key="nr_d")
            sdiv("Ejercicios")
            e1,e2,e3 = st.columns([3,1,2])
            with e1: nr_ej=st.text_input("Ejercicio",placeholder="Press banca",key="nr_ej",label_visibility="collapsed")
            with e2: nr_s =st.number_input("Series",1,20,4,key="nr_s",label_visibility="collapsed")
            with e3: nr_r =st.text_input("Reps",placeholder="8-12",key="nr_r",label_visibility="collapsed")
            e4,e5,e6 = st.columns([2,2,2])
            with e4: nr_p =st.text_input("Peso",placeholder="60kg",key="nr_p",label_visibility="collapsed")
            with e5: nr_dc=st.text_input("Descanso",placeholder="90s",key="nr_dc",label_visibility="collapsed")
            with e6: nr_nt=st.text_input("Nota",placeholder="Tecnica...",key="nr_nt",label_visibility="collapsed")
            if st.button("Anadir ejercicio",key="btn_add_ej"):
                if nr_ej:
                    st.session_state.ej_temp.append({
                        "ejercicio":nr_ej,"series":nr_s,"reps":nr_r or "8-12",
                        "peso":nr_p,"descanso":nr_dc or "60s","notas":nr_nt})
                    st.success(f"'{nr_ej}' anadido.")
                else: st.warning("Escribe el nombre del ejercicio.")
            if st.session_state.ej_temp:
                filas_ej = "".join(
                    f'<div class="row"><span class="rl">{i+1}. {e["ejercicio"]}</span>'
                    f'<span class="rr">{e["series"]}x{e["reps"]}</span></div>'
                    for i,e in enumerate(st.session_state.ej_temp))
                st.markdown(card(filas_ej),unsafe_allow_html=True)
            if st.button("Guardar rutina",key="btn_save_rut"):
                if not nr_n: st.warning("Dale un nombre.")
                elif not st.session_state.ej_temp: st.warning("Anade al menos un ejercicio.")
                else:
                    st.session_state.datos.setdefault("rutinas_custom",{})[nr_n] = {
                        "desc":nr_d,"ejercicios":st.session_state.ej_temp.copy()}
                    save_datos()
                    st.session_state.ej_temp = []
                    st.success(f"Rutina '{nr_n}' guardada.")
                    st.rerun()

    with g3:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        r1,r2 = st.columns(2)
        with r1:
            reg_tipo = st.selectbox("Tipo de sesion",
                ["PPL — Empuje","PPL — Tiron","PPL — Piernas",
                 "Full Body","Upper","Lower","HIIT","Calistenia","Cardio","Otro"],key="reg_tipo")
        with r2:
            reg_dur = st.number_input("Duracion (min)",10,300,60,key="reg_dur")
        reg_notas = st.text_area("Notas del entreno",placeholder="Sensaciones, PRs, observaciones...",height=65,key="reg_notas")
        sdiv("Series realizadas")
        sr1,sr2,sr3,sr4 = st.columns(4)
        with sr1: ej_n =st.text_input("Ejercicio",placeholder="Sentadilla",key="ej_n",label_visibility="collapsed")
        with sr2: set_s=st.number_input("Series",1,20,3,key="set_s",label_visibility="collapsed")
        with sr3: set_r=st.text_input("Reps",placeholder="10",key="set_r",label_visibility="collapsed")
        with sr4: set_p=st.text_input("Peso",placeholder="80kg",key="set_p",label_visibility="collapsed")
        if st.button("Anadir serie",key="btn_add_set"):
            if ej_n:
                st.session_state.sets_temp.append({
                    "ejercicio":ej_n,"series":set_s,"reps":set_r or "—","peso":set_p or "—"})
                st.success(f"'{ej_n}' registrado.")
            else: st.warning("Escribe el nombre del ejercicio.")
        if st.session_state.sets_temp:
            filas_s = "".join(
                f'<div class="row"><span class="rl">{s["ejercicio"]}</span>'
                f'<span class="rr">{s["series"]}x{s["reps"]} · {s["peso"]}</span></div>'
                for s in st.session_state.sets_temp)
            st.markdown(card(filas_s),unsafe_allow_html=True)
        if st.button("Guardar sesion",key="btn_save_ses"):
            reg = st.session_state.datos.setdefault("registro_entreno",{})
            reg.setdefault(hoy(),[]).append({
                "tipo":reg_tipo,"duracion":reg_dur,"notas":reg_notas,
                "series":st.session_state.sets_temp.copy(),
                "hora":datetime.now().strftime("%H:%M"),
            })
            save_datos()
            st.session_state.sets_temp = []
            st.success("Sesion guardada.")
            st.rerun()
        sdiv("Ultimas sesiones")
        reg_all = st.session_state.datos.get("registro_entreno",{})
        if not reg_all:
            st.markdown(card('<div style="text-align:center;padding:.85rem 0">'
                '<p style="color:var(--text3);font-size:.77rem;margin:0">Sin sesiones registradas todavia</p></div>'),
                unsafe_allow_html=True)
        for fk in sorted(reg_all.keys(),reverse=True)[:7]:
            for ses in reg_all[fk]:
                ns = len(ses.get("series",[]))
                st.markdown(card(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">'
                    f'<span style="font-weight:600;font-size:.84rem;color:var(--dark)">{ses["tipo"]}</span>'
                    f'<span class="badge bn">{fk}</span></div>'
                    f'<div style="display:flex;gap:.35rem;flex-wrap:wrap;font-size:.76rem;color:var(--text2)">'
                    f'<span>{ses["duracion"]} min</span><span style="color:var(--border2)">·</span>'
                    f'<span>{ns} ejercicios</span><span style="color:var(--border2)">·</span>'
                    f'<span>{ses.get("hora","")}</span></div>'
                    f'{"<p style=margin-top:.3rem;font-size:.72rem;color:var(--text3)>" + ses["notas"] + "</p>" if ses.get("notas") else ""}'),
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════════════════════════════════════
with t_hist:
    st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
    hist_c = st.session_state.datos.get("historial_calorias",{})
    hist_m = st.session_state.datos.get("historial_macros",{})
    reg_e  = st.session_state.datos.get("registro_entreno",{})
    if not hist_c:
        st.markdown(card('<div style="text-align:center;padding:1.25rem 0">'
            '<div class="lbl" style="text-align:center">Sin historial</div>'
            '<p style="color:var(--text3);font-size:.77rem;margin:0">Empieza a registrar alimentos en Nutricion</p></div>'),
            unsafe_allow_html=True)
    else:
        fechas = sorted(hist_c.keys())[-14:]
        vals   = [hist_c.get(f,0) for f in fechas]
        etiq   = [f[-5:] for f in fechas]
        obj_h  = get_obj_cal()
        if vals:
            prom    = round(sum(vals)/len(vals))
            maxi    = max(vals)
            dias_ok = sum(1 for v in vals if 0<v<=obj_h)
            st.markdown(card(
                f'<div class="lbl">Resumen de los ultimos 14 dias</div>'
                f'<div class="sgrid">'
                f'<div><div class="lbl">Promedio diario</div>'
                f'<div class="sv">{prom}</div><div class="ms">kcal/dia</div></div>'
                f'<div><div class="lbl">Dias en objetivo</div>'
                f'<div class="sv" style="color:var(--green)">{dias_ok}</div>'
                f'<div class="ms">de {len([v for v in vals if v>0])} registrados</div></div>'
                f'</div>',accent=True),
                unsafe_allow_html=True)
            max_v = max(vals+[obj_h,1])
            bars  = '<div style="display:flex;align-items:flex-end;gap:3px;height:90px;margin-top:1rem">'
            for et,vl in zip(etiq,vals):
                h   = int(vl/max_v*90) if vl>0 else 2
                clr = "var(--green)" if vl<=obj_h and vl>0 else ("var(--red)" if vl>obj_h else "var(--bg2)")
                bars += (f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">'
                         f'<div style="flex:1;display:flex;align-items:flex-end;width:100%">'
                         f'<div style="width:100%;height:{h}px;background:{clr};border-radius:3px 3px 0 0"></div></div>'
                         f'<div style="font-family:JetBrains Mono,monospace;font-size:.44rem;color:var(--text3);white-space:nowrap">{et}</div>'
                         f'</div>')
            bars += '</div>'
            st.markdown(card(
                f'<div class="lbl">Calorias diarias</div>{bars}'
                f'<div style="display:flex;gap:.5rem;margin-top:.5rem;flex-wrap:wrap">'
                f'<span class="badge bp" style="font-size:.54rem">Verde = dentro del objetivo</span>'
                f'<span class="badge bw" style="font-size:.54rem">Rojo = por encima</span></div>'),
                unsafe_allow_html=True)
        dias_m = [d for d in fechas if d in hist_m and any(v>0 for v in hist_m[d].values())]
        if dias_m:
            pm = {"prot":0.0,"carb":0.0,"grasa":0.0}
            for d in dias_m:
                for k in pm: pm[k] += hist_m[d].get(k,0)
            n  = len(dias_m)
            pm = {k:round(v/n,1) for k,v in pm.items()}
            st.markdown(card(
                f'<div class="lbl">Macros promedio diario</div>'
                f'<div class="mgrid">'
                f'<div><div class="lbl">Proteina</div><div class="mv" style="color:var(--green)">{pm["prot"]}g</div></div>'
                f'<div><div class="lbl">Carbos</div><div class="mv" style="color:var(--blue)">{pm["carb"]}g</div></div>'
                f'<div><div class="lbl">Grasas</div><div class="mv" style="color:var(--amber)">{pm["grasa"]}g</div></div>'
                f'</div>'),unsafe_allow_html=True)
        ses_t = sum(len(v) for v in reg_e.values())
        min_t = sum(s.get("duracion",0) for v in reg_e.values() for s in v)
        if ses_t>0:
            st.markdown(card(
                f'<div class="lbl">Entrenamientos totales</div>'
                f'<div class="sgrid">'
                f'<div><div class="lbl">Sesiones</div><div class="sv">{ses_t}</div></div>'
                f'<div><div class="lbl">Horas totales</div>'
                f'<div class="sv" style="color:var(--green)">{round(min_t/60,1)}</div></div>'
                f'</div>'),unsafe_allow_html=True)
        if st.button("Borrar historial completo",key="btn_del_hist"):
            d = st.session_state.datos
            d["historial_calorias"] = {}
            d["historial_macros"]   = {}
            d["diario_comidas"]     = {}
            save_datos()
            st.success("Historial borrado.")
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
with t_cfg:
    st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)

    # Sesion
    sdiv("Sesion activa")
    st.markdown(card(
        f'<div class="row"><span class="rl">Usuario</span><span class="rr">{st.session_state.user_email}</span></div>'
        f'<div class="row"><span class="rl">Estado</span><span class="rr">Conectado</span></div>'),
        unsafe_allow_html=True)
    if st.button("Cerrar sesion",key="btn_logout"):
        for k in ["logged_in","user_id","user_email","datos","scan_res","ia_dieta_res",
                  "ej_temp","sets_temp","comidas_dc_temp"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    # IA Provider
    sdiv("Proveedor de inteligencia artificial")
    st.markdown(card(
        '<div class="lbl">Comparativa de proveedores</div>'
        '<div class="row"><span class="rl">Groq (recomendado)</span>'
        '<span class="rr"><span class="badge bp">1500 peticiones/dia</span></span></div>'
        '<div class="row"><span class="rl">Gemini</span>'
        '<span class="rr"><span class="badge bw">~20 peticiones/dia</span></span></div>'
        '<p style="font-size:.75rem;color:var(--text3);margin-top:.5rem;margin-bottom:0">'
        'Groq es la opcion recomendada: mas generosa, mas rapida y completamente gratuita.</p>'),
        unsafe_allow_html=True)
    prov_sel = st.selectbox("",["Groq (recomendado)","Gemini"],
        index=0 if "Groq" in st.session_state.proveedor_ia else 1,
        key="prov_sel",label_visibility="collapsed")
    if st.button("Cambiar proveedor",key="btn_prov"):
        st.session_state.proveedor_ia = prov_sel
        st.success(f"Proveedor: {prov_sel}")
        st.rerun()

    # Groq Key
    sdiv("Groq API Key")
    st.markdown(card(
        '<div class="row"><span class="rl">1. Regístrate en</span><span class="rr">console.groq.com/keys</span></div>'
        '<div class="row"><span class="rl">2. Pulsa</span><span class="rr">Create API Key</span></div>'
        '<div class="row"><span class="rl">3. La clave empieza por</span><span class="rr">gsk_...</span></div>'
        '<div class="row"><span class="rl">4. Sin tarjeta de credito</span><span class="rr">100% gratuita</span></div>'),
        unsafe_allow_html=True)
    gi = st.text_input("Groq Key",value=st.session_state.groq_key,type="password",placeholder="gsk_...",key="gi")
    g1b,g2b = st.columns(2)
    with g1b:
        if st.button("Guardar",key="btn_groq"):
            st.session_state.groq_key = gi.strip()
            st.session_state.datos.setdefault("perfil",{})["groq_key"] = gi.strip()
            save_datos()
            st.success("Guardada.")
    with g2b:
        if st.session_state.groq_key and st.button("Probar",key="btn_tg"):
            with st.spinner("Probando..."):
                prev = st.session_state.proveedor_ia
                st.session_state.proveedor_ia = "Groq (recomendado)"
                res  = ia_call("Responde solo: OK")
                st.session_state.proveedor_ia = prev
                st.success(f"OK: {res[:50]}") if "OK" in res or len(res)<80 else st.error(res[:150])

    # Gemini Key
    sdiv("Gemini API Key")
    mi = st.text_input("Gemini Key",value=st.session_state.gemini_key,type="password",placeholder="AIzaSy...",key="mi")
    mg1,mg2 = st.columns(2)
    with mg1:
        if st.button("Guardar",key="btn_gem"):
            st.session_state.gemini_key = mi.strip()
            st.session_state.datos.setdefault("perfil",{})["gemini_key"] = mi.strip()
            save_datos()
            st.success("Guardada.")
    with mg2:
        if st.session_state.gemini_key and st.button("Probar",key="btn_tm"):
            with st.spinner("Probando..."):
                prev = st.session_state.proveedor_ia
                st.session_state.proveedor_ia = "Gemini"
                res  = ia_call("Responde solo: OK")
                st.session_state.proveedor_ia = prev
                st.success(f"OK: {res[:50]}") if "OK" in res or len(res)<80 else st.error(res[:150])

    # Perfil
    sdiv("Perfil personal")
    pf_c = get_perfil()
    cfg1,cfg2 = st.columns(2)
    with cfg1:
        cn = st.text_input("Nombre",value=pf_c.get("nombre",""),key="cn")
        cp2= st.number_input("Peso (kg)",30.0,250.0,float(pf_c.get("peso",75.0)),.5,key="cp2")
        ca3= st.number_input("Altura (cm)",100,250,int(pf_c.get("altura",175)),key="ca3")
    with cfg2:
        ce = st.number_input("Edad",10,100,int(pf_c.get("edad",25)),key="ce")
        coc= st.number_input("Objetivo kcal/dia",800,6000,int(pf_c.get("objetivo_cal",2000)),50,key="coc")
        cpr= st.number_input("Obj. proteina (g)",0,400,int(pf_c.get("obj_prot",150)),5,key="cpr")
    cfg3,cfg4 = st.columns(2)
    with cfg3: ccb=st.number_input("Obj. carbos (g)",0,800,int(pf_c.get("obj_carb",220)),5,key="ccb")
    with cfg4: cgr=st.number_input("Obj. grasas (g)",0,300,int(pf_c.get("obj_grasa",60)),5,key="cgr")
    if st.button("Guardar perfil",key="btn_perfil"):
        st.session_state.datos.setdefault("perfil",{}).update({
            "nombre":cn,"peso":cp2,"altura":ca3,"edad":ce,
            "objetivo_cal":coc,"obj_prot":cpr,"obj_carb":ccb,"obj_grasa":cgr,
        })
        save_datos()
        st.success("Perfil guardado.")
        st.rerun()

    # Supabase
    sdiv("Base de datos Supabase (opcional)")
    st.markdown(card(
        '<div class="lbl">Para persistencia en la nube entre dispositivos</div>'
        '<div class="row"><span class="rl">1. Crea cuenta gratis en</span><span class="rr">supabase.com</span></div>'
        '<div class="row"><span class="rl">2. Nuevo proyecto</span><span class="rr">Settings > API</span></div>'
        '<div class="row"><span class="rl">3. Copia URL y anon key</span><span class="rr">a Streamlit Secrets</span></div>'
        '<div class="row"><span class="rl">4. Secrets necesarios</span><span class="rr">SUPABASE_URL · SUPABASE_KEY</span></div>'
        f'<div class="row"><span class="rl">Estado actual</span>'
        f'<span class="rr">{"<span class=badge bp>Conectado</span>" if get_supabase() else "<span class=badge bw>Local (sin Supabase)</span>"}</span></div>'),
        unsafe_allow_html=True)

    # Info version
    sdiv("Acerca de")
    st.markdown(card(
        '<div class="row"><span class="rl">Version</span><span class="rr">FitAI Pro 4.0</span></div>'
        '<div class="row"><span class="rl">Stack</span><span class="rr">Streamlit · Groq · Gemini · Supabase</span></div>'
        '<div class="row"><span class="rl">Datos</span><span class="rr">Privados por usuario</span></div>'
        '<div class="row"><span class="rl">Hosting</span><span class="rr">Streamlit Community Cloud (gratis)</span></div>'),
        unsafe_allow_html=True)

    # Restore profile keys at bottom of config
    pfs = st.session_state.datos.get("perfil",{})
    if not st.session_state.groq_key   and pfs.get("groq_key"):
        st.session_state.groq_key   = pfs["groq_key"]
    if not st.session_state.gemini_key and pfs.get("gemini_key"):
        st.session_state.gemini_key = pfs["gemini_key"]
