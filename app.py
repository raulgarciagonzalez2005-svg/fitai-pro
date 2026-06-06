import streamlit as st
import json, os, re, base64, io, hashlib, uuid, requests
from datetime import date, datetime
from PIL import Image

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

st.set_page_config(page_title="FitAI Pro", page_icon="📊",
                   layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Sora:wght@400;600;700;800&display=swap');

:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface2: #f1f5f9;
  --border: #e2e8f0;
  --border2: #cbd5e1;
  --green: #10b981;
  --green2: #059669;
  --green3: rgba(16,185,129,.10);
  --green4: rgba(16,185,129,.05);
  --blue: #3b82f6;
  --blue2: #2563eb;
  --blue3: rgba(59,130,246,.10);
  --blue4: rgba(59,130,246,.05);
  --teal: #14b8a6;
  --teal3: rgba(20,184,166,.10);
  --sky: #0ea5e9;
  --emerald: #34d399;
  --text: #0f172a;
  --text2: #475569;
  --text3: #64748b;
  --text4: #94a3b8;
  --shadow: 0 1px 3px rgba(0,0,0,.05), 0 4px 12px rgba(0,0,0,.03);
  --shadow2: 0 10px 30px rgba(15,23,42,.08);
  --r: 16px;
  --rsm: 12px;
  --rxs: 6px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
  max-width: 840px !important;
  padding: 0 1.5rem 6rem !important;
  margin: 0 auto !important;
}

/* ── TOP HEADER ── */
.fap-header {
  background: var(--surface);
  border-radius: 0 0 20px 20px;
  padding: 1.5rem;
  margin: 0 -1.5rem 1.5rem;
  box-shadow: var(--shadow);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
}
.fap-greeting { font-size: .65rem; font-weight: 700; color: var(--text4); letter-spacing: .08em; text-transform: uppercase; }
.fap-name { font-family: 'Sora', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--text); line-height: 1.2; margin-top: .15rem; }
.fap-date { font-size: .7rem; font-weight: 500; color: var(--text3); margin-top: .2rem; }
.fap-avatar {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, var(--green), var(--blue));
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: .85rem; font-weight: 700; color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(16,185,129,.2);
}

/* ── CARDS (Fuerzan texto blanco y alta visibilidad) ── */
.fap-card {
  background: var(--surface);
  border-radius: var(--r);
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.fap-card-green, .fap-card-green *, .fap-card-green div, .fap-card-green span {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none !important;
  color: #ffffff !important;
}
.fap-card-green { box-shadow: 0 6px 20px rgba(16,185,129,.2); }

.fap-card-blue, .fap-card-blue *, .fap-card-blue div, .fap-card-blue span {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none !important;
  color: #ffffff !important;
}
.fap-card-blue { box-shadow: 0 6px 20px rgba(59,130,246,.18); }

.fap-card-teal, .fap-card-teal *, .fap-card-teal div, .fap-card-teal span {
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  border: none !important;
  color: #ffffff !important;
}

/* ── SECTION LABELS ── */
.fap-lbl {
  font-size: .65rem;
  font-weight: 700;
  color: var(--text3);
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: .6rem;
}
.fap-lbl-green { color: var(--green) !important; }
.fap-lbl-blue  { color: var(--blue)  !important; }

/* ── BIG NUMBER (Escalado para evitar roturas) ── */
.fap-big {
  font-family: 'Sora', sans-serif;
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text);
  line-height: 1.1;
}
.fap-big-sub {
  font-size: .65rem;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-top: .2rem;
}

/* ── PROGRESS BAR ── */
.fap-pb { background: var(--surface2); border-radius: 999px; height: 8px; overflow: hidden; margin-top: .6rem; }
.fap-pb-f { height: 100%; border-radius: 999px; transition: width .6s ease; }

/* ── RINGS ── */
.fap-ring-wrap { display: flex; flex-direction: column; align-items: center; gap: .4rem; }
.fap-ring { position: relative; width: 100px; height: 100px; }
.fap-ring svg { transform: rotate(-90deg); }
.fap-ring-val { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); text-align: center; }
.fap-ring-num { font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 800; color: var(--text); line-height: 1; }
.fap-ring-unit { font-size: .55rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: .05em; }
.fap-ring-label { font-size: .65rem; font-weight: 700; color: var(--text2); text-transform: uppercase; letter-spacing: .05em; text-align: center; }
.fap-mgrid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.fap-sgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

