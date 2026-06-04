import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import date, datetime
from PIL import Image
import io
import re

st.set_page_config(
    page_title="FitAI Pro",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Fraunces:ital,wght@0,700;0,900;1,700&display=swap');

:root {
  --bg:        #0c0d10;
  --surface:   #13141a;
  --surface2:  #1a1c24;
  --surface3:  #22253000;
  --border:    rgba(255,255,255,0.06);
  --border2:   rgba(255,255,255,0.10);
  --accent:    #e8ff5a;
  --accent2:   #5affcc;
  --red:       #ff5a5a;
  --blue:      #5a9eff;
  --purple:    #b45aff;
  --text:      #f0f2f7;
  --text2:     #8a8fa8;
  --text3:     #44485a;
  --r:         14px;
  --r-sm:      8px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

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
  max-width: 760px !important;
  padding: 2rem 1.25rem 8rem !important;
  margin: 0 auto !important;
}

/* ─── HERO ─── */
.hero {
  padding: 2rem 0 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.75rem;
}
.hero-eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: .65rem;
  color: var(--text3);
  letter-spacing: .18em;
  text-transform: uppercase;
  margin-bottom: .6rem;
}
.hero-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(2.4rem, 8vw, 4rem);
  font-weight: 900;
  line-height: .95;
  color: var(--text);
  letter-spacing: -.03em;
}
.hero-title em {
  font-style: italic;
  color: var(--accent);
}
.hero-sub {
  margin-top: .75rem;
  font-size: .82rem;
  color: var(--text2);
  letter-spacing: .01em;
}

/* ─── CARDS ─── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.25rem 1.4rem;
  margin-bottom: .9rem;
  position: relative;
  overflow: hidden;
}
.card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,.03) 0%, transparent 60%);
  pointer-events: none;
}
.card-label {
  font-family: 'DM Mono', monospace;
  font-size: .6rem;
  color: var(--text3);
  letter-spacing: .15em;
  text-transform: uppercase;
  margin-bottom: .7rem;
}
.card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: .3rem;
  line-height: 1.3;
}
.card p, .card li {
  font-size: .84rem;
  color: var(--text2);
  line-height: 1.6;
}

/* ─── BIG STAT ─── */
.stat-num {
  font-family: 'Fraunces', serif;
  font-size: 3.2rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -.04em;
}
.stat-unit {
  font-size: .72rem;
  color: var(--text3);
  font-family: 'DM Mono', monospace;
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-top: .3rem;
}

/* ─── PROGRESS ─── */
.pbar { background: var(--surface2); border-radius: 999px; height: 3px; overflow: hidden; margin-top: .5rem; }
.pbar-fill { height: 100%; border-radius: 999px; transition: width .6s cubic-bezier(.4,0,.2,1); }

/* ─── BADGES ─── */
.badge {
  display: inline-flex; align-items: center; gap: .25rem;
  padding: .2rem .55rem;
  border-radius: 6px;
  font-size: .72rem;
  font-weight: 600;
  margin: .15rem .1rem 0 0;
  font-family: 'DM Mono', monospace;
  letter-spacing: .02em;
}
.badge-kcal  { background: rgba(232,255,90,.1);  color: var(--accent); }
.badge-prot  { background: rgba(90,255,204,.1);  color: var(--accent2); }
.badge-carb  { background: rgba(90,158,255,.1);  color: var(--blue); }
.badge-fat   { background: rgba(180,90,255,.1);  color: var(--purple); }
.badge-ok    { background: rgba(90,255,204,.1);  color: var(--accent2); }
.badge-warn  { background: rgba(255,90,90,.1);   color: var(--red); }
.badge-neutral { background: rgba(255,255,255,.06); color: var(--text2); }

/* ─── TYPE BADGES ─── */
.type-badge {
  font-family: 'DM Mono', monospace;
  font-size: .58rem;
  font-weight: 500;
  padding: .18rem .5rem;
  border-radius: 5px;
  letter-spacing: .06em;
  text-transform: uppercase;
}

/* ─── DIVIDER ─── */
.sdiv {
  display: flex; align-items: center; gap: .75rem;
  margin: 1.5rem 0 1rem;
}
.sdiv-line { flex: 1; height: 1px; background: var(--border); }
.sdiv-lbl {
  font-family: 'DM Mono', monospace;
  font-size: .6rem;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .15em;
  white-space: nowrap;
}

/* ─── BUTTONS ─── */
div.stButton > button {
  background: var(--accent) !important;
  color: #0c0d10 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .85rem !important;
  font-weight: 700 !important;
  letter-spacing: .01em !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  padding: .65rem 1.3rem !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: opacity .15s, transform .1s !important;
}
div.stButton > button:hover {
  opacity: .88 !important;
  transform: translateY(-1px) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

/* ─── INPUTS ─── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stNumberInput input {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r-sm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .85rem !important;
  transition: border-color .15s !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
  border-color: var(--accent) !important;
  outline: none !important;
}
div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
}
label, .stSelectbox label, .stNumberInput label, .stTextInput label {
  color: var(--text2) !important;
  font-size: .78rem !important;
  font-weight: 500 !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ─── TABS ─── */
[data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  padding: 4px !important;
  gap: 2px !important;
}
[data-baseweb="tab"] {
  color: var(--text3) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: .78rem !important;
  border-radius: 6px !important;
  padding: .42rem .9rem !important;
  transition: color .15s !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: var(--accent) !important;
  color: #0c0d10 !important;
}

/* ─── FILE UPLOADER ─── */
[data-testid="stFileUploader"] {
  border: 1.5px dashed var(--border2) !important;
  border-radius: var(--r) !important;
  background: var(--surface) !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--accent) !important;
}

/* ─── ALERTS ─── */
[data-testid="stAlert"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r-sm) !important;
  font-size: .83rem !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ─── SLIDER ─── */
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {
  color: var(--text3) !important;
  font-size: .75rem !important;
}

