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
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM  ·  Dark Premium  ·  Inspired by INDYA / fitness apps
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;600;700;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
  --bg:       #0a0e1a;
  --bg2:      #0f1525;
  --bg3:      #141929;
  --surface:  #1a2035;
  --surface2: #1f2740;
  --border:   #ffffff12;
  --border2:  #ffffff1e;
  --cyan:     #00e5ff;
  --cyan2:    #00b8d4;
  --cyan3:    rgba(0,229,255,.15);
  --green:    #00e676;
  --green2:   #00c853;
  --green3:   rgba(0,230,118,.12);
  --pink:     #ff4081;
  --amber:    #ffab40;
  --purple:   #7c4dff;
  --text:     #e8eaf6;
  --text2:    #90a4ae;
  --text3:    #546e7a;
  --r:        16px;
  --rsm:      10px;
  --glow-c:   0 0 20px rgba(0,229,255,.25);
  --glow-g:   0 0 20px rgba(0,230,118,.25);
  --glow-p:   0 0 20px rgba(255,64,129,.2);
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
  max-width: 780px !important;
  padding: 0 1.1rem 7rem !important;
  margin: 0 auto !important;
}

/* ── HERO ── */
.hero {
  padding: 2.4rem 0 1.8rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
  position: relative;
}
.hero::after {
  content: '';
  position: absolute;
  top: 0; left: -20px; right: -20px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}
.hero-tag {
  font-family: 'Orbitron', monospace;
  font-size: .55rem;
  color: var(--cyan);
  letter-spacing: .22em;
  text-transform: uppercase;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: .6rem;
}
.hero-dot {
  width: 7px; height: 7px;
  background: var(--cyan);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--cyan);
  animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
  0%,100% { opacity: 1; }
  50%      { opacity: .3; }
}
.hero-title {
  font-family: 'Orbitron', monospace;
  font-size: clamp(2.4rem, 9vw, 5rem);
  font-weight: 900;
  line-height: .88;
  letter-spacing: -.02em;
  color: #fff;
  margin-bottom: .9rem;
}
.hero-title .accent { color: var(--cyan); text-shadow: var(--glow-c); }
.hero-sub {
  font-size: .75rem;
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
  padding: 1.25rem 1.4rem;
  margin-bottom: .85rem;
  transition: border-color .2s, box-shadow .2s;
  position: relative;
  overflow: hidden;
}
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--border2), transparent);
}
.card:hover {
  border-color: var(--border2);
  box-shadow: 0 8px 32px rgba(0,0,0,.4);
}
.card.accent {
  background: linear-gradient(135deg, #00363a 0%, #004d40 50%, #00251a 100%);
  border-color: rgba(0,230,118,.3);
  box-shadow: var(--glow-g);
}
.card.accent-cyan {
  background: linear-gradient(135deg, #001f2d 0%, #002b3d 50%, #00151e 100%);
  border-color: rgba(0,229,255,.3);
  box-shadow: var(--glow-c);
}
.card.accent-pink {
  background: linear-gradient(135deg, #1a0010 0%, #2d0018 50%, #1a0010 100%);
  border-color: rgba(255,64,129,.3);
  box-shadow: var(--glow-p);
}

.lbl {
  font-family: 'Orbitron', monospace;
  font-size: .5rem;
  color: var(--text3);
  letter-spacing: .18em;
  text-transform: uppercase;
  margin-bottom: .65rem;
}
.lbl.c { color: var(--cyan); }
.lbl.g { color: var(--green); }

/* ── BIG NUMBER ── */
.big {
  font-family: 'Orbitron', monospace;
  font-size: 3.2rem;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -.02em;
  color: #fff;
}
.big.cyan  { color: var(--cyan);  text-shadow: var(--glow-c); }
.big.green { color: var(--green); text-shadow: var(--glow-g); }
.big.pink  { color: var(--pink);  text-shadow: var(--glow-p); }
.big-sub {
  font-size: .6rem;
  color: var(--text3);
  font-family: 'Orbitron', monospace;
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-top: .3rem;
}

/* ── CIRCULAR PROGRESS ── */
.ring-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .5rem;
}
.ring {
  position: relative;
  width: 100px; height: 100px;
}
.ring svg { transform: rotate(-90deg); }
.ring-val {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%,-50%);
  text-align: center;
}
.ring-num {
  font-family: 'Orbitron', monospace;
  font-size: .95rem;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}
.ring-pct {
  font-family: 'Orbitron', monospace;
  font-size: .45rem;
  color: var(--text3);
  letter-spacing: .1em;
}

/* ── PROGRESS BAR ── */
.pb {
  background: rgba(255,255,255,.06);
  border-radius: 999px;
  height: 5px;
  overflow: hidden;
  margin-top: .6rem;
}
.pb-f {
  height: 100%;
  border-radius: 999px;
  transition: width .7s cubic-bezier(.4,0,.2,1);
  position: relative;
}
.pb-f::after {
  content: '';
  position: absolute;
  right: 0; top: -1px; bottom: -1px;
  width: 6px;
  border-radius: 50%;
  background: inherit;
  filter: brightness(1.5);
}

/* ── MACRO GRID ── */
.mgrid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.mv {
  font-family: 'Orbitron', monospace;
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1;
  color: #fff;
}
.ms { font-size: .55rem; color: var(--text3); font-family: 'Orbitron', monospace; margin-top: .15rem; letter-spacing: .08em; }

/* ── STAT GRID ── */
.sgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.sv {
  font-family: 'Orbitron', monospace;
  font-size: 1.7rem;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

/* ── BADGES ── */
.badge {
  display: inline-flex;
  align-items: center;
  padding: .2rem .6rem;
  border-radius: 6px;
  font-size: .62rem;
  font-weight: 600;
  margin: .1rem .05rem 0 0;
  font-family: 'Orbitron', monospace;
  border: 1px solid transparent;
  letter-spacing: .04em;
}
.bk  { background: var(--green3);  color: var(--green);  border-color: rgba(0,230,118,.25); }
.bp  { background: rgba(0,229,255,.1); color: var(--cyan);  border-color: rgba(0,229,255,.25); }
.bc  { background: rgba(124,77,255,.12); color: #b39ddb; border-color: rgba(124,77,255,.25); }
.bf  { background: rgba(255,171,64,.1);  color: var(--amber); border-color: rgba(255,171,64,.25); }
.bn  { background: rgba(255,255,255,.05); color: var(--text2); border-color: var(--border); }
.bw  { background: rgba(255,64,129,.1);  color: var(--pink);  border-color: rgba(255,64,129,.25); }
.bpurp { background: rgba(124,77,255,.12); color: #b39ddb; border-color: rgba(124,77,255,.25); }

/* ── ROWS ── */
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .38rem 0;
  border-bottom: 1px solid var(--border);
  font-size: .8rem;
}
.row:last-child { border-bottom: none; }
.rl { color: var(--text2); font-family: 'DM Sans', sans-serif; }
.rr { color: var(--text); font-family: 'Orbitron', monospace; font-size: .65rem; letter-spacing: .04em; }

/* ── SEPARATOR ── */
.sep {
  display: flex;
  align-items: center;
  gap: .65rem;
  margin: 1.6rem 0 1rem;
}
.sep-l { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, var(--border2)); }
.sep-l.r { background: linear-gradient(90deg, var(--border2), transparent); }
.sep-t {
  font-family: 'Orbitron', monospace;
  font-size: .5rem;
  color: var(--cyan);
  text-transform: uppercase;
  letter-spacing: .18em;
  white-space: nowrap;
}

/* ── TYPE BADGE ── */
.typebadge {
  font-family: 'Orbitron', monospace;
  font-size: .48rem;
  font-weight: 700;
  padding: .18rem .5rem;
  border-radius: 6px;
  letter-spacing: .06em;
  text-transform: uppercase;
  border: 1px solid;
}

/* ── BUTTONS ── */
div.stButton > button {
  background: linear-gradient(135deg, var(--cyan2), var(--cyan)) !important;
  color: #000 !important;
  font-family: 'Orbitron', monospace !important;
  font-size: .68rem !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: var(--rsm) !important;
  padding: .65rem 1.2rem !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: all .2s !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  box-shadow: 0 4px 20px rgba(0,229,255,.3) !important;
}
div.stButton > button:hover {
  box-shadow: 0 6px 28px rgba(0,229,255,.5) !important;
  transform: translateY(-1px) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

/* ── INPUTS ── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stNumberInput input {
  background: var(--bg2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .83rem !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 3px rgba(0,229,255,.12) !important;
}
div[data-baseweb="select"] > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  color: var(--text) !important;
}
label { color: var(--text2) !important; font-size: .75rem !important; font-family: 'DM Sans', sans-serif !important; }

/* ── TABS ── */
[data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--rsm) !important;
  padding: 3px !important;
  gap: 2px !important;
}
[data-baseweb="tab"] {
  color: var(--text3) !important;
  font-family: 'Orbitron', monospace !important;
  font-weight: 700 !important;
  font-size: .6rem !important;
  border-radius: 8px !important;
  padding: .38rem .85rem !important;
  letter-spacing: .05em !important;
  text-transform: uppercase !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: linear-gradient(135deg, var(--cyan2), var(--cyan)) !important;
  color: #000 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  border: 1.5px dashed var(--border2) !important;
  border-radius: var(--r) !important;
  background: var(--bg2) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  font-size: .78rem !important;
  color: var(--cyan) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--rsm) !important;
}
[data-testid="stExpander"] summary {
  color: var(--text2) !important;
  font-size: .78rem !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── FOOD PILL ── */
.food-pill {
  display: inline-flex;
  align-items: center;
  gap: .4rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: .22rem .65rem;
  font-size: .72rem;
  color: var(--text2);
  margin: .1rem;
}

/* ── LOGIN ── */
.login-hero {
  text-align: center;
  padding: 3rem 0 2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
  position: relative;
}
.login-hero::before {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(0,229,255,.06) 0%, transparent 70%);
  pointer-events: none;
}

/* ── GLOWING CIRCLE ── */
.glow-circle {
  width: 56px; height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  margin: 0 auto .5rem;
}

/* ── MEAL CARD ── */
.meal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: .5rem;
}
.meal-title {
  font-family: 'Orbitron', monospace;
  font-size: .72rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: .05em;
}

