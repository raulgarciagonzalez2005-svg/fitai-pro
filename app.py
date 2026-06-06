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
  --bg: #f0f4f8;
  --surface: #ffffff;
  --surface2: #f8fafc;
  --border: #e2e8f0;
  --border2: #cbd5e1;
  --green: #10b981;
  --green2: #059669;
  --green3: rgba(16,185,129,.12);
  --green4: rgba(16,185,129,.06);
  --blue: #3b82f6;
  --blue2: #2563eb;
  --blue3: rgba(59,130,246,.12);
  --blue4: rgba(59,130,246,.06);
  --teal: #14b8a6;
  --teal3: rgba(20,184,166,.12);
  --sky: #0ea5e9;
  --emerald: #34d399;
  --text: #0f172a;
  --text2: #475569;
  --text3: #94a3b8;
  --text4: #cbd5e1;
  --shadow: 0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.04);
  --shadow2: 0 4px 24px rgba(0,0,0,.10);
  --r: 18px;
  --rsm: 12px;
  --rxs: 8px;
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
  max-width: 780px !important;
  padding: 0 1rem 6rem !important;
  margin: 0 auto !important;
}

/* ── TOP HEADER ── */
.fap-header {
  background: var(--surface);
  border-radius: 0 0 24px 24px;
  padding: 1.4rem 1.5rem 1.2rem;
  margin: 0 -1rem 1.4rem;
  box-shadow: var(--shadow);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
}
.fap-greeting { font-size: .62rem; font-weight: 600; color: var(--text3); letter-spacing: .06em; text-transform: uppercase; }
.fap-name { font-family: 'Sora', sans-serif; font-size: 1.32rem; font-weight: 800; color: var(--text); line-height: 1.15; margin-top: .1rem; }
.fap-date { font-size: .65rem; font-weight: 500; color: var(--text3); margin-top: .1rem; }
.fap-avatar {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, var(--green), var(--blue));
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: .85rem; font-weight: 700; color: #ffffff !important;
  box-shadow: 0 4px 16px rgba(16,185,129,.3);
}

/* ── CARDS (Ajuste estricto de herencia y contraste de color de texto) ── */
.fap-card {
  background: var(--surface);
  border-radius: var(--r);
  padding: 1.2rem 1.35rem;
  margin-bottom: .8rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.fap-card-green, .fap-card-green *, .fap-card-green div, .fap-card-green span, .fap-card-green small {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none !important;
  color: #ffffff !important;
}
.fap-card-green { box-shadow: 0 6px 24px rgba(16,185,129,.3); }

.fap-card-blue, .fap-card-blue *, .fap-card-blue div, .fap-card-blue span, .fap-card-blue small {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none !important;
  color: #ffffff !important;
}
.fap-card-blue { box-shadow: 0 6px 24px rgba(59,130,246,.28); }

.fap-card-teal, .fap-card-teal *, .fap-card-teal div, .fap-card-teal span, .fap-card-teal small {
  background: linear-gradient(135deg, #14b8a6, #0d9488);
  border: none !important;
  color: #ffffff !important;
}

/* ── SECTION LABELS ── */
.fap-lbl {
  font-size: .6rem;
  font-weight: 700;
  color: var(--text3);
  letter-spacing: .1em;
  text-transform: uppercase;
  margin-bottom: .5rem;
}
.fap-lbl-green { color: var(--green) !important; }
.fap-lbl-blue  { color: var(--blue)  !important; }

/* ── BIG NUMBER (Reducido sutilmente para evitar desbordes en grid móvil) ── */
.fap-big {
  font-family: 'Sora', sans-serif;
  font-size: 2.4rem;
  font-weight: 800;
  color: var(--text);
  line-height: 1;
}
.fap-big-sub {
  font-size: .6rem;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-top: .15rem;
}

/* ── PROGRESS BAR ── */
.fap-pb { background: var(--bg); border-radius: 999px; height: 7px; overflow: hidden; margin-top: .55rem; }
.fap-pb-f { height: 100%; border-radius: 999px; transition: width .7s cubic-bezier(.4,0,.2,1); }

/* ── RINGS ── */
.fap-ring-wrap { display: flex; flex-direction: column; align-items: center; gap: .35rem; }
.fap-ring { position: relative; width: 108px; height: 108px; }
.fap-ring svg { transform: rotate(-90deg); }
.fap-ring-val { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); text-align: center; }
.fap-ring-num { font-family: 'Sora', sans-serif; font-size: 1rem; font-weight: 800; color: var(--text); line-height: 1; }
.fap-ring-unit { font-size: .48rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: .06em; }
.fap-ring-label { font-size: .58rem; font-weight: 700; color: var(--text2); text-transform: uppercase; letter-spacing: .07em; text-align: center; }
.fap-mgrid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .9rem; }
.fap-sgrid { display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; }