/* ── MINI STAT ── */
.fap-mini {
  background: var(--surface);
  border-radius: var(--rsm);
  padding: 1.1rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  text-align: center;
}
.fap-mini-val { font-family: 'Sora', sans-serif; font-size: 1.5rem; font-weight: 800; color: var(--text); line-height: 1; }
.fap-mini-lbl { font-size: .6rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: .06em; margin-top: .2rem; }

/* ── BADGES LIMPIOS (Sin emojis) ── */
.fap-badge {
  display: inline-flex; align-items: center;
  padding: .25rem .65rem;
  border-radius: 999px;
  font-size: .65rem;
  font-weight: 700;
  margin: .1rem .1rem 0 0;
}
.b-green  { background: var(--green3); color: var(--green2); }
.b-blue   { background: var(--blue3);  color: var(--blue2); }
.b-teal   { background: var(--teal3);  color: var(--teal); }
.b-sky    { background: rgba(14,165,233,.10); color: #0284c7; }
.b-gray   { background: var(--surface2); color: var(--text2); border: 1px solid var(--border); }
.b-amber  { background: rgba(245,158,11,.10); color: #b45309; }
.b-red    { background: rgba(239,68,68,.08);  color: #dc2626; }

/* ── ROWS Y TABLAS ── */
.fap-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .5rem 0; border-bottom: 1px solid var(--border); font-size: .82rem;
}
.fap-row:last-child { border-bottom: none; }
.fap-rl { color: var(--text2); }
.fap-rr { color: var(--text); font-size: .8rem; font-weight: 600; }
.fap-meal-hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: .5rem; }
.fap-meal-ttl { font-family: 'Sora', sans-serif; font-size: .95rem; font-weight: 700; color: var(--text); }

/* Encabezados Profesionales de Tablas */
.fap-table-hdr {
  display: flex; justify-content: space-between;
  background: var(--surface2);
  padding: .4rem .6rem;
  border-radius: var(--rxs);
  font-size: .65rem;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .05em;
  margin-bottom: .25rem;
}

/* ── DIVIDER ── */
.fap-sep { display: flex; align-items: center; gap: .7rem; margin: 1.5rem 0 1rem; }
.fap-sep-l { flex: 1; height: 1px; background: var(--border); }
.fap-sep-t { font-size: .6rem; font-weight: 800; color: var(--green); text-transform: uppercase; letter-spacing: .12em; white-space: nowrap; }

/* ── TYPE BADGE ── */
.fap-typebadge {
  font-size: .55rem; font-weight: 800;
  padding: .2rem .6rem; border-radius: 999px;
  letter-spacing: .05em; text-transform: uppercase;
}
.fap-exnum { font-family: 'DM Mono', monospace; font-size: .75rem; font-weight: 600; color: var(--green); min-width: 28px; }

/* ── BUTTONS (Color corporativo mate, sin degradado "IA") ── */
div.stButton > button {
  background: var(--green2) !important;
  color: #ffffff !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .85rem !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: var(--rsm) !important;
  padding: .7rem 1.4rem !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: background .2s static, transform .1s ease !important;
  box-shadow: none !important;
  letter-spacing: .02em !important;
}
div.stButton > button:hover {
  background: #047857 !important;
}
div.stButton > button:active { transform: scale(0.99) !important; }

/* ── INPUTS REALES (Fondo blanco e invariables al contraste externo) ── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stNumberInput input {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1.5px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .85rem !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(16,185,129,.1) !important;
}
div[data-baseweb="select"] > div {
  background: #ffffff !important;
  border: 1.5px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  color: #0f172a !important;
}
label {
  color: var(--text) !important;
  font-size: .78rem !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  margin-bottom: .2rem !important;
  display: inline-block;
}

/* ── TABS (Sin emojis) ── */
[data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border-radius: var(--rsm) !important;
  padding: 4px !important;
  gap: 4px !important;
  box-shadow: var(--shadow) !important;
  border: 1px solid var(--border) !important;
}
[data-baseweb="tab"] {
  color: var(--text3) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  font-size: .72rem !important;
  border-radius: var(--rxs) !important;
  padding: .45rem 1rem !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: var(--green2) !important;
  color: #ffffff !important;
}

/* ── ALERTS Y ELEMENTOS ADICIONALES ── */
[data-testid="stAlert"] {
  background: var(--green4) !important;
  border: 1px solid rgba(16,185,129,.15) !important;
  border-left: 4px solid var(--green) !important;
  border-radius: var(--rsm) !important;
  font-size: .8rem !important;
  color: var(--green2) !important;
}
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--rsm) !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="stExpander"] summary {
  color: var(--text2) !important;
  font-size: .82rem !important;
  font-weight: 700 !important;
}