/* ─── EXPANDER ─── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
}
[data-testid="stExpander"] summary {
  color: var(--text2) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .84rem !important;
  font-weight: 600 !important;
}

/* ─── SCROLLBAR ─── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 999px; }

/* ─── MOBILE ─── */
@media (max-width: 520px) {
  .stat-num { font-size: 2.4rem; }
  .block-container { padding: 1rem .8rem 6rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────
DATA_FILE = "fitai_data.json"

ALIMENTOS_DB = {
    "Pollo a la plancha (100g)":    {"cal":165,"prot":31.0,"carb":0.0,"grasa":3.6},
    "Pechuga de pavo (100g)":       {"cal":135,"prot":30.0,"carb":0.0,"grasa":1.0},
    "Atún en agua (100g)":          {"cal":116,"prot":26.0,"carb":0.0,"grasa":1.0},
    "Salmón (100g)":                {"cal":208,"prot":20.0,"carb":0.0,"grasa":13.0},
    "Ternera magra (100g)":         {"cal":170,"prot":26.0,"carb":0.0,"grasa":7.0},
    "Huevo entero (1 ud ~60g)":     {"cal":86, "prot":7.5, "carb":0.6,"grasa":6.0},
    "Claras de huevo (100g)":       {"cal":52, "prot":11.0,"carb":0.7,"grasa":0.2},
    "Queso fresco 0% (100g)":       {"cal":62, "prot":11.0,"carb":3.3,"grasa":0.4},
    "Yogur griego natural (100g)":  {"cal":97, "prot":9.0, "carb":3.6,"grasa":5.0},
    "Yogur griego 0% (100g)":       {"cal":59, "prot":10.0,"carb":3.5,"grasa":0.4},
    "Leche semidesnatada (100ml)":  {"cal":46, "prot":3.3, "carb":4.7,"grasa":1.6},
    "Whey protein (30g)":           {"cal":114,"prot":24.0,"carb":3.0,"grasa":1.5},
    "Avena (100g)":                 {"cal":389,"prot":17.0,"carb":66.0,"grasa":7.0},
    "Arroz blanco cocido (100g)":   {"cal":130,"prot":2.7, "carb":28.0,"grasa":0.3},
    "Arroz integral cocido (100g)": {"cal":122,"prot":2.6, "carb":25.0,"grasa":0.9},
    "Pasta integral cocida (100g)": {"cal":124,"prot":5.0, "carb":25.0,"grasa":1.0},
    "Pan integral (35g/rebanada)":  {"cal":80, "prot":3.5, "carb":14.0,"grasa":1.0},
    "Boniato cocido (100g)":        {"cal":90, "prot":2.0, "carb":21.0,"grasa":0.1},
    "Patata cocida (100g)":         {"cal":77, "prot":2.0, "carb":17.0,"grasa":0.1},
    "Lentejas cocidas (100g)":      {"cal":116,"prot":9.0, "carb":20.0,"grasa":0.4},
    "Garbanzos cocidos (100g)":     {"cal":164,"prot":8.9, "carb":27.0,"grasa":2.6},
    "Aguacate (100g)":              {"cal":160,"prot":2.0, "carb":9.0, "grasa":15.0},
    "Aceite de oliva (10ml)":       {"cal":90, "prot":0.0, "carb":0.0, "grasa":10.0},
    "Almendras (30g)":              {"cal":174,"prot":6.0, "carb":6.0, "grasa":15.0},
    "Plátano mediano (120g)":       {"cal":107,"prot":1.3, "carb":27.0,"grasa":0.4},
    "Manzana mediana (150g)":       {"cal":78, "prot":0.4, "carb":21.0,"grasa":0.2},
    "Naranja (150g)":               {"cal":70, "prot":1.3, "carb":17.0,"grasa":0.2},
    "Brócoli (100g)":               {"cal":34, "prot":2.8, "carb":7.0, "grasa":0.4},
    "Espinacas (100g)":             {"cal":23, "prot":2.9, "carb":3.6, "grasa":0.4},
    "Tomate (100g)":                {"cal":18, "prot":0.9, "carb":3.9, "grasa":0.2},
    "Pepino (100g)":                {"cal":15, "prot":0.7, "carb":3.6, "grasa":0.1},
    "Lechuga (100g)":               {"cal":15, "prot":1.4, "carb":2.9, "grasa":0.2},
    "Zanahoria (100g)":             {"cal":41, "prot":0.9, "carb":10.0,"grasa":0.2},
}

DIETAS_TEMPLATE = {
    "Volumen limpio (~2800 kcal)": {
        "objetivo": "Ganar masa muscular con mínima grasa",
        "macros": {"prot":175,"carb":350,"grasa":75},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Avena 80g + Whey 30g + Plátano + Leche 200ml","cal":580,"prot":42,"carb":82,"grasa":10},
            {"nombre":"Media mañana","alimentos":"Yogur griego 200g + Almendras 30g + Manzana","cal":330,"prot":22,"carb":30,"grasa":16},
            {"nombre":"Almuerzo","alimentos":"Arroz integral 150g + Pollo 200g + Brócoli + AOVE 10ml","cal":720,"prot":72,"carb":85,"grasa":14},
            {"nombre":"Merienda","alimentos":"Pan integral 70g + Atún 100g + Tomate","cal":290,"prot":36,"carb":28,"grasa":3},
            {"nombre":"Cena","alimentos":"Salmón 200g + Boniato 200g + Espinacas salteadas","cal":580,"prot":45,"carb":48,"grasa":28},
            {"nombre":"Antes de dormir","alimentos":"Claras de huevo 200g + Queso fresco 0%","cal":220,"prot":34,"carb":7,"grasa":3},
        ],
    },
    "Definición (~1900 kcal)": {
        "objetivo": "Perder grasa conservando músculo",
        "macros": {"prot":180,"carb":160,"grasa":60},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Claras 4 + 1 huevo + Avena 50g","cal":380,"prot":38,"carb":35,"grasa":9},
            {"nombre":"Media mañana","alimentos":"Yogur griego 0% 200g + Proteína en polvo","cal":250,"prot":35,"carb":10,"grasa":3},
            {"nombre":"Almuerzo","alimentos":"Pechuga pavo 200g + Patata 150g + Verduras","cal":430,"prot":62,"carb":35,"grasa":5},
            {"nombre":"Merienda","alimentos":"Atún 100g + Pan integral 35g + Pepino","cal":230,"prot":30,"carb":18,"grasa":2},
            {"nombre":"Cena","alimentos":"Merluza/Pollo 200g + Brócoli + Espinacas + AOVE 5ml","cal":380,"prot":48,"carb":12,"grasa":14},
            {"nombre":"Antes de dormir","alimentos":"Queso fresco 0% 150g","cal":93,"prot":17,"carb":5,"grasa":0.6},
        ],
    },
    "Mantenimiento (~2300 kcal)": {
        "objetivo": "Mantener composición corporal actual",
        "macros": {"prot":155,"carb":260,"grasa":70},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Avena 60g + Leche 200ml + 2 Huevos + Fruta","cal":490,"prot":28,"carb":62,"grasa":14},
            {"nombre":"Media mañana","alimentos":"Fruta + Almendras 25g + Queso fresco","cal":270,"prot":14,"carb":25,"grasa":13},
            {"nombre":"Almuerzo","alimentos":"Arroz 120g + Ternera magra 150g + Ensalada + AOVE","cal":600,"prot":45,"carb":60,"grasa":18},
            {"nombre":"Merienda","alimentos":"Plátano + Pan integral + Pavo 80g","cal":310,"prot":26,"carb":42,"grasa":4},
            {"nombre":"Cena","alimentos":"Salmón 150g + Garbanzos 100g + Verduras a la plancha","cal":540,"prot":40,"carb":42,"grasa":21},
        ],
    },
    "Vegana alta proteína (~2200 kcal)": {
        "objetivo": "Dieta plant-based con proteína suficiente",
        "macros": {"prot":140,"carb":280,"grasa":65},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Avena 80g + Proteína vegana 30g + Plátano","cal":520,"prot":35,"carb":80,"grasa":10},
            {"nombre":"Media mañana","alimentos":"Hummus 100g + Pan integral + Tomate","cal":290,"prot":12,"carb":35,"grasa":10},
            {"nombre":"Almuerzo","alimentos":"Lentejas 200g + Arroz 100g + Verduras + AOVE","cal":590,"prot":28,"carb":95,"grasa":12},
            {"nombre":"Merienda","alimentos":"Aguacate + Pan integral + Batido espinacas","cal":350,"prot":10,"carb":30,"grasa":22},
            {"nombre":"Cena","alimentos":"Tofu 200g + Garbanzos 100g + Brócoli + AOVE","cal":470,"prot":38,"carb":35,"grasa":20},
        ],
    },
}