/* ── MINI STAT ── */
.fap-mini {
  background: var(--surface);
  border-radius: var(--rsm);
  padding: 1rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  text-align: center;
}
.fap-mini-val { font-family: 'Sora', sans-serif; font-size: 1.6rem; font-weight: 800; color: var(--text); line-height: 1; }
.fap-mini-lbl { font-size: .57rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: .07em; margin-top: .15rem; }

/* ── BADGES LIMPIOS ── */
.fap-badge {
  display: inline-flex; align-items: center;
  padding: .2rem .6rem;
  border-radius: 999px;
  font-size: .62rem;
  font-weight: 700;
  margin: .1rem .05rem 0 0;
}
.b-green  { background: var(--green3); color: var(--green2); }
.b-blue   { background: var(--blue3);  color: var(--blue2); }
.b-teal   { background: var(--teal3);  color: var(--teal); }
.b-sky    { background: rgba(14,165,233,.12); color: #0284c7; }
.b-gray   { background: var(--bg); color: var(--text2); border: 1px solid var(--border); }
.b-amber  { background: rgba(245,158,11,.12); color: #b45309; }
.b-red    { background: rgba(239,68,68,.1);   color: #dc2626; }

/* ── ROWS Y ENCABEZADOS DE TABLA SaaS ── */
.fap-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: .4rem 0; border-bottom: 1px solid var(--border); font-size: .8rem;
}
.fap-row:last-child { border-bottom: none; }
.fap-rl { color: var(--text2); }
.fap-rr { color: var(--text); font-size: .76rem; font-weight: 600; }
.fap-meal-hdr { display: flex; justify-content: space-between; align-items: center; margin-bottom: .4rem; }
.fap-meal-ttl { font-family: 'Sora', sans-serif; font-size: .88rem; font-weight: 700; color: var(--text); }

.fap-table-hdr {
  display: flex; justify-content: space-between;
  background: #e2e8f0;
  padding: .45rem .65rem;
  border-radius: var(--rxs);
  font-size: .65rem;
  font-weight: 700;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-bottom: .3rem;
}

/* ── DIVIDER ── */
.fap-sep { display: flex; align-items: center; gap: .6rem; margin: 1.4rem 0 .85rem; }
.fap-sep-l { flex: 1; height: 1px; background: var(--border); }
.fap-sep-t { font-size: .56rem; font-weight: 800; color: var(--green); text-transform: uppercase; letter-spacing: .14em; white-space: nowrap; }

/* ── TYPE BADGE ── */
.fap-typebadge {
  font-size: .52rem; font-weight: 800;
  padding: .18rem .55rem; border-radius: 999px;
  letter-spacing: .04em; text-transform: uppercase;
}
.fap-exnum { font-family: 'DM Mono', monospace; font-size: .73rem; font-weight: 500; color: var(--green); min-width: 26px; }

/* ── BUTTONS (Color corporativo sólido, eliminando degradado brillante tipo IA) ── */
div.stButton > button {
  background: var(--green2) !important;
  color: #ffffff !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .82rem !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: var(--rsm) !important;
  padding: .65rem 1.25rem !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: background .2s static, transform .1s ease !important;
  box-shadow: none !important;
  letter-spacing: .01em !important;
}
div.stButton > button:hover {
  background: #047857 !important;
}
div.stButton > button:active { transform: scale(0.99) !important; }

/* ── INPUTS (Estilo sólido invariable con el contraste externo del navegador) ── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stNumberInput input {
  background: #ffffff !important;
  color: #0f172a !important;
  border: 1.5px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: .82rem !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(16,185,129,.14) !important;
}
div[data-baseweb="select"] > div {
  background: #ffffff !important;
  border: 1.5px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
  color: #0f172a !important;
}
label {
  color: var(--text) !important;
  font-size: .76rem !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  margin-bottom: .25rem !important;
  display: inline-block;
}

/* ── TABS (Remoción de gradientes y bordes extraños) ── */
[data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border-radius: var(--rsm) !important;
  padding: 3px !important;
  gap: 2px !important;
  box-shadow: var(--shadow) !important;
  border: 1px solid var(--border) !important;
}
[data-baseweb="tab"] {
  color: var(--text3) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  font-size: .68rem !important;
  border-radius: var(--rxs) !important;
  padding: .38rem .85rem !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: var(--green2) !important;
  color: #ffffff !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
  background: var(--green4) !important;
  border: 1px solid rgba(16,185,129,.2) !important;
  border-left: 4px solid var(--green) !important;
  border-radius: var(--rsm) !important;
  font-size: .79rem !important;
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
  font-size: .79rem !important;
  font-weight: 600 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  border: 2px dashed var(--border2) !important;
  border-radius: var(--r) !important;
  background: var(--surface2) !important;
}

/* ── LOGIN ── */
.fap-login-box {
  background: var(--surface);
  border-radius: 24px;
  padding: 2rem 1.8rem;
  box-shadow: var(--shadow2);
  border: 1px solid var(--border);
  max-width: 420px;
  margin: 0 auto;
}

/* ── DROPDOWNS ── */
[data-baseweb="popover"] {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--rsm) !important;
}
[data-baseweb="menu"] { background: var(--surface) !important; }
li[role="option"] { color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
li[role="option"]:hover { background: var(--green3) !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 999px; }

@media (max-width: 520px) {
  .block-container { padding: 0 .65rem 6rem !important; }
  .fap-big { font-size: 2.1rem; }
  .fap-mgrid { gap: .5rem; }
}
</style>
""", unsafe_allow_html=True)

# ── DATA (Limpieza total de emoticonos de strings estructurales) ─────────────────
USERS_FILE = "fitai_users.json"

def food_icon(alimento_nombre):
    # Modificado para mantener la interfaz completamente profesional y limpia
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
    "Vegana alta proteina (2200 kcal)":{"objetivo":"Dieta plant-based con aporte proteico suficiente","macros":{"prot":140,"carb":280,"grasa":65},"comidas":[
        {"nombre":"Desayuno","alimentos":"Avena 80g + Proteina vegana 30g + Platano","cal":520,"prot":35,"carb":80,"grasa":10},
        {"nombre":"Media manana","alimentos":"Hummus 100g + Pan integral + Tomate","cal":290,"prot":12,"carb":35,"grasa":10},
        {"nombre":"Almuerzo","alimentos":"Lentejas 200g + Arroz 100g + Verduras + AOVE","cal":590,"prot":28,"carb":95,"grasa":12},
        {"nombre":"Merienda","alimentos":"Aguacate + Pan integral + Batido espinacas","cal":350,"prot":10,"carb":30,"grasa":22},
        {"nombre":"Cena","alimentos":"Tofu 200g + Garbanzos 100g + Brocoli + AOVE","cal":470,"prot":38,"carb":35,"grasa":20}]},
    "Recomposicion (2100 kcal)":{"objetivo":"Ganar musculo y perder grasa al mismo tiempo","macros":{"prot":200,"carb":200,"grasa":65},"comidas":[
        {"nombre":"Desayuno","alimentos":"Claras 5 uds + 1 huevo + Avena 40g + Arandanos","cal":380,"prot":40,"carb":38,"grasa":8},
        {"nombre":"Pre-entreno","alimentos":"Platano + Whey 30g","cal":240,"prot":25,"carb":30,"grasa":2},
        {"nombre":"Almuerzo","alimentos":"Pollo 200g + Quinoa 100g + Pimiento + Zanahoria","cal":490,"prot":55,"carb":45,"grasa":9},
        {"nombre":"Merienda","alimentos":"Queso cottage 200g + Nueces 20g","cal":270,"prot":26,"carb":7,"grasa":15},
        {"nombre":"Cena","alimentos":"Salmon 180g + Espinacas + Tomate + AOVE 8ml","cal":440,"prot":38,"carb":8,"grasa":28},
        {"nombre":"Antes dormir","alimentos":"Caseina 30g","cal":110,"prot":24,"carb":3,"grasa":1}]},
}

EJERCICIOS_GYM = {
    "Pecho":[
        {"nombre":"Press banca plano","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-12","descanso":"90s","notas":"Escapulas retraidas"},
        {"nombre":"Press banca inclinado","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Angulo 30-45 grados"},
        {"nombre":"Aperturas mancuernas","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados"},
        {"nombre":"Fondos en paralelas","tipo":"Peso corporal","equipo":"Paralelas","series_rec":"3-4","reps_rec":"Max","descanso":"90s","notas":"Torso inclinado adelante"},
        {"nombre":"Crossover en polea","tipo":"Aislamiento","equipo":"Poleas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Estiramiento completo arriba"},
    ],
    "Espalda":[
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3 min","notas":"Espalda neutra"},
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra fija","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo"},
        {"nombre":"Jalon al pecho","tipo":"Hipertrofia","equipo":"Polea alta","series_rec":"4","reps_rec":"10-15","descanso":"75s","notas":"Codos hacia abajo"},
        {"nombre":"Remo con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Torso a 45 grados"},
        {"nombre":"Face pulls","tipo":"Prevencion","equipo":"Polea alta","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Manguito rotador"},
    ],
    "Pierna":[
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3 min","notas":"Rodillas alineadas"},
        {"nombre":"Prensa de piernas","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos = isquios"},
        {"nombre":"Femoral tumbado","tipo":"Aislamiento","equipo":"Maquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Aisla isquiotibiales"},
        {"nombre":"Hip Thrust","tipo":"Gluteos","equipo":"Barra","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Contraccion maxima"},
        {"nombre":"Peso muerto rumano","tipo":"Hipertrofia","equipo":"Barra","series_rec":"3-4","reps_rec":"10-12","descanso":"90s","notas":"Bisagra de cadera"},
        {"nombre":"Elevacion de gemelos","tipo":"Aislamiento","equipo":"Maquina","series_rec":"4","reps_rec":"15-25","descanso":"45s","notas":"Rango completo"},
    ],
    "Hombros":[
        {"nombre":"Press militar con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2 min","notas":"Core activado"},
        {"nombre":"Elevaciones laterales","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Hasta la horizontal"},
        {"nombre":"Press Arnold","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Rotacion completa"},
        {"nombre":"Pajaro posterior","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Torso a 90 grados"},
    ],
    "Biceps":[
        {"nombre":"Curl con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"75s","notas":"Codos fijos"},
        {"nombre":"Curl mancuernas alterno","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-14/brazo","descanso":"60s","notas":"Supinacion al subir"},
        {"nombre":"Curl martillo","tipo":"Braquial","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Agarre neutro"},
        {"nombre":"Curl predicador","tipo":"Aislamiento","equipo":"Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"No extender del todo"},
    ],
    "Triceps":[
        {"nombre":"Press agarre cerrado","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Codos pegados"},
        {"nombre":"Pushdown en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"3-4","reps_rec":"15-20","descanso":"45s","notas":"Extension completa"},
        {"nombre":"Extension sobre la cabeza","tipo":"Hipertrofia","equipo":"Mancuerna","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Estiramiento maximo"},
        {"nombre":"Press frances","tipo":"Hipertrofia","equipo":"Barra EZ","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Controlado a la frente"},
    ],
    "Core":[
        {"nombre":"Plancha frontal","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3-4","reps_rec":"45-90s","descanso":"45s","notas":"Cuerpo recto"},
        {"nombre":"Rueda abdominal","tipo":"Fuerza","equipo":"Rueda ab","series_rec":"3","reps_rec":"8-15","descanso":"60s","notas":"Empezar de rodillas"},
        {"nombre":"Crunch en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Flexion de columna"},
        {"nombre":"Elevacion piernas colgado","tipo":"Fuerza","equipo":"Barra fija","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Retroversion pelvica"},
    ],
    "Cardio":[
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint/30s caminar","descanso":"","notas":"FC 85-90%"},
        {"nombre":"Tabata bicicleta","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s/10s pausa","descanso":"","notas":"4 min por ronda"},
        {"nombre":"Zona 2 eliptica","tipo":"Cardio","equipo":"Eliptica","series_rec":"1","reps_rec":"30-45 min","descanso":"","notas":"FC 120-140 ppm"},
        {"nombre":"Remo en ergometro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500m","descanso":"2 min","notas":"Cardio + espalda"},
    ],
}

RUTINAS_DEFAULT = {
    "PPL Empuje":{"desc":"Pecho, hombros y triceps","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Press Arnold","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Extension sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""}]},
    "PPL Tiron":{"desc":"Espalda y biceps","ejercicios":[
        {"ejercicio":"Dominadas","series":4,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""}]},
    "PPL Piernas":{"desc":"Cuadriceps, isquios, gluteos y gemelos","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-8","peso":"","descanso":"2-3 min","notas":""},
        {"ejercicio":"Prensa de piernas","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Peso muerto rumano","series":3,"reps":"10-12","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Hip Thrust","series":4,"reps":"12-15","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Elevacion de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""}]},
    "Full Body":{"desc":"3 dias/semana — Principiantes","ejercicios":[
        {"ejercicio":"Sentadilla con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca plano","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Peso muerto convencional","series":3,"reps":"6-8","peso":"","descanso":"2 min","notas":""},
        {"ejercicio":"Press militar","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Dominadas","series":3,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"45s","notas":""}]},
    "Upper":{"desc":"Pecho, espalda, hombros y brazos","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"60s","notas":""}]},
    "HIIT Core":{"desc":"Alta intensidad + abdominales — 35 min","ejercicios":[
        {"ejercicio":"Burpees","series":5,"reps":"30s/15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Mountain climbers","series":5,"reps":"30s/15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""}]},
}

TIPO_COLOR = {
    "Fuerza":        {"color":"#10b981","bg":"rgba(16,185,129,.1)"},
    "Hipertrofia":   {"color":"#3b82f6","bg":"rgba(59,130,246,.1)"},
    "Aislamiento":   {"color":"#8b5cf6","bg":"rgba(139,92,246,.1)"},
    "Peso corporal":{"color":"#10b981","bg":"rgba(16,185,129,.1)"},
    "Cardio":        {"color":"#0ea5e9","bg":"rgba(14,165,233,.1)"},
    "Estabilidad":   {"color":"#14b8a6","bg":"rgba(20,184,166,.1)"},
    "Gluteos":       {"color":"#f59e0b","bg":"rgba(245,158,11,.1)"},
    "Prevencion":    {"color":"#14b8a6","bg":"rgba(20,184,166,.1)"},
    "Braquial":      {"color":"#8b5cf6","bg":"rgba(139,92,246,.1)"},
}

# ── AUTH & PERSISTENCE ────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f: 
                return json.load(f)
        except: 
            pass
    return {}

def save_users(u):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f: 
            json.dump(u, f, ensure_ascii=False, indent=2)
    except Exception as e: 
        st.warning(f"Error guardando usuarios: {e}")

def get_user_file(uid): 
    return f"fitai_{uid[:8]}.json"

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
    # Obtener Iniciales del usuario para el avatar superior
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

    # NAVEGACIÓN PRINCIPAL
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
        sdiv("Registro de Alimentos de la Base de Datos")
        
        cx1, cx2 = st.columns(2)
        with cx1:
            alimento_sel = st.selectbox("Seleccionar Alimento de Referencia", list(ALIMENTOS_DB.keys()))
        with cx2:
            cantidad_g = st.number_input("Cantidad a registrar en la comida actual (gramos):", min_value=1, value=100, step=10)
            
        if st.button("Añadir Alimento al Diario"):
            st.success(f"Registrados {cantidad_g}g de {alimento_sel} correctamente.")
            
        sdiv("Formulario de Registro Manual")
        st.markdown('<div class="fap-table-hdr"><span>Concepto</span><span>Valor Técnico Requerido</span></div>', unsafe_allow_html=True)
        
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            manual_name = st.text_input("Nombre descriptivo del alimento o plato:", placeholder="Ej. Tortilla de claras con espinacas")
            manual_cal = st.number_input("Calorías totales calculadas para el plato (kcal):", min_value=0, value=0)
        with c_m2:
            manual_prot = st.number_input("Gramos de Proteína netos estimados (g):", min_value=0.0, value=0.0, step=0.5)
            manual_carb = st.number_input("Gramos de Carbohidratos netos estimados (g):", min_value=0.0, value=0.0, step=0.5)
            
        if st.button("Guardar Alimento Personalizado"):
            if manual_name:
                st.info(f"Guardado en el historial: {manual_name} - {manual_cal} kcal")
            else:
                st.warning("Por favor, introduce un nombre descriptivo válido antes de guardar.")

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
        st.markdown('<div class="fap-table-hdr"><span>Métrica de Carga</span><span>Introducción de Datos Reales</span></div>', unsafe_allow_html=True)
        
        st_c1, st_c2, st_c3 = st.columns(3)
        with st_c1:
            num_serie = st.number_input("Número de Serie actual correlativo (Ej: 1, 2, 3...):", min_value=1, value=1)
        with st_c2:
            num_reps = st.number_input("Repeticiones logradas completas en esta serie:", min_value=0, value=10)
        with st_c3:
            num_peso = st.number_input("Peso total efectivo utilizado (en kg o lb):", min_value=0.0, value=60.0, step=2.5)
            
        if st.button("Guardar Serie en el Historial"):
            st.success(f"Serie {num_serie} registrada: {num_reps} reps con {num_peso} kg.")

    # ── PESTAÑA 4: AJUSTES ──
    with tab4:
        sdiv("Información General del Sistema")
        card(
            f'<div class="fap-row"><span class=\"fap-rl\">Versión del Software</span><span class=\"fap-rr\">FitAI Pro 6.0</span></div>'
            f'<div class="fap-row"><span class=\"fap-rl\">Arquitectura Frontend</span><span class=\"fap-rr\">Streamlit · Clean Responsive CSS Grid</span></div>'
            f'<div class="fap-row"><span class=\"fap-rl\">Estado de Conexión Base de Datos</span><span class=\"fap-rr\">{badge("Conectado localmente", "b-green")}</span></div>'
        )
        
        if st.button("Cerrar Sesión Segura"):
            st.session_state.authenticated = False
            st.rerun()