.fap-login-box {
  background: var(--surface);
  border-radius: 20px;
  padding: 2.2rem 2rem;
  box-shadow: var(--shadow2);
  border: 1px solid var(--border);
  max-width: 420px;
  margin: 2rem auto;
}

[data-baseweb="popover"] { background: var(--surface) !important; border: 1px solid var(--border2) !important; border-radius: var(--rsm) !important; }
[data-baseweb="menu"] { background: var(--surface) !important; }
li[role="option"] { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
li[role="option"]:hover { background: var(--green3) !important; }

@media (max-width: 520px) {
  .block-container { padding: 0 .75rem 5rem !important; }
  .fap-big { font-size: 1.9rem; }
  .fap-mgrid { gap: .6rem; }
}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
USERS_FILE = "fitai_users.json"

def food_icon(alimento_nombre):
    # Función modificada para no romper la estética seria del software profesional
    return ""

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
    "Volumen limpio (2800 kcal)":{"objetivo":"Ganar masa muscular con minima acumulacion de grasa","macros":{"prot":175,"carb":350,"grasa":75},"comidas":[
        {"nombre":"Desayuno","alimentos":"Avena 80g + Whey 30g + Platano + Leche 200ml","cal":580,"prot":42,"carb":82,"grasa":10},
        {"nombre":"Media manana","alimentos":"Yogur griego 200g + Almendras 30g + Manzana","cal":330,"prot":22,"carb":30,"grasa":16},
        {"nombre":"Almuerzo","alimentos":"Arroz integral 150g + Pollo 200g + Brocoli + AOVE 10ml","cal":720,"prot":72,"carb":85,"grasa":14},
        {"nombre":"Merienda","alimentos":"Pan integral 70g + Atun 100g + Tomate","cal":290,"prot":36,"carb":28,"grasa":3},
        {"nombre":"Cena","alimentos":"Salmon 200g + Boniato 200g + Espinacas salteadas","cal":580,"prot":45,"carb":48,"grasa":28},
        {"nombre":"Antes dormir","alimentos":"Claras 200g + Queso fresco 0% 150g","cal":220,"prot":34,"carb":7,"grasa":3}]},
    "Definicion (1900 kcal)":{"objetivo":"Reducir grasa corporal conservando la masa muscular","macros":{"prot":180,"carb":160,"grasa":60},"comidas":[
        {"nombre":"Desayuno","alimentos":"Claras 4 uds + 1 huevo + Avena 50g","cal":380,"prot":38,"carb":35,"grasa":9},
        {"nombre":"Media manana","alimentos":"Yogur griego 0% 200g + Caseina 30g","cal":250,"prot":35,"carb":10,"grasa":3},
        {"nombre":"Almuerzo","alimentos":"Pechuga pavo 200g + Patata 150g + Verduras","cal":430,"prot":62,"carb":35,"grasa":5},
        {"nombre":"Merienda","alimentos":"Atun 100g + Pan integral 35g + Pepino","cal":230,"prot":30,"carb":18,"grasa":2},
        {"nombre":"Cena","alimentos":"Merluza 200g + Brocoli + Espinacas + AOVE 5ml","cal":380,"prot":48,"carb":12,"grasa":14},
        {"nombre":"Antes dormir","alimentos":"Queso fresco 0% 150g","cal":93,"prot":17,"carb":5,"grasa":1}]},
    "Mantenimiento (2300 kcal)":{"objetivo":"Mantener composicion corporal y rendimiento","macros":{"prot":155,"carb":260,"grasa":70},"comidas":[
        {"nombre":"Desayuno","alimentos":"Avena 60g + Leche 200ml + 2 Huevos + Fruta","cal":490,"prot":28,"carb":62,"grasa":14},
        {"nombre":"Media manana","alimentos":"Fruta + Almendras 25g + Queso fresco","cal":270,"prot":14,"carb":25,"grasa":13},
        {"nombre":"Almuerzo","alimentos":"Arroz 120g + Ternera magra 150g + Ensalada + AOVE","cal":600,"prot":45,"carb":60,"grasa":18},
        {"nombre":"Merienda","alimentos":"Platano + Pan integral + Pavo 80g","cal":310,"prot":26,"carb":42,"grasa":4},
        {"nombre":"Cena","alimentos":"Salmon 150g + Garbanzos 100g + Verduras","cal":540,"prot":40,"carb":42,"grasa":21}]},
}