/* ── EXERCISE CARD ── */
.ex-idx {
  font-family: 'Orbitron', monospace;
  font-size: .55rem;
  color: var(--cyan);
  min-width: 24px;
  font-weight: 700;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--surface2); border-radius: 999px; }

/* ── MOBILE ── */
@media (max-width: 520px) {
  .hero-title { font-size: 2.4rem; }
  .big { font-size: 2.6rem; }
  .block-container { padding: 0 .8rem 6rem !important; }
  .mgrid { gap: .5rem; }
}

/* Dropdown list background */
[data-baseweb="popover"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
}
[data-baseweb="menu"] {
  background: var(--surface2) !important;
}
li[role="option"] {
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}
li[role="option"]:hover {
  background: var(--surface) !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════════
DATA_FILE  = "fitai_data.json"
USERS_FILE = "fitai_users.json"

FOOD_ICONS = {
    "Pollo":"🍗","pavo":"🦃","Atun":"🐟","Salmon":"🐠","Merluza":"🐟",
    "Ternera":"🥩","Cerdo":"🥩","Huevo":"🥚","Claras":"🥚",
    "Queso":"🧀","Yogur":"🥛","Leche":"🥛","Whey":"💪","Caseina":"💪",
    "Avena":"🌾","Arroz":"🍚","Pasta":"🍝","Pan":"🍞",
    "Boniato":"🍠","Patata":"🥔","Quinoa":"🌿","Lentejas":"🫘",
    "Garbanzos":"🫘","Alubias":"🫘","Aguacate":"🥑","Aceite":"🫒",
    "Almendras":"🌰","Nueces":"🌰","Platano":"🍌","Manzana":"🍎",
    "Naranja":"🍊","Fresas":"🍓","Arandanos":"🫐",
    "Brocoli":"🥦","Espinacas":"🥬","Tomate":"🍅","Pepino":"🥒",
    "Lechuga":"🥬","Zanahoria":"🥕","Pimiento":"🫑","Calabacin":"🥒",
    "Tofu":"🧆","Tempeh":"🧆","Aceitunas":"🫒","Hummus":"🫘",
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
        "objetivo":"Ganar masa muscular con minima acumulacion de grasa",
        "macros":{"prot":175,"carb":350,"grasa":75},
        "comidas":[
            {"nombre":"Desayuno","alimentos":"Avena 80g + Whey 30g + Platano + Leche 200ml","cal":580,"prot":42,"carb":82,"grasa":10},
            {"nombre":"Media manana","alimentos":"Yogur griego 200g + Almendras 30g + Manzana","cal":330,"prot":22,"carb":30,"grasa":16},
            {"nombre":"Almuerzo","alimentos":"Arroz integral 150g + Pollo 200g + Brocoli + AOVE 10ml","cal":720,"prot":72,"carb":85,"grasa":14},
            {"nombre":"Merienda","alimentos":"Pan integral 70g + Atun 100g + Tomate","cal":290,"prot":36,"carb":28,"grasa":3},
            {"nombre":"Cena","alimentos":"Salmon 200g + Boniato 200g + Espinacas salteadas","cal":580,"prot":45,"carb":48,"grasa":28},
            {"nombre":"Antes de dormir","alimentos":"Claras 200g + Queso fresco 0% 150g","cal":220,"prot":34,"carb":7,"grasa":3},
        ],
    },
    "Definicion (1900 kcal)": {
        "objetivo":"Reducir grasa corporal conservando la masa muscular",
        "macros":{"prot":180,"carb":160,"grasa":60},
        "comidas":[
            {"nombre":"Desayuno","alimentos":"Claras 4 uds + 1 huevo + Avena 50g","cal":380,"prot":38,"carb":35,"grasa":9},
            {"nombre":"Media manana","alimentos":"Yogur griego 0% 200g + Caseina 30g","cal":250,"prot":35,"carb":10,"grasa":3},
            {"nombre":"Almuerzo","alimentos":"Pechuga pavo 200g + Patata 150g + Verduras","cal":430,"prot":62,"carb":35,"grasa":5},
            {"nombre":"Merienda","alimentos":"Atun 100g + Pan integral 35g + Pepino","cal":230,"prot":30,"carb":18,"grasa":2},
            {"nombre":"Cena","alimentos":"Merluza 200g + Brocoli + Espinacas + AOVE 5ml","cal":380,"prot":48,"carb":12,"grasa":14},
            {"nombre":"Antes de dormir","alimentos":"Queso fresco 0% 150g","cal":93,"prot":17,"carb":5,"grasa":0.6},
        ],
    },
    "Mantenimiento (2300 kcal)": {
        "objetivo":"Mantener composicion corporal y rendimiento",
        "macros":{"prot":155,"carb":260,"grasa":70},
        "comidas":[
            {"nombre":"Desayuno","alimentos":"Avena 60g + Leche 200ml + 2 Huevos + Fruta","cal":490,"prot":28,"carb":62,"grasa":14},
            {"nombre":"Media manana","alimentos":"Fruta + Almendras 25g + Queso fresco","cal":270,"prot":14,"carb":25,"grasa":13},
            {"nombre":"Almuerzo","alimentos":"Arroz 120g + Ternera magra 150g + Ensalada + AOVE","cal":600,"prot":45,"carb":60,"grasa":18},
            {"nombre":"Merienda","alimentos":"Platano + Pan integral + Pavo 80g","cal":310,"prot":26,"carb":42,"grasa":4},
            {"nombre":"Cena","alimentos":"Salmon 150g + Garbanzos 100g + Verduras a la plancha","cal":540,"prot":40,"carb":42,"grasa":21},
        ],
    },
    "Vegana alta proteina (2200 kcal)": {
        "objetivo":"Dieta plant-based con aporte proteico suficiente",
        "macros":{"prot":140,"carb":280,"grasa":65},
        "comidas":[
            {"nombre":"Desayuno","alimentos":"Avena 80g + Proteina vegana 30g + Platano","cal":520,"prot":35,"carb":80,"grasa":10},
            {"nombre":"Media manana","alimentos":"Hummus 100g + Pan integral + Tomate","cal":290,"prot":12,"carb":35,"grasa":10},
            {"nombre":"Almuerzo","alimentos":"Lentejas 200g + Arroz 100g + Verduras + AOVE","cal":590,"prot":28,"carb":95,"grasa":12},
            {"nombre":"Merienda","alimentos":"Aguacate + Pan integral + Batido espinacas","cal":350,"prot":10,"carb":30,"grasa":22},
            {"nombre":"Cena","alimentos":"Tofu 200g + Garbanzos 100g + Brocoli + AOVE","cal":470,"prot":38,"carb":35,"grasa":20},
        ],
    },
    "Recomposicion (2100 kcal)": {
        "objetivo":"Ganar musculo y perder grasa al mismo tiempo",
        "macros":{"prot":200,"carb":200,"grasa":65},
        "comidas":[
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
    "Pecho":[
        {"nombre":"Press banca plano","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-12","descanso":"90s","notas":"Escapulas retraidas, toque suave al pecho"},
        {"nombre":"Press banca inclinado","tipo":"Hipertrofia","equipo":"Barra o Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Angulo 30-45 grados"},
        {"nombre":"Aperturas con mancuernas","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados"},
        {"nombre":"Fondos en paralelas","tipo":"Peso corporal","equipo":"Paralelas","series_rec":"3-4","reps_rec":"Max","descanso":"90s","notas":"Torso inclinado hacia adelante"},
        {"nombre":"Crossover en polea","tipo":"Aislamiento","equipo":"Poleas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Estiramiento completo arriba"},
    ],
    "Espalda":[
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3 min","notas":"Espalda neutra, barra pegada al cuerpo"},
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra fija","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo, sin balanceo"},
        {"nombre":"Jalon al pecho","tipo":"Hipertrofia","equipo":"Polea alta","series_rec":"4","reps_rec":"10-15","descanso":"75s","notas":"Codos hacia abajo y atras"},
        {"nombre":"Remo con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Torso a 45 grados"},
        {"nombre":"Face pulls","tipo":"Prevencion","equipo":"Polea alta","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Esencial para el manguito rotador"},
    ],
    "Pierna":[
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3 min","notas":"Rodillas en la direccion de los pies"},
        {"nombre":"Prensa de piernas","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos isquios, pies bajos cuadriceps"},
        {"nombre":"Femoral tumbado","tipo":"Aislamiento","equipo":"Maquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Aisla isquiotibiales"},
        {"nombre":"Hip Thrust","tipo":"Gluteos","equipo":"Barra o Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Contraccion maxima arriba"},
        {"nombre":"Peso muerto rumano","tipo":"Hipertrofia","equipo":"Barra","series_rec":"3-4","reps_rec":"10-12","descanso":"90s","notas":"Bisagra de cadera perfecta"},
        {"nombre":"Elevacion de gemelos","tipo":"Aislamiento","equipo":"Maquina","series_rec":"4","reps_rec":"15-25","descanso":"45s","notas":"Rango completo"},
    ],
    "Hombros":[
        {"nombre":"Press militar con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2 min","notas":"Core activado"},
        {"nombre":"Elevaciones laterales","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Hasta la horizontal"},
        {"nombre":"Press Arnold","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Rotacion completa"},
        {"nombre":"Pajaro posterior","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Torso a 90 grados"},
    ],
    "Biceps":[
        {"nombre":"Curl con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"75s","notas":"Codos fijos a los costados"},
        {"nombre":"Curl con mancuernas alterno","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-14/brazo","descanso":"60s","notas":"Supinacion al subir"},
        {"nombre":"Curl martillo","tipo":"Braquial","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Agarre neutro"},
        {"nombre":"Curl predicador","tipo":"Aislamiento","equipo":"Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"No extender completamente"},
    ],
    "Triceps":[
        {"nombre":"Press banca agarre cerrado","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Codos pegados al tronco"},
        {"nombre":"Pushdown en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"3-4","reps_rec":"15-20","descanso":"45s","notas":"Extension completa abajo"},
        {"nombre":"Extension sobre la cabeza","tipo":"Hipertrofia","equipo":"Mancuerna","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Estiramiento maximo abajo"},
        {"nombre":"Press frances","tipo":"Hipertrofia","equipo":"Barra EZ","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Baja a la frente controlado"},
    ],
    "Core":[
        {"nombre":"Plancha frontal","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3-4","reps_rec":"45-90s","descanso":"45s","notas":"Cuerpo completamente recto"},
        {"nombre":"Rueda abdominal","tipo":"Fuerza","equipo":"Rueda ab","series_rec":"3","reps_rec":"8-15","descanso":"60s","notas":"Empezar de rodillas"},
        {"nombre":"Crunch en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Flexion de columna, no de caderas"},
        {"nombre":"Elevacion de piernas colgado","tipo":"Fuerza","equipo":"Barra fija","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Retroversion pelvica al subir"},
        {"nombre":"Dead bug","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"8-12/lado","descanso":"45s","notas":"Espalda baja pegada al suelo"},
    ],
    "Cardio":[
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint / 30s caminar","descanso":"—","notas":"FC al 85-90% del maximo"},
        {"nombre":"Tabata en bicicleta","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s / 10s pausa","descanso":"—","notas":"4 minutos totales por ronda"},
        {"nombre":"Zona 2 en eliptica","tipo":"Cardio","equipo":"Eliptica","series_rec":"1","reps_rec":"30-45 min","descanso":"—","notas":"FC 120-140 ppm"},
        {"nombre":"Remo en ergometro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500 m","descanso":"2 min","notas":"Combo cardio + espalda + piernas"},
    ],
    "Calistenia":[
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Progresion: australianas, negativas, completas"},
        {"nombre":"Fondos en paralelas","tipo":"Fuerza","equipo":"Paralelas","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo"},
        {"nombre":"Flexiones","tipo":"Peso corporal","equipo":"Suelo","series_rec":"4","reps_rec":"Max","descanso":"60s","notas":"Variantes: inclinadas, diamante, arqueras"},
        {"nombre":"Pistol squat","tipo":"Fuerza","equipo":"Peso corporal","series_rec":"3","reps_rec":"5-10/pierna","descanso":"90s","notas":"Gran activacion unilateral"},
    ],
}

RUTINAS_DEFAULT = {
    "PPL — Empuje":{"desc":"Pecho, hombros y triceps","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Press Arnold","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Extension sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
    ]},
    "PPL — Tiron":{"desc":"Espalda y biceps","ejercicios":[
        {"ejercicio":"Dominadas","series":4,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
    ]},
    "PPL — Piernas":{"desc":"Cuadriceps, isquios, gluteos y gemelos","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-8","peso":"","descanso":"2-3 min","notas":""},
        {"ejercicio":"Prensa de piernas","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Peso muerto rumano","series":3,"reps":"10-12","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Hip Thrust","series":4,"reps":"12-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Elevacion de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
    ]},
    "Full Body — Principiantes":{"desc":"3 dias por semana","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca plano","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Peso muerto convencional","series":3,"reps":"6-8","peso":"","descanso":"2 min","notas":""},
        {"ejercicio":"Press militar","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Dominadas","series":3,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"45s","notas":""},
    ]},
    "Upper — Tren superior":{"desc":"Pecho, espalda, hombros y brazos","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"60s","notas":""},
    ]},
    "HIIT + Core":{"desc":"Alta intensidad + trabajo abdominal, aprox 35 min","ejercicios":[
        {"ejercicio":"Burpees","series":5,"reps":"30s / 15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Mountain climbers","series":5,"reps":"30s / 15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""},
    ]},
}

TIPO_COLOR = {
    "Fuerza":        ({"color":"#00e676","bg":"rgba(0,230,118,.12)","border":"rgba(0,230,118,.3)"}),
    "Hipertrofia":   ({"color":"#00e5ff","bg":"rgba(0,229,255,.1)","border":"rgba(0,229,255,.25)"}),
    "Aislamiento":   ({"color":"#b39ddb","bg":"rgba(124,77,255,.12)","border":"rgba(124,77,255,.25)"}),
    "Peso corporal": ({"color":"#00e676","bg":"rgba(0,230,118,.12)","border":"rgba(0,230,118,.3)"}),
    "Cardio":        ({"color":"#ffab40","bg":"rgba(255,171,64,.1)","border":"rgba(255,171,64,.25)"}),
    "Estabilidad":   ({"color":"#80cbc4","bg":"rgba(128,203,196,.1)","border":"rgba(128,203,196,.25)"}),
    "Gluteos":       ({"color":"#ff4081","bg":"rgba(255,64,129,.1)","border":"rgba(255,64,129,.25)"}),
    "Prevencion":    ({"color":"#80cbc4","bg":"rgba(128,203,196,.1)","border":"rgba(128,203,196,.25)"}),
    "Braquial":      ({"color":"#b39ddb","bg":"rgba(124,77,255,.12)","border":"rgba(124,77,255,.25)"}),
}

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH & PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}

def save_users(users):
    try:
        with open(USERS_FILE,"w",encoding="utf-8") as f: json.dump(users,f,ensure_ascii=False,indent=2)
    except Exception as e: st.warning(f"Error guardando usuarios: {e}")

def get_user_file(uid): return f"fitai_user_{uid[:8]}.json"

EMPTY_DATA = lambda: {
    "historial_calorias":{},"historial_macros":{},
    "diario_comidas":{},"rutinas_custom":{},
    "dietas_custom":{},"perfil":{},"registro_entreno":{},
    "api_keys":{},
}

@st.cache_resource(show_spinner=False)
def get_supabase_client():
    if not SUPABASE_AVAILABLE: return None
    try:
        url = st.secrets.get("SUPABASE_URL","")
        key = st.secrets.get("SUPABASE_KEY","")
        if url and key: return create_client(url, key)
    except: pass
    return None

def get_supabase(): return get_supabase_client()
def supabase_ok(): return get_supabase() is not None

def sb_register(email, pw):
    sb = get_supabase()
    if sb:
        try:
            r = sb.auth.sign_up({"email": email, "password": pw})
            if r.user: return True, r.user.id
            return False, "Error al registrar."
        except Exception as e:
            err = str(e)
            if "already" in err.lower() or "registered" in err.lower():
                return False, "Este correo ya esta registrado."
            return False, err
    users = load_users()
    if email in users: return False, "El correo ya esta registrado."
    uid = str(uuid.uuid4())
    users[email] = {"uid": uid, "pw_hash": hash_pw(pw), "created": str(datetime.now())}
    save_users(users)
    return True, uid

def sb_login(email, pw):
    sb = get_supabase()
    if sb:
        try:
            r = sb.auth.sign_in_with_password({"email": email, "password": pw})
            if r.user: return True, r.user.id, ""
            return False, "", "Credenciales incorrectas."
        except Exception as e:
            err = str(e)
            if "invalid" in err.lower() or "credentials" in err.lower():
                return False, "", "Correo o contrasena incorrectos."
            return False, "", err
    users = load_users()
    if email not in users: return False, "", "Correo no registrado."
    if users[email]["pw_hash"] != hash_pw(pw): return False, "", "Contrasena incorrecta."
    return True, users[email]["uid"], ""

def load_user_data(uid):
    sb = get_supabase()
    if sb:
        try:
            r = sb.table("user_data").select("*").eq("user_id", uid).execute()
            if r.data:
                row = r.data[0]
                return {
                    "historial_calorias": row.get("historial_calorias") or {},
                    "historial_macros":   row.get("historial_macros")   or {},
                    "diario_comidas":     row.get("diario_comidas")     or {},
                    "rutinas_custom":     row.get("rutinas_custom")     or {},
                    "dietas_custom":      row.get("dietas_custom")      or {},
                    "perfil":             row.get("perfil")             or {},
                    "registro_entreno":   row.get("registro_entreno")   or {},
                    "api_keys":           row.get("api_keys")           or {},
                }
        except: pass
    path = get_user_file(uid)
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8") as f:
                d = json.load(f)
                d.setdefault("api_keys", {})
                return d
        except: pass
    return EMPTY_DATA()

def save_user_data(uid, data):
    sb = get_supabase()
    if sb:
        try:
            payload = {
                "user_id":            uid,
                "historial_calorias": data.get("historial_calorias", {}),
                "historial_macros":   data.get("historial_macros",   {}),
                "diario_comidas":     data.get("diario_comidas",     {}),
                "rutinas_custom":     data.get("rutinas_custom",     {}),
                "dietas_custom":      data.get("dietas_custom",      {}),
                "perfil":             data.get("perfil",             {}),
                "registro_entreno":   data.get("registro_entreno",   {}),
                "api_keys":           data.get("api_keys",           {}),
            }
            sb.table("user_data").upsert(payload, on_conflict="user_id").execute()
            return
        except: pass
    try:
        with open(get_user_file(uid),"w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Error al guardar: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def _ss(k, v):
    if k not in st.session_state: st.session_state[k] = v

_ss("logged_in", False); _ss("user_id", ""); _ss("user_email", "")
_ss("datos", {}); _ss("gemini_key", ""); _ss("groq_key", "")
_ss("proveedor_ia", "Groq (recomendado)"); _ss("scan_res", None)
_ss("ia_dieta_res", None); _ss("ej_temp", []); _ss("sets_temp", [])
_ss("comidas_dc_temp", []); _ss("auth_mode", "login")

if not st.session_state.gemini_key:
    try: st.session_state.gemini_key = st.secrets.get("GEMINI_KEY","")
    except: pass
if not st.session_state.groq_key:
    try: st.session_state.groq_key = st.secrets.get("GROQ_KEY","")
    except: pass

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def hoy(): return str(date.today())
def get_perfil(): return st.session_state.datos.get("perfil",{})
def get_obj_cal(): return int(get_perfil().get("objetivo_cal",2000))
def cal_hoy(): return st.session_state.datos.get("historial_calorias",{}).get(hoy(),0)
def macros_hoy(): return st.session_state.datos.get("historial_macros",{}).get(hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0})

def save_datos(): save_user_data(st.session_state.user_id, st.session_state.datos)

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
    return (f'<div class="pb"><div class="pb-f" style="width:{pct}%;'
            f'background:linear-gradient(90deg,{color}88,{color})"></div></div>')

def ring_svg(pct, color, label, value, unit=""):
    r=42; circ=2*3.14159*r; dash=circ*(min(pct,100)/100); gap=circ-dash
    return (
        f'<div class="ring-wrap">'
        f'<div class="ring">'
        f'<svg width="100" height="100" viewBox="0 0 100 100">'
        f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>'
        f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="8"'
        f' stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"'
        f' style="filter:drop-shadow(0 0 6px {color})"/>'
        f'</svg>'
        f'<div class="ring-val"><div class="ring-num">{value}</div>'
        f'<div class="ring-pct">{unit}</div></div>'
        f'</div>'
        f'<div style="font-family:Orbitron,monospace;font-size:.5rem;color:var(--text3);'
        f'text-transform:uppercase;letter-spacing:.1em">{label}</div>'
        f'</div>'
    )

def ia_call(prompt, img_bytes=None):
    prov = st.session_state.proveedor_ia
    if "Groq" in prov:
        key = st.session_state.groq_key.strip()
        if not key: return "ERROR_NO_KEY"
        try:
            import requests
            headers = {"Authorization":f"Bearer {key}","Content-Type":"application/json"}
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode()
                try: ext = Image.open(io.BytesIO(img_bytes)).format.lower().replace("jpg","jpeg")
                except: ext = "jpeg"
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
        except Exception as e: return f"Error de conexion: {str(e)[:150]}"
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
    except: pass
    return 0

def sdiv(label):
    st.markdown(
        f'<div class="sep"><div class="sep-l"></div>'
        f'<span class="sep-t">⚡ {label}</span>'
        f'<div class="sep-l r"></div></div>',
        unsafe_allow_html=True)

def card(content, variant=""):
    cls = f"card {variant}" if variant else "card"
    return f'<div class="{cls}">{content}</div>'

def food_icon(name):
    for k,v in FOOD_ICONS.items():
        if k.lower() in name.lower(): return v
    return "🥗"

# ═══════════════════════════════════════════════════════════════════════════════
# ── LOGIN / REGISTER ────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-hero">
      <div style="font-family:Orbitron,monospace;font-size:.55rem;color:var(--cyan);
                  letter-spacing:.22em;text-transform:uppercase;margin-bottom:.9rem">
        ⚡ Tu asistente fitness con IA
      </div>
      <div style="font-family:Orbitron,monospace;font-size:3.8rem;font-weight:900;
                  line-height:.88;color:#fff;letter-spacing:-.02em;margin-bottom:.8rem">
        FIT<span style="color:var(--cyan);text-shadow:0 0 20px rgba(0,229,255,.6)">AI</span><br>
        <span style="font-size:1.8rem;color:var(--text3)">PRO</span>
      </div>
      <div style="font-size:.75rem;color:var(--text3);display:flex;align-items:center;
                  justify-content:center;gap:.6rem;flex-wrap:wrap">
        <span>Nutricion</span><span style="color:var(--border2)">·</span>
        <span>Dietas IA</span><span style="color:var(--border2)">·</span>
        <span>Gimnasio</span><span style="color:var(--border2)">·</span>
        <span>Historial</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1,2.2,1])
    with col_c:
        mode = st.session_state.auth_mode
        st.markdown(
            f'<div style="text-align:center;margin-bottom:1.2rem">'
            f'<span style="font-family:Orbitron,monospace;font-size:.6rem;'
            f'color:var(--text3);letter-spacing:.15em;text-transform:uppercase">'
            f'{"Iniciar sesion" if mode=="login" else "Crear cuenta"}</span></div>',
            unsafe_allow_html=True)

        auth_email = st.text_input("Correo electronico", placeholder="hola@ejemplo.com", key="auth_email")
        auth_pw    = st.text_input("Contrasena", type="password", placeholder="Minimo 6 caracteres", key="auth_pw")

        if mode == "register":
            auth_nombre = st.text_input("Tu nombre (opcional)", placeholder="Alex", key="auth_nombre")

        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

        if mode == "login":
            if st.button("⚡ ENTRAR", key="btn_login"):
                if not auth_email or not auth_pw:
                    st.warning("Rellena correo y contrasena.")
                else:
                    ok, uid, err = sb_login(auth_email.strip().lower(), auth_pw)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = uid
                        st.session_state.user_email = auth_email.strip().lower()
                        st.session_state.datos      = load_user_data(uid)
                        # Restaurar API keys guardadas en la cuenta
                        ak = st.session_state.datos.get("api_keys", {})
                        pf = st.session_state.datos.get("perfil", {})
                        if not st.session_state.groq_key:
                            st.session_state.groq_key = (ak.get("groq_key") or pf.get("groq_key") or "")
                        if not st.session_state.gemini_key:
                            st.session_state.gemini_key = (ak.get("gemini_key") or pf.get("gemini_key") or "")
                        if ak.get("proveedor_ia"):
                            st.session_state.proveedor_ia = ak["proveedor_ia"]
                        st.rerun()
                    else:
                        st.error(err)
            st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
            if st.button("Crear cuenta nueva →", key="btn_go_reg"):
                st.session_state.auth_mode = "register"
                st.rerun()
        else:
            if st.button("⚡ REGISTRARME", key="btn_register"):
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
                        st.session_state.datos = EMPTY_DATA()
                        st.session_state.datos["perfil"] = {
                            "nombre": nombre_r, "objetivo_cal": 2000,
                            "obj_prot": 150, "obj_carb": 220, "obj_grasa": 60,
                        }
                        save_datos()
                        st.success("Cuenta creada. Bienvenido/a!")
                        st.rerun()
                    else:
                        st.error(uid_or_err)
            st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
            if st.button("← Ya tengo cuenta", key="btn_go_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# ── MAIN APP ────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════
nombre_u = get_perfil().get("nombre","") or st.session_state.user_email.split("@")[0]

st.markdown(
    f'<div class="hero">'
    f'<div class="hero-tag"><div class="hero-dot"></div>Hola, {nombre_u}</div>'
    f'<div class="hero-title">FIT<span class="accent">AI</span><br>'
    f'<span style="font-size:.42em;color:var(--text3);letter-spacing:.08em">PRO</span></div>'
    f'<div class="hero-sub">'
    f'<span>Nutricion</span><span class="hero-sep">·</span>'
    f'<span>Dietas</span><span class="hero-sep">·</span>'
    f'<span>Gimnasio</span><span class="hero-sep">·</span>'
    f'<span>IA</span></div></div>',
    unsafe_allow_html=True,
)

t_nut, t_diet, t_gym, t_hist, t_cfg = st.tabs([
    "⚡ Kcal", "🥗 Dietas", "💪 Gym", "📊 Stats", "⚙ Config"
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
    pct_cal  = int(min(c_hoy_v/obj_c*100,100)) if obj_c else 0

    # Fila principal: ring grande + stats
    c1,c2 = st.columns([1,2])
    with c1:
        color_ring = "#00e5ff" if ok else "#ff4081"
        st.markdown(card(ring_svg(pct_cal, color_ring, "Kcal hoy", c_hoy_v, "kcal")), unsafe_allow_html=True)
    with c2:
        nc = "var(--cyan)" if ok else "var(--pink)"
        sv_val = f'<span style="color:{nc};font-family:Orbitron,monospace;font-size:2rem;font-weight:700">{restante if ok else exceso}</span>'
        sl = "disponibles" if ok else "excedido"
        st.markdown(card(
            f'<div class="lbl g">Objetivo diario</div>'
            f'<div style="font-family:Orbitron,monospace;font-size:2.5rem;font-weight:700;color:#fff;line-height:1">{obj_c}</div>'
            f'<div class="big-sub">kcal / dia</div>'
            f'{pb(c_hoy_v,obj_c,color_ring)}'
            f'<div style="margin-top:.8rem">{sv_val} <span style="font-family:Orbitron,monospace;font-size:.55rem;color:var(--text3);letter-spacing:.08em;text-transform:uppercase">{sl}</span></div>'
        ), unsafe_allow_html=True)

    # Macros como anillos
    pct_p  = int(min(m_hoy["prot"] /obj_p *100,100)) if obj_p  else 0
    pct_cb = int(min(m_hoy["carb"] /obj_cb*100,100)) if obj_cb else 0
    pct_g  = int(min(m_hoy["grasa"]/obj_g *100,100)) if obj_g  else 0
    st.markdown(card(
        f'<div class="lbl c">Macronutrientes</div>'
        f'<div class="mgrid" style="justify-items:center">'
        f'{ring_svg(pct_p,"#00e676","Proteina",f"{m_hoy[chr(39)+chr(112)+chr(114)+chr(111)+chr(116)+chr(39)]:.0f}g",f"/{obj_p}g")}'
        f'{ring_svg(pct_cb,"#7c4dff","Carbos",f"{m_hoy[chr(39)+chr(99)+chr(97)+chr(114)+chr(98)+chr(39)]:.0f}g",f"/{obj_cb}g")}'
        f'{ring_svg(pct_g,"#ffab40","Grasas",f"{m_hoy[chr(39)+chr(103)+chr(114)+chr(97)+chr(115)+chr(97)+chr(39)]:.0f}g",f"/{obj_g}g")}'
        f'</div>'
    ), unsafe_allow_html=True)

    # Scanner IA
    sdiv("Scanner IA — Analizar foto")
    prov = st.session_state.proveedor_ia
    key_act = st.session_state.groq_key if "Groq" in prov else st.session_state.gemini_key
    if not key_act.strip():
        st.markdown(card(
            f'<div style="text-align:center;padding:.5rem">'
            f'<div style="font-size:2rem;margin-bottom:.5rem">🔑</div>'
            f'<div class="lbl c" style="text-align:center">API Key requerida</div>'
            f'<p style="font-size:.78rem;color:var(--text3);margin:0">Configura tu clave en la pestaña Config para activar el scanner IA</p>'
            f'</div>'
        ), unsafe_allow_html=True)
    else:
        img_up = st.file_uploader("📷 Sube una foto del plato", type=["jpg","jpeg","png","webp"], key="up_scan")
        if img_up:
            st.image(img_up, use_container_width=True)
            sc1,sc2 = st.columns(2)
            with sc1: comida_scan = st.selectbox("Tipo de comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="sc_com")
            with sc2:
                if st.button("⚡ ANALIZAR", key="btn_scan"):
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
                        res = ia_call(prompt_s, img_up.read())
                        if res=="ERROR_NO_KEY": st.warning("Configura tu API Key en Config.")
                        else: st.session_state.scan_res = res

    if st.session_state.scan_res:
        st.markdown(card(
            f'<div class="lbl c">Resultado del analisis IA</div>'
            f'<p style="white-space:pre-wrap;color:var(--text2);font-size:.82rem;line-height:1.9">'
            f'{st.session_state.scan_res}</p>',
            "accent-cyan"), unsafe_allow_html=True)
        kd = extraer_kcal(st.session_state.scan_res)
        if kd>0:
            r1,r2 = st.columns(2)
            with r1:
                if st.button(f"✅ Registrar {kd} kcal", key="btn_reg_scan"):
                    registrar_alimento("Foto analizada por IA",kd,0,0,0, st.session_state.get("sc_com","Extra"))
                    st.session_state.scan_res = None
                    st.success("Registrado correctamente.")
                    st.rerun()
            with r2:
                if st.button("✕ Descartar", key="btn_disc"):
                    st.session_state.scan_res = None
                    st.rerun()

    # Registrar alimento de la base de datos
    sdiv("Registrar alimento")
    ra1,ra2 = st.columns([3,1])
    with ra1: alim = st.selectbox("Alimento",list(ALIMENTOS_DB.keys()),key="sel_alim",label_visibility="collapsed")
    with ra2: cant = st.number_input("g",1,2000,100,key="cant",label_visibility="collapsed")
    ad  = ALIMENTOS_DB[alim]; fac = cant/100
    cav = round(ad["cal"]*fac); prv = round(ad["prot"]*fac,1)
    cbv = round(ad["carb"]*fac,1); grv = round(ad["grasa"]*fac,1)
    ico = food_icon(alim)
    st.markdown(card(
        f'<div style="display:flex;align-items:center;gap:.8rem">'
        f'<div style="font-size:2.2rem;line-height:1;filter:drop-shadow(0 0 8px rgba(255,255,255,.2))">{ico}</div>'
        f'<div style="flex:1">'
        f'<div style="font-family:Orbitron,monospace;font-size:.72rem;font-weight:700;color:#fff;margin-bottom:.4rem">'
        f'{alim[:35]} — {cant}g</div>'
        f'<span class="badge bk">⚡ {cav} kcal</span>'
        f'<span class="badge bp">P {prv}g</span>'
        f'<span class="badge bc">C {cbv}g</span>'
        f'<span class="badge bf">G {grv}g</span>'
        f'</div></div>'
    ), unsafe_allow_html=True)
    ra3,ra4 = st.columns([2,1])
    with ra3: com_db = st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="com_db")
    with ra4:
        if st.button("➕ Añadir", key="btn_add_db"):
            registrar_alimento(f"{alim} ({cant}g)",cav,prv,cbv,grv,com_db)
            st.success(f"✅ {cav} kcal registradas")
            st.rerun()

    # Registro manual
    sdiv("Registro manual libre")
    m1,m2,m3,m4 = st.columns([3,1,1,1])
    with m1: nm  = st.text_input("Nombre",placeholder="Plato casero",key="nm",label_visibility="collapsed")
    with m2: km  = st.number_input("kcal",0,5000,0,5,key="km",label_visibility="collapsed")
    with m3: pm  = st.number_input("P(g)",0.0,300.0,0.0,.5,key="pm",label_visibility="collapsed")
    with m4: cbm = st.number_input("C(g)",0.0,500.0,0.0,.5,key="cbm",label_visibility="collapsed")
    m5,m6 = st.columns([2,1])
    with m5: comm = st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="comm")
    with m6:
        if st.button("➕ Añadir", key="btn_man"):
            if km>0:
                registrar_alimento(nm or "Alimento libre",km,pm,cbm,0.0,comm)
                st.success(f"✅ {km} kcal anadidas"); st.rerun()
            else: st.warning("Introduce kcal mayor que 0")

    # Diario del dia
    sdiv("Diario de hoy")
    diario = st.session_state.datos.get("diario_comidas",{}).get(hoy(),[])
    if not diario:
        st.markdown(card(
            f'<div style="text-align:center;padding:1.2rem 0">'
            f'<div style="font-size:2.5rem;margin-bottom:.5rem">🍽️</div>'
            f'<div class="lbl" style="text-align:center">Sin registros todavia</div>'
            f'<p style="color:var(--text3);font-size:.77rem;margin:0">Empieza anadiendo alimentos arriba</p>'
            f'</div>'
        ), unsafe_allow_html=True)
    else:
        grupos = {}
        for item in diario: grupos.setdefault(item["comida"],[]).append(item)
        for nc2,items in grupos.items():
            tc = sum(i["cal"] for i in items)
            filas = "".join(
                f'<div class="row">'
                f'<span class="rl">'
                f'<span style="font-family:Orbitron,monospace;font-size:.52rem;color:var(--cyan)">{i["hora"]}</span>'
                f'&nbsp;&nbsp;{food_icon(i["alimento"])}&nbsp;{i["alimento"]}</span>'
                f'<span class="rr">{i["cal"]} kcal</span></div>'
                for i in items)
            st.markdown(card(
                f'<div class="meal-header">'
                f'<span class="meal-title">{nc2}</span>'
                f'<span class="badge bk">{tc} kcal</span></div>{filas}'
            ), unsafe_allow_html=True)

    if st.button("🗑️ Resetear diario de hoy", key="btn_reset"):
        d = st.session_state.datos
        d.setdefault("historial_calorias",{})[hoy()] = 0
        d.setdefault("historial_macros",{})[hoy()] = {"prot":0.0,"carb":0.0,"grasa":0.0}
        d.setdefault("diario_comidas",{})[hoy()] = []
        save_datos(); st.success("Diario reseteado."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DIETAS
# ══════════════════════════════════════════════════════════════════════════════
with t_diet:
    dt1,dt2,dt3,dt4 = st.tabs(["Planes","Calculadora","IA Dietista","Mis dietas"])

    with dt1:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        plan_k = st.selectbox("Plan nutricional",list(DIETAS_TEMPLATE.keys()),key="plan_k")
        plan   = DIETAS_TEMPLATE[plan_k]
        tc_p   = sum(c["cal"]   for c in plan["comidas"])
        tp_p   = sum(c["prot"]  for c in plan["comidas"])
        tcb_p  = sum(c["carb"]  for c in plan["comidas"])
        tg_p   = sum(c["grasa"] for c in plan["comidas"])
        st.markdown(card(
            f'<div class="lbl g">Objetivo del plan</div>'
            f'<div style="font-family:Orbitron,monospace;font-size:.8rem;font-weight:700;color:#fff;margin-bottom:.7rem">{plan["objetivo"]}</div>'
            f'<span class="badge bk">⚡ {tc_p} kcal</span>'
            f'<span class="badge bp">P {tp_p}g</span>'
            f'<span class="badge bc">C {tcb_p}g</span>'
            f'<span class="badge bf">G {tg_p}g</span>',
            "accent"), unsafe_allow_html=True)
        for c in plan["comidas"]:
            ico_c = food_icon(c["alimentos"])
            st.markdown(card(
                f'<div class="meal-header">'
                f'<div style="display:flex;align-items:center;gap:.5rem">'
                f'<span style="font-size:1.5rem;filter:drop-shadow(0 0 6px rgba(255,255,255,.15))">{ico_c}</span>'
                f'<span class="meal-title">{c["nombre"]}</span></div>'
                f'<span class="badge bk">{c["cal"]} kcal</span></div>'
                f'<p style="margin:0 0 .5rem;font-size:.78rem;color:var(--text2)">{c["alimentos"]}</p>'
                f'<span class="badge bp">P {c["prot"]}g</span>'
                f'<span class="badge bc">C {c["carb"]}g</span>'
                f'<span class="badge bf">G {c["grasa"]}g</span>'
            ), unsafe_allow_html=True)
        if st.button("⚡ Usar como objetivo diario",key="btn_usar"):
            st.session_state.datos.setdefault("perfil",{}).update({
                "objetivo_cal":tc_p,"obj_prot":tp_p,"obj_carb":tcb_p,"obj_grasa":tg_p})
            save_datos(); st.success(f"✅ Objetivo actualizado: {tc_p} kcal/dia"); st.rerun()

    with dt2:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        pf2 = get_perfil()
        d1,d2 = st.columns(2)
        with d1:
            dp  = st.number_input("Peso (kg)",  30.0,250.0,float(pf2.get("peso",75)),.5,key="dp")
            da  = st.number_input("Altura (cm)",100,250,int(pf2.get("altura",175)),key="da")
        with d2:
            de  = st.number_input("Edad",10,100,int(pf2.get("edad",25)),key="de")
            dsx = st.selectbox("Sexo biologico",["Hombre","Mujer"],key="dsx")
        dact = st.selectbox("Nivel de actividad",[
            "Sedentario (sin ejercicio)","Ligero (1-2 dias/semana)",
            "Moderado (3-4 dias/semana)","Activo (5-6 dias/semana)","Muy activo (2 veces/dia)"],
            index=2,key="dact")
        dobj = st.selectbox("Objetivo",[
            "Perdida de grasa (-300 kcal)","Perdida agresiva (-500 kcal)",
            "Mantenimiento","Volumen limpio (+200 kcal)","Volumen (+400 kcal)"],key="dobj")
        if st.button("⚡ CALCULAR MI TDEE Y MACROS",key="btn_calc"):
            tdee  = calcular_tdee(dp,da,de,dsx,dact)
            delta = {"Perdida de grasa (-300 kcal)":-300,"Perdida agresiva (-500 kcal)":-500,
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
                f'<div class="lbl c">Resultado del calculo</div>'
                f'<div class="sgrid" style="margin-bottom:.8rem">'
                f'<div><div class="lbl">Mantenimiento</div>'
                f'<div class="sv">{tdee}</div><div class="ms">kcal/dia</div></div>'
                f'<div><div class="lbl">Tu objetivo</div>'
                f'<div class="sv" style="color:var(--cyan);text-shadow:var(--glow-c)">{cobj_k}</div>'
                f'<div class="ms">kcal/dia</div></div></div>'
                f'<p style="font-family:Orbitron,monospace;font-size:.65rem;margin-bottom:.6rem;color:var(--text2)">IMC: <b style="color:#fff">{imc}</b> — {cat}</p>'
                f'<span class="badge bk">P {prot_g}g</span>'
                f'<span class="badge bc">C {carb_g}g</span>'
                f'<span class="badge bf">G {gras_g}g</span>',
                "accent-cyan"), unsafe_allow_html=True)
            if st.button("✅ Guardar estos objetivos",key="btn_sc"):
                st.session_state.datos.setdefault("perfil",{}).update({
                    "peso":dp,"altura":da,"edad":de,
                    "objetivo_cal":cobj_k,"obj_prot":prot_g,"obj_carb":carb_g,"obj_grasa":gras_g})
                save_datos(); st.success("✅ Objetivos guardados."); st.rerun()

    with dt3:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        key_a = st.session_state.groq_key if "Groq" in st.session_state.proveedor_ia else st.session_state.gemini_key
        if not key_a.strip():
            st.markdown(card(
                f'<div style="text-align:center;padding:.5rem">'
                f'<div style="font-size:2rem;margin-bottom:.5rem">🤖</div>'
                f'<div class="lbl c" style="text-align:center">API Key requerida</div>'
                f'<p style="font-size:.78rem;color:var(--text3);margin:0">Configura tu clave en la pestaña Config</p>'
                f'</div>'
            ), unsafe_allow_html=True)
        else:
            pf3 = get_perfil()
            d1,d2 = st.columns(2)
            with d1:
                iap  = st.number_input("Peso (kg)",30.0,250.0,float(pf3.get("peso",75)),.5,key="iap")
                iaa  = st.number_input("Altura (cm)",100,250,int(pf3.get("altura",175)),key="iaa")
                iae  = st.number_input("Edad",10,100,int(pf3.get("edad",25)),key="iae")
            with d2:
                iasx = st.selectbox("Sexo",["Hombre","Mujer"],key="iasx")
                iaob = st.selectbox("Objetivo",["Perder grasa","Ganar musculo","Mantenimiento","Mejorar rendimiento","Salud general"],key="iaob")
                iaac = st.selectbox("Actividad",["Sedentario","Ligero","Moderado","Activo","Muy activo"],key="iaac")
            iarest = st.multiselect("Restricciones",["Sin gluten","Sin lactosa","Vegetariano","Vegano","Sin cerdo","Sin mariscos","Bajo en sodio","Bajo en azucar"],key="iarest")
            iaext  = st.text_area("Contexto adicional",placeholder="Alergias, horarios, patologias...",height=60,key="iaext")
            if st.button("🤖 GENERAR PLAN CON IA",key="btn_ia"):
                rest_s = ", ".join(iarest) if iarest else "ninguna"
                pr = (f"Eres un dietista-nutricionista experto. Crea un plan completo en espanol para:\n"
                      f"- Perfil: {iasx}, {iae} anios, {iap}kg, {iaa}cm\n"
                      f"- Objetivo: {iaob} | Actividad: {iaac} | Restricciones: {rest_s}\n"
                      f"- Info extra: {iaext or 'ninguna'}\n\n"
                      f"Incluye:\n1. Calorias y macros en gramos\n"
                      f"2. Plan de 5-6 comidas con alimentos concretos y cantidades\n"
                      f"3. Timing nutricional pre/post entreno\n"
                      f"4. Lista de la compra semanal\n5. 3 consejos clave\n\nSe muy especifico.")
                with st.spinner("Generando tu plan personalizado..."):
                    res = ia_call(pr)
                    if res=="ERROR_NO_KEY": st.warning("Configura tu API Key en Config.")
                    else: st.session_state.ia_dieta_res = res
            if st.session_state.ia_dieta_res:
                st.markdown(card(
                    f'<div class="lbl c">Plan generado por IA</div>'
                    f'<p style="white-space:pre-wrap;color:var(--text2);font-size:.8rem;line-height:1.9">'
                    f'{st.session_state.ia_dieta_res}</p>',
                    "accent-cyan"), unsafe_allow_html=True)
                if st.button("🔄 Nuevo plan",key="btn_ia_r"):
                    st.session_state.ia_dieta_res = None; st.rerun()

    with dt4:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        dc_all = st.session_state.datos.get("dietas_custom",{})
        if dc_all:
            dc_sel = st.selectbox("Mis dietas",["— Nueva —"]+list(dc_all.keys()),key="dc_sel")
            if dc_sel!="— Nueva —":
                dc = dc_all[dc_sel]
                if dc.get("notas"):
                    st.markdown(card(f'<p style="font-size:.8rem;color:var(--text2)">{dc["notas"]}</p>'),unsafe_allow_html=True)
                for c in dc.get("comidas",[]):
                    st.markdown(card(
                        f'<div class="meal-header">'
                        f'<span class="meal-title">{food_icon(c.get("alimentos",""))} {c["nombre"]}</span>'
                        f'<span class="badge bk">{c.get("cal",0)} kcal</span></div>'
                        f'<p style="margin:0 0 .4rem;font-size:.78rem;color:var(--text2)">{c.get("alimentos","")}</p>'
                        f'<span class="badge bp">P {c.get("prot",0)}g</span>'
                        f'<span class="badge bc">C {c.get("carb",0)}g</span>'
                        f'<span class="badge bf">G {c.get("grasa",0)}g</span>'
                    ), unsafe_allow_html=True)
                if st.button("🗑️ Eliminar esta dieta",key="btn_del_dc"):
                    del st.session_state.datos["dietas_custom"][dc_sel]
                    save_datos(); st.success("Dieta eliminada."); st.rerun()
        sdiv("Crear nueva dieta")
        nc_nom = st.text_input("Nombre de la dieta",placeholder="Mi dieta de verano",key="nc_nom")
        nc_not = st.text_area("Descripcion y notas",placeholder="Objetivo, duracion...",height=50,key="nc_not")
        sdiv("Añadir comidas")
        dc1,dc2 = st.columns([2,1])
        with dc1:
            nc_cn = st.text_input("Nombre comida",placeholder="Almuerzo",key="nc_cn")
            nc_al = st.text_area("Alimentos",placeholder="Pollo 150g, Arroz 100g",height=45,key="nc_al")
        with dc2:
            nc_cal = st.number_input("kcal",0,3000,0,10,key="nc_cal")
            nc_pr  = st.number_input("P (g)",0.0,200.0,0.0,.5,key="nc_pr")
            nc_cb2 = st.number_input("C (g)",0.0,500.0,0.0,.5,key="nc_cb2")
            nc_gr  = st.number_input("G (g)",0.0,200.0,0.0,.5,key="nc_gr")
        if st.button("➕ Añadir comida",key="btn_add_nc"):
            if nc_cn:
                st.session_state.comidas_dc_temp.append({"nombre":nc_cn,"alimentos":nc_al,"cal":nc_cal,"prot":nc_pr,"carb":nc_cb2,"grasa":nc_gr})
                st.success(f"'{nc_cn}' anadida.")
            else: st.warning("Escribe el nombre de la comida.")
        if st.session_state.comidas_dc_temp:
            tot_dc = sum(c["cal"] for c in st.session_state.comidas_dc_temp)
            filas_dc = "".join(
                f'<div class="row"><span class="rl">{i+1}. {food_icon(c.get("alimentos",""))} {c["nombre"]}</span>'
                f'<span class="rr">{c["cal"]} kcal</span></div>'
                for i,c in enumerate(st.session_state.comidas_dc_temp))
            st.markdown(card(f'{filas_dc}<div style="text-align:right;margin-top:.4rem"><span class="badge bk">Total: {tot_dc} kcal</span></div>'),unsafe_allow_html=True)
        if st.button("💾 Guardar dieta",key="btn_save_dc"):
            if not nc_nom: st.warning("Dale un nombre a la dieta.")
            elif not st.session_state.comidas_dc_temp: st.warning("Anade al menos una comida.")
            else:
                st.session_state.datos.setdefault("dietas_custom",{})[nc_nom] = {"notas":nc_not,"comidas":st.session_state.comidas_dc_temp.copy()}
                save_datos(); st.session_state.comidas_dc_temp = []
                st.success(f"✅ Dieta '{nc_nom}' guardada."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# GIMNASIO
# ══════════════════════════════════════════════════════════════════════════════
with t_gym:
    g1,g2,g3 = st.tabs(["Ejercicios","Rutinas","Registro"])

    with g1:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        grupo = st.selectbox("Grupo muscular",list(EJERCICIOS_GYM.keys()),key="grupo")
        for ej in EJERCICIOS_GYM[grupo]:
            tc = TIPO_COLOR.get(ej["tipo"],{"color":"#00e5ff","bg":"rgba(0,229,255,.1)","border":"rgba(0,229,255,.25)"})
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:.4rem;flex-wrap:wrap;margin-bottom:.4rem">'
                f'<span style="font-family:Orbitron,monospace;font-size:.72rem;font-weight:700;color:#fff">{ej["nombre"]}</span>'
                f'<span class="typebadge" style="color:{tc["color"]};background:{tc["bg"]};border-color:{tc["border"]}">{ej["tipo"]}</span></div>'
                f'<div style="font-family:Orbitron,monospace;font-size:.55rem;color:var(--text3);margin-bottom:.3rem;letter-spacing:.06em">{ej["equipo"]}</div>'
                f'<div style="display:flex;gap:.5rem;flex-wrap:wrap;font-size:.76rem;color:var(--text2);margin-bottom:.3rem">'
                f'<span style="font-family:Orbitron,monospace;font-size:.6rem;color:var(--cyan)">{ej["series_rec"]}x</span>'
                f'<span>{ej["reps_rec"]} reps</span>'
                f'<span style="color:var(--border2)">·</span>'
                f'<span>{ej["descanso"]}</span></div>'
                f'<p style="font-size:.72rem;color:var(--text3);font-style:italic;margin:0">{ej["notas"]}</p>'
            ), unsafe_allow_html=True)

    with g2:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        todas = {**RUTINAS_DEFAULT,**st.session_state.datos.get("rutinas_custom",{})}
        rut_k = st.selectbox("Rutina",list(todas.keys()),key="rut_k")
        rut   = todas[rut_k]
        desc  = rut.get("desc","") if isinstance(rut,dict) else ""
        ejs   = rut.get("ejercicios",rut) if isinstance(rut,dict) else rut
        if desc:
            st.markdown(f'<div style="font-family:Orbitron,monospace;font-size:.58rem;color:var(--text3);margin-bottom:.8rem;letter-spacing:.06em">{desc}</div>',unsafe_allow_html=True)
        for idx,ej in enumerate(ejs):
            p_s = f' · {ej["peso"]}' if ej.get("peso") else ""
            n_s = f'<p style="font-size:.7rem;color:var(--text3);font-style:italic;margin-top:.25rem">{ej["notas"]}</p>' if ej.get("notas") else ""
            st.markdown(card(
                f'<div style="display:flex;align-items:flex-start;gap:.7rem">'
                f'<div class="ex-idx">{idx+1:02d}</div>'
                f'<div style="flex:1">'
                f'<div style="font-family:Orbitron,monospace;font-size:.7rem;font-weight:700;color:#fff;margin-bottom:.3rem">{ej["ejercicio"]}</div>'
                f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;font-size:.75rem;color:var(--text2)">'
                f'<span style="color:var(--cyan);font-family:Orbitron,monospace;font-size:.58rem">{ej["series"]}x</span>'
                f'<span>{ej["reps"]} reps</span>'
                f'<span style="color:var(--border2)">·</span>'
                f'<span>{ej["descanso"]}{p_s}</span></div>{n_s}</div></div>'
            ), unsafe_allow_html=True)

        sdiv("Crear rutina personalizada")
        with st.expander("✚ Nueva rutina"):
            nr_n = st.text_input("Nombre",placeholder="Mi rutina de lunes",key="nr_n")
            nr_d = st.text_input("Descripcion",placeholder="Pecho y triceps",key="nr_d")
            e1,e2,e3 = st.columns([3,1,2])
            with e1: nr_ej=st.text_input("Ejercicio",placeholder="Press banca",key="nr_ej",label_visibility="collapsed")
            with e2: nr_s =st.number_input("Series",1,20,4,key="nr_s",label_visibility="collapsed")
            with e3: nr_r =st.text_input("Reps",placeholder="8-12",key="nr_r",label_visibility="collapsed")
            e4,e5,e6 = st.columns(3)
            with e4: nr_p =st.text_input("Peso",placeholder="60kg",key="nr_p",label_visibility="collapsed")
            with e5: nr_dc=st.text_input("Descanso",placeholder="90s",key="nr_dc",label_visibility="collapsed")
            with e6: nr_nt=st.text_input("Nota",placeholder="Tecnica...",key="nr_nt",label_visibility="collapsed")
            if st.button("➕ Añadir ejercicio",key="btn_add_ej"):
                if nr_ej:
                    st.session_state.ej_temp.append({"ejercicio":nr_ej,"series":nr_s,"reps":nr_r or "8-12","peso":nr_p,"descanso":nr_dc or "60s","notas":nr_nt})
                    st.success(f"'{nr_ej}' anadido.")
                else: st.warning("Escribe el nombre del ejercicio.")
            if st.session_state.ej_temp:
                filas_ej = "".join(
                    f'<div class="row"><span class="rl"><span class="ex-idx">{i+1:02d}</span> {e["ejercicio"]}</span>'
                    f'<span class="rr">{e["series"]}x{e["reps"]}</span></div>'
                    for i,e in enumerate(st.session_state.ej_temp))
                st.markdown(card(filas_ej),unsafe_allow_html=True)
            if st.button("💾 Guardar rutina",key="btn_save_rut"):
                if not nr_n: st.warning("Dale un nombre.")
                elif not st.session_state.ej_temp: st.warning("Anade al menos un ejercicio.")
                else:
                    st.session_state.datos.setdefault("rutinas_custom",{})[nr_n] = {"desc":nr_d,"ejercicios":st.session_state.ej_temp.copy()}
                    save_datos(); st.session_state.ej_temp = []
                    st.success(f"✅ Rutina '{nr_n}' guardada."); st.rerun()

    with g3:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        r1,r2 = st.columns(2)
        with r1: reg_tipo = st.selectbox("Tipo de sesion",["PPL — Empuje","PPL — Tiron","PPL — Piernas","Full Body","Upper","Lower","HIIT","Calistenia","Cardio","Otro"],key="reg_tipo")
        with r2: reg_dur  = st.number_input("Duracion (min)",10,300,60,key="reg_dur")
        reg_notas = st.text_area("Notas del entreno",placeholder="Sensaciones, PRs, observaciones...",height=60,key="reg_notas")
        sdiv("Series realizadas")
        sr1,sr2,sr3,sr4 = st.columns(4)
        with sr1: ej_n =st.text_input("Ejercicio",placeholder="Sentadilla",key="ej_n",label_visibility="collapsed")
        with sr2: set_s=st.number_input("Series",1,20,3,key="set_s",label_visibility="collapsed")
        with sr3: set_r=st.text_input("Reps",placeholder="10",key="set_r",label_visibility="collapsed")
        with sr4: set_p=st.text_input("Peso",placeholder="80kg",key="set_p",label_visibility="collapsed")
        if st.button("➕ Añadir serie",key="btn_add_set"):
            if ej_n:
                st.session_state.sets_temp.append({"ejercicio":ej_n,"series":set_s,"reps":set_r or "—","peso":set_p or "—"})
                st.success(f"'{ej_n}' registrado.")
            else: st.warning("Escribe el nombre del ejercicio.")
        if st.session_state.sets_temp:
            filas_s = "".join(
                f'<div class="row"><span class="rl"><span class="ex-idx">{i+1:02d}</span> {s["ejercicio"]}</span>'
                f'<span class="rr">{s["series"]}x{s["reps"]} · {s["peso"]}</span></div>'
                for i,s in enumerate(st.session_state.sets_temp))
            st.markdown(card(filas_s),unsafe_allow_html=True)
        if st.button("💾 Guardar sesion",key="btn_save_ses"):
            reg = st.session_state.datos.setdefault("registro_entreno",{})
            reg.setdefault(hoy(),[]).append({
                "tipo":reg_tipo,"duracion":reg_dur,"notas":reg_notas,
                "series":st.session_state.sets_temp.copy(),"hora":datetime.now().strftime("%H:%M"),
            })
            save_datos(); st.session_state.sets_temp = []
            st.success("✅ Sesion guardada."); st.rerun()

        sdiv("Ultimas sesiones")
        reg_all = st.session_state.datos.get("registro_entreno",{})
        if not reg_all:
            st.markdown(card('<div style="text-align:center;padding:.85rem"><p style="color:var(--text3);font-size:.77rem;margin:0">Sin sesiones registradas todavia</p></div>'),unsafe_allow_html=True)
        for fk in sorted(reg_all.keys(),reverse=True)[:7]:
            for ses in reg_all[fk]:
                ns = len(ses.get("series",[]))
                st.markdown(card(
                    f'<div class="meal-header">'
                    f'<span class="meal-title">{ses["tipo"]}</span>'
                    f'<span class="badge bn">{fk}</span></div>'
                    f'<div style="display:flex;gap:.5rem;flex-wrap:wrap;font-family:Orbitron,monospace;font-size:.55rem;color:var(--text2)">'
                    f'<span style="color:var(--cyan)">{ses["duracion"]} min</span>'
                    f'<span style="color:var(--border2)">·</span>'
                    f'<span>{ns} ejercicios</span>'
                    f'<span style="color:var(--border2)">·</span>'
                    f'<span>{ses.get("hora","")}</span></div>'
                    f'{"<p style=margin-top:.3rem;font-size:.72rem;color:var(--text3)>" + ses["notas"] + "</p>" if ses.get("notas") else ""}'
                ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HISTORIAL / STATS
# ══════════════════════════════════════════════════════════════════════════════
with t_hist:
    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
    hist_c = st.session_state.datos.get("historial_calorias",{})
    hist_m = st.session_state.datos.get("historial_macros",{})
    reg_e  = st.session_state.datos.get("registro_entreno",{})
    if not hist_c:
        st.markdown(card(
            '<div style="text-align:center;padding:1.5rem 0">'
            '<div style="font-size:3rem;margin-bottom:.5rem">📊</div>'
            '<div class="lbl c" style="text-align:center">Sin historial</div>'
            '<p style="color:var(--text3);font-size:.77rem;margin:0">Empieza a registrar alimentos en Nutricion</p></div>'
        ), unsafe_allow_html=True)
    else:
        fechas = sorted(hist_c.keys())[-14:]
        vals   = [hist_c.get(f,0) for f in fechas]
        etiq   = [f[-5:] for f in fechas]
        obj_h  = get_obj_cal()
        if vals:
            prom    = round(sum(vals)/len(vals))
            maxi    = max(vals)
            dias_ok = sum(1 for v in vals if 0<v<=obj_h)
            total_r = len([v for v in vals if v>0])

            # Stats row
            st.markdown(card(
                f'<div class="lbl c">Resumen · Ultimos 14 dias</div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">'
                f'<div><div class="lbl">Promedio</div>'
                f'<div class="sv" style="color:var(--cyan);text-shadow:var(--glow-c)">{prom}</div>'
                f'<div class="ms">kcal/dia</div></div>'
                f'<div><div class="lbl">Dias en objetivo</div>'
                f'<div class="sv" style="color:var(--green);text-shadow:var(--glow-g)">{dias_ok}</div>'
                f'<div class="ms">de {total_r} registrados</div></div>'
                f'<div><div class="lbl">Maximo</div>'
                f'<div class="sv" style="color:var(--amber)">{maxi}</div>'
                f'<div class="ms">kcal en un dia</div></div>'
                f'</div>',
                "accent-cyan"), unsafe_allow_html=True)

            # Gráfica de barras
            max_v = max(vals+[obj_h,1])
            bars  = '<div style="display:flex;align-items:flex-end;gap:3px;height:100px;margin-top:1rem;padding-bottom:2px">'
            for et,vl in zip(etiq,vals):
                h   = int(vl/max_v*100) if vl>0 else 3
                if vl>obj_h and vl>0:
                    clr = "linear-gradient(180deg,#ff4081,#ff008066)"
                elif vl>0:
                    clr = "linear-gradient(180deg,#00e5ff,#00e5ff44)"
                else:
                    clr = "rgba(255,255,255,.05)"
                bars += (
                    f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px">'
                    f'<div style="flex:1;display:flex;align-items:flex-end;width:100%">'
                    f'<div style="width:100%;height:{h}px;background:{clr};border-radius:4px 4px 0 0;'
                    f'box-shadow:{("0 0 8px rgba(0,229,255,.4)" if vl<=obj_h and vl>0 else "0 0 8px rgba(255,64,129,.4)" if vl>obj_h else "none")}"></div></div>'
                    f'<div style="font-family:Orbitron,monospace;font-size:.38rem;color:var(--text3);white-space:nowrap">{et}</div>'
                    f'</div>')
            bars += '</div>'
            # Línea objetivo
            obj_h_pct = int(obj_h/max_v*100)
            st.markdown(card(
                f'<div class="lbl c">Calorias diarias · 14 dias</div>'
                f'<div style="position:relative">{bars}'
                f'<div style="position:absolute;bottom:{obj_h_pct}%;left:0;right:0;height:1px;'
                f'background:rgba(0,230,118,.4);border-top:1px dashed rgba(0,230,118,.4)"></div></div>'
                f'<div style="display:flex;gap:.5rem;margin-top:.6rem;flex-wrap:wrap">'
                f'<span class="badge bp" style="font-size:.5rem">Azul = dentro del objetivo</span>'
                f'<span class="badge bw" style="font-size:.5rem">Rojo = excedido</span>'
                f'<span class="badge bk" style="font-size:.5rem">-- Objetivo diario</span></div>'
            ), unsafe_allow_html=True)

        # Macros promedio
        dias_m = [d for d in fechas if d in hist_m and any(v>0 for v in hist_m[d].values())]
        if dias_m:
            pm = {"prot":0.0,"carb":0.0,"grasa":0.0}
            for d in dias_m:
                for k in pm: pm[k] += hist_m[d].get(k,0)
            n  = len(dias_m)
            pm = {k:round(v/n,1) for k,v in pm.items()}
            st.markdown(card(
                f'<div class="lbl c">Macros promedio diario</div>'
                f'<div class="mgrid">'
                f'<div><div class="lbl">Proteina</div>'
                f'<div class="mv" style="color:var(--green);text-shadow:var(--glow-g)">{pm["prot"]}g</div></div>'
                f'<div><div class="lbl">Carbohidatos</div>'
                f'<div class="mv" style="color:#b39ddb">{pm["carb"]}g</div></div>'
                f'<div><div class="lbl">Grasas</div>'
                f'<div class="mv" style="color:var(--amber)">{pm["grasa"]}g</div></div>'
                f'</div>'
            ), unsafe_allow_html=True)

        # Estadísticas de entreno
        ses_t = sum(len(v) for v in reg_e.values())
        min_t = sum(s.get("duracion",0) for v in reg_e.values() for s in v)
        if ses_t>0:
            st.markdown(card(
                f'<div class="lbl c">Estadisticas de entreno</div>'
                f'<div class="sgrid">'
                f'<div><div class="lbl">Sesiones totales</div>'
                f'<div class="sv" style="color:var(--cyan);text-shadow:var(--glow-c)">{ses_t}</div></div>'
                f'<div><div class="lbl">Horas totales</div>'
                f'<div class="sv" style="color:var(--green);text-shadow:var(--glow-g)">{round(min_t/60,1)}</div></div>'
                f'</div>'
            ), unsafe_allow_html=True)

        if st.button("🗑️ Borrar historial completo",key="btn_del_hist"):
            d = st.session_state.datos
            d["historial_calorias"] = {}; d["historial_macros"] = {}; d["diario_comidas"] = {}
            save_datos(); st.success("Historial borrado."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
with t_cfg:
    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)

    # Sesion activa
    sdiv("Sesion activa")
    st.markdown(card(
        f'<div class="row"><span class="rl">Usuario</span><span class="rr">{st.session_state.user_email}</span></div>'
        f'<div class="row"><span class="rl">Base de datos</span>'
        f'<span class="rr">{"<span class=badge bp>Supabase conectado</span>" if supabase_ok() else "<span class=badge bn>Local (sin Supabase)</span>"}</span></div>'
        f'<div class="row"><span class="rl">Estado</span>'
        f'<span class="rr"><span class="badge bk">● Activo</span></span></div>'
    ), unsafe_allow_html=True)
    if st.button("🔒 Cerrar sesion",key="btn_logout"):
        for k in ["logged_in","user_id","user_email","datos","scan_res","ia_dieta_res","ej_temp","sets_temp","comidas_dc_temp"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    # Proveedor IA
    sdiv("Proveedor de IA")
    st.markdown(card(
        '<div class="lbl c">Comparativa</div>'
        '<div class="row"><span class="rl">Groq (recomendado)</span>'
        '<span class="rr"><span class="badge bk">1500 req/dia · Gratis</span></span></div>'
        '<div class="row"><span class="rl">Gemini</span>'
        '<span class="rr"><span class="badge bw">~20 req/dia</span></span></div>'
        '<p style="font-size:.73rem;color:var(--text3);margin-top:.5rem;margin-bottom:0">'
        'Groq: mas generosa, mas rapida y completamente gratuita.</p>'
    ), unsafe_allow_html=True)
    prov_sel = st.selectbox("",["Groq (recomendado)","Gemini"],
        index=0 if "Groq" in st.session_state.proveedor_ia else 1,
        key="prov_sel",label_visibility="collapsed")
    if st.button("💾 Cambiar proveedor",key="btn_prov"):
        st.session_state.proveedor_ia = prov_sel
        st.session_state.datos.setdefault("api_keys",{})["proveedor_ia"] = prov_sel
        save_datos(); st.success(f"✅ Proveedor: {prov_sel}"); st.rerun()

    # Groq Key
    sdiv("Groq API Key — console.groq.com/keys")
    st.markdown(card(
        '<div class="row"><span class="rl">1. Cuenta gratuita</span><span class="rr">console.groq.com/keys</span></div>'
        '<div class="row"><span class="rl">2. Pulsa</span><span class="rr">Create API Key</span></div>'
        '<div class="row"><span class="rl">3. Formato</span><span class="rr">gsk_...</span></div>'
        '<div class="row"><span class="rl">4. Se guarda en tu cuenta</span><span class="rr"><span class="badge bk">Sin repetirla</span></span></div>'
    ), unsafe_allow_html=True)
    gi   = st.text_input("Groq Key",value=st.session_state.groq_key,type="password",placeholder="gsk_...",key="gi")
    g1b,g2b = st.columns(2)
    with g1b:
        if st.button("💾 Guardar y vincular",key="btn_groq"):
            st.session_state.groq_key = gi.strip()
            st.session_state.datos.setdefault("api_keys",{})["groq_key"] = gi.strip()
            st.session_state.datos.setdefault("api_keys",{})["proveedor_ia"] = st.session_state.proveedor_ia
            save_datos(); st.success("✅ Guardada y vinculada a tu cuenta.")
    with g2b:
        if st.session_state.groq_key and st.button("⚡ Probar",key="btn_tg"):
            with st.spinner("Probando..."):
                prev = st.session_state.proveedor_ia
                st.session_state.proveedor_ia = "Groq (recomendado)"
                res  = ia_call("Responde solo: OK")
                st.session_state.proveedor_ia = prev
                st.success(f"✅ {res[:60]}") if ("OK" in res or len(res)<80) else st.error(res[:150])

    # Gemini Key
    sdiv("Gemini API Key — aistudio.google.com")
    mi   = st.text_input("Gemini Key",value=st.session_state.gemini_key,type="password",placeholder="AIzaSy...",key="mi")
    mg1,mg2 = st.columns(2)
    with mg1:
        if st.button("💾 Guardar y vincular",key="btn_gem"):
            st.session_state.gemini_key = mi.strip()
            st.session_state.datos.setdefault("api_keys",{})["gemini_key"] = mi.strip()
            save_datos(); st.success("✅ Guardada y vinculada a tu cuenta.")
    with mg2:
        if st.session_state.gemini_key and st.button("⚡ Probar",key="btn_tm"):
            with st.spinner("Probando..."):
                prev = st.session_state.proveedor_ia
                st.session_state.proveedor_ia = "Gemini"
                res  = ia_call("Responde solo: OK")
                st.session_state.proveedor_ia = prev
                st.success(f"✅ {res[:60]}") if ("OK" in res or len(res)<80) else st.error(res[:150])

    # Perfil
    sdiv("Perfil personal")
    pf_c = get_perfil()
    cfg1,cfg2 = st.columns(2)
    with cfg1:
        cn  = st.text_input("Nombre",value=pf_c.get("nombre",""),key="cn")
        cp2 = st.number_input("Peso (kg)",30.0,250.0,float(pf_c.get("peso",75.0)),.5,key="cp2")
        ca3 = st.number_input("Altura (cm)",100,250,int(pf_c.get("altura",175)),key="ca3")
    with cfg2:
        ce  = st.number_input("Edad",10,100,int(pf_c.get("edad",25)),key="ce")
        coc = st.number_input("Objetivo kcal/dia",800,6000,int(pf_c.get("objetivo_cal",2000)),50,key="coc")
        cpr = st.number_input("Obj. proteina (g)",0,400,int(pf_c.get("obj_prot",150)),5,key="cpr")
    cfg3,cfg4 = st.columns(2)
    with cfg3: ccb=st.number_input("Obj. carbos (g)",0,800,int(pf_c.get("obj_carb",220)),5,key="ccb")
    with cfg4: cgr=st.number_input("Obj. grasas (g)",0,300,int(pf_c.get("obj_grasa",60)),5,key="cgr")
    if st.button("💾 Guardar perfil",key="btn_perfil"):
        st.session_state.datos.setdefault("perfil",{}).update({
            "nombre":cn,"peso":cp2,"altura":ca3,"edad":ce,
            "objetivo_cal":coc,"obj_prot":cpr,"obj_carb":ccb,"obj_grasa":cgr,
        })
        save_datos(); st.success("✅ Perfil guardado."); st.rerun()

    # Info
    sdiv("Acerca de FitAI Pro")
    st.markdown(card(
        '<div class="row"><span class="rl">Version</span><span class="rr">FitAI Pro 5.0 Dark</span></div>'
        '<div class="row"><span class="rl">Stack</span><span class="rr">Streamlit · Groq · Gemini · Supabase</span></div>'
        '<div class="row"><span class="rl">Datos</span><span class="rr">Privados por usuario · RLS</span></div>'
        '<div class="row"><span class="rl">Hosting</span><span class="rr">Streamlit Community Cloud</span></div>'
    ), unsafe_allow_html=True)

    # Restaurar API keys al entrar a config
    ak = st.session_state.datos.get("api_keys", {})
    if not st.session_state.groq_key   and ak.get("groq_key"):
        st.session_state.groq_key   = ak["groq_key"]
    if not st.session_state.gemini_key and ak.get("gemini_key"):
        st.session_state.gemini_key = ak["gemini_key"]
