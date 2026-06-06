import streamlit as st
import json, os, re, base64, io, hashlib, uuid, requests
from datetime import date, datetime
from PIL import Image

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

st.set_page_config(page_title="FitAI Pro", page_icon="💪",
                   layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Poppins:wght@400;500;600;700&display=swap');
:root {
  --bg:#f4f5f7; --surface:#fff; --border:#e8eaed; --border2:#d0d3d9;
  --orange:#ff6b35; --orange2:#ff8c5a; --orange3:rgba(255,107,53,.12);
  --purple:#6c5ce7; --purple2:rgba(108,92,231,.12);
  --green:#00b894; --green2:rgba(0,184,148,.12);
  --blue:#0984e3; --blue2:rgba(9,132,227,.1);
  --red:#e17055; --amber:#fdcb6e; --amber2:rgba(253,203,110,.18);
  --text:#2d3436; --text2:#636e72; --text3:#b2bec3;
  --shadow:0 2px 16px rgba(0,0,0,.07); --shadow2:0 6px 28px rgba(0,0,0,.13);
  --r:20px; --rsm:12px; --rxs:8px;
}
*,*::before,*::after{box-sizing:border-box}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{
  background:var(--bg)!important; color:var(--text)!important;
  font-family:'Poppins',sans-serif!important}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"]{display:none!important}
.block-container{max-width:800px!important;padding:0 1rem 7rem!important;margin:0 auto!important}
.top-header{background:var(--surface);border-radius:0 0 28px 28px;
  padding:1.5rem 1.4rem 1.3rem;margin:0 -1rem 1.5rem;
  box-shadow:var(--shadow);display:flex;justify-content:space-between;align-items:center}
.header-greeting{font-size:.7rem;color:var(--text3);font-weight:700;letter-spacing:.04em}
.header-name{font-family:'Nunito',sans-serif;font-size:1.4rem;font-weight:900;color:var(--text);line-height:1.1}
.header-avatar{width:46px;height:46px;
  background:linear-gradient(135deg,var(--orange),var(--purple));
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:1.3rem;box-shadow:0 4px 16px rgba(255,107,53,.35)}
.card{background:var(--surface);border-radius:var(--r);padding:1.25rem 1.35rem;
  margin-bottom:.85rem;box-shadow:var(--shadow);border:1px solid var(--border);transition:box-shadow .2s}
.card:hover{box-shadow:var(--shadow2)}
.card-orange{background:linear-gradient(135deg,#ff6b35,#ff8c5a);border:none;color:#fff;
  box-shadow:0 6px 24px rgba(255,107,53,.35)}
.card-purple{background:linear-gradient(135deg,#6c5ce7,#a29bfe);border:none;color:#fff}
.lbl{font-size:.62rem;font-weight:700;color:var(--text3);letter-spacing:.1em;
  text-transform:uppercase;margin-bottom:.5rem}
.lbl-orange{color:var(--orange)!important}
.big{font-family:'Nunito',sans-serif;font-size:2.9rem;font-weight:900;line-height:1;color:var(--text)}
.big-sub{font-size:.62rem;color:var(--text3);font-weight:700;margin-top:.2rem;
  text-transform:uppercase;letter-spacing:.07em}
.ring-wrap{display:flex;flex-direction:column;align-items:center;gap:.4rem}
.ring{position:relative;width:110px;height:110px}
.ring svg{transform:rotate(-90deg)}
.ring-val{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center}
.ring-num{font-family:'Nunito',sans-serif;font-size:1.05rem;font-weight:900;color:var(--text);line-height:1}
.ring-unit{font-size:.5rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.06em}
.ring-label{font-size:.6rem;font-weight:700;color:var(--text2);text-transform:uppercase;
  letter-spacing:.07em;text-align:center}
.pb{background:var(--bg);border-radius:999px;height:8px;overflow:hidden;margin-top:.55rem}
.pb-f{height:100%;border-radius:999px;transition:width .7s cubic-bezier(.4,0,.2,1)}
.mgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}
.sgrid{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.mini-stat{background:var(--surface);border-radius:var(--rsm);padding:1rem;
  box-shadow:var(--shadow);border:1px solid var(--border);text-align:center}
.mini-val{font-family:'Nunito',sans-serif;font-size:1.65rem;font-weight:900;color:var(--text);line-height:1}
.mini-lbl{font-size:.58rem;font-weight:700;color:var(--text3);text-transform:uppercase;
  letter-spacing:.07em;margin-top:.15rem}
.badge{display:inline-flex;align-items:center;padding:.22rem .65rem;border-radius:999px;
  font-size:.63rem;font-weight:700;margin:.1rem .05rem 0 0}
.bk,.b-orange{background:var(--orange3);color:var(--orange)}
.bp,.b-green{background:var(--green2);color:var(--green)}
.bc,.b-purple{background:var(--purple2);color:var(--purple)}
.bf,.b-amber{background:var(--amber2);color:#b7860b}
.bn,.b-gray{background:var(--bg);color:var(--text2);border:1px solid var(--border)}
.bw,.b-red{background:rgba(225,112,85,.12);color:var(--red)}
.b-blue{background:var(--blue2);color:var(--blue)}
.row{display:flex;justify-content:space-between;align-items:center;
  padding:.4rem 0;border-bottom:1px solid var(--border);font-size:.81rem}
.row:last-child{border-bottom:none}
.rl{color:var(--text2)} .rr{color:var(--text);font-size:.77rem;font-weight:600}
.meal-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:.45rem}
.meal-title{font-family:'Nunito',sans-serif;font-size:.9rem;font-weight:900;color:var(--text)}
.sep{display:flex;align-items:center;gap:.65rem;margin:1.5rem 0 .9rem}
.sep-l{flex:1;height:2px;background:var(--bg);border-radius:999px}
.sep-t{font-size:.58rem;font-weight:800;color:var(--orange);text-transform:uppercase;
  letter-spacing:.14em;white-space:nowrap}
.typebadge{font-size:.54rem;font-weight:800;padding:.2rem .58rem;border-radius:999px;
  letter-spacing:.05em;text-transform:uppercase}
.ex-num{font-family:'Nunito',sans-serif;font-size:.75rem;font-weight:900;
  color:var(--orange);min-width:26px}
div.stButton>button{
  background:linear-gradient(135deg,var(--orange),var(--orange2))!important;
  color:#fff!important;font-family:'Poppins',sans-serif!important;
  font-size:.83rem!important;font-weight:700!important;border:none!important;
  border-radius:var(--rsm)!important;padding:.68rem 1.3rem!important;width:100%!important;
  cursor:pointer!important;transition:all .2s!important;
  box-shadow:0 4px 16px rgba(255,107,53,.3)!important;letter-spacing:.01em!important}
div.stButton>button:hover{box-shadow:0 6px 24px rgba(255,107,53,.5)!important;
  transform:translateY(-1px)!important}
div.stButton>button:active{transform:translateY(0)!important}
div[data-baseweb="input"] input,div[data-baseweb="textarea"] textarea,.stNumberInput input{
  background:var(--bg)!important;color:var(--text)!important;
  border:1.5px solid var(--border2)!important;border-radius:var(--rsm)!important;
  font-family:'Poppins',sans-serif!important;font-size:.83rem!important}
div[data-baseweb="input"] input:focus,div[data-baseweb="textarea"] textarea:focus{
  border-color:var(--orange)!important;box-shadow:0 0 0 3px rgba(255,107,53,.14)!important}
div[data-baseweb="select"]>div{background:var(--bg)!important;
  border:1.5px solid var(--border2)!important;border-radius:var(--rsm)!important;
  color:var(--text)!important}
label{color:var(--text2)!important;font-size:.75rem!important;
  font-family:'Poppins',sans-serif!important;font-weight:600!important}
[data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:var(--rsm)!important;
  padding:4px!important;gap:3px!important;box-shadow:var(--shadow)!important;
  border:1px solid var(--border)!important}
[data-baseweb="tab"]{color:var(--text3)!important;font-family:'Poppins',sans-serif!important;
  font-weight:700!important;font-size:.7rem!important;border-radius:var(--rxs)!important;
  padding:.4rem .9rem!important}
[aria-selected="true"][data-baseweb="tab"]{
  background:linear-gradient(135deg,var(--orange),var(--orange2))!important;
  color:#fff!important;box-shadow:0 2px 10px rgba(255,107,53,.35)!important}
[data-testid="stFileUploader"]{border:2px dashed var(--border2)!important;
  border-radius:var(--r)!important;background:var(--bg)!important}
[data-testid="stAlert"]{background:var(--orange3)!important;
  border:1px solid rgba(255,107,53,.25)!important;
  border-left:4px solid var(--orange)!important;
  border-radius:var(--rsm)!important;font-size:.8rem!important;color:var(--orange)!important}
[data-testid="stExpander"]{background:var(--surface)!important;
  border:1px solid var(--border)!important;border-radius:var(--rsm)!important;
  box-shadow:var(--shadow)!important}
[data-testid="stExpander"] summary{color:var(--text2)!important;font-size:.8rem!important;
  font-weight:600!important}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:999px}
.login-box{background:var(--surface);border-radius:24px;padding:2rem 1.8rem;
  box-shadow:var(--shadow2);border:1px solid var(--border);max-width:420px;margin:0 auto}
[data-baseweb="popover"]{background:var(--surface)!important;
  border:1px solid var(--border2)!important;border-radius:var(--rsm)!important}
[data-baseweb="menu"]{background:var(--surface)!important}
li[role="option"]{color:var(--text)!important;font-family:'Poppins',sans-serif!important}
li[role="option"]:hover{background:var(--orange3)!important}
@media(max-width:520px){.block-container{padding:0 .7rem 6rem!important}
  .big{font-size:2.4rem} .mgrid{gap:.5rem}}
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
USERS_FILE = "fitai_users.json"
FOOD_ICONS = {
    "Pollo":"🍗","pavo":"🦃","Atun":"🐟","Salmon":"🐠","Merluza":"🐟",
    "Ternera":"🥩","Cerdo":"🥩","Huevo":"🥚","Claras":"🥚","Queso":"🧀",
    "Yogur":"🥛","Leche":"🥛","Whey":"💪","Caseina":"💪","Avena":"🌾",
    "Arroz":"🍚","Pasta":"🍝","Pan":"🍞","Boniato":"🍠","Patata":"🥔",
    "Quinoa":"🌿","Lentejas":"🫘","Garbanzos":"🫘","Alubias":"🫘",
    "Aguacate":"🥑","Aceite":"🫒","Almendras":"🌰","Nueces":"🌰",
    "Platano":"🍌","Manzana":"🍎","Naranja":"🍊","Fresas":"🍓",
    "Arandanos":"🫐","Brocoli":"🥦","Espinacas":"🥬","Tomate":"🍅",
    "Pepino":"🥒","Lechuga":"🥬","Zanahoria":"🥕","Pimiento":"🫑",
    "Calabacin":"🥒","Tofu":"🧆","Tempeh":"🧆","Aceitunas":"🫒","Hummus":"🫘",
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
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint/30s caminar","descanso":"—","notas":"FC 85-90%"},
        {"nombre":"Tabata bicicleta","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s/10s pausa","descanso":"—","notas":"4 min por ronda"},
        {"nombre":"Zona 2 eliptica","tipo":"Cardio","equipo":"Eliptica","series_rec":"1","reps_rec":"30-45 min","descanso":"—","notas":"FC 120-140 ppm"},
        {"nombre":"Remo en ergometro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500m","descanso":"2 min","notas":"Cardio + espalda"},
    ],
}
RUTINAS_DEFAULT = {
    "PPL — Empuje":{"desc":"Pecho, hombros y triceps","ejercicios":[
        {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Press banca inclinado","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Press Arnold","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Extension sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""}]},
    "PPL — Tiron":{"desc":"Espalda y biceps","ejercicios":[
        {"ejercicio":"Dominadas","series":4,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
        {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
        {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
        {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""}]},
    "PPL — Piernas":{"desc":"Cuadriceps, isquios, gluteos y gemelos","ejercicios":[
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
    "HIIT + Core":{"desc":"Alta intensidad + abdominales — 35 min","ejercicios":[
        {"ejercicio":"Burpees","series":5,"reps":"30s/15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Mountain climbers","series":5,"reps":"30s/15s pausa","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
        {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
        {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""}]},
}
TIPO_COLOR = {
    "Fuerza":       {"color":"#00b894","bg":"rgba(0,184,148,.12)"},
    "Hipertrofia":  {"color":"#0984e3","bg":"rgba(9,132,227,.1)"},
    "Aislamiento":  {"color":"#6c5ce7","bg":"rgba(108,92,231,.1)"},
    "Peso corporal":{"color":"#00b894","bg":"rgba(0,184,148,.12)"},
    "Cardio":       {"color":"#ff6b35","bg":"rgba(255,107,53,.1)"},
    "Estabilidad":  {"color":"#00cec9","bg":"rgba(0,206,201,.1)"},
    "Gluteos":      {"color":"#e17055","bg":"rgba(225,112,85,.1)"},
    "Prevencion":   {"color":"#00cec9","bg":"rgba(0,206,201,.1)"},
    "Braquial":     {"color":"#6c5ce7","bg":"rgba(108,92,231,.1)"},
}

# ── AUTH & PERSISTENCE ────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE,"r",encoding="utf-8") as f: return json.load(f)
        except: pass
    return {}
def save_users(u):
    try:
        with open(USERS_FILE,"w",encoding="utf-8") as f: json.dump(u,f,ensure_ascii=False,indent=2)
    except Exception as e: st.warning(f"Error guardando usuarios: {e}")
def get_user_file(uid): return f"fitai_{uid[:8]}.json"
def empty_data():
    return {"historial_calorias":{},"historial_macros":{},"diario_comidas":{},
            "rutinas_custom":{},"dietas_custom":{},"perfil":{},"registro_entreno":{},"api_keys":{}}

def _clean_url(url):
    if not url: return ""
    url = url.strip().rstrip("/")
    for s in ["/rest/v1","/auth/v1","/storage/v1","/functions/v1"]:
        if url.endswith(s): url = url[:-len(s)]
    return url.rstrip("/")

@st.cache_resource(show_spinner=False)
def get_sb():
    if not SUPABASE_AVAILABLE: return None
    try:
        url = _clean_url(st.secrets.get("SUPABASE_URL",""))
        key = st.secrets.get("SUPABASE_KEY","")
        if url and key: return create_client(url, key)
    except: pass
    return None

def sb_ok(): return get_sb() is not None

def sb_register(email, pw):
    sb = get_sb()
    if sb:
        try:
            r = sb.auth.sign_up({"email":email,"password":pw})
            if r.user: return True, r.user.id
            return False,"Error al registrar. Prueba con otro correo."
        except Exception as e:
            err = str(e).lower()
            if "already" in err or "registered" in err: return False,"Este correo ya esta registrado."
            return False,f"Error: {str(e)[:100]}"
    users = load_users()
    if email in users: return False,"El correo ya esta registrado (local)."
    uid = str(uuid.uuid4())
    users[email] = {"uid":uid,"pw_hash":hash_pw(pw),"created":str(datetime.now())}
    save_users(users)
    return True, uid

def sb_login(email, pw):
    sb = get_sb()
    if sb:
        try:
            r = sb.auth.sign_in_with_password({"email":email,"password":pw})
            if r.user: return True, r.user.id, ""
            return False,"","Credenciales incorrectas."
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ["invalid","credentials","wrong","email","password"]):
                return False,"","Correo o contrasena incorrectos."
            if "confirm" in err or "not confirmed" in err:
                return False,"","Confirma tu correo (revisa el email)."
            return False,"",f"Error: {str(e)[:100]}"
    users = load_users()
    if email not in users: return False,"","Correo no registrado."
    if users[email]["pw_hash"] != hash_pw(pw): return False,"","Contrasena incorrecta."
    return True, users[email]["uid"], ""

def load_udata(uid):
    sb = get_sb()
    if sb:
        try:
            r = sb.table("user_data").select("*").eq("user_id",uid).execute()
            if r.data:
                row = r.data[0]
                return {k: row.get(k) or {} for k in
                    ["historial_calorias","historial_macros","diario_comidas",
                     "rutinas_custom","dietas_custom","perfil","registro_entreno","api_keys"]}
        except: pass
    path = get_user_file(uid)
    if os.path.exists(path):
        try:
            with open(path,"r",encoding="utf-8") as f:
                d = json.load(f); d.setdefault("api_keys",{}); return d
        except: pass
    return empty_data()

def save_udata(uid, data):
    sb = get_sb()
    if sb:
        try:
            payload = {"user_id":uid}
            for k in ["historial_calorias","historial_macros","diario_comidas",
                       "rutinas_custom","dietas_custom","perfil","registro_entreno","api_keys"]:
                payload[k] = data.get(k,{})
            sb.table("user_data").upsert(payload,on_conflict="user_id").execute()
            return
        except: pass
    try:
        with open(get_user_file(uid),"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception as e: st.warning(f"Error al guardar: {e}")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def _ss(k,v):
    if k not in st.session_state: st.session_state[k]=v
for k,v in [("logged_in",False),("user_id",""),("user_email",""),("datos",{}),
            ("gemini_key",""),("groq_key",""),("proveedor_ia","Groq (recomendado)"),
            ("scan_res",None),("ia_res",None),("ej_temp",[]),("sets_temp",[]),
            ("dc_temp",[]),("auth_mode","login"),("calc_res",None)]:
    _ss(k,v)

if not st.session_state.gemini_key:
    try: st.session_state.gemini_key = st.secrets.get("GEMINI_KEY","")
    except: pass
if not st.session_state.groq_key:
    try: st.session_state.groq_key = st.secrets.get("GROQ_KEY","")
    except: pass

# ── HELPERS ───────────────────────────────────────────────────────────────────
def hoy(): return str(date.today())
def get_pf(): return st.session_state.datos.get("perfil",{})
def obj_cal(): return int(get_pf().get("objetivo_cal",2000))
def cal_hoy(): return st.session_state.datos.get("historial_calorias",{}).get(hoy(),0)
def mac_hoy(): return st.session_state.datos.get("historial_macros",{}).get(hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0})
def save_datos(): save_udata(st.session_state.user_id, st.session_state.datos)
def food_icon(n):
    for k,v in FOOD_ICONS.items():
        if k.lower() in n.lower(): return v
    return "🥗"
def sdiv(lbl):
    st.markdown(f'<div class="sep"><div class="sep-l"></div><span class="sep-t">{lbl}</span><div class="sep-l"></div></div>',unsafe_allow_html=True)
def C(html, cls=""):
    return f'<div class="card {cls}">{html}</div>'

def pb(val, mx, color):
    pct = min(val/mx*100,100) if mx>0 else 0
    return f'<div class="pb"><div class="pb-f" style="width:{pct:.1f}%;background:{color}"></div></div>'

def ring(pct, color, label, val_str, unit_str=""):
    r=46; c=2*3.14159*r; d=c*min(pct,100)/100; g=c-d
    return (f'<div class="ring-wrap"><div class="ring">'
            f'<svg width="110" height="110" viewBox="0 0 110 110">'
            f'<circle cx="55" cy="55" r="{r}" fill="none" stroke="#f0f1f3" stroke-width="9"/>'
            f'<circle cx="55" cy="55" r="{r}" fill="none" stroke="{color}" stroke-width="9"'
            f' stroke-dasharray="{d:.1f} {g:.1f}" stroke-linecap="round"/></svg>'
            f'<div class="ring-val"><div class="ring-num">{val_str}</div>'
            f'<div class="ring-unit">{unit_str}</div></div></div>'
            f'<div class="ring-label">{label}</div></div>')

def calcular_tdee(peso, altura, edad, sexo, act):
    bmr = (88.36+13.4*peso+4.8*altura-5.7*edad) if sexo=="Hombre" else (447.6+9.2*peso+3.1*altura-4.3*edad)
    f = {"Sedentario (sin ejercicio)":1.2,"Ligero (1-2 dias/semana)":1.375,
         "Moderado (3-4 dias/semana)":1.55,"Activo (5-6 dias/semana)":1.725,"Muy activo (2 veces/dia)":1.9}
    return int(bmr*f.get(act,1.55))

def registrar_alimento(nombre, cal, prot, carb, grasa, comida):
    d = st.session_state.datos
    d.setdefault("historial_calorias",{})[hoy()] = cal_hoy()+int(cal)
    dm = d.setdefault("historial_macros",{}).setdefault(hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0})
    dm["prot"]  = round(dm["prot"] +float(prot),1)
    dm["carb"]  = round(dm["carb"] +float(carb),1)
    dm["grasa"] = round(dm["grasa"]+float(grasa),1)
    d.setdefault("diario_comidas",{}).setdefault(hoy(),[]).append(
        {"comida":comida,"alimento":nombre,"cal":int(cal),"prot":float(prot),
         "carb":float(carb),"grasa":float(grasa),"hora":datetime.now().strftime("%H:%M")})
    save_datos()

def ia_call(prompt, img_bytes=None):
    prov = st.session_state.proveedor_ia
    if "Groq" in prov:
        key = st.session_state.groq_key.strip()
        if not key: return "ERROR_NO_KEY"
        try:
            hdrs = {"Authorization":f"Bearer {key}","Content-Type":"application/json"}
            if img_bytes:
                b64 = base64.b64encode(img_bytes).decode()
                try: ext = Image.open(io.BytesIO(img_bytes)).format.lower().replace("jpg","jpeg")
                except: ext = "jpeg"
                msgs = [{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:image/{ext};base64,{b64}"}},
                    {"type":"text","text":prompt}]}]
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
            else:
                msgs = [{"role":"user","content":prompt}]
                model = "llama-3.3-70b-versatile"
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers=hdrs,json={"model":model,"messages":msgs,"max_tokens":1200,"temperature":0.4},timeout=30)
            if r.status_code==401: return "API Key de Groq invalida. Verifica en console.groq.com/keys"
            if r.status_code==429: return "Limite de Groq alcanzado. Espera un minuto."
            if r.status_code!=200: return f"Error Groq {r.status_code}"
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e: return f"Error conexion: {str(e)[:120]}"
    else:
        key = st.session_state.gemini_key.strip()
        if not key: return "ERROR_NO_KEY"
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            m = genai.GenerativeModel("gemini-1.5-flash")
            if img_bytes:
                return m.generate_content([prompt,Image.open(io.BytesIO(img_bytes))]).text
            return m.generate_content(prompt).text
        except Exception as e:
            err=str(e)
            if "QUOTA" in err.upper() or "429" in err: return "Cuota Gemini agotada. Cambia a Groq."
            return f"Error Gemini: {err[:120]}"

def extraer_kcal(txt):
    try:
        m=re.search(r"TOTAL.*?(\d{2,4})\s*kcal",txt,re.IGNORECASE)
        if m: return int(m.group(1))
        m2=re.search(r"(\d{3,4})\s*kcal",txt,re.IGNORECASE)
        if m2: return int(m2.group(1))
    except: pass
    return 0

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#ff6b35 0%,#ff8c5a 55%,#6c5ce7 100%);
                border-radius:0 0 32px 32px;padding:2.8rem 1.4rem 2.2rem;margin:0 -1rem 2rem;text-align:center">
      <div style="font-size:.6rem;font-weight:800;color:rgba(255,255,255,.7);
                  letter-spacing:.2em;text-transform:uppercase;margin-bottom:.7rem">
        💪 Tu asistente fitness con IA
      </div>
      <div style="font-family:'Nunito',sans-serif;font-size:4rem;font-weight:900;
                  color:#fff;line-height:.88;letter-spacing:-.02em;margin-bottom:.5rem">
        Fit<span style="color:#fdcb6e">AI</span>
      </div>
      <div style="font-family:'Nunito',sans-serif;font-size:1rem;font-weight:700;
                  color:rgba(255,255,255,.75);margin-bottom:.7rem">PRO</div>
      <div style="font-size:.72rem;color:rgba(255,255,255,.65);
                  display:flex;justify-content:center;gap:.5rem;flex-wrap:wrap">
        <span>Nutricion</span><span>·</span><span>Dietas IA</span>
        <span>·</span><span>Gimnasio</span><span>·</span><span>Progreso</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([0.3, 3, 0.3])
    with col:
        mode = st.session_state.auth_mode
        t = "Bienvenido de nuevo 👋" if mode=="login" else "Crear cuenta 🚀"
        s = "Accede a tu cuenta" if mode=="login" else "Registrate gratis en segundos"
        st.markdown(f'<div class="login-box"><div style="text-align:center;margin-bottom:1.4rem">'
                    f'<div style="font-family:Nunito,sans-serif;font-size:1.3rem;font-weight:900;'
                    f'color:var(--text)">{t}</div>'
                    f'<div style="font-size:.73rem;color:var(--text3);margin-top:.2rem">{s}</div>'
                    f'</div>', unsafe_allow_html=True)

        email_in = st.text_input("📧 Correo electronico", placeholder="hola@ejemplo.com", key="ae")
        pw_in    = st.text_input("🔒 Contrasena", type="password", placeholder="Minimo 6 caracteres", key="ap")
        if mode=="register":
            nombre_in = st.text_input("👤 Nombre (opcional)", placeholder="Alex", key="an")

        st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)

        if mode=="login":
            if st.button("Entrar →", key="btn_login"):
                if not email_in or not pw_in:
                    st.warning("Rellena correo y contrasena.")
                else:
                    ok, uid, err = sb_login(email_in.strip().lower(), pw_in)
                    if ok:
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = uid
                        st.session_state.user_email = email_in.strip().lower()
                        st.session_state.datos      = load_udata(uid)
                        ak = st.session_state.datos.get("api_keys",{})
                        if not st.session_state.groq_key:
                            st.session_state.groq_key = ak.get("groq_key","")
                        if not st.session_state.gemini_key:
                            st.session_state.gemini_key = ak.get("gemini_key","")
                        if ak.get("proveedor_ia"):
                            st.session_state.proveedor_ia = ak["proveedor_ia"]
                        st.rerun()
                    else:
                        st.error(f"❌ {err}")
            st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
            if st.button("Crear cuenta nueva →", key="btn_go_reg"):
                st.session_state.auth_mode="register"; st.rerun()
        else:
            if st.button("Registrarme →", key="btn_reg"):
                if not email_in or not pw_in:
                    st.warning("Rellena correo y contrasena.")
                elif len(pw_in)<6:
                    st.warning("La contrasena debe tener al menos 6 caracteres.")
                else:
                    ok, uid_or_err = sb_register(email_in.strip().lower(), pw_in)
                    if ok:
                        nom = st.session_state.get("an","")
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = uid_or_err
                        st.session_state.user_email = email_in.strip().lower()
                        st.session_state.datos      = empty_data()
                        st.session_state.datos["perfil"] = {
                            "nombre":nom,"objetivo_cal":2000,"obj_prot":150,"obj_carb":220,"obj_grasa":60}
                        save_datos()
                        st.success("✅ Cuenta creada. Bienvenido/a!"); st.rerun()
                    else:
                        st.error(f"❌ {uid_or_err}")
            st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
            if st.button("← Ya tengo cuenta", key="btn_go_login"):
                st.session_state.auth_mode="login"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
nombre_u = get_pf().get("nombre","") or st.session_state.user_email.split("@")[0]
fecha_str = datetime.now().strftime("%A %d %b").capitalize()
st.markdown(f"""
<div class="top-header">
  <div>
    <div class="header-greeting">Hola de nuevo 👋</div>
    <div class="header-name">{nombre_u}</div>
    <div style="font-size:.62rem;color:var(--text3);margin-top:.1rem">{fecha_str}</div>
  </div>
  <div class="header-avatar">💪</div>
</div>
""", unsafe_allow_html=True)

t_nut,t_diet,t_gym,t_hist,t_cfg = st.tabs(["🍎 Kcal","🥗 Dietas","💪 Gym","📊 Stats","⚙️ Config"])

# ══════════════════════════════════════════════════════════════════════════════
# NUTRICION
# ══════════════════════════════════════════════════════════════════════════════
with t_nut:
    cv   = cal_hoy(); oc = obj_cal(); mh = mac_hoy()
    pf   = get_pf()
    op   = int(pf.get("obj_prot",150))
    ocb  = int(pf.get("obj_carb",220))
    og   = int(pf.get("obj_grasa",60))
    rest = max(oc-cv,0); exc = max(cv-oc,0); ok_c = cv<=oc
    pct  = int(min(cv/oc*100,100)) if oc else 0
    pct_p  = int(min(mh["prot"] /op *100,100)) if op  else 0
    pct_cb = int(min(mh["carb"] /ocb*100,100)) if ocb else 0
    pct_g  = int(min(mh["grasa"]/og *100,100)) if og  else 0
    rc = "#ff6b35" if ok_c else "#e17055"

    c1,c2 = st.columns([1,1.8])
    with c1:
        st.markdown(C(ring(pct,rc,"Kcal hoy",str(cv),"kcal")), unsafe_allow_html=True)
    with c2:
        ev = rest if ok_c else exc
        el = "kcal restantes" if ok_c else "kcal excedidas"
        ec = "#00b894" if ok_c else "#e17055"
        st.markdown(C(
            f'<div class="lbl lbl-orange">Objetivo diario</div>'
            f'<div class="big">{oc}</div>'
            f'<div class="big-sub">kcal / dia</div>'
            f'{pb(cv,oc,rc)}'
            f'<div style="margin-top:.7rem;display:flex;align-items:center;gap:.5rem">'
            f'<span style="font-family:Nunito,sans-serif;font-size:1.5rem;font-weight:900;color:{ec}">{ev}</span>'
            f'<span style="font-size:.63rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.05em">{el}</span></div>'
        ), unsafe_allow_html=True)

    pv=f"{mh['prot']:.0f}g"; cbv=f"{mh['carb']:.0f}g"; gv=f"{mh['grasa']:.0f}g"
    st.markdown(C(
        f'<div class="lbl lbl-orange">Macronutrientes</div>'
        f'<div class="mgrid" style="justify-items:center">'
        f'{ring(pct_p,"#00b894","Proteina",pv,f"/{op}g")}'
        f'{ring(pct_cb,"#6c5ce7","Carbohidr.",cbv,f"/{ocb}g")}'
        f'{ring(pct_g,"#fdcb6e","Grasas",gv,f"/{og}g")}'
        f'</div>'
    ), unsafe_allow_html=True)

    sdiv("Scanner IA")
    prov_a = st.session_state.proveedor_ia
    key_a  = st.session_state.groq_key if "Groq" in prov_a else st.session_state.gemini_key
    if not key_a.strip():
        st.info("🔑 Configura tu API Key en Config para activar el scanner IA.")
    else:
        img_up = st.file_uploader("📷 Foto del plato",type=["jpg","jpeg","png","webp"],key="up_scan")
        if img_up:
            st.image(img_up,use_container_width=True)
            s1,s2 = st.columns(2)
            with s1: com_scan=st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="sc_com")
            with s2:
                if st.button("🔍 Analizar",key="btn_scan"):
                    with st.spinner("Analizando..."):
                        pr=("Eres nutricionista experto. Analiza en espanol con formato:\n"
                            "Alimentos detectados:\n- [alimento] — [X] kcal · P:[Xg] C:[Xg] G:[Xg]\n\n"
                            "TOTAL: [NNN] kcal | P:[Xg] C:[Xg] G:[Xg]\nValoracion: [frase]")
                        res=ia_call(pr,img_up.read())
                        if res=="ERROR_NO_KEY": st.warning("Configura API Key en Config.")
                        else: st.session_state.scan_res=res
    if st.session_state.scan_res:
        st.markdown(C(f'<div class="lbl lbl-orange">Analisis IA</div>'
                      f'<p style="white-space:pre-wrap;color:var(--text2);font-size:.8rem;line-height:1.85;margin:0">'
                      f'{st.session_state.scan_res}</p>'), unsafe_allow_html=True)
        kd=extraer_kcal(st.session_state.scan_res)
        if kd>0:
            r1,r2=st.columns(2)
            with r1:
                if st.button(f"✅ Registrar {kd} kcal",key="btn_reg_scan"):
                    registrar_alimento("Foto IA",kd,0,0,0,st.session_state.get("sc_com","Extra"))
                    st.session_state.scan_res=None; st.success("Registrado."); st.rerun()
            with r2:
                if st.button("✕ Descartar",key="btn_disc"):
                    st.session_state.scan_res=None; st.rerun()

    sdiv("Registrar alimento")
    ra1,ra2=st.columns([3,1])
    with ra1: alim=st.selectbox("Alimento",list(ALIMENTOS_DB.keys()),key="sel_alim",label_visibility="collapsed")
    with ra2: cant=st.number_input("g",1,2000,100,key="cant",label_visibility="collapsed")
    ad=ALIMENTOS_DB[alim]; fac=cant/100
    cav=round(ad["cal"]*fac); prv=round(ad["prot"]*fac,1)
    cbv2=round(ad["carb"]*fac,1); grv=round(ad["grasa"]*fac,1)
    st.markdown(C(
        f'<div style="display:flex;align-items:center;gap:.8rem">'
        f'<div style="font-size:2.2rem">{food_icon(alim)}</div>'
        f'<div><div style="font-family:Nunito,sans-serif;font-size:.88rem;font-weight:800;'
        f'color:var(--text);margin-bottom:.35rem">{alim} — {cant}g</div>'
        f'<span class="badge bk">🔥 {cav} kcal</span>'
        f'<span class="badge bp">P {prv}g</span>'
        f'<span class="badge bc">C {cbv2}g</span>'
        f'<span class="badge bf">G {grv}g</span></div></div>'
    ), unsafe_allow_html=True)
    ra3,ra4=st.columns([2,1])
    with ra3: com_db=st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="com_db")
    with ra4:
        if st.button("➕ Añadir",key="btn_add_db"):
            registrar_alimento(f"{alim} ({cant}g)",cav,prv,cbv2,grv,com_db)
            st.success(f"✅ {cav} kcal"); st.rerun()

    sdiv("Registro manual")
    m1,m2,m3,m4=st.columns([3,1,1,1])
    with m1: nm=st.text_input("Nombre",placeholder="Plato casero",key="nm",label_visibility="collapsed")
    with m2: km=st.number_input("kcal",0,5000,0,5,key="km",label_visibility="collapsed")
    with m3: pm2=st.number_input("P(g)",0.0,300.0,0.0,.5,key="pm2",label_visibility="collapsed")
    with m4: cbm=st.number_input("C(g)",0.0,500.0,0.0,.5,key="cbm",label_visibility="collapsed")
    m5,m6=st.columns([2,1])
    with m5: comm=st.selectbox("Comida",["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="comm")
    with m6:
        if st.button("➕ Añadir",key="btn_man"):
            if km>0: registrar_alimento(nm or "Libre",km,pm2,cbm,0,comm); st.success(f"✅ {km} kcal"); st.rerun()
            else: st.warning("Introduce kcal > 0")

    sdiv("Diario de hoy")
    diario=st.session_state.datos.get("diario_comidas",{}).get(hoy(),[])
    if not diario:
        st.markdown(C('<div style="text-align:center;padding:1.2rem 0">'
                      '<div style="font-size:2.5rem;margin-bottom:.4rem">🍽️</div>'
                      '<div class="lbl" style="text-align:center">Sin registros todavia</div>'
                      '<p style="color:var(--text3);font-size:.77rem;margin:0">Añade alimentos arriba</p></div>'),
                    unsafe_allow_html=True)
    else:
        grupos={}
        for item in diario: grupos.setdefault(item["comida"],[]).append(item)
        for nc2,items in grupos.items():
            tc=sum(i["cal"] for i in items)
            filas="".join(f'<div class="row"><span class="rl">'
                          f'<span style="font-size:.62rem;color:var(--orange);font-weight:700">{i["hora"]}</span>'
                          f'  {food_icon(i["alimento"])} {i["alimento"]}</span>'
                          f'<span class="rr">{i["cal"]} kcal</span></div>' for i in items)
            st.markdown(C(f'<div class="meal-header"><span class="meal-title">{nc2}</span>'
                          f'<span class="badge bk">{tc} kcal</span></div>{filas}'), unsafe_allow_html=True)

    if st.button("🗑️ Resetear diario",key="btn_reset"):
        d=st.session_state.datos
        d.setdefault("historial_calorias",{})[hoy()]=0
        d.setdefault("historial_macros",{})[hoy()]={"prot":0.0,"carb":0.0,"grasa":0.0}
        d.setdefault("diario_comidas",{})[hoy()]=[]
        save_datos(); st.success("Diario reseteado."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DIETAS
# ══════════════════════════════════════════════════════════════════════════════
with t_diet:
    dt1,dt2,dt3,dt4=st.tabs(["Planes","Calculadora","IA Dietista","Mis dietas"])
    with dt1:
        plan_k=st.selectbox("Plan",list(DIETAS_TEMPLATE.keys()),key="plan_k")
        plan=DIETAS_TEMPLATE[plan_k]
        tc_p=sum(c["cal"] for c in plan["comidas"]); tp_p=sum(c["prot"] for c in plan["comidas"])
        tcb_p=sum(c["carb"] for c in plan["comidas"]); tg_p=sum(c["grasa"] for c in plan["comidas"])
        st.markdown(C(f'<div class="lbl" style="color:rgba(255,255,255,.75)">Objetivo</div>'
                      f'<div style="font-family:Nunito,sans-serif;font-size:.9rem;font-weight:800;color:#fff;margin-bottom:.6rem">{plan["objetivo"]}</div>'
                      f'<span class="badge" style="background:rgba(255,255,255,.25);color:#fff">🔥 {tc_p} kcal</span>'
                      f'<span class="badge" style="background:rgba(255,255,255,.2);color:#fff">P {tp_p}g</span>'
                      f'<span class="badge" style="background:rgba(255,255,255,.2);color:#fff">C {tcb_p}g</span>'
                      f'<span class="badge" style="background:rgba(255,255,255,.2);color:#fff">G {tg_p}g</span>',
                      "card-orange"), unsafe_allow_html=True)
        for c in plan["comidas"]:
            st.markdown(C(f'<div class="meal-header">'
                          f'<div style="display:flex;align-items:center;gap:.5rem">'
                          f'<span style="font-size:1.5rem">{food_icon(c["alimentos"])}</span>'
                          f'<span class="meal-title">{c["nombre"]}</span></div>'
                          f'<span class="badge bk">{c["cal"]} kcal</span></div>'
                          f'<p style="margin:.2rem 0 .4rem;font-size:.78rem;color:var(--text2)">{c["alimentos"]}</p>'
                          f'<span class="badge bp">P {c["prot"]}g</span>'
                          f'<span class="badge bc">C {c["carb"]}g</span>'
                          f'<span class="badge bf">G {c["grasa"]}g</span>'), unsafe_allow_html=True)
        if st.button("✅ Usar como objetivo diario",key="btn_usar"):
            st.session_state.datos.setdefault("perfil",{}).update(
                {"objetivo_cal":tc_p,"obj_prot":tp_p,"obj_carb":tcb_p,"obj_grasa":tg_p})
            save_datos(); st.success(f"Objetivo: {tc_p} kcal/dia"); st.rerun()

    with dt2:
        pf2=get_pf()
        d1,d2=st.columns(2)
        with d1:
            dp=st.number_input("Peso (kg)",30.0,250.0,float(pf2.get("peso",75)),.5,key="dp")
            da=st.number_input("Altura (cm)",100,250,int(pf2.get("altura",175)),key="da")
        with d2:
            de=st.number_input("Edad",10,100,int(pf2.get("edad",25)),key="de")
            dsx=st.selectbox("Sexo",["Hombre","Mujer"],key="dsx")
        dact=st.selectbox("Actividad",["Sedentario (sin ejercicio)","Ligero (1-2 dias/semana)",
            "Moderado (3-4 dias/semana)","Activo (5-6 dias/semana)","Muy activo (2 veces/dia)"],index=2,key="dact")
        dobj=st.selectbox("Objetivo",["Perdida de grasa (-300 kcal)","Perdida agresiva (-500 kcal)",
            "Mantenimiento","Volumen limpio (+200 kcal)","Volumen (+400 kcal)"],key="dobj")
        if st.button("🔢 Calcular TDEE",key="btn_calc"):
            tdee=calcular_tdee(dp,da,de,dsx,dact)
            delta={"Perdida de grasa (-300 kcal)":-300,"Perdida agresiva (-500 kcal)":-500,
                   "Mantenimiento":0,"Volumen limpio (+200 kcal)":200,"Volumen (+400 kcal)":400}[dobj]
            cobj=tdee+delta; perd="Perdida" in dobj
            prot_g=round(dp*(2.2 if perd else 1.9)); gras_g=round(dp*(1.0 if perd else 1.1))
            carb_g=max(round((cobj-prot_g*4-gras_g*9)/4),50)
            imc=round(dp/((da/100)**2),1)
            cat="Bajo peso" if imc<18.5 else "Normopeso" if imc<25 else "Sobrepeso" if imc<30 else "Obesidad"
            st.session_state.calc_res={"tdee":tdee,"cobj":cobj,"prot":prot_g,"carb":carb_g,"grasa":gras_g,"imc":imc,"cat":cat,"dp":dp,"da":da,"de":de}
        if st.session_state.calc_res:
            res=st.session_state.calc_res
            st.markdown(C(
                f'<div class="lbl lbl-orange">Resultado</div>'
                f'<div class="sgrid" style="margin-bottom:.8rem">'
                f'<div class="mini-stat"><div class="mini-val">{res["tdee"]}</div><div class="mini-lbl">Mantenimiento kcal</div></div>'
                f'<div class="mini-stat" style="border:2px solid var(--orange)">'
                f'<div class="mini-val" style="color:var(--orange)">{res["cobj"]}</div>'
                f'<div class="mini-lbl">Tu objetivo kcal</div></div></div>'
                f'<p style="font-size:.8rem;font-weight:600;margin-bottom:.5rem">IMC: <b>{res["imc"]}</b> — {res["cat"]}</p>'
                f'<span class="badge bp">P {res["prot"]}g</span>'
                f'<span class="badge bc">C {res["carb"]}g</span>'
                f'<span class="badge bf">G {res["grasa"]}g</span>'
            ), unsafe_allow_html=True)
            if st.button("💾 Guardar objetivos",key="btn_sc"):
                st.session_state.datos.setdefault("perfil",{}).update(
                    {"peso":res["dp"],"altura":res["da"],"edad":res["de"],
                     "objetivo_cal":res["cobj"],"obj_prot":res["prot"],"obj_carb":res["carb"],"obj_grasa":res["grasa"]})
                save_datos(); st.success("✅ Guardados."); st.rerun()

    with dt3:
        key_ia=st.session_state.groq_key if "Groq" in st.session_state.proveedor_ia else st.session_state.gemini_key
        if not key_ia.strip():
            st.info("🔑 Configura tu API Key en Config.")
        else:
            pf3=get_pf(); d1,d2=st.columns(2)
            with d1:
                iap=st.number_input("Peso (kg)",30.0,250.0,float(pf3.get("peso",75)),.5,key="iap")
                iaa=st.number_input("Altura (cm)",100,250,int(pf3.get("altura",175)),key="iaa")
                iae=st.number_input("Edad",10,100,int(pf3.get("edad",25)),key="iae")
            with d2:
                iasx=st.selectbox("Sexo",["Hombre","Mujer"],key="iasx")
                iaob=st.selectbox("Objetivo",["Perder grasa","Ganar musculo","Mantenimiento","Mejorar rendimiento","Salud general"],key="iaob")
                iaac=st.selectbox("Actividad",["Sedentario","Ligero","Moderado","Activo","Muy activo"],key="iaac")
            iarest=st.multiselect("Restricciones",["Sin gluten","Sin lactosa","Vegetariano","Vegano","Sin cerdo","Sin mariscos","Bajo sodio","Bajo azucar"],key="iarest")
            iaext=st.text_area("Info adicional",placeholder="Alergias, patologias...",height=60,key="iaext")
            if st.button("🤖 Generar plan con IA",key="btn_ia"):
                rest_s=", ".join(iarest) if iarest else "ninguna"
                pr=(f"Eres dietista-nutricionista experto. Plan completo en espanol para:\n"
                    f"- {iasx}, {iae} anios, {iap}kg, {iaa}cm\n- Objetivo: {iaob} | Actividad: {iaac} | Restricciones: {rest_s}\n"
                    f"- Extra: {iaext or 'ninguna'}\nIncluye: 1)Calorias y macros 2)Plan 5-6 comidas con cantidades exactas "
                    f"3)Timing pre/post entreno 4)Lista compra semanal 5)3 consejos. Muy especifico.")
                with st.spinner("Generando plan..."):
                    res=ia_call(pr)
                    if res=="ERROR_NO_KEY": st.warning("Configura API Key en Config.")
                    else: st.session_state.ia_res=res
            if st.session_state.ia_res:
                st.markdown(C(f'<div class="lbl lbl-orange">Plan generado por IA</div>'
                              f'<p style="white-space:pre-wrap;color:var(--text2);font-size:.8rem;line-height:1.85;margin:0">{st.session_state.ia_res}</p>'),
                            unsafe_allow_html=True)
                if st.button("🔄 Nuevo plan",key="btn_ia_r"):
                    st.session_state.ia_res=None; st.rerun()

    with dt4:
        dc_all=st.session_state.datos.get("dietas_custom",{})
        if dc_all:
            dc_sel=st.selectbox("Mis dietas",["— Nueva —"]+list(dc_all.keys()),key="dc_sel")
            if dc_sel!="— Nueva —":
                dc=dc_all[dc_sel]
                if dc.get("notas"):
                    st.markdown(C(f'<p style="font-size:.8rem;color:var(--text2);margin:0">{dc["notas"]}</p>'),unsafe_allow_html=True)
                for c in dc.get("comidas",[]):
                    st.markdown(C(f'<div class="meal-header">'
                                  f'<span class="meal-title">{food_icon(c.get("alimentos",""))} {c["nombre"]}</span>'
                                  f'<span class="badge bk">{c.get("cal",0)} kcal</span></div>'
                                  f'<p style="margin:0 0 .4rem;font-size:.78rem;color:var(--text2)">{c.get("alimentos","")}</p>'
                                  f'<span class="badge bp">P {c.get("prot",0)}g</span>'
                                  f'<span class="badge bc">C {c.get("carb",0)}g</span>'
                                  f'<span class="badge bf">G {c.get("grasa",0)}g</span>'),unsafe_allow_html=True)
                if st.button("🗑️ Eliminar dieta",key="btn_del_dc"):
                    del st.session_state.datos["dietas_custom"][dc_sel]; save_datos(); st.success("Eliminada."); st.rerun()
        sdiv("Crear nueva dieta")
        nc_nom=st.text_input("Nombre",placeholder="Mi dieta de verano",key="nc_nom")
        nc_not=st.text_area("Descripcion",placeholder="Objetivo...",height=50,key="nc_not")
        sdiv("Añadir comidas")
        dc1,dc2=st.columns([2,1])
        with dc1:
            nc_cn=st.text_input("Nombre comida",placeholder="Almuerzo",key="nc_cn")
            nc_al=st.text_area("Alimentos",placeholder="Pollo 150g, Arroz 100g",height=45,key="nc_al")
        with dc2:
            nc_cal=st.number_input("kcal",0,3000,0,10,key="nc_cal")
            nc_pr=st.number_input("P(g)",0.0,200.0,0.0,.5,key="nc_pr")
            nc_cb2=st.number_input("C(g)",0.0,500.0,0.0,.5,key="nc_cb2")
            nc_gr=st.number_input("G(g)",0.0,200.0,0.0,.5,key="nc_gr")
        if st.button("➕ Añadir comida",key="btn_add_nc"):
            if nc_cn:
                st.session_state.dc_temp.append({"nombre":nc_cn,"alimentos":nc_al,"cal":nc_cal,"prot":nc_pr,"carb":nc_cb2,"grasa":nc_gr})
                st.success(f"'{nc_cn}' añadida.")
            else: st.warning("Escribe nombre de la comida.")
        if st.session_state.dc_temp:
            tot=sum(c["cal"] for c in st.session_state.dc_temp)
            filas="".join(f'<div class="row"><span class="rl">{i+1}. {food_icon(c.get("alimentos",""))} {c["nombre"]}</span>'
                          f'<span class="rr">{c["cal"]} kcal</span></div>'
                          for i,c in enumerate(st.session_state.dc_temp))
            st.markdown(C(f'{filas}<div style="text-align:right;margin-top:.4rem">'
                          f'<span class="badge bk">Total: {tot} kcal</span></div>'),unsafe_allow_html=True)
        if st.button("💾 Guardar dieta",key="btn_save_dc"):
            if not nc_nom: st.warning("Dale un nombre.")
            elif not st.session_state.dc_temp: st.warning("Añade al menos una comida.")
            else:
                st.session_state.datos.setdefault("dietas_custom",{})[nc_nom]={"notas":nc_not,"comidas":st.session_state.dc_temp.copy()}
                save_datos(); st.session_state.dc_temp=[]; st.success(f"✅ '{nc_nom}' guardada."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# GIMNASIO
# ══════════════════════════════════════════════════════════════════════════════
with t_gym:
    g1,g2,g3=st.tabs(["Ejercicios","Rutinas","Registro"])
    with g1:
        grupo=st.selectbox("Grupo muscular",list(EJERCICIOS_GYM.keys()),key="grupo")
        for ej in EJERCICIOS_GYM[grupo]:
            tc=TIPO_COLOR.get(ej["tipo"],{"color":"#ff6b35","bg":"rgba(255,107,53,.1)"})
            st.markdown(C(
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:.3rem;margin-bottom:.4rem">'
                f'<span style="font-family:Nunito,sans-serif;font-size:.88rem;font-weight:800;color:var(--text)">{ej["nombre"]}</span>'
                f'<span class="typebadge" style="color:{tc["color"]};background:{tc["bg"]}">{ej["tipo"]}</span></div>'
                f'<div style="font-size:.68rem;color:var(--text3);font-weight:600;margin-bottom:.3rem">{ej["equipo"]}</div>'
                f'<div style="display:flex;gap:.5rem;flex-wrap:wrap;font-size:.77rem;color:var(--text2);margin-bottom:.3rem">'
                f'<span style="font-weight:700;color:var(--orange)">{ej["series_rec"]} series</span>'
                f'<span>·</span><span>{ej["reps_rec"]} reps</span><span>·</span><span>{ej["descanso"]}</span></div>'
                f'<p style="font-size:.72rem;color:var(--text3);font-style:italic;margin:0">{ej["notas"]}</p>'
            ), unsafe_allow_html=True)

    with g2:
        todas={**RUTINAS_DEFAULT,**st.session_state.datos.get("rutinas_custom",{})}
        rut_k=st.selectbox("Rutina",list(todas.keys()),key="rut_k")
        rut=todas[rut_k]
        desc=rut.get("desc","") if isinstance(rut,dict) else ""
        ejs=rut.get("ejercicios",rut) if isinstance(rut,dict) else rut
        if desc:
            st.markdown(f'<div style="font-size:.72rem;font-weight:700;color:var(--text3);margin-bottom:.8rem;text-transform:uppercase;letter-spacing:.06em">{desc}</div>',unsafe_allow_html=True)
        for idx,ej in enumerate(ejs):
            ps=f" · {ej['peso']}" if ej.get("peso") else ""
            ns=f'<p style="font-size:.7rem;color:var(--text3);font-style:italic;margin-top:.2rem">{ej["notas"]}</p>' if ej.get("notas") else ""
            st.markdown(C(
                f'<div style="display:flex;align-items:flex-start;gap:.7rem">'
                f'<div class="ex-num">{idx+1:02d}</div>'
                f'<div style="flex:1"><div style="font-family:Nunito,sans-serif;font-size:.85rem;font-weight:800;color:var(--text);margin-bottom:.25rem">{ej["ejercicio"]}</div>'
                f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;font-size:.76rem;color:var(--text2)">'
                f'<span style="font-weight:700;color:var(--orange)">{ej["series"]}x</span>'
                f'<span>{ej["reps"]} reps</span><span>·</span><span>{ej["descanso"]}{ps}</span></div>{ns}</div></div>'
            ), unsafe_allow_html=True)
        sdiv("Crear rutina personalizada")
        with st.expander("✚ Nueva rutina"):
            nr_n=st.text_input("Nombre",placeholder="Mi rutina lunes",key="nr_n")
            nr_d=st.text_input("Descripcion",placeholder="Pecho y triceps",key="nr_d")
            e1,e2,e3=st.columns([3,1,2])
            with e1: nr_ej=st.text_input("Ejercicio",placeholder="Press banca",key="nr_ej",label_visibility="collapsed")
            with e2: nr_s=st.number_input("Series",1,20,4,key="nr_s",label_visibility="collapsed")
            with e3: nr_r=st.text_input("Reps",placeholder="8-12",key="nr_r",label_visibility="collapsed")
            e4,e5,e6=st.columns(3)
            with e4: nr_p=st.text_input("Peso",placeholder="60kg",key="nr_p",label_visibility="collapsed")
            with e5: nr_dc=st.text_input("Descanso",placeholder="90s",key="nr_dc",label_visibility="collapsed")
            with e6: nr_nt=st.text_input("Nota",placeholder="...",key="nr_nt",label_visibility="collapsed")
            if st.button("➕ Añadir ejercicio",key="btn_add_ej"):
                if nr_ej:
                    st.session_state.ej_temp.append({"ejercicio":nr_ej,"series":nr_s,"reps":nr_r or "8-12","peso":nr_p,"descanso":nr_dc or "60s","notas":nr_nt})
                    st.success(f"'{nr_ej}' añadido.")
                else: st.warning("Escribe nombre del ejercicio.")
            if st.session_state.ej_temp:
                filas="".join(f'<div class="row"><span class="rl"><span class="ex-num">{i+1:02d}</span> {e["ejercicio"]}</span>'
                              f'<span class="rr">{e["series"]}x{e["reps"]}</span></div>'
                              for i,e in enumerate(st.session_state.ej_temp))
                st.markdown(C(filas),unsafe_allow_html=True)
            if st.button("💾 Guardar rutina",key="btn_save_rut"):
                if not nr_n: st.warning("Dale un nombre.")
                elif not st.session_state.ej_temp: st.warning("Añade al menos un ejercicio.")
                else:
                    st.session_state.datos.setdefault("rutinas_custom",{})[nr_n]={"desc":nr_d,"ejercicios":st.session_state.ej_temp.copy()}
                    save_datos(); st.session_state.ej_temp=[]; st.success(f"✅ '{nr_n}' guardada."); st.rerun()

    with g3:
        r1,r2=st.columns(2)
        with r1: reg_tipo=st.selectbox("Tipo",["PPL — Empuje","PPL — Tiron","PPL — Piernas","Full Body","Upper","Lower","HIIT","Cardio","Otro"],key="reg_tipo")
        with r2: reg_dur=st.number_input("Duracion (min)",10,300,60,key="reg_dur")
        reg_notas=st.text_area("Notas",placeholder="Sensaciones, PRs...",height=60,key="reg_notas")
        sdiv("Series realizadas")
        sr1,sr2,sr3,sr4=st.columns(4)
        with sr1: ej_n=st.text_input("Ejercicio",placeholder="Sentadilla",key="ej_n",label_visibility="collapsed")
        with sr2: set_s=st.number_input("Series",1,20,3,key="set_s",label_visibility="collapsed")
        with sr3: set_r=st.text_input("Reps",placeholder="10",key="set_r",label_visibility="collapsed")
        with sr4: set_p=st.text_input("Peso",placeholder="80kg",key="set_p",label_visibility="collapsed")
        if st.button("➕ Añadir serie",key="btn_add_set"):
            if ej_n:
                st.session_state.sets_temp.append({"ejercicio":ej_n,"series":set_s,"reps":set_r or "—","peso":set_p or "—"})
                st.success(f"'{ej_n}' añadido.")
            else: st.warning("Escribe nombre del ejercicio.")
        if st.session_state.sets_temp:
            filas="".join(f'<div class="row"><span class="rl"><span class="ex-num">{i+1:02d}</span> {s["ejercicio"]}</span>'
                          f'<span class="rr">{s["series"]}x{s["reps"]} · {s["peso"]}</span></div>'
                          for i,s in enumerate(st.session_state.sets_temp))
            st.markdown(C(filas),unsafe_allow_html=True)
        if st.button("💾 Guardar sesion",key="btn_save_ses"):
            reg=st.session_state.datos.setdefault("registro_entreno",{})
            reg.setdefault(hoy(),[]).append({"tipo":reg_tipo,"duracion":reg_dur,"notas":reg_notas,
                "series":st.session_state.sets_temp.copy(),"hora":datetime.now().strftime("%H:%M")})
            save_datos(); st.session_state.sets_temp=[]; st.success("✅ Sesion guardada."); st.rerun()
        sdiv("Ultimas sesiones")
        reg_all=st.session_state.datos.get("registro_entreno",{})
        if not reg_all:
            st.markdown(C('<div style="text-align:center;padding:.85rem"><p style="color:var(--text3);font-size:.77rem;margin:0">Sin sesiones todavia</p></div>'),unsafe_allow_html=True)
        for fk in sorted(reg_all.keys(),reverse=True)[:7]:
            for ses in reg_all[fk]:
                ns=len(ses.get("series",[]))
                st.markdown(C(
                    f'<div class="meal-header"><span class="meal-title">🏋️ {ses["tipo"]}</span>'
                    f'<span class="badge bn">{fk}</span></div>'
                    f'<div style="display:flex;gap:.5rem;flex-wrap:wrap;font-size:.75rem;color:var(--text2)">'
                    f'<span style="font-weight:700;color:var(--orange)">{ses["duracion"]} min</span>'
                    f'<span>·</span><span>{ns} ejercicios</span><span>·</span><span>{ses.get("hora","")}</span></div>'
                    f'{"<p style=margin-top:.3rem;font-size:.72rem;color:var(--text3)>"+ses["notas"]+"</p>" if ses.get("notas") else ""}'
                ),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STATS / HISTORIAL
# ══════════════════════════════════════════════════════════════════════════════
with t_hist:
    hist_c=st.session_state.datos.get("historial_calorias",{})
    hist_m=st.session_state.datos.get("historial_macros",{})
    reg_e=st.session_state.datos.get("registro_entreno",{})
    if not hist_c:
        st.markdown(C('<div style="text-align:center;padding:1.5rem 0">'
                      '<div style="font-size:3rem;margin-bottom:.5rem">📊</div>'
                      '<div class="lbl lbl-orange" style="text-align:center">Sin historial todavia</div>'
                      '<p style="color:var(--text3);font-size:.77rem;margin:0">Empieza registrando alimentos en la pestana Kcal</p></div>'),
                    unsafe_allow_html=True)
    else:
        fechas=sorted(hist_c.keys())[-14:]
        vals=[hist_c.get(f,0) for f in fechas]
        etiq=[f[-5:] for f in fechas]
        obj_h=obj_cal()
        prom=round(sum(vals)/len(vals)) if vals else 0
        maxi=max(vals) if vals else 0
        dias_ok=sum(1 for v in vals if 0<v<=obj_h)
        total_r=len([v for v in vals if v>0])

        st.markdown(
            f'<div class="sgrid" style="margin-bottom:.85rem">'
            f'<div class="mini-stat"><div class="mini-val" style="color:var(--orange)">{prom}</div>'
            f'<div class="mini-lbl">Promedio kcal/dia</div></div>'
            f'<div class="mini-stat"><div class="mini-val" style="color:var(--green)">{dias_ok}</div>'
            f'<div class="mini-lbl">Dias en objetivo / {total_r}</div></div></div>',
            unsafe_allow_html=True)

        if vals:
            max_v=max(vals+[obj_h,1])
            bars='<div style="display:flex;align-items:flex-end;gap:4px;height:100px;padding-bottom:2px">'
            for et,vl in zip(etiq,vals):
                h=int(vl/max_v*100) if vl>0 else 2
                if vl>obj_h and vl>0: clr="linear-gradient(180deg,#e17055,#fab1a0)"
                elif vl>0:            clr="linear-gradient(180deg,#ff6b35,#fdcb6e)"
                else:                 clr="#e8eaed"
                bars+=(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px">'
                       f'<div style="flex:1;display:flex;align-items:flex-end;width:100%">'
                       f'<div style="width:100%;height:{h}%;background:{clr};border-radius:5px 5px 0 0;min-height:4px"></div></div>'
                       f'<div style="font-size:.48rem;font-weight:700;color:var(--text3);text-align:center;margin-top:3px">{et}</div></div>')
            bars+='</div>'
            st.markdown(C(
                f'<div class="lbl lbl-orange">Calorias diarias — 14 dias</div>{bars}'
                f'<div style="display:flex;gap:.5rem;margin-top:.6rem;flex-wrap:wrap">'
                f'<span class="badge bk" style="font-size:.52rem">Naranja = en objetivo</span>'
                f'<span class="badge bw" style="font-size:.52rem">Rojo = excedido</span></div>'
            ), unsafe_allow_html=True)

        dias_m=[d for d in fechas if d in hist_m and any(v>0 for v in hist_m[d].values())]
        if dias_m:
            pm={"prot":0.0,"carb":0.0,"grasa":0.0}
            for d in dias_m:
                for k in pm: pm[k]+=hist_m[d].get(k,0)
            n=len(dias_m); pm={k:round(v/n,1) for k,v in pm.items()}
            st.markdown(C(
                f'<div class="lbl lbl-orange">Macros promedio diario</div>'
                f'<div class="mgrid">'
                f'<div class="mini-stat"><div class="mini-val" style="color:var(--green)">{pm["prot"]}g</div><div class="mini-lbl">Proteina</div></div>'
                f'<div class="mini-stat"><div class="mini-val" style="color:var(--purple)">{pm["carb"]}g</div><div class="mini-lbl">Carbos</div></div>'
                f'<div class="mini-stat"><div class="mini-val" style="color:#b7860b">{pm["grasa"]}g</div><div class="mini-lbl">Grasas</div></div>'
                f'</div>'
            ), unsafe_allow_html=True)

        ses_t=sum(len(v) for v in reg_e.values())
        min_t=sum(s.get("duracion",0) for v in reg_e.values() for s in v)
        if ses_t>0:
            st.markdown(
                f'<div class="sgrid">'
                f'<div class="mini-stat"><div class="mini-val" style="color:var(--orange)">{ses_t}</div><div class="mini-lbl">Sesiones totales</div></div>'
                f'<div class="mini-stat"><div class="mini-val" style="color:var(--purple)">{round(min_t/60,1)}</div><div class="mini-lbl">Horas entrenando</div></div>'
                f'</div>', unsafe_allow_html=True)

        if st.button("🗑️ Borrar historial completo",key="btn_del_hist"):
            d=st.session_state.datos
            d["historial_calorias"]={}; d["historial_macros"]={}; d["diario_comidas"]={}
            save_datos(); st.success("Historial borrado."); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
with t_cfg:
    sdiv("Sesion activa")
    db_lbl="✅ Supabase conectado" if sb_ok() else "💾 Solo local (sin Supabase)"
    db_badge="bp" if sb_ok() else "bn"
    st.markdown(C(
        f'<div class="row"><span class="rl">Usuario</span><span class="rr">{st.session_state.user_email}</span></div>'
        f'<div class="row"><span class="rl">Base de datos</span><span class="rr"><span class="badge {db_badge}">{db_lbl}</span></span></div>'
        f'<div class="row"><span class="rl">Estado</span><span class="rr"><span class="badge bp">● Activo</span></span></div>'
    ), unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesion",key="btn_logout"):
        for k in ["logged_in","user_id","user_email","datos","scan_res","ia_res","ej_temp","sets_temp","dc_temp","calc_res"]:
            st.session_state.pop(k,None)
        st.rerun()

    sdiv("Proveedor de IA")
    st.markdown(C(
        '<div class="lbl lbl-orange">Comparativa</div>'
        '<div class="row"><span class="rl">🟢 Groq (recomendado)</span><span class="rr"><span class="badge bp">1500 req/dia · Gratis</span></span></div>'
        '<div class="row"><span class="rl">🔵 Gemini</span><span class="rr"><span class="badge bw">~20 req/dia</span></span></div>'
        '<p style="font-size:.73rem;color:var(--text3);margin-top:.5rem;margin-bottom:0">Groq: mas generosa, rapida y completamente gratuita.</p>'
    ), unsafe_allow_html=True)
    prov_sel=st.selectbox("",["Groq (recomendado)","Gemini"],
        index=0 if "Groq" in st.session_state.proveedor_ia else 1,key="prov_sel",label_visibility="collapsed")
    if st.button("💾 Cambiar proveedor",key="btn_prov"):
        st.session_state.proveedor_ia=prov_sel
        st.session_state.datos.setdefault("api_keys",{})["proveedor_ia"]=prov_sel
        save_datos(); st.success(f"✅ Proveedor: {prov_sel}"); st.rerun()

    sdiv("Groq API Key — Guardada en tu cuenta (1 sola vez)")
    st.markdown(C(
        '<div class="row"><span class="rl">1. Cuenta gratuita</span><span class="rr">console.groq.com/keys</span></div>'
        '<div class="row"><span class="rl">2. Pulsa</span><span class="rr">Create API Key</span></div>'
        '<div class="row"><span class="rl">3. Formato</span><span class="rr">gsk_...</span></div>'
        '<div class="row"><span class="rl">Se guarda en tu cuenta</span><span class="rr"><span class="badge bp">No la repitas nunca mas</span></span></div>'
    ), unsafe_allow_html=True)
    gi=st.text_input("Groq Key",value=st.session_state.groq_key,type="password",placeholder="gsk_...",key="gi")
    g1b,g2b=st.columns(2)
    with g1b:
        if st.button("💾 Guardar y vincular",key="btn_groq"):
            st.session_state.groq_key=gi.strip()
            ak=st.session_state.datos.setdefault("api_keys",{})
            ak["groq_key"]=gi.strip(); ak["proveedor_ia"]=st.session_state.proveedor_ia
            save_datos(); st.success("✅ Guardada en tu cuenta.")
    with g2b:
        if st.session_state.groq_key and st.button("⚡ Probar",key="btn_tg"):
            with st.spinner("Probando..."):
                prev=st.session_state.proveedor_ia; st.session_state.proveedor_ia="Groq (recomendado)"
                res=ia_call("Responde solo la palabra: OK"); st.session_state.proveedor_ia=prev
                st.success(f"✅ OK: {res[:50]}") if ("OK" in res or len(res)<80) else st.error(res[:150])

    sdiv("Gemini API Key — aistudio.google.com")
    mi=st.text_input("Gemini Key",value=st.session_state.gemini_key,type="password",placeholder="AIzaSy...",key="mi")
    mg1,mg2=st.columns(2)
    with mg1:
        if st.button("💾 Guardar y vincular",key="btn_gem"):
            st.session_state.gemini_key=mi.strip()
            st.session_state.datos.setdefault("api_keys",{})["gemini_key"]=mi.strip()
            save_datos(); st.success("✅ Guardada en tu cuenta.")
    with mg2:
        if st.session_state.gemini_key and st.button("⚡ Probar",key="btn_tm"):
            with st.spinner("Probando..."):
                prev=st.session_state.proveedor_ia; st.session_state.proveedor_ia="Gemini"
                res=ia_call("Responde solo la palabra: OK"); st.session_state.proveedor_ia=prev
                st.success(f"✅ OK: {res[:50]}") if ("OK" in res or len(res)<80) else st.error(res[:150])

    sdiv("Perfil personal")
    pf_c=get_pf()
    cfg1,cfg2=st.columns(2)
    with cfg1:
        cn=st.text_input("Nombre",value=pf_c.get("nombre",""),key="cn")
        cp2=st.number_input("Peso (kg)",30.0,250.0,float(pf_c.get("peso",75.0)),.5,key="cp2")
        ca3=st.number_input("Altura (cm)",100,250,int(pf_c.get("altura",175)),key="ca3")
    with cfg2:
        ce=st.number_input("Edad",10,100,int(pf_c.get("edad",25)),key="ce")
        coc=st.number_input("Obj. kcal/dia",800,6000,int(pf_c.get("objetivo_cal",2000)),50,key="coc")
        cpr=st.number_input("Obj. proteina (g)",0,400,int(pf_c.get("obj_prot",150)),5,key="cpr")
    cfg3,cfg4=st.columns(2)
    with cfg3: ccb=st.number_input("Obj. carbos (g)",0,800,int(pf_c.get("obj_carb",220)),5,key="ccb")
    with cfg4: cgr=st.number_input("Obj. grasas (g)",0,300,int(pf_c.get("obj_grasa",60)),5,key="cgr")
    if st.button("💾 Guardar perfil",key="btn_perfil"):
        st.session_state.datos.setdefault("perfil",{}).update(
            {"nombre":cn,"peso":cp2,"altura":ca3,"edad":ce,
             "objetivo_cal":coc,"obj_prot":cpr,"obj_carb":ccb,"obj_grasa":cgr})
        save_datos(); st.success("✅ Perfil guardado."); st.rerun()

    sdiv("Supabase — Base de datos en la nube")
    st.markdown(C(
        '<div class="lbl lbl-orange">URL CORRECTA (sin /rest/v1/ al final)</div>'
        '<div class="row"><span class="rl">✅ Correcto</span><span class="rr">https://xxxx.supabase.co</span></div>'
        '<div class="row"><span class="rl">❌ Incorrecto</span><span class="rr">https://xxxx.supabase.co/rest/v1/</span></div>'
        '<div class="row"><span class="rl">Configurar en</span><span class="rr">Streamlit → Manage app → Secrets</span></div>'
        f'<div class="row"><span class="rl">Estado actual</span>'
        f'<span class="rr"><span class="badge {"bp" if sb_ok() else "bw"}">{"✅ Conectado" if sb_ok() else "❌ No conectado"}</span></span></div>'
    ), unsafe_allow_html=True)

    sdiv("Acerca de")
    st.markdown(C(
        '<div class="row"><span class="rl">Version</span><span class="rr">FitAI Pro 5.2</span></div>'
        '<div class="row"><span class="rl">Stack</span><span class="rr">Streamlit · Groq · Gemini · Supabase</span></div>'
        '<div class="row"><span class="rl">Datos</span><span class="rr">Privados por usuario · RLS activo</span></div>'
        '<div class="row"><span class="rl">Hosting</span><span class="rr">Streamlit Community Cloud (gratis)</span></div>'
    ), unsafe_allow_html=True)

    # Restaurar API keys si hace falta al entrar a Config
    ak=st.session_state.datos.get("api_keys",{})
    if not st.session_state.groq_key   and ak.get("groq_key"):   st.session_state.groq_key   = ak["groq_key"]
    if not st.session_state.gemini_key and ak.get("gemini_key"): st.session_state.gemini_key = ak["gemini_key"]