EJERCICIOS_GYM = {
    "Pecho":[
        {"nombre":"Press banca plano","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-12","descanso":"90s","notas":"Escapulas retraidas"},
        {"nombre":"Press banca inclinado","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Angulo 30-45 grados"},
    ],
    "Espalda":[
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3 min","notas":"Espalda neutra"},
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra fija","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo"},
    ],
    "Pierna":[
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3 min","notas":"Rodillas alineadas"},
        {"nombre":"Prensa de piernas","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos = isquios"},
    ]
}

# ── COMPONENTES UI AUXILIARES ─────────────────────────────────────────────────
def card(html_content, card_type=""):
    cls = f"fap-card fap-card-{card_type}" if card_type else "fap-card"
    st.markdown(f'<div class="{cls}">{html_content}</div>', unsafe_allow_html=True)

def badge(text, b_type="b-gray"):
    return f'<span class="fap-badge {b_type}">{text}</span>'

def sdiv(title):
    st.markdown(f'<div class="fap-sep"><div class="fap-sep-l"></div><div class="fap-sep-t">{title}</div><div class="fap-sep-l"></div></div>', unsafe_allow_html=True)

def ring(pct, num, unit, label):
    dash = int(pct * 283 / 100)
    return (
        f'<div class="fap-ring-wrap">'
        f'<div class="fap-ring">'
        f'<svg width="100" height="100" viewBox="0 0 100 100">'
        f'<circle cx="50" cy="50" r="45" stroke="#e2e8f0" stroke-width="7" fill="transparent"/>'
        f'<circle cx="50" cy="50" r="45" stroke="var(--green)" stroke-width="7" fill="transparent" '
        f'stroke-dasharray="283" stroke-dasharray="{dash} 283" stroke-linecap="round"/>'
        f'</svg>'
        f'<div class="fap-ring-val">'
        f'<div class="fap-ring-num">{num}</div>'
        f'<div class="fap-ring-unit">{unit}</div>'
        f'</div></div>'
        f'<div class="fap-ring-label">{label}</div></div>'
    )

# ── LOGICA DE CONTROL DE SESION ───────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_name" not in st.session_state:
    st.session_state.user_name = "Usuario"