EJERCICIOS_GYM = {
    "Pecho": [
        {"nombre":"Press banca plano","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-12","descanso":"90s","notas":"Escápulas retraídas, toque suave al pecho"},
        {"nombre":"Press banca inclinado","tipo":"Hipertrofia","equipo":"Barra / Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Ángulo 30-45°, activa porción clavicular"},
        {"nombre":"Press banca declinado","tipo":"Hipertrofia","equipo":"Barra","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Activa porción esternocostal"},
        {"nombre":"Aperturas con mancuernas","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados"},
        {"nombre":"Fondos en paralelas","tipo":"Peso corporal","equipo":"Paralelas","series_rec":"3-4","reps_rec":"Máx","descanso":"90s","notas":"Torso inclinado adelante para enfatizar pecho"},
        {"nombre":"Crossover en polea","tipo":"Aislamiento","equipo":"Poleas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Estira bien en la parte superior del movimiento"},
    ],
    "Espalda": [
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3 min","notas":"Espalda neutra, barra pegada al cuerpo"},
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra fija","series_rec":"4","reps_rec":"Máx","descanso":"90s","notas":"Rango completo, sin balanceo"},
        {"nombre":"Jalón al pecho","tipo":"Hipertrofia","equipo":"Polea alta","series_rec":"4","reps_rec":"10-15","descanso":"75s","notas":"Codos hacia abajo, lleva barra a la barbilla"},
        {"nombre":"Remo con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Torso 45°, barra al ombligo"},
        {"nombre":"Remo en polea baja","tipo":"Hipertrofia","equipo":"Polea baja","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Pecho erguido, tirón hacia el abdomen"},
        {"nombre":"Face pulls","tipo":"Prevención","equipo":"Polea alta","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Esencial para salud del manguito rotador"},
    ],
    "Pierna": [
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3 min","notas":"Rodillas en dirección de los pies"},
        {"nombre":"Prensa de piernas","tipo":"Hipertrofia","equipo":"Máquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos = isquios / bajos = cuádriceps"},
        {"nombre":"Extensión de cuádriceps","tipo":"Aislamiento","equipo":"Máquina","series_rec":"3","reps_rec":"15-20","descanso":"60s","notas":"Contracción completa en la extensión"},
        {"nombre":"Femoral tumbado","tipo":"Aislamiento","equipo":"Máquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Aísla isquiotibiales eficazmente"},
        {"nombre":"Peso muerto rumano","tipo":"Hipertrofia","equipo":"Barra / Mancuernas","series_rec":"3-4","reps_rec":"10-12","descanso":"90s","notas":"Bisagra de cadera, isquios en tensión"},
        {"nombre":"Hip Thrust","tipo":"Glúteos","equipo":"Barra / Máquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Contracción máxima arriba, pelvis neutra"},
        {"nombre":"Zancadas caminando","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"12/pierna","descanso":"75s","notas":"Rodilla trasera casi toca el suelo"},
        {"nombre":"Elevación de gemelos","tipo":"Aislamiento","equipo":"Máquina / Libre","series_rec":"4","reps_rec":"15-25","descanso":"45s","notas":"Rango completo, pausa arriba y abajo"},
    ],
    "Hombros": [
        {"nombre":"Press militar con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2 min","notas":"Core activado, no arquear la lumbar"},
        {"nombre":"Press Arnold","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Rotación completa activa todos los fascículos"},
        {"nombre":"Elevaciones laterales","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Codo ligeramente flexionado, hasta la horizontal"},
        {"nombre":"Pájaro posterior","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Torso a 90°, activa deltoides posterior"},
        {"nombre":"Encogimientos de trapecios","tipo":"Fuerza","equipo":"Barra / Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Movimiento vertical puro, sin rotación"},
    ],
    "Bíceps": [
        {"nombre":"Curl con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"75s","notas":"Codos fijos a los lados del tronco"},
        {"nombre":"Curl con mancuernas alterno","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-14/brazo","descanso":"60s","notas":"Supina en la subida para más contracción"},
        {"nombre":"Curl martillo","tipo":"Braquial","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Agarre neutro, activa braquirradial"},
        {"nombre":"Curl predicador","tipo":"Aislamiento","equipo":"Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"No extender completamente para evitar lesión"},
    ],
    "Tríceps": [
        {"nombre":"Press banca agarre cerrado","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Codos pegados al cuerpo, no abrir"},
        {"nombre":"Extensión sobre la cabeza","tipo":"Hipertrofia","equipo":"Mancuerna / Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Estiramiento máximo en la parte baja"},
        {"nombre":"Press francés","tipo":"Hipertrofia","equipo":"Barra EZ","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Tumbado, baja la barra a la frente"},
        {"nombre":"Pushdown en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"3-4","reps_rec":"15-20","descanso":"45s","notas":"Codos fijos, extensión completa abajo"},
        {"nombre":"Kickbacks","tipo":"Aislamiento","equipo":"Mancuerna","series_rec":"3","reps_rec":"15-20/brazo","descanso":"45s","notas":"Brazo paralelo al suelo, solo mueve el antebrazo"},
    ],
    "Core": [
        {"nombre":"Plancha","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3-4","reps_rec":"45-90s","descanso":"45s","notas":"Cuerpo recto, no elevar caderas"},
        {"nombre":"Plancha lateral","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"30-60s/lado","descanso":"30s","notas":"Cadera levantada, cuerpo perfectamente alineado"},
        {"nombre":"Crunch en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Flexión de columna, no de cadera"},
        {"nombre":"Rueda abdominal","tipo":"Fuerza","equipo":"Rueda","series_rec":"3","reps_rec":"8-15","descanso":"60s","notas":"Empieza de rodillas, progresión de pie"},
        {"nombre":"Elevación de piernas colgado","tipo":"Fuerza","equipo":"Barra fija","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Pelvis en retroversión al subir"},
        {"nombre":"Dead bug","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"8-12/lado","descanso":"45s","notas":"Espalda baja pegada al suelo siempre"},
    ],
    "Cardio": [
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint / 30s caminar","descanso":"—","notas":"FC en sprints ~85-90% de la máxima"},
        {"nombre":"Tabata en bicicleta","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s esfuerzo / 10s pausa","descanso":"—","notas":"Protocolo Tabata clásico · 4 minutos totales"},
        {"nombre":"Elíptica zona 2","tipo":"Cardio","equipo":"Elíptica","series_rec":"1","reps_rec":"30-45 min","descanso":"—","notas":"FC 120-140 ppm, puedes hablar con dificultad leve"},
        {"nombre":"Remo ergómetro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500 m","descanso":"2 min","notas":"Excelente combo cardio + espalda + piernas"},
        {"nombre":"Saltar a la comba","tipo":"Cardio","equipo":"Comba","series_rec":"5","reps_rec":"2 min","descanso":"60s","notas":"Bajo impacto articular, alta quema calórica"},
    ],
}

RUTINAS_DEFAULT = {
    "PPL — Push (Empuje)": {
        "desc": "Pecho, hombros y tríceps",
        "ejercicios": [
            {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Press banca inclinado mancuernas","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Press Arnold","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Extensión sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
        ],
    },
    "PPL — Pull (Tirón)": {
        "desc": "Espalda y bíceps",
        "ejercicios": [
            {"ejercicio":"Dominadas","series":4,"reps":"Máx","peso":"Corporal","descanso":"90s","notas":""},
            {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Jalón al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Remo en polea baja","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
        ],
    },
    "PPL — Legs (Piernas)": {
        "desc": "Cuádriceps, isquios, glúteos y gemelos",
        "ejercicios": [
            {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-8","peso":"","descanso":"2-3 min","notas":""},
            {"ejercicio":"Prensa de piernas","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Peso muerto rumano","series":3,"reps":"10-12","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Femoral tumbado","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Hip Thrust","series":4,"reps":"12-15","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Elevación de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
        ],
    },
    "Full Body (principiantes)": {
        "desc": "Sesión completa 3 días / semana",
        "ejercicios": [
            {"ejercicio":"Sentadilla con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Press banca plano","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Peso muerto convencional","series":3,"reps":"6-8","peso":"","descanso":"2 min","notas":""},
            {"ejercicio":"Press militar con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Dominadas","series":3,"reps":"Máx","peso":"Corporal","descanso":"90s","notas":""},
            {"ejercicio":"Plancha","series":3,"reps":"60s","peso":"","descanso":"45s","notas":""},
        ],
    },
    "Upper / Lower — Upper": {
        "desc": "Tren superior: pecho, espalda, hombros, brazos",
        "ejercicios": [
            {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Press banca inclinado mancuernas","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Jalón al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Elevaciones laterales","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        ],
    },
    "Upper / Lower — Lower": {
        "desc": "Tren inferior: cuádriceps, isquios, glúteos, core",
        "ejercicios": [
            {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-10","peso":"","descanso":"2 min","notas":""},
            {"ejercicio":"Peso muerto rumano","series":4,"reps":"8-12","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Prensa de piernas","series":3,"reps":"12-15","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Femoral tumbado","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Zancadas caminando","series":3,"reps":"12/pierna","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Elevación de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Crunch en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        ],
    },
    "HIIT + Core": {
        "desc": "Alta intensidad + trabajo abdominal · ~35 min",
        "ejercicios": [
            {"ejercicio":"Burpees","series":5,"reps":"30s trabajo / 15s pausa","peso":"","descanso":"30s","notas":""},
            {"ejercicio":"Mountain climbers","series":5,"reps":"30s trabajo / 15s pausa","peso":"","descanso":"30s","notas":""},
            {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Sprint en sitio","series":6,"reps":"20s / 10s pausa","peso":"","descanso":"—","notas":""},
            {"ejercicio":"Plancha","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
            {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""},
        ],
    },
}

TIPO_COLOR = {
    "Fuerza":        ("#ff5a5a","rgba(255,90,90,.12)"),
    "Hipertrofia":   ("#5a9eff","rgba(90,158,255,.12)"),
    "Aislamiento":   ("#b45aff","rgba(180,90,255,.12)"),
    "Peso corporal": ("#5affcc","rgba(90,255,204,.12)"),
    "Cardio":        ("#e8ff5a","rgba(232,255,90,.12)"),
    "Estabilidad":   ("#5affcc","rgba(90,255,204,.12)"),
    "Glúteos":       ("#ff9eb5","rgba(255,158,181,.12)"),
    "Prevención":    ("#5affcc","rgba(90,255,204,.12)"),
    "Braquial":      ("#b45aff","rgba(180,90,255,.12)"),
}

# ─────────────────────────────────────
# PERSISTENCIA
# ─────────────────────────────────────
def cargar_datos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "historial_calorias": {}, "historial_macros": {},
        "diario_comidas": {}, "rutinas_custom": {},
        "dietas_custom": {}, "perfil": {}, "registro_entreno": {},
    }

def guardar_datos(datos):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"No se pudo guardar: {e}")

# ─────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────
if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "scan_resultado" not in st.session_state:
    st.session_state.scan_resultado = None
if "ia_dieta_res" not in st.session_state:
    st.session_state.ia_dieta_res = None
if "ej_temp" not in st.session_state:
    st.session_state.ej_temp = []
if "sets_temp" not in st.session_state:
    st.session_state.sets_temp = []
if "comidas_dc_temp" not in st.session_state:
    st.session_state.comidas_dc_temp = []

# ─────────────────────────────────────
# HELPERS
# ─────────────────────────────────────
def hoy():
    return str(date.today())

def get_perfil():
    return st.session_state.datos.get("perfil", {})

def get_obj_cal():
    return int(get_perfil().get("objetivo_cal", 2000))

def cal_hoy():
    return st.session_state.datos["historial_calorias"].get(hoy(), 0)

def macros_hoy():
    return st.session_state.datos.get("historial_macros", {}).get(
        hoy(), {"prot": 0.0, "carb": 0.0, "grasa": 0.0}
    )

def registrar_alimento(nombre, cal, prot, carb, grasa, comida):
    d = st.session_state.datos
    d["historial_calorias"][hoy()] = cal_hoy() + cal
    hm = d.setdefault("historial_macros", {})
    dm = hm.setdefault(hoy(), {"prot": 0.0, "carb": 0.0, "grasa": 0.0})
    dm["prot"]  = round(dm["prot"]  + prot,  1)
    dm["carb"]  = round(dm["carb"]  + carb,  1)
    dm["grasa"] = round(dm["grasa"] + grasa, 1)
    dc = d.setdefault("diario_comidas", {})
    dc.setdefault(hoy(), []).append({
        "comida": comida, "alimento": nombre,
        "cal": cal, "prot": prot, "carb": carb, "grasa": grasa,
        "hora": datetime.now().strftime("%H:%M"),
    })
    guardar_datos(d)

def calcular_tdee(peso, altura, edad, sexo, actividad):
    bmr = (88.36 + 13.4 * peso + 4.8 * altura - 5.7 * edad) if sexo == "Hombre" \
          else (447.6 + 9.2 * peso + 3.1 * altura - 4.3 * edad)
    factores = {
        "Sedentario (sin ejercicio)":     1.2,
        "Ligero (1-2 días/semana)":       1.375,
        "Moderado (3-4 días/semana)":     1.55,
        "Activo (5-6 días/semana)":       1.725,
        "Muy activo (2 veces/día)":       1.9,
    }
    return int(bmr * factores.get(actividad, 1.55))

def pbar(val, mx, color):
    pct = min(val / mx * 100, 100) if mx > 0 else 0
    return (f'<div class="pbar">'
            f'<div class="pbar-fill" style="width:{pct}%;background:{color}"></div>'
            f'</div>')

def gemini_call(prompt, img_bytes=None):
    try:
        genai.configure(api_key=st.session_state.gemini_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        if img_bytes:
            img = Image.open(io.BytesIO(img_bytes))
            return model.generate_content([prompt, img]).text
        return model.generate_content(prompt).text
    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "INVALID" in err.upper():
            return "❌ API Key inválida. Verifica en ⚙️ Config."
        if "QUOTA" in err.upper():
            return "❌ Cuota de API agotada. Espera unos minutos."
        if "SAFETY" in err.upper():
            return "⚠️ Imagen bloqueada por filtros de seguridad."
        return f"❌ Error: {err}"

def extraer_kcal(texto):
    try:
        m = re.search(r"TOTAL.*?(\d{2,4})\s*kcal", texto, re.IGNORECASE)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return 0

def sdiv(label):
    st.markdown(
        f'<div class="sdiv"><div class="sdiv-line"></div>'
        f'<span class="sdiv-lbl">{label}</span>'
        f'<div class="sdiv-line"></div></div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────
# HERO
# ─────────────────────────────────────
perfil_nombre = get_perfil().get("nombre", "")
saludo = f"Hola, {perfil_nombre}" if perfil_nombre else "Tu asistente de fitness"

st.markdown(
    f'<div class="hero">'
    f'<div class="hero-eyebrow">{saludo}</div>'
    f'<div class="hero-title">Fit<em>AI</em> Pro</div>'
    f'<div class="hero-sub">Nutrición · Dietas · Gimnasio · IA — Todo en uno</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────
t_nut, t_diet, t_gym, t_hist, t_cfg = st.tabs([
    "🥗 Nutrición", "📋 Dietas", "🏋️ Gimnasio", "📊 Historial", "⚙️ Config"
])

# ══════════════════════════════════════════════
# NUTRICIÓN
# ══════════════════════════════════════════════
with t_nut:
    c_hoy    = cal_hoy()
    obj_c    = get_obj_cal()
    m_hoy    = macros_hoy()
    perfil   = get_perfil()
    obj_prot = int(perfil.get("obj_prot",  150))
    obj_carb = int(perfil.get("obj_carb",  220))
    obj_gras = int(perfil.get("obj_grasa",  60))
    restante = max(obj_c - c_hoy, 0)
    exceso   = max(c_hoy - obj_c, 0)
    ok_hoy   = c_hoy <= obj_c

    # Dashboard principal
    col1, col2 = st.columns([3, 2])
    with col1:
        kcal_color = "var(--accent2)" if ok_hoy else "var(--red)"
        bar_color  = "var(--accent)"  if ok_hoy else "var(--red)"
        st.markdown(
            f'<div class="card">'
            f'<div class="card-label">Calorías de hoy</div>'
            f'<div class="stat-num" style="color:{kcal_color}">{c_hoy}</div>'
            f'<div class="stat-unit">de {obj_c} kcal objetivo</div>'
            f'{pbar(c_hoy, obj_c, bar_color)}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        if ok_hoy:
            status_txt = f"<span style='color:var(--accent2);font-size:1.5rem;font-weight:700;font-family:Fraunces,serif'>+{restante}</span><br><span style='font-size:.72rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.1em;text-transform:uppercase'>kcal libres</span>"
        else:
            status_txt = f"<span style='color:var(--red);font-size:1.5rem;font-weight:700;font-family:Fraunces,serif'>+{exceso}</span><br><span style='font-size:.72rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.1em;text-transform:uppercase'>excedido</span>"
        st.markdown(
            f'<div class="card" style="height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;min-height:100px">'
            f'{status_txt}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Macros
    macro_pct_p = int(min(m_hoy["prot"]  / obj_prot * 100, 100)) if obj_prot else 0
    macro_pct_c = int(min(m_hoy["carb"]  / obj_carb * 100, 100)) if obj_carb else 0
    macro_pct_g = int(min(m_hoy["grasa"] / obj_gras * 100, 100)) if obj_gras else 0

    st.markdown(
        f'<div class="card">'
        f'<div class="card-label">Macros del día</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem">'
        f'<div>'
        f'  <div style="font-size:.7rem;color:var(--text3);margin-bottom:.2rem;font-family:DM Mono,monospace;letter-spacing:.08em">PROTEÍNA</div>'
        f'  <div style="font-size:1.5rem;font-weight:700;color:var(--accent2);font-family:Fraunces,serif">{m_hoy["prot"]}g</div>'
        f'  <div style="font-size:.7rem;color:var(--text3)">/{obj_prot}g · {macro_pct_p}%</div>'
        f'  {pbar(m_hoy["prot"], obj_prot, "var(--accent2)")}'
        f'</div>'
        f'<div>'
        f'  <div style="font-size:.7rem;color:var(--text3);margin-bottom:.2rem;font-family:DM Mono,monospace;letter-spacing:.08em">CARBOS</div>'
        f'  <div style="font-size:1.5rem;font-weight:700;color:var(--blue);font-family:Fraunces,serif">{m_hoy["carb"]}g</div>'
        f'  <div style="font-size:.7rem;color:var(--text3)">/{obj_carb}g · {macro_pct_c}%</div>'
        f'  {pbar(m_hoy["carb"], obj_carb, "var(--blue)")}'
        f'</div>'
        f'<div>'
        f'  <div style="font-size:.7rem;color:var(--text3);margin-bottom:.2rem;font-family:DM Mono,monospace;letter-spacing:.08em">GRASAS</div>'
        f'  <div style="font-size:1.5rem;font-weight:700;color:var(--purple);font-family:Fraunces,serif">{m_hoy["grasa"]}g</div>'
        f'  <div style="font-size:.7rem;color:var(--text3)">/{obj_gras}g · {macro_pct_g}%</div>'
        f'  {pbar(m_hoy["grasa"], obj_gras, "var(--purple)")}'
        f'</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Scanner IA
    sdiv("Scanner con IA")
    if not st.session_state.gemini_key:
        st.info("⚙️ Configura tu API Key en la pestaña Config para activar el scanner de IA.")
    else:
        img_up = st.file_uploader("Sube una foto del plato", type=["jpg","jpeg","png","webp"], key="up_scan")
        if img_up:
            st.image(img_up, use_container_width=True)
            col_sf1, col_sf2 = st.columns(2)
            with col_sf1:
                comida_scan = st.selectbox(
                    "Comida", ["Desayuno","Media mañana","Almuerzo","Merienda","Cena","Extra"],
                    key="sc_comida"
                )
            with col_sf2:
                if st.button("Analizar con IA →", key="btn_scan"):
                    with st.spinner("Analizando imagen..."):
                        prompt_s = """Eres un nutricionista experto. Analiza esta imagen de comida en español con este formato exacto:

**Alimentos detectados:**
- [alimento] — [X] kcal · P:[Xg] C:[Xg] G:[Xg]

**TOTAL: [NNN] kcal | P:[Xg] C:[Xg] G:[Xg]**

**Valoración:** [una frase sobre el equilibrio nutricional del plato]

Si no hay comida visible, indícalo."""
                        st.session_state.scan_resultado = gemini_call(prompt_s, img_up.read())

        if st.session_state.scan_resultado:
            st.markdown(
                f'<div class="card">{st.session_state.scan_resultado}</div>',
                unsafe_allow_html=True,
            )
            kcals_det = extraer_kcal(st.session_state.scan_resultado)
            if kcals_det > 0:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"Registrar {kcals_det} kcal", key="btn_reg_scan"):
                        c_n = st.session_state.get("sc_comida", "Extra")
                        registrar_alimento("Analizado por IA (foto)", kcals_det, 0, 0, 0, c_n)
                        st.session_state.scan_resultado = None
                        st.success("✓ Registrado correctamente.")
                        st.rerun()
                with c2:
                    if st.button("Descartar", key="btn_disc"):
                        st.session_state.scan_resultado = None
                        st.rerun()

    # Base de alimentos
    sdiv("Registrar desde base de datos")
    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        alim = st.selectbox("Alimento", list(ALIMENTOS_DB.keys()), key="sel_alim", label_visibility="collapsed")
    with col_a2:
        cant = st.number_input("Gramos", min_value=1, max_value=2000, value=100, key="cant", label_visibility="collapsed")

    ad = ALIMENTOS_DB[alim]
    f  = cant / 100
    ca = round(ad["cal"] * f)
    pr = round(ad["prot"] * f, 1)
    cb = round(ad["carb"] * f, 1)
    gr = round(ad["grasa"] * f, 1)
    st.markdown(
        f'<div class="card" style="padding:.75rem 1.2rem">'
        f'<span class="badge badge-kcal">⚡ {ca} kcal</span>'
        f'<span class="badge badge-prot">P {pr}g</span>'
        f'<span class="badge badge-carb">C {cb}g</span>'
        f'<span class="badge badge-fat">G {gr}g</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col_a3, col_a4 = st.columns([2, 1])
    with col_a3:
        com_db = st.selectbox(
            "Comida", ["Desayuno","Media mañana","Almuerzo","Merienda","Cena","Extra"],
            key="com_db"
        )
    with col_a4:
        if st.button("Añadir →", key="btn_add_db"):
            registrar_alimento(f"{alim} ({cant}g)", ca, pr, cb, gr, com_db)
            st.success(f"✓ {ca} kcal registradas")
            st.rerun()

    # Manual
    sdiv("Registro manual")
    c_m1, c_m2, c_m3, c_m4 = st.columns([3, 1, 1, 1])
    with c_m1:
        nm = st.text_input("Nombre", placeholder="Plato personalizado", key="nm", label_visibility="collapsed")
    with c_m2:
        km = st.number_input("kcal", 0, 5000, 0, 5, key="km", label_visibility="collapsed")
    with c_m3:
        pm = st.number_input("P(g)", 0.0, 300.0, 0.0, 0.5, key="pm", label_visibility="collapsed")
    with c_m4:
        cbm = st.number_input("C(g)", 0.0, 500.0, 0.0, 0.5, key="cbm", label_visibility="collapsed")
    c_m5, c_m6 = st.columns([2, 1])
    with c_m5:
        comm = st.selectbox(
            "Comida", ["Desayuno","Media mañana","Almuerzo","Merienda","Cena","Extra"],
            key="comm"
        )
    with c_m6:
        if st.button("Añadir →", key="btn_man"):
            if km > 0:
                registrar_alimento(nm or "Alimento libre", km, pm, cbm, 0.0, comm)
                st.success(f"✓ {km} kcal")
                st.rerun()
            else:
                st.warning("Introduce kcal > 0")

    # Diario
    sdiv("Diario de hoy")
    diario = st.session_state.datos.get("diario_comidas", {}).get(hoy(), [])
    if not diario:
        st.markdown(
            '<div class="card" style="text-align:center;padding:1.5rem">'
            '<div style="font-size:2rem;margin-bottom:.5rem">🍽️</div>'
            '<p style="color:var(--text3)">Sin registros todavía</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        grupos = {}
        for item in diario:
            grupos.setdefault(item["comida"], []).append(item)
        for nombre_c, items in grupos.items():
            total_c = sum(i["cal"] for i in items)
            filas = "".join(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:.35rem 0;border-bottom:1px solid var(--border);font-size:.82rem">'
                f'<span style="color:var(--text2)">'
                f'<span style="color:var(--text3);font-family:DM Mono,monospace;font-size:.72rem">{i["hora"]}</span>'
                f' &nbsp;{i["alimento"]}</span>'
                f'<span style="color:var(--accent);font-weight:600;font-family:DM Mono,monospace">{i["cal"]} kcal</span>'
                f'</div>'
                for i in items
            )
            st.markdown(
                f'<div class="card">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">'
                f'<span style="font-weight:700;color:var(--text);font-size:.9rem">{nombre_c}</span>'
                f'<span class="badge badge-kcal">{total_c} kcal</span>'
                f'</div>{filas}</div>',
                unsafe_allow_html=True,
            )

    if st.button("Resetear diario de hoy", key="btn_reset"):
        d = st.session_state.datos
        d["historial_calorias"][hoy()] = 0
        d.setdefault("historial_macros", {})[hoy()] = {"prot": 0.0, "carb": 0.0, "grasa": 0.0}
        d.setdefault("diario_comidas", {})[hoy()] = []
        guardar_datos(d)
        st.success("Diario reseteado.")
        st.rerun()


# ══════════════════════════════════════════════
# DIETAS
# ══════════════════════════════════════════════
with t_diet:
    dt1, dt2, dt3, dt4 = st.tabs(["Planes", "Calculadora", "IA Dietista", "Mis dietas"])

    with dt1:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
        plan_k = st.selectbox("Plan de nutrición", list(DIETAS_TEMPLATE.keys()), key="plan_k")
        plan   = DIETAS_TEMPLATE[plan_k]
        tot_cal = sum(c["cal"]   for c in plan["comidas"])
        tot_p   = sum(c["prot"]  for c in plan["comidas"])
        tot_cb  = sum(c["carb"]  for c in plan["comidas"])
        tot_gr  = sum(c["grasa"] for c in plan["comidas"])

        st.markdown(
            f'<div class="card">'
            f'<div class="card-label">Objetivo del plan</div>'
            f'<div style="font-size:.95rem;font-weight:600;color:var(--text);margin-bottom:.6rem">{plan["objetivo"]}</div>'
            f'<span class="badge badge-kcal">⚡ {tot_cal} kcal</span>'
            f'<span class="badge badge-prot">P {tot_p}g</span>'
            f'<span class="badge badge-carb">C {tot_cb}g</span>'
            f'<span class="badge badge-fat">G {tot_gr}g</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for c in plan["comidas"]:
            st.markdown(
                f'<div class="card">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem">'
                f'<h4>{c["nombre"]}</h4>'
                f'<span class="badge badge-kcal">{c["cal"]} kcal</span>'
                f'</div>'
                f'<p style="margin-bottom:.5rem">{c["alimentos"]}</p>'
                f'<span class="badge badge-prot">P {c["prot"]}g</span>'
                f'<span class="badge badge-carb">C {c["carb"]}g</span>'
                f'<span class="badge badge-fat">G {c["grasa"]}g</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if st.button("Usar este plan como objetivo diario", key="btn_usar_plan"):
            st.session_state.datos.setdefault("perfil", {}).update({
                "objetivo_cal": tot_cal, "obj_prot": tot_p,
                "obj_carb": tot_cb, "obj_grasa": tot_gr,
            })
            guardar_datos(st.session_state.datos)
            st.success(f"✓ Objetivos actualizados: {tot_cal} kcal / día")
            st.rerun()

    with dt2:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
        pf = get_perfil()
        c1, c2 = st.columns(2)
        with c1:
            cp   = st.number_input("Peso (kg)",    30.0, 250.0, float(pf.get("peso", 75)),   0.5, key="cp")
            ca2  = st.number_input("Altura (cm)",  100,  250,   int(pf.get("altura", 175)),       key="ca2")
        with c2:
            ced  = st.number_input("Edad",         10,   100,   int(pf.get("edad", 25)),          key="ced")
            csx  = st.selectbox("Sexo biológico", ["Hombre","Mujer"], key="csx")

        cact = st.selectbox("Nivel de actividad", [
            "Sedentario (sin ejercicio)", "Ligero (1-2 días/semana)",
            "Moderado (3-4 días/semana)", "Activo (5-6 días/semana)", "Muy activo (2 veces/día)",
        ], index=2, key="cact")

        cobj = st.selectbox("Objetivo", [
            "Pérdida de grasa (-300 kcal)", "Pérdida agresiva (-500 kcal)",
            "Mantenimiento", "Volumen limpio (+200 kcal)", "Volumen (+400 kcal)",
        ], key="cobj")

        if st.button("Calcular →", key="btn_calc"):
            tdee  = calcular_tdee(cp, ca2, ced, csx, cact)
            delta = {
                "Pérdida de grasa (-300 kcal)": -300,
                "Pérdida agresiva (-500 kcal)":  -500,
                "Mantenimiento":                     0,
                "Volumen limpio (+200 kcal)":      200,
                "Volumen (+400 kcal)":             400,
            }[cobj]
            cobj_k  = tdee + delta
            perdida = "Pérdida" in cobj
            prot_g  = round(cp * (2.2 if perdida else 1.9))
            gras_g  = round(cp * (1.0 if perdida else 1.1))
            carb_g  = max(round((cobj_k - prot_g * 4 - gras_g * 9) / 4), 50)
            imc     = round(cp / ((ca2 / 100) ** 2), 1)
            cat_imc = ("Bajo peso"  if imc < 18.5 else
                       "Normopeso"  if imc < 25   else
                       "Sobrepeso"  if imc < 30   else "Obesidad")

            st.markdown(
                f'<div class="card">'
                f'<div class="card-label">Resultado del cálculo</div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-bottom:.75rem">'
                f'<div>'
                f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">MANTENIMIENTO</div>'
                f'  <div style="font-size:1.4rem;font-weight:700;color:var(--text);font-family:Fraunces,serif">{tdee} kcal</div>'
                f'</div>'
                f'<div>'
                f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">OBJETIVO</div>'
                f'  <div style="font-size:1.4rem;font-weight:700;color:var(--accent);font-family:Fraunces,serif">{cobj_k} kcal</div>'
                f'</div>'
                f'</div>'
                f'<p style="margin-bottom:.5rem">IMC: <b style="color:var(--text)">{imc} — {cat_imc}</b></p>'
                f'<span class="badge badge-prot">P {prot_g}g</span>'
                f'<span class="badge badge-carb">C {carb_g}g</span>'
                f'<span class="badge badge-fat">G {gras_g}g</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Guardar estos objetivos", key="btn_save_calc"):
                st.session_state.datos.setdefault("perfil", {}).update({
                    "peso": cp, "altura": ca2, "edad": ced,
                    "objetivo_cal": cobj_k, "obj_prot": prot_g,
                    "obj_carb": carb_g, "obj_grasa": gras_g,
                })
                guardar_datos(st.session_state.datos)
                st.success("✓ Objetivos guardados.")
                st.rerun()

    with dt3:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
        if not st.session_state.gemini_key:
            st.info("⚙️ Configura tu API Key en la pestaña Config para usar la IA.")
        else:
            pf2 = get_perfil()
            c1, c2 = st.columns(2)
            with c1:
                ia_p  = st.number_input("Peso (kg)",   30.0, 250.0, float(pf2.get("peso",75)),   0.5, key="ia_p")
                ia_a  = st.number_input("Altura (cm)", 100,  250,   int(pf2.get("altura",175)),       key="ia_a")
                ia_e  = st.number_input("Edad",        10,   100,   int(pf2.get("edad",25)),          key="ia_e")
            with c2:
                ia_sx = st.selectbox("Sexo", ["Hombre","Mujer"], key="ia_sx")
                ia_ob = st.selectbox("Objetivo", [
                    "Perder grasa", "Ganar músculo", "Mantenimiento",
                    "Mejorar rendimiento deportivo", "Salud general",
                ], key="ia_ob")
                ia_ac = st.selectbox("Actividad", [
                    "Sedentario","Ligero","Moderado","Activo","Muy activo"
                ], key="ia_ac")

            ia_rest = st.multiselect("Restricciones alimentarias", [
                "Sin gluten","Sin lactosa","Vegetariano","Vegano",
                "Sin cerdo","Sin mariscos","Bajo en sodio","Bajo en azúcar",
            ], key="ia_rest")
            ia_ext = st.text_area(
                "Contexto adicional",
                placeholder="Alergias, horarios, patologías, preferencias...",
                height=70, key="ia_ext"
            )

            if st.button("Generar plan personalizado con IA →", key="btn_ia"):
                rest_str = ", ".join(ia_rest) if ia_rest else "ninguna"
                prompt_d = f"""Eres un dietista-nutricionista experto. Crea un plan de dieta completo en español para:
- Perfil: {ia_sx}, {ia_e} años, {ia_p}kg, {ia_a}cm
- Objetivo: {ia_ob} · Actividad: {ia_ac} · Restricciones: {rest_str}
- Info extra: {ia_ext or 'ninguna'}

Incluye:
1. Calorías recomendadas y macros diarios (en gramos)
2. Plan de 5-6 comidas con alimentos, cantidades y calorías
3. Timing nutricional pre/post entreno si aplica
4. Lista de la compra semanal
5. 3 consejos clave para el objetivo

Sé específico con cantidades. Usa formato claro con emojis."""
                with st.spinner("Generando tu plan personalizado..."):
                    st.session_state.ia_dieta_res = gemini_call(prompt_d)

            if st.session_state.ia_dieta_res:
                st.markdown(
                    f'<div class="card">{st.session_state.ia_dieta_res}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Generar otro plan", key="btn_ia_reset"):
                    st.session_state.ia_dieta_res = None
                    st.rerun()

    with dt4:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
        dc_all = st.session_state.datos.get("dietas_custom", {})

        if dc_all:
            dc_sel = st.selectbox("Ver dieta guardada", ["— Nueva —"] + list(dc_all.keys()), key="dc_sel")
            if dc_sel != "— Nueva —":
                dc = dc_all[dc_sel]
                if dc.get("notas"):
                    st.markdown(
                        f'<div class="card"><p>{dc["notas"]}</p></div>',
                        unsafe_allow_html=True,
                    )
                for c in dc.get("comidas", []):
                    st.markdown(
                        f'<div class="card">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">'
                        f'<h4>{c["nombre"]}</h4>'
                        f'<span class="badge badge-kcal">{c.get("cal",0)} kcal</span>'
                        f'</div>'
                        f'<p style="margin-bottom:.45rem">{c.get("alimentos","")}</p>'
                        f'<span class="badge badge-prot">P {c.get("prot",0)}g</span>'
                        f'<span class="badge badge-carb">C {c.get("carb",0)}g</span>'
                        f'<span class="badge badge-fat">G {c.get("grasa",0)}g</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                if st.button("Eliminar esta dieta", key="btn_del_dc"):
                    del st.session_state.datos["dietas_custom"][dc_sel]
                    guardar_datos(st.session_state.datos)
                    st.success("Dieta eliminada.")
                    st.rerun()

        sdiv("Crear nueva dieta")
        nc_nom = st.text_input("Nombre de la dieta", placeholder="Mi dieta de verano", key="nc_nom")
        nc_not = st.text_area("Notas", placeholder="Objetivo, duración, observaciones...", height=60, key="nc_not")

        sdiv("Añadir comidas")
        c1, c2 = st.columns([2, 1])
        with c1:
            nc_cn = st.text_input("Nombre de la comida", placeholder="Almuerzo", key="nc_cn")
            nc_al = st.text_area("Alimentos y cantidades", placeholder="Pollo 150g, Arroz 100g...", height=55, key="nc_al")
        with c2:
            nc_cal = st.number_input("kcal",    0,   3000,  0,  10,  key="nc_cal")
            nc_pr  = st.number_input("Prot (g)", 0.0, 200.0, 0.0, 0.5, key="nc_pr")
            nc_cb  = st.number_input("Carb (g)", 0.0, 500.0, 0.0, 0.5, key="nc_cb")
            nc_gr  = st.number_input("Gras (g)", 0.0, 200.0, 0.0, 0.5, key="nc_gr")

        if st.button("+ Añadir comida", key="btn_add_nc"):
            if nc_cn:
                st.session_state.comidas_dc_temp.append({
                    "nombre": nc_cn, "alimentos": nc_al,
                    "cal": nc_cal, "prot": nc_pr, "carb": nc_cb, "grasa": nc_gr,
                })
                st.success(f"'{nc_cn}' añadida al plan.")
            else:
                st.warning("Escribe el nombre de la comida.")

        if st.session_state.comidas_dc_temp:
            tot_dc = sum(c["cal"] for c in st.session_state.comidas_dc_temp)
            filas_dc = "".join(
                f'<div style="display:flex;justify-content:space-between;font-size:.82rem;padding:.3rem 0;border-bottom:1px solid var(--border)">'
                f'<span style="color:var(--text2)">{i+1}. {c["nombre"]}</span>'
                f'<span style="color:var(--accent);font-family:DM Mono,monospace">{c["cal"]} kcal</span>'
                f'</div>'
                for i, c in enumerate(st.session_state.comidas_dc_temp)
            )
            st.markdown(
                f'<div class="card">{filas_dc}'
                f'<div style="text-align:right;margin-top:.5rem;font-size:.8rem;color:var(--text3)">Total: {tot_dc} kcal</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if st.button("Guardar dieta →", key="btn_save_dc"):
            if not nc_nom:
                st.warning("Dale un nombre a la dieta.")
            elif not st.session_state.comidas_dc_temp:
                st.warning("Añade al menos una comida.")
            else:
                st.session_state.datos.setdefault("dietas_custom", {})[nc_nom] = {
                    "notas": nc_not,
                    "comidas": st.session_state.comidas_dc_temp.copy(),
                }
                guardar_datos(st.session_state.datos)
                st.session_state.comidas_dc_temp = []
                st.success(f"✓ Dieta '{nc_nom}' guardada.")
                st.rerun()


# ══════════════════════════════════════════════
# GIMNASIO
# ══════════════════════════════════════════════
with t_gym:
    g1, g2, g3 = st.tabs(["Ejercicios", "Rutinas", "Registro"])

    with g1:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
        grupo = st.selectbox("Grupo muscular", list(EJERCICIOS_GYM.keys()), key="grupo_sel")
        for ej in EJERCICIOS_GYM[grupo]:
            tc, tbg = TIPO_COLOR.get(ej["tipo"], ("#8a8fa8","rgba(138,143,168,.12)"))
            st.markdown(
                f'<div class="card">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:.5rem;flex-wrap:wrap;margin-bottom:.4rem">'
                f'<h4>{ej["nombre"]}</h4>'
                f'<span class="type-badge" style="color:{tc};background:{tbg}">{ej["tipo"]}</span>'
                f'</div>'
                f'<p style="font-size:.78rem;color:var(--text3);margin-bottom:.35rem">🏋️ {ej["equipo"]}</p>'
                f'<p style="font-size:.82rem">'
                f'<span style="color:var(--text2)">📦 {ej["series_rec"]} series</span>'
                f'<span style="color:var(--text3)"> · </span>'
                f'<span style="color:var(--text2)">🔁 {ej["reps_rec"]} reps</span>'
                f'<span style="color:var(--text3)"> · </span>'
                f'<span style="color:var(--text2)">⏱ {ej["descanso"]}</span>'
                f'</p>'
                f'<p style="font-size:.78rem;color:var(--text3);font-style:italic;margin-top:.3rem">💡 {ej["notas"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with g2:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
        todas = {**RUTINAS_DEFAULT, **st.session_state.datos.get("rutinas_custom", {})}
        rut_k = st.selectbox("Rutina", list(todas.keys()), key="rut_k")
        rut   = todas[rut_k]
        desc  = rut.get("desc", "") if isinstance(rut, dict) else ""
        ejs   = rut.get("ejercicios", rut) if isinstance(rut, dict) else rut

        if desc:
            st.markdown(
                f'<div style="font-size:.8rem;color:var(--text3);margin-bottom:.75rem">{desc}</div>',
                unsafe_allow_html=True,
            )

        for ej in ejs:
            peso_s  = f" · {ej['peso']}" if ej.get("peso") else ""
            notas_s = (
                f'<p style="font-size:.78rem;color:var(--text3);font-style:italic;margin-top:.3rem">💡 {ej["notas"]}</p>'
                if ej.get("notas") else ""
            )
            st.markdown(
                f'<div class="card">'
                f'<h4>{ej["ejercicio"]}</h4>'
                f'<p style="font-size:.82rem;margin-top:.3rem">'
                f'<span style="color:var(--text2)">📦 {ej["series"]} series</span>'
                f'<span style="color:var(--text3)"> · </span>'
                f'<span style="color:var(--text2)">🔁 {ej["reps"]} reps</span>'
                f'<span style="color:var(--text3)"> · </span>'
                f'<span style="color:var(--text2)">⏱ {ej["descanso"]}{peso_s}</span>'
                f'</p>'
                f'{notas_s}</div>',
                unsafe_allow_html=True,
            )

        sdiv("Crear rutina personalizada")
        with st.expander("➕ Nueva rutina"):
            nr_n = st.text_input("Nombre", placeholder="Mi rutina de lunes", key="nr_n")
            nr_d = st.text_input("Descripción", placeholder="Pecho y tríceps", key="nr_d")
            sdiv("Ejercicios")
            c1, c2, c3 = st.columns([3, 1, 2])
            with c1:
                rn = st.text_input("Ejercicio", placeholder="Sentadilla", key="rn", label_visibility="collapsed")
            with c2:
                rs = st.number_input("Series", 1, 20, 3, key="rs", label_visibility="collapsed")
            with c3:
                rr = st.text_input("Reps", placeholder="10-12", key="rr", label_visibility="collapsed")
            c4, c5 = st.columns(2)
            with c4:
                rp = st.text_input("Peso/carga", placeholder="60 kg", key="rp")
            with c5:
                rd = st.text_input("Descanso", placeholder="90s", key="rd")
            rnotas = st.text_input("Notas técnicas", placeholder="Opcional", key="rnotas")

            if st.button("+ Agregar ejercicio", key="btn_add_ej"):
                if rn:
                    st.session_state.ej_temp.append({
                        "ejercicio": rn, "series": rs,
                        "reps": rr or "—", "peso": rp,
                        "descanso": rd or "—", "notas": rnotas,
                    })
                    st.success(f"'{rn}' añadido.")
                else:
                    st.warning("Escribe el nombre del ejercicio.")

            if st.session_state.ej_temp:
                st.caption(f"{len(st.session_state.ej_temp)} ejercicio(s) en la lista")
                for i, e in enumerate(st.session_state.ej_temp):
                    st.markdown(f"&nbsp;&nbsp;{i+1}. {e['ejercicio']} — {e['series']}×{e['reps']}")

            if st.button("Guardar rutina →", key="btn_save_rut"):
                if not nr_n:
                    st.warning("Pon nombre a la rutina.")
                elif not st.session_state.ej_temp:
                    st.warning("Añade al menos un ejercicio.")
                else:
                    st.session_state.datos.setdefault("rutinas_custom", {})[nr_n] = {
                        "desc": nr_d,
                        "ejercicios": st.session_state.ej_temp.copy(),
                    }
                    guardar_datos(st.session_state.datos)
                    st.session_state.ej_temp = []
                    st.success(f"✓ Rutina '{nr_n}' guardada.")
                    st.rerun()

    with g3:
        st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)

        # Definir todos los inputs ANTES de cualquier lógica condicional
        c1, c2 = st.columns(2)
        with c1:
            reg_f = st.date_input("Fecha", value=date.today(), key="reg_f")
        with c2:
            reg_t = st.selectbox(
                "Tipo de sesión",
                ["Push","Pull","Legs","Full Body","Upper","Lower","HIIT","Cardio","Otro"],
                key="reg_t"
            )

        reg_dur   = st.slider("Duración (min)", 15, 180, 60, 5, key="reg_dur")
        reg_notas = st.text_area("Notas de la sesión", placeholder="Sensaciones, PRs, fatiga...", height=70, key="reg_notas")

        sdiv("Series realizadas")
        c1, c2, c3, c4 = st.columns([3, 1, 2, 2])
        with c1:
            se = st.text_input("Ejercicio", placeholder="Press banca", key="se", label_visibility="collapsed")
        with c2:
            ss = st.number_input("Series", 1, 20, 3, key="ss", label_visibility="collapsed")
        with c3:
            sr = st.text_input("Reps", placeholder="8, 8, 7", key="sr", label_visibility="collapsed")
        with c4:
            sp = st.text_input("Kg", placeholder="80", key="sp", label_visibility="collapsed")

        if st.button("+ Añadir serie", key="btn_add_set"):
            if se:
                st.session_state.sets_temp.append({
                    "ejercicio": se, "series": ss,
                    "reps": sr or "—", "peso": sp or "—",
                })
                st.success(f"'{se}' añadido.")
            else:
                st.warning("Escribe el nombre del ejercicio.")

        if st.session_state.sets_temp:
            filas_s = "".join(
                f'<div style="display:flex;justify-content:space-between;font-size:.82rem;'
                f'padding:.3rem 0;border-bottom:1px solid var(--border)">'
                f'<span style="color:var(--text2)">{e["ejercicio"]}</span>'
                f'<span style="color:var(--text3);font-family:DM Mono,monospace">'
                f'{e["series"]} × {e["reps"]} · {e["peso"]} kg</span>'
                f'</div>'
                for e in st.session_state.sets_temp
            )
            st.markdown(f'<div class="card">{filas_s}</div>', unsafe_allow_html=True)

        if st.button("Guardar entrenamiento →", key="btn_save_ent"):
            if not st.session_state.sets_temp:
                st.warning("Añade al menos una serie.")
            else:
                d = st.session_state.datos
                d.setdefault("registro_entreno", {}).setdefault(str(reg_f), []).append({
                    "tipo":     reg_t,
                    "duracion": reg_dur,
                    "notas":    reg_notas,
                    "sets":     st.session_state.sets_temp.copy(),
                    "hora":     datetime.now().strftime("%H:%M"),
                })
                guardar_datos(d)
                st.session_state.sets_temp = []
                st.success(f"✓ Entreno de {reg_dur} min guardado.")
                st.rerun()

        sdiv("Historial de entrenamientos")
        reg_hist = st.session_state.datos.get("registro_entreno", {})
        if not reg_hist:
            st.markdown(
                '<div class="card" style="text-align:center;padding:1.5rem">'
                '<div style="font-size:2rem;margin-bottom:.5rem">🏋️</div>'
                '<p style="color:var(--text3)">Sin entrenamientos registrados</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            for fecha_e in sorted(reg_hist.keys(), reverse=True)[:8]:
                for ses in reg_hist[fecha_e]:
                    chips = " ".join(
                        f'<span style="font-size:.72rem;color:var(--text3);background:var(--surface2);'
                        f'border-radius:5px;padding:.12rem .4rem;display:inline-block;margin:.1rem;'
                        f'font-family:DM Mono,monospace">'
                        f'{s["ejercicio"]} {s["series"]}×{s["reps"]} {s["peso"]}kg</span>'
                        for s in ses["sets"]
                    )
                    nota_html = (
                        f'<p style="margin-top:.35rem;font-size:.78rem;color:var(--text3)">{ses["notas"]}</p>'
                        if ses.get("notas") else ""
                    )
                    st.markdown(
                        f'<div class="card">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">'
                        f'<span style="font-weight:700;color:var(--text);font-size:.9rem">{fecha_e} · {ses["tipo"]}</span>'
                        f'<span class="badge badge-carb">{ses["duracion"]} min</span>'
                        f'</div>'
                        f'<div style="line-height:2">{chips}</div>'
                        f'{nota_html}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )


# ══════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════
with t_hist:
    st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)
    hist_c = st.session_state.datos.get("historial_calorias", {})
    hist_m = st.session_state.datos.get("historial_macros",   {})

    if not hist_c:
        st.markdown(
            '<div class="card" style="text-align:center;padding:2rem">'
            '<div style="font-size:2.5rem;margin-bottom:.75rem">📊</div>'
            '<p style="color:var(--text3)">Sin datos todavía. ¡Empieza a registrar en Nutrición!</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        obj_c2 = get_obj_cal()
        fechas = sorted(hist_c.keys(), reverse=True)[:14]
        max_c  = max(hist_c.values()) or 1

        rows = ""
        for f in fechas:
            v   = hist_c[f]
            pct = v / max_c * 100
            col = "var(--accent2)" if v <= obj_c2 else "var(--red)"
            rows += (
                f'<div style="display:flex;align-items:center;gap:10px;margin:.3rem 0">'
                f'<span style="color:var(--text3);min-width:90px;font-family:DM Mono,monospace;font-size:.72rem">{f}</span>'
                f'<div style="flex:1;background:var(--surface2);border-radius:999px;height:5px;overflow:hidden">'
                f'<div style="width:{pct}%;height:100%;background:{col};border-radius:999px"></div></div>'
                f'<span style="min-width:75px;color:{col};font-weight:600;text-align:right;'
                f'font-family:DM Mono,monospace;font-size:.78rem">{v} kcal</span>'
                f'</div>'
            )
        st.markdown(
            f'<div class="card"><div class="card-label">Últimos 14 días</div>{rows}</div>',
            unsafe_allow_html=True,
        )

        vals    = list(hist_c.values())
        dias_ok = sum(1 for v in vals if v <= obj_c2)
        promedio = int(sum(vals) / len(vals)) if vals else 0

        st.markdown(
            f'<div class="card">'
            f'<div class="card-label">Estadísticas globales</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem">'
            f'<div>'
            f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">DÍAS REGISTRADOS</div>'
            f'  <div style="font-size:1.6rem;font-weight:700;font-family:Fraunces,serif;color:var(--text)">{len(vals)}</div>'
            f'</div>'
            f'<div>'
            f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">PROMEDIO</div>'
            f'  <div style="font-size:1.6rem;font-weight:700;font-family:Fraunces,serif;color:var(--text)">{promedio} kcal</div>'
            f'</div>'
            f'<div>'
            f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">DÍAS EN OBJETIVO</div>'
            f'  <div style="font-size:1.6rem;font-weight:700;font-family:Fraunces,serif;color:var(--accent2)">{dias_ok}/{len(vals)}</div>'
            f'</div>'
            f'<div>'
            f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">DÍA MÁXIMO</div>'
            f'  <div style="font-size:1.6rem;font-weight:700;font-family:Fraunces,serif;color:var(--red)">{max(vals)} kcal</div>'
            f'</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        if hist_m:
            pv = [v["prot"]  for v in hist_m.values()]
            cv = [v["carb"]  for v in hist_m.values()]
            gv = [v["grasa"] for v in hist_m.values()]
            if pv:
                st.markdown(
                    f'<div class="card">'
                    f'<div class="card-label">Macros promedio diario</div>'
                    f'<span class="badge badge-prot">P {round(sum(pv)/len(pv),1)}g</span>'
                    f'<span class="badge badge-carb">C {round(sum(cv)/len(cv),1)}g</span>'
                    f'<span class="badge badge-fat">G {round(sum(gv)/len(gv),1)}g</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        reg_h = st.session_state.datos.get("registro_entreno", {})
        if reg_h:
            tot_ses = sum(len(v) for v in reg_h.values())
            tot_min = sum(s["duracion"] for v in reg_h.values() for s in v)
            st.markdown(
                f'<div class="card">'
                f'<div class="card-label">Entrenamientos</div>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem">'
                f'<div>'
                f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">SESIONES TOTALES</div>'
                f'  <div style="font-size:1.6rem;font-weight:700;font-family:Fraunces,serif;color:var(--text)">{tot_ses}</div>'
                f'</div>'
                f'<div>'
                f'  <div style="font-size:.7rem;color:var(--text3);font-family:DM Mono,monospace;letter-spacing:.08em">TIEMPO TOTAL</div>'
                f'  <div style="font-size:1.6rem;font-weight:700;font-family:Fraunces,serif;color:var(--text)">{tot_min} min</div>'
                f'  <div style="font-size:.72rem;color:var(--text3)">{round(tot_min/60,1)} horas</div>'
                f'</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        if st.button("Borrar historial completo", key="btn_del_hist"):
            d = st.session_state.datos
            d["historial_calorias"] = {}
            d["historial_macros"]   = {}
            d["diario_comidas"]     = {}
            guardar_datos(d)
            st.success("Historial borrado.")
            st.rerun()


# ══════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════
with t_cfg:
    st.markdown('<div style="margin-bottom:.75rem"></div>', unsafe_allow_html=True)

    sdiv("API Key de Google AI Studio")
    st.markdown(
        '<div class="card">'
        '<p style="margin-bottom:.4rem">Obtén tu clave gratuita en <b style="color:var(--text)">aistudio.google.com</b> → "Crear clave de API".</p>'
        '<p style="font-size:.78rem;color:var(--text3)">Necesaria para el Scanner IA y el Dietista IA.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    api_in = st.text_input(
        "API Key", type="password",
        value=st.session_state.gemini_key,
        placeholder="AIzaSy...",
        label_visibility="collapsed"
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Guardar clave", key="btn_sk"):
            if api_in.strip():
                st.session_state.gemini_key = api_in.strip()
                st.success("✓ Clave guardada.")
            else:
                st.warning("Introduce una clave válida.")
    with c2:
        if st.session_state.gemini_key:
            if st.button("Probar conexión", key="btn_test"):
                with st.spinner("Probando..."):
                    try:
                        genai.configure(api_key=st.session_state.gemini_key)
                        m = genai.GenerativeModel("gemini-2.0-flash")
                        r = m.generate_content("Responde solo la palabra: OK")
                        st.success(f"✓ Conexión exitosa · {r.text.strip()}")
                    except Exception as e:
                        st.error(f"✗ {e}")

    sdiv("Perfil personal")
    pf3 = get_perfil()
    c1, c2 = st.columns(2)
    with c1:
        p_n  = st.text_input("Nombre",        value=pf3.get("nombre",""),                    placeholder="Tu nombre")
        p_p  = st.number_input("Peso (kg)",   30.0, 250.0, float(pf3.get("peso",70)),   0.5)
        p_a  = st.number_input("Altura (cm)", 100,  250,   int(pf3.get("altura",170)))
        p_e  = st.number_input("Edad",        10,   100,   int(pf3.get("edad",25)))
    with c2:
        p_oc = st.number_input("Objetivo kcal/día", 1000, 6000, int(pf3.get("objetivo_cal",2000)), 50)
        p_op = st.number_input("Proteína obj. (g)", 50,   400,  int(pf3.get("obj_prot",150)),       5)
        p_ocb= st.number_input("Carbos obj. (g)",   50,   800,  int(pf3.get("obj_carb",220)),        5)
        p_og = st.number_input("Grasas obj. (g)",   20,   300,  int(pf3.get("obj_grasa",60)),        5)

    if st.button("Guardar perfil →", key="btn_sp"):
        st.session_state.datos["perfil"] = {
            "nombre":      p_n,
            "peso":        p_p,
            "altura":      p_a,
            "edad":        p_e,
            "objetivo_cal": p_oc,
            "obj_prot":    p_op,
            "obj_carb":    p_ocb,
            "obj_grasa":   p_og,
        }
        guardar_datos(st.session_state.datos)
        st.success("✓ Perfil guardado.")
        st.rerun()

    sdiv("Acerca de")
    st.markdown(
        '<div class="card">'
        '<p style="font-weight:600;color:var(--text);margin-bottom:.3rem">FitAI Pro v4.0</p>'
        '<p>Streamlit + Google Gemini 2.0 Flash</p>'
        '<p style="color:var(--text3);margin-top:.3rem;font-size:.78rem">'
        'Datos guardados localmente en <code>fitai_data.json</code></p>'
        '</div>',
        unsafe_allow_html=True,
    )