# ── INTERFAZ DE LOGUEO / REGISTRO ──
if not st.session_state.authenticated:
    st.markdown('<div class="fap-login-box">', unsafe_allow_html=True)
    st.subheader("Iniciar Sesión")
    
    username = st.text_input("Nombre de Usuario", value="Entrenador", key="login_user")
    password = st.text_input("Contraseña", type="password", value="****")
    
    if st.button("Ingresar al Panel"):
        st.session_state.authenticated = True
        st.session_state.user_name = username
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Obtener Iniciales para un Avatar Limpio tipo SaaS profesional
    initials = "".join([w[0].upper() for w in st.session_state.user_name.split()[:2]]) if st.session_state.user_name else "US"
    
    # ── HEADER PRINCIPAL ──
    st.markdown(
        f'<div class="fap-header">'
        f'<div>'
        f'  <div class="fap-greeting">Panel de Control Activo</div>'
        f'  <div class="fap-name">FitAI Pro v6.0</div>'
        f'  <div class="fap-date">{datetime.now().strftime("%A, %d %B %Y")}</div>'
        f'</div>'
        f'<div class="fap-avatar">{initials}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # NAVEGACIÓN POR PESTAÑAS (Emojis removidos)
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Nutricion", "Entrenamiento", "Ajustes"])

    # ── PESTAÑA 1: DASHBOARD ──
    with tab1:
        sdiv("Métricas Diarias")
        
        c1, c2 = st.columns(2)
        with c1:
            card(
                f'<div class="fap-lbl fap-lbl-green">Estado de Energía</div>'
                f'<div class="fap-big">2,150</div>'
                f'<div class="fap-big-sub">Kcal Totales Consumidas</div>'
                f'<div class="fap-pb"><div class="fap-pb-f" style="width: 76%; background: #ffffff;"></div></div>',
                card_type="green"
            )
        with c2:
            card(
                f'<div class="fap-lbl fap-lbl-blue">Hidratación</div>'
                f'<div class="fap-big">2.4 Litros</div>'
                f'<div class="fap-big-sub">Meta Diaria: 3.0L</div>'
                f'<div class="fap-pb"><div class="fap-pb-f" style="width: 80%; background: #ffffff;"></div></div>',
                card_type="blue"
            )
            
        sdiv("Distribución de Macronutrientes")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown(ring(75, "150g", "de 200g", "Proteínas"), unsafe_allow_html=True)
        with col_r2:
            st.markdown(ring(60, "210g", "de 350g", "Carbohidratos"), unsafe_allow_html=True)
        with col_r3:
            st.markdown(ring(90, "63g", "de 70g", "Grasas"), unsafe_allow_html=True)

    # ── PESTAÑA 2: NUTRICIÓN ──
    with tab2:
        sdiv("Registro de Alimentos")
        
        # Corrección crítica: Se remueve label_visibility para que las cajas digan explícitamente qué datos van ahí
        cx1, cx2 = st.columns(2)
        with cx1:
            alimento_sel = st.selectbox("Seleccionar Alimento de la Base de Datos", list(ALIMENTOS_DB.keys()))
        with cx2:
            cantidad_g = st.number_input("Cantidad a registrar (en gramos)", min_value=1, value=100, step=10)
            
        if st.button("Añadir Alimento al Diario"):
            st.success(f"Registrados {cantidad_g}g de {alimento_sel} correctamente.")
            
        sdiv("Formulario de Registro Manual (Campos Completamente Identificados)")
        
        # Corrección crítica de campos vacíos sin explicación
        st.markdown('<div class="fap-table-hdr"><span>Concepto</span><span>Valor Técnico Requerido</span></div>', unsafe_allow_html=True)
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            manual_name = st.text_input("Nombre descriptivo del alimento o plato:", placeholder="Ej. Tortilla de claras con espinacas")
            manual_cal = st.number_input("Calorías totales del plato (kcal):", min_value=0, value=0)
        with c_m2:
            manual_prot = st.number_input("Gramos de Proteína netos (g):", min_value=0.0, value=0.0, step=0.5)
            manual_carb = st.number_input("Gramos de Carbohidratos netos (g):", min_value=0.0, value=0.0, step=0.5)
            
        if st.button("Guardar Alimento Personalizado"):
            if manual_name:
                st.info(f"Guardado: {manual_name} - {manual_cal} kcal")
            else:
                st.warning("Por favor, introduce un nombre válido antes de guardar.")

    # ── PESTAÑA 3: ENTRENAMIENTO ──
    with tab3:
        sdiv("Rutina Programada")
        grupo_sel = st.selectbox("Selecciona Grupo Muscular a entrenar hoy:", list(EJERCICIOS_GYM.keys()))
        
        st.markdown('<div class="fap-table-hdr"><span>Ejercicio</span><span>Series Recomendadas</span><span>Descanso</span></div>', unsafe_allow_html=True)
        for ex in EJERCICIOS_GYM[grupo_sel]:
            st.markdown(
                f'<div class="fap-row">'
                f'  <span><b style="color:var(--text);">{ex["nombre"]}</b> <br/><small style="color:var(--text3);">{ex["notas"]}</small></span>'
                f'  <span>{badge(ex["series_rec"] + " x " + ex["reps_rec"], "b-blue")}</span>'
                f'  <span>{badge(ex["descanso"], "b-gray")}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
        sdiv("Registro de Series Realizadas")
        # Corrección: Nombres e indicaciones explícitas de variables en la tabla
        st.markdown('<div class="fap-table-hdr"><span>Métrica de Carga</span><span>Introducción de Datos Reales</span></div>', unsafe_allow_html=True)
        
        st_c1, st_c2, st_c3 = st.columns(3)
        with st_c1:
            num_serie = st.number_input("Número de Serie actual (Ej: 1, 2, 3...)", min_value=1, value=1)
        with st_c2:
            num_reps = st.number_input("Repeticiones logradas en esta serie:", min_value=0, value=10)
        with st_c3:
            num_peso = st.number_input("Peso total levantado (en kg o lb):", min_value=0.0, value=60.0, step=2.5)
            
        if st.button("Guardar Serie en el Historial"):
            st.success(f"Serie {num_serie} registrada: {num_reps} reps con {num_peso} kg.")

    # ── PESTAÑA 4: AJUSTES DE CONFIGURACIÓN ──
    with tab4:
        sdiv("Información del Sistema de Datos")
        card(
            f'<div class="fap-row"><span class=\"fap-rl\">Versión del Software</span><span class=\"fap-rr\">FitAI Pro 6.0</span></div>'
            f'<div class="fap-row"><span class=\"fap-rl\">Arquitectura Frontend</span><span class=\"fap-rr\">Streamlit · Clean Responsive CSS Grid</span></div>'
            f'<div class="fap-row"><span class=\"fap-rl\">Estado de Conexión Base de Datos</span><span class=\"fap-rr\">{badge("Conectado localmente", "b-green")}</span></div>'
        )
        
        if st.button("Cerrar Sesión Segura"):
            st.session_state.authenticated = False
            st.rerun()
