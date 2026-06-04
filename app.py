import streamlit as st
import google.generativeai as genai
import json
import os
import math
from datetime import date, datetime
from PIL import Image
import io

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FitAI Pro",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS RESPONSIVE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg:#0d0f14; --card:#161a23; --card2:#1b2030;
    --accent:#e8ff47; --accent2:#ff5c3a; --green:#39d98a; --blue:#4fa3ff;
    --text:#e8eaf0; --muted:#6b7280; --radius:14px;
}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{
    background:var(--bg)!important;color:var(--text)!important;
    font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
.block-container{max-width:700px!important;padding:1rem 1rem 5rem!important;margin:0 auto!important;}
.hero-title{font-family:'Bebas Neue',sans-serif!important;font-size:clamp(2.4rem,8vw,4rem)!important;
    color:var(--accent)!important;letter-spacing:.04em;line-height:1;margin-bottom:0;}
.hero-sub{font-size:.85rem;color:var(--muted);margin-top:.2rem;margin-bottom:1.5rem;}
.fit-card{background:var(--card);border:1px solid #252a35;border-radius:var(--radius);
    padding:1rem 1.1rem;margin-bottom:.8rem;}
.fit-card h4{font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:var(--accent);
    margin:0 0 .35rem 0;letter-spacing:.05em;}
.fit-card p,.fit-card li{font-size:.87rem;color:var(--text);margin:.15rem 0;}
.macro-pill{display:inline-block;border-radius:8px;padding:.18rem .55rem;
    font-size:.78rem;font-weight:600;margin:.1rem .15rem 0 0;}
.mp-p{background:#1e3a2a;color:#39d98a;}
.mp-c{background:#1e2a3a;color:#4fa3ff;}
.mp-f{background:#3a2a1e;color:#ffb347;}
.mp-cal{background:#2a1e3a;color:#c97fff;}
.badge-green{background:#1e3a2a;color:var(--green);border-radius:8px;
    padding:.15rem .55rem;font-size:.8rem;font-weight:600;}
.badge-red{background:#3a1e1e;color:var(--accent2);border-radius:8px;
    padding:.15rem .55rem;font-size:.8rem;font-weight:600;}
.cal-total{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;color:var(--accent);line-height:1;}
.cal-bar-bg{background:#1e2330;border-radius:999px;height:12px;width:100%;margin-top:.5rem;overflow:hidden;}
.cal-bar-fill{height:100%;border-radius:999px;transition:width .4s ease;}
.macro-ring-wrap{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin:.5rem 0;}
.macro-ring{text-align:center;font-size:.75rem;color:var(--muted);}
.macro-ring b{display:block;font-size:1rem;color:var(--text);}
.section-label{font-family:'Bebas Neue',sans-serif;font-size:1rem;letter-spacing:.1em;
    color:var(--muted);text-transform:uppercase;margin:.6rem 0 .3rem;}
div.stButton>button{background:var(--accent)!important;color:#0d0f14!important;
    font-family:'Bebas Neue',sans-serif!important;font-size:1.05rem!important;
    letter-spacing:.08em!important;border:none!important;border-radius:10px!important;
    padding:.6rem 1.2rem!important;width:100%!important;cursor:pointer!important;
    transition:opacity .15s ease!important;}
div.stButton>button:hover{opacity:.85!important;}
div[data-baseweb="input"] input,div[data-baseweb="select"] div,
div[data-baseweb="textarea"] textarea,.stNumberInput input{
    background:#1e2330!important;color:var(--text)!important;
    border:1px solid #2e3447!important;border-radius:10px!important;
    font-family:'DM Sans',sans-serif!important;}
[data-baseweb="tab-list"]{background:var(--card)!important;border-radius:10px!important;
    padding:4px!important;gap:3px!important;border:1px solid #252a35!important;}
[data-baseweb="tab"]{color:var(--muted)!important;font-family:'DM Sans',sans-serif!important;
    font-weight:500!important;border-radius:8px!important;padding:.4rem .8rem!important;font-size:.85rem!important;}
[aria-selected="true"][data-baseweb="tab"]{background:var(--accent)!important;color:#0d0f14!important;}
[data-testid="stFileUploader"]{border:2px dashed #2e3447!important;border-radius:var(--radius)!important;
    background:#161a23!important;padding:1rem!important;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:#2e3447;border-radius:999px;}
@media(max-width:480px){
    .block-container{padding:.5rem .5rem 5rem!important;}
    .cal-total{font-size:2.2rem;}
    div.stButton>button{font-size:.95rem!important;padding:.55rem .9rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES & DATOS BASE
# ─────────────────────────────────────────────
DATA_FILE = "fitai_data.json"

# Macros por 100g de alimentos comunes
ALIMENTOS_DB = {
    "Pollo a la plancha (100g)":    {"cal":165,"prot":31,"carb":0,"grasa":3.6},
    "Arroz cocido (100g)":          {"cal":130,"prot":2.7,"carb":28,"grasa":0.3},
    "Huevo entero (1 ud ~60g)":     {"cal":86, "prot":7.5,"carb":0.6,"grasa":6},
    "Claras de huevo (100g)":       {"cal":52, "prot":11,"carb":0.7,"grasa":0.2},
    "Pechuga de pavo (100g)":       {"cal":135,"prot":30,"carb":0,"grasa":1},
    "Atún en agua (100g)":          {"cal":116,"prot":26,"carb":0,"grasa":1},
    "Salmón (100g)":                {"cal":208,"prot":20,"carb":0,"grasa":13},
    "Ternera magra (100g)":         {"cal":170,"prot":26,"carb":0,"grasa":7},
    "Queso fresco 0% (100g)":       {"cal":62, "prot":11,"carb":3.3,"grasa":0.4},
    "Yogur griego (100g)":          {"cal":97, "prot":9,"carb":3.6,"grasa":5},
    "Leche semidesnatada (200ml)":  {"cal":92, "prot":6.6,"carb":9.4,"grasa":3.2},
    "Whey protein (30g)":           {"cal":114,"prot":24,"carb":3,"grasa":1.5},
    "Avena (100g)":                 {"cal":389,"prot":17,"carb":66,"grasa":7},
    "Pan integral (1 rebanada 35g)":{"cal":80, "prot":3.5,"carb":14,"grasa":1},
    "Pasta integral cocida (100g)": {"cal":124,"prot":5,"carb":25,"grasa":1},
    "Boniato cocido (100g)":        {"cal":90, "prot":2,"carb":21,"grasa":0.1},
    "Patata cocida (100g)":         {"cal":77, "prot":2,"carb":17,"grasa":0.1},
    "Lentejas cocidas (100g)":      {"cal":116,"prot":9,"carb":20,"grasa":0.4},
    "Garbanzos cocidos (100g)":     {"cal":164,"prot":8.9,"carb":27,"grasa":2.6},
    "Aguacate (100g)":              {"cal":160,"prot":2,"carb":9,"grasa":15},
    "Aceite de oliva (1 cdta 5ml)": {"cal":45, "prot":0,"carb":0,"grasa":5},
    "Almendras (30g)":              {"cal":174,"prot":6,"carb":6,"grasa":15},
    "Plátano mediano (120g)":       {"cal":107,"prot":1.3,"carb":27,"grasa":0.4},
    "Manzana mediana (150g)":       {"cal":78, "prot":0.4,"carb":21,"grasa":0.2},
    "Brócoli (100g)":               {"cal":34, "prot":2.8,"carb":7,"grasa":0.4},
    "Espinacas (100g)":             {"cal":23, "prot":2.9,"carb":3.6,"grasa":0.4},
    "Tomate (100g)":                {"cal":18, "prot":0.9,"carb":3.9,"grasa":0.2},
    "Pepino (100g)":                {"cal":15, "prot":0.7,"carb":3.6,"grasa":0.1},
}

DIETAS_TEMPLATE = {
    "Volumen limpio (≈2800 kcal)": {
        "objetivo": "Ganar masa muscular con mínima grasa",
        "macros": {"prot": 175, "carb": 350, "grasa": 75},
        "comidas": [
            {"nombre": "Desayuno", "alimentos": "Avena 80g + Whey 30g + Plátano + Leche 200ml", "cal": 580, "prot": 42, "carb": 82, "grasa": 10},
            {"nombre": "Media mañana", "alimentos": "Yogur griego 200g + Almendras 30g + Manzana", "cal": 330, "prot": 22, "carb": 30, "grasa": 16},
            {"nombre": "Almuerzo", "alimentos": "Arroz integral 150g + Pollo 200g + Brócoli + AOVE 10ml", "cal": 720, "prot": 72, "carb": 85, "grasa": 14},
            {"nombre": "Merienda", "alimentos": "Pan integral 70g + Atún 100g + Tomate", "cal": 290, "prot": 36, "carb": 28, "grasa": 3},
            {"nombre": "Cena", "alimentos": "Salmón 200g + Boniato 200g + Espinacas salteadas", "cal": 580, "prot": 45, "carb": 48, "grasa": 28},
            {"nombre": "Post-cena (opcional)", "alimentos": "Claras de huevo 200g + Queso fresco 0%", "cal": 220, "prot": 34, "carb": 7, "grasa": 3},
        ],
    },
    "Definición (≈1900 kcal)": {
        "objetivo": "Perder grasa conservando músculo",
        "macros": {"prot": 180, "carb": 160, "grasa": 60},
        "comidas": [
            {"nombre": "Desayuno", "alimentos": "Claras 4 + 1 huevo entero + Avena 50g + Café", "cal": 380, "prot": 38, "carb": 35, "grasa": 9},
            {"nombre": "Media mañana", "alimentos": "Yogur griego 0% 200g + Proteína en polvo", "cal": 250, "prot": 35, "carb": 10, "grasa": 3},
            {"nombre": "Almuerzo", "alimentos": "Pechuga pavo 200g + Patata cocida 150g + Verduras", "cal": 430, "prot": 62, "carb": 35, "grasa": 5},
            {"nombre": "Merienda", "alimentos": "Atún 100g + Pan integral 35g + Pepino", "cal": 230, "prot": 30, "carb": 18, "grasa": 2},
            {"nombre": "Cena", "alimentos": "Merluza/Pollo 200g + Brócoli + Espinacas + AOVE 5ml", "cal": 380, "prot": 48, "carb": 12, "grasa": 14},
            {"nombre": "Antes de dormir", "alimentos": "Queso fresco 0% 150g + Canela", "cal": 93, "prot": 17, "carb": 5, "grasa": 0.6},
        ],
    },
    "Mantenimiento (≈2300 kcal)": {
        "objetivo": "Mantener composición corporal actual",
        "macros": {"prot": 155, "carb": 260, "grasa": 70},
        "comidas": [
            {"nombre": "Desayuno", "alimentos": "Avena 60g + Leche + 2 Huevos + Fruta", "cal": 490, "prot": 28, "carb": 62, "grasa": 14},
            {"nombre": "Media mañana", "alimentos": "Fruta + Almendras 25g + Queso fresco", "cal": 270, "prot": 14, "carb": 25, "grasa": 13},
            {"nombre": "Almuerzo", "alimentos": "Arroz 120g + Ternera magra 150g + Ensalada AOVE", "cal": 600, "prot": 45, "carb": 60, "grasa": 18},
            {"nombre": "Merienda", "alimentos": "Plátano + Pan integral + Pavo 80g", "cal": 310, "prot": 26, "carb": 42, "grasa": 4},
            {"nombre": "Cena", "alimentos": "Salmón 150g + Garbanzos 100g + Verduras a la plancha", "cal": 540, "prot": 40, "carb": 42, "grasa": 21},
        ],
    },
    "Vegana alta proteína (≈2200 kcal)": {
        "objetivo": "Dieta plant-based equilibrada con proteína suficiente",
        "macros": {"prot": 140, "carb": 280, "grasa": 65},
        "comidas": [
            {"nombre": "Desayuno", "alimentos": "Avena 80g + Proteína vegana 30g + Plátano + Leche soja", "cal": 520, "prot": 35, "carb": 80, "grasa": 10},
            {"nombre": "Media mañana", "alimentos": "Hummus 100g + Pan integral + Tomate", "cal": 290, "prot": 12, "carb": 35, "grasa": 10},
            {"nombre": "Almuerzo", "alimentos": "Lentejas 200g + Arroz 100g + Verduras + AOVE", "cal": 590, "prot": 28, "carb": 95, "grasa": 12},
            {"nombre": "Merienda", "alimentos": "Aguacate + Pan integral + Espinacas batido", "cal": 350, "prot": 10, "carb": 30, "grasa": 22},
            {"nombre": "Cena", "alimentos": "Tofu 200g + Garbanzos 100g + Brócoli salteado AOVE", "cal": 470, "prot": 38, "carb": 35, "grasa": 20},
        ],
    },
}

# Ejercicios por grupo muscular con variantes y descripción
EJERCICIOS_GYM = {
    "🫁 Pecho": [
        {"nombre":"Press banca plano","tipo":"Fuerza/Hiper","equipo":"Barra","series_rec":"4","reps_rec":"6-12","descanso":"90s","notas":"Escapulas retraídas, toque suave al pecho"},
        {"nombre":"Press banca inclinado","tipo":"Hiper","equipo":"Barra/Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Ángulo 30-45°, activa clavicular"},
        {"nombre":"Press banca declinado","tipo":"Hiper","equipo":"Barra","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Activa porción esternocostal"},
        {"nombre":"Aperturas con mancuernas","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados"},
        {"nombre":"Fondos en paralelas","tipo":"Peso corporal","equipo":"Paralelas","series_rec":"3-4","reps_rec":"Máx","descanso":"90s","notas":"Inclina el torso hacia adelante para enfatizar pecho"},
        {"nombre":"Crossover en polea","tipo":"Aislamiento","equipo":"Poleas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Estira bien en la parte superior"},
        {"nombre":"Press con mancuernas neutro","tipo":"Hiper","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"75s","notas":"Agarre neutro, más amigable con hombro"},
    ],
    "🦾 Espalda": [
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3min","notas":"Espalda neutra, barra cerca del cuerpo"},
        {"nombre":"Dominadas","tipo":"Fuerza/Hiper","equipo":"Barra fija","series_rec":"4","reps_rec":"Máx","descanso":"90s","notas":"Rango completo, sin balanceo"},
        {"nombre":"Jalón al pecho","tipo":"Hiper","equipo":"Polea alta","series_rec":"4","reps_rec":"10-15","descanso":"75s","notas":"Lleva la barra a la barbilla, codos hacia abajo"},
        {"nombre":"Remo con barra","tipo":"Fuerza/Hiper","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Torso a 45°, barra al ombligo"},
        {"nombre":"Remo en polea baja","tipo":"Hiper","equipo":"Polea baja","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Pecho erguido, tirón al abdomen"},
        {"nombre":"Remo con mancuerna","tipo":"Hiper","equipo":"Mancuerna","series_rec":"3","reps_rec":"10-15/lado","descanso":"60s","notas":"Apoya una rodilla en banco"},
        {"nombre":"Pull-over","tipo":"Aislamiento","equipo":"Mancuerna/Polea","series_rec":"3","reps_rec":"15","descanso":"60s","notas":"Activa serrato y dorsal"},
        {"nombre":"Face pulls","tipo":"Salud hombro","equipo":"Polea alta","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Esencial para salud manguito rotador"},
    ],
    "🦵 Pierna": [
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3min","notas":"Rodillas siguen la dirección de los pies"},
        {"nombre":"Sentadilla frontal","tipo":"Fuerza/Hiper","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2min","notas":"Más cuádriceps, requiere movilidad tobillo"},
        {"nombre":"Prensa de piernas","tipo":"Hiper","equipo":"Máquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos = isquios; pies bajos = cuádriceps"},
        {"nombre":"Extensión de cuádriceps","tipo":"Aislamiento","equipo":"Máquina","series_rec":"3","reps_rec":"15-20","descanso":"60s","notas":"Contrae en la extensión completa"},
        {"nombre":"Femoral tumbado","tipo":"Aislamiento","equipo":"Máquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Aísla isquiotibiales"},
        {"nombre":"Peso muerto rumano","tipo":"Hiper","equipo":"Barra/Mancuernas","series_rec":"3-4","reps_rec":"10-12","descanso":"90s","notas":"Bisagra de cadera, isquios en tensión"},
        {"nombre":"Zancadas caminando","tipo":"Hiper","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-16/pierna","descanso":"75s","notas":"Rodilla trasera casi toca el suelo"},
        {"nombre":"Hip Thrust","tipo":"Glúteos","equipo":"Barra/Máquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Contracción máxima arriba, pelvis neutra"},
        {"nombre":"Elevación de gemelos","tipo":"Aislamiento","equipo":"Máquina/Libre","series_rec":"4","reps_rec":"15-25","descanso":"45s","notas":"Rango completo, pausa arriba y abajo"},
    ],
    "💪 Hombros": [
        {"nombre":"Press militar con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2min","notas":"De pie o sentado, core activado"},
        {"nombre":"Press Arnold","tipo":"Hiper","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Rotación completa, activa todos los fascículos"},
        {"nombre":"Elevaciones laterales","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Codo ligeramente flexionado, sube hasta la horizontal"},
        {"nombre":"Elevaciones frontales","tipo":"Aislamiento","equipo":"Disco/Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"45s","notas":"Hombro anterior, evitar si hay dolor"},
        {"nombre":"Pájaro (posterior deltoides)","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Torso a 90°, abre brazos como pájaros"},
        {"nombre":"Encogimientos de trapecios","tipo":"Fuerza","equipo":"Barra/Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Movimiento vertical puro, sin rotación"},
    ],
    "💪 Bíceps": [
        {"nombre":"Curl con barra","tipo":"Fuerza/Hiper","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"75s","notas":"Codos fijos a los lados del tronco"},
        {"nombre":"Curl con mancuernas alterno","tipo":"Hiper","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-14/brazo","descanso":"60s","notas":"Supina en la subida para más contracción"},
        {"nombre":"Curl martillo","tipo":"Braquial","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Agarre neutro, activa braquirradial"},
        {"nombre":"Curl predicador","tipo":"Aislamiento","equipo":"Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"No extiende completamente para evitar lesión"},
        {"nombre":"Curl en polea baja","tipo":"Aislamiento","equipo":"Polea","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Tensión constante en todo el rango"},
    ],
    "🦴 Tríceps": [
        {"nombre":"Press banca agarre cerrado","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Codos cerca del cuerpo, no abrir"},
        {"nombre":"Fondos en banco","tipo":"Peso corporal","equipo":"Banco","series_rec":"3","reps_rec":"15-20","descanso":"60s","notas":"Cuerpo cerca del banco, codos atrás"},
        {"nombre":"Extensión sobre la cabeza","tipo":"Hiper","equipo":"Mancuerna/Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Estiramiento máximo en la parte baja"},
        {"nombre":"Press francés","tipo":"Hiper","equipo":"Barra EZ","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Tumbado, baja a la frente"},
        {"nombre":"Pushdown en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"3-4","reps_rec":"15-20","descanso":"45s","notas":"Codos fijos, extensión completa abajo"},
        {"nombre":"Kickbacks","tipo":"Aislamiento","equipo":"Mancuerna","series_rec":"3","reps_rec":"15-20/brazo","descanso":"45s","notas":"Brazo paralelo al suelo, extrae solo el antebrazo"},
    ],
    "🧘 Core": [
        {"nombre":"Plancha","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3-4","reps_rec":"45-90s","descanso":"45s","notas":"Cuerpo recto, no elevar caderas"},
        {"nombre":"Plancha lateral","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"30-60s/lado","descanso":"30s","notas":"Cadera levantada, cuerpo alineado"},
        {"nombre":"Crunch en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Flexión de columna, no de cadera"},
        {"nombre":"Rueda abdominal","tipo":"Fuerza","equipo":"Rueda","series_rec":"3","reps_rec":"8-15","descanso":"60s","notas":"Empieza de rodillas, progresión de pie"},
        {"nombre":"Elevación de piernas colgado","tipo":"Fuerza","equipo":"Barra fija","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Pelvis en retroversión al subir"},
        {"nombre":"Dead bug","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"8-12/lado","descanso":"45s","notas":"Espalda baja pegada al suelo siempre"},
        {"nombre":"Cable woodchop","tipo":"Funcional","equipo":"Polea","series_rec":"3","reps_rec":"12-15/lado","descanso":"45s","notas":"Rotación desde cadera, no de hombros"},
    ],
    "🏃 Cardio": [
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint / 30s caminar","descanso":"—","notas":"FC máxima en sprints ~85-90%"},
        {"nombre":"Bicicleta estática tabata","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s esfuerzo / 10s pausa","descanso":"—","notas":"Protocolo Tabata clásico"},
        {"nombre":"Elíptica zona 2","tipo":"Cardio","equipo":"Elíptica","series_rec":"1","reps_rec":"30-45 min","descanso":"—","notas":"FC 120-140ppm, habla con dificultad leve"},
        {"nombre":"Remo ergómetro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500m","descanso":"2min","notas":"Excelente cardio + espalda/piernas"},
        {"nombre":"Saltar a la comba","tipo":"Cardio","equipo":"Comba","series_rec":"5","reps_rec":"2 min","descanso":"60s","notas":"Bajo impacto articular, alta quema"},
    ],
}

# ─────────────────────────────────────────────
# PERSISTENCIA
# ─────────────────────────────────────────────
def cargar_datos() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "historial_calorias": {},
        "historial_macros": {},
        "diario_comidas": {},
        "rutinas_custom": {},
        "dietas_custom": {},
        "perfil": {},
        "registro_entreno": {},
    }

def guardar_datos(datos: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"No se pudo guardar en disco: {e}")

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "analisis_resultado" not in st.session_state:
    st.session_state.analisis_resultado = None
if "ia_dieta_resultado" not in st.session_state:
    st.session_state.ia_dieta_resultado = None
if "ejercicios_temp" not in st.session_state:
    st.session_state.ejercicios_temp = []

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def hoy() -> str:
    return str(date.today())

def get_perfil() -> dict:
    return st.session_state.datos.get("perfil", {})

def get_objetivo_cal() -> int:
    return int(get_perfil().get("objetivo_cal", 2000))

def calorias_hoy() -> int:
    return st.session_state.datos["historial_calorias"].get(hoy(), 0)

def macros_hoy() -> dict:
    return st.session_state.datos.get("historial_macros", {}).get(hoy(), {"prot":0,"carb":0,"grasa":0})

def añadir_alimento(nombre: str, cal: int, prot: float, carb: float, grasa: float, comida: str) -> None:
    datos = st.session_state.datos
    # calorías
    datos["historial_calorias"][hoy()] = calorias_hoy() + cal
    # macros
    hm = datos.setdefault("historial_macros", {})
    dm = hm.setdefault(hoy(), {"prot":0,"carb":0,"grasa":0})
    dm["prot"]  = round(dm["prot"]  + prot,  1)
    dm["carb"]  = round(dm["carb"]  + carb,  1)
    dm["grasa"] = round(dm["grasa"] + grasa, 1)
    # diario
    dc = datos.setdefault("diario_comidas", {})
    lista = dc.setdefault(hoy(), [])
    lista.append({"comida": comida, "alimento": nombre, "cal": cal,
                  "prot": prot, "carb": carb, "grasa": grasa,
                  "hora": datetime.now().strftime("%H:%M")})
    guardar_datos(datos)

def calcular_tdee(peso, altura, edad, sexo, actividad) -> int:
    """Harris-Benedict + factor actividad"""
    if sexo == "Hombre":
        bmr = 88.36 + 13.4*peso + 4.8*altura - 5.7*edad
    else:
        bmr = 447.6 + 9.2*peso + 3.1*altura - 4.3*edad
    factores = {
        "Sedentario (sin ejercicio)": 1.2,
        "Ligero (1-2 días/semana)": 1.375,
        "Moderado (3-4 días/semana)": 1.55,
        "Activo (5-6 días/semana)": 1.725,
        "Muy activo (2 veces/día)": 1.9,
    }
    return int(bmr * factores.get(actividad, 1.55))

def barra_macro(valor, maximo, color):
    pct = min(valor/maximo*100, 100) if maximo > 0 else 0
    return f'<div class="cal-bar-bg"><div class="cal-bar-fill" style="width:{pct}%;background:{color};"></div></div>'

def gemini_call(prompt: str, imagen_bytes: bytes = None) -> str:
    try:
        genai.configure(api_key=st.session_state.gemini_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        if imagen_bytes:
            image = Image.open(io.BytesIO(imagen_bytes))
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "INVALID" in err.upper():
            return "❌ **API Key inválida.** Verifica en ⚙️ Config."
        elif "QUOTA" in err.upper():
            return "❌ **Cuota agotada.** Espera unos minutos."
        elif "SAFETY" in err.upper():
            return "⚠️ **Imagen bloqueada por filtros de seguridad.**"
        return f"❌ Error: {err}"

def extraer_calorias_texto(texto: str) -> int:
    import re
    try:
        m = re.search(r"[Tt]otal.*?(\d{2,4})\s*kcal", texto)
        if m: return int(m.group(1))
    except Exception:
        pass
    return 0

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<p class="hero-title">FITAI PRO</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Nutrición · Dietas · Gym · IA — Todo en uno · Gratis</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_nut, tab_dietas, tab_gym, tab_hist, tab_cfg = st.tabs([
    "🥗 Nutrición", "📋 Dietas", "🏋️ Gym", "📊 Historial", "⚙️ Config"
])

# ══════════════════════════════════════════════
# TAB 1 — NUTRICIÓN (centro de todo)
# ══════════════════════════════════════════════
with tab_nut:

    # ── Dashboard del día ──
    cal_hoy = calorias_hoy()
    obj_cal = get_objetivo_cal()
    macros  = macros_hoy()
    perfil  = get_perfil()
    obj_prot  = int(perfil.get("obj_prot",  150))
    obj_carb  = int(perfil.get("obj_carb",  220))
    obj_grasa = int(perfil.get("obj_grasa",  60))

    pct_cal = min(cal_hoy / obj_cal * 100, 100) if obj_cal else 0
    color_cal = "#e8ff47" if pct_cal < 90 else "#ff5c3a"
    restantes = max(obj_cal - cal_hoy, 0)
    estado_cal = "✅ En rango" if cal_hoy <= obj_cal else f"⚠️ +{cal_hoy - obj_cal} kcal excedido"

    st.markdown("##### 📊 Resumen de hoy")
    col_d1, col_d2 = st.columns([2,1])
    with col_d1:
        st.markdown(f'<div class="cal-total">{cal_hoy}</div>', unsafe_allow_html=True)
        st.caption(f"de {obj_cal} kcal · Restan **{restantes}** kcal")
        st.markdown(barra_macro(cal_hoy, obj_cal, color_cal), unsafe_allow_html=True)
    with col_d2:
        st.markdown(f"<br><br><span class='{'badge-green' if cal_hoy<=obj_cal else 'badge-red'}'>{estado_cal}</span>", unsafe_allow_html=True)

    # Macros del día
    st.markdown(
        f"""<div class="fit-card" style="margin-top:.8rem">
        <h4>Macros del día</h4>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.6rem;">
          <div>
            <span style="font-size:.75rem;color:#6b7280">🥩 Proteína</span>
            <div style="font-weight:700;color:#39d98a;font-size:1.1rem">{macros['prot']}g</div>
            <div style="font-size:.72rem;color:#6b7280">/{obj_prot}g</div>
            {barra_macro(macros['prot'], obj_prot, '#39d98a')}
          </div>
          <div>
            <span style="font-size:.75rem;color:#6b7280">🌾 Carbos</span>
            <div style="font-weight:700;color:#4fa3ff;font-size:1.1rem">{macros['carb']}g</div>
            <div style="font-size:.72rem;color:#6b7280">/{obj_carb}g</div>
            {barra_macro(macros['carb'], obj_carb, '#4fa3ff')}
          </div>
          <div>
            <span style="font-size:.75rem;color:#6b7280">🫒 Grasas</span>
            <div style="font-weight:700;color:#ffb347;font-size:1.1rem">{macros['grasa']}g</div>
            <div style="font-size:.72rem;color:#6b7280">/{obj_grasa}g</div>
            {barra_macro(macros['grasa'], obj_grasa, '#ffb347')}
          </div>
        </div></div>""",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Scanner IA con foto ──
    st.markdown("##### 📸 Scanner de alimentos con IA")
    if not st.session_state.gemini_key:
        st.warning("⚠️ Configura tu API Key en **⚙️ Config** para usar el scanner IA.")
    else:
        img_file = st.file_uploader("Sube foto del plato", type=["jpg","jpeg","png","webp"],
                                     help="Haz la foto con el móvil y súbela", key="up_scanner")
        if img_file:
            st.image(img_file, caption="Foto cargada", use_container_width=True)
            comida_foto = st.selectbox("¿Qué comida es?", ["Desayuno","Media mañana","Almuerzo","Merienda","Cena","Extra"], key="sel_comida_foto")
            if st.button("🔍 Analizar con Gemini 2.5 Flash", key="btn_scan"):
                with st.spinner("Analizando imagen..."):
                    prompt_scan = """Eres un nutricionista experto. Analiza esta imagen y responde SIEMPRE en español con este formato exacto:

**🍽️ Alimentos detectados:**
- [alimento] — aprox. [X] kcal · P:[Xg] C:[Xg] G:[Xg]
(continúa para cada alimento)

**🔥 TOTAL: [NNN] kcal | P:[Xg] C:[Xg] G:[Xg]**

**💡 Valoración nutricional:** [frase breve: equilibrio macro, calidad nutricional, sugerencia si aplica]

Si no hay comida en la imagen, indícalo claramente."""
                    resultado = gemini_call(prompt_scan, img_file.read())
                    st.session_state.analisis_resultado = resultado

        if st.session_state.analisis_resultado:
            st.markdown(f'<div class="fit-card">{st.session_state.analisis_resultado}</div>', unsafe_allow_html=True)
            cals_d = extraer_calorias_texto(st.session_state.analisis_resultado)
            if cals_d > 0:
                col_sc1, col_sc2 = st.columns(2)
                with col_sc1:
                    if st.button(f"✅ Registrar ~{cals_d} kcal", key="btn_reg_scan"):
                        comida_n = st.session_state.get("sel_comida_foto", "Extra")
                        añadir_alimento("📸 Analizado por IA", cals_d, 0, 0, 0, comida_n)
                        st.session_state.analisis_resultado = None
                        st.success("¡Registrado!")
                        st.rerun()
                with col_sc2:
                    if st.button("🗑️ Descartar", key="btn_disc_scan"):
                        st.session_state.analisis_resultado = None
                        st.rerun()

    st.divider()

    # ── Registro desde base de datos ──
    st.markdown("##### 🗂️ Registrar desde base de alimentos")
    col_al1, col_al2 = st.columns([3,1])
    with col_al1:
        alim_sel = st.selectbox("Alimento", list(ALIMENTOS_DB.keys()), key="sel_alim")
    with col_al2:
        cantidad_g = st.number_input("g/und", min_value=1, max_value=1000, value=100, key="cant_alim")

    alim_data = ALIMENTOS_DB[alim_sel]
    factor = cantidad_g / 100
    cal_a  = round(alim_data["cal"]  * factor)
    prot_a = round(alim_data["prot"] * factor, 1)
    carb_a = round(alim_data["carb"] * factor, 1)
    gras_a = round(alim_data["grasa"]* factor, 1)

    st.markdown(
        f"""<div class="fit-card">
        <span class="macro-pill mp-cal">🔥 {cal_a} kcal</span>
        <span class="macro-pill mp-p">P {prot_a}g</span>
        <span class="macro-pill mp-c">C {carb_a}g</span>
        <span class="macro-pill mp-f">G {gras_a}g</span>
        </div>""",
        unsafe_allow_html=True,
    )
    comida_sel2 = st.selectbox("Comida del día", ["Desayuno","Media mañana","Almuerzo","Merienda","Cena","Extra"], key="sel_comida2")
    if st.button("➕ Añadir al diario", key="btn_add_db"):
        añadir_alimento(f"{alim_sel} ({cantidad_g}g)", cal_a, prot_a, carb_a, gras_a, comida_sel2)
        st.success(f"✅ {alim_sel} registrado — {cal_a} kcal")
        st.rerun()

    st.divider()

    # ── Registro manual ──
    st.markdown("##### ✏️ Registro manual libre")
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns([3,1,1,1,2])
    with col_m1: nom_m = st.text_input("Alimento", placeholder="Mi plato casero", label_visibility="collapsed", key="nom_man")
    with col_m2: cal_m = st.number_input("kcal", min_value=0, max_value=5000, value=0, step=5, label_visibility="collapsed", key="cal_man")
    with col_m3: pro_m = st.number_input("P(g)", min_value=0.0, max_value=300.0, value=0.0, step=0.5, label_visibility="collapsed", key="pro_man")
    with col_m4: car_m = st.number_input("C(g)", min_value=0.0, max_value=500.0, value=0.0, step=0.5, label_visibility="collapsed", key="car_man")
    with col_m5: com_m = st.selectbox("Comida", ["Desayuno","Media mañana","Almuerzo","Merienda","Cena","Extra"], label_visibility="collapsed", key="com_man")
    if st.button("➕ Registrar manual", key="btn_man"):
        if cal_m > 0:
            añadir_alimento(nom_m or "Alimento libre", cal_m, pro_m, car_m, 0.0, com_m)
            st.success(f"✅ {nom_m or 'Alimento'}: {cal_m} kcal registradas")
            st.rerun()
        else:
            st.warning("Introduce kcal > 0.")

    st.divider()

    # ── Diario del día ──
    st.markdown("##### 📓 Diario de hoy")
    diario_hoy = st.session_state.datos.get("diario_comidas", {}).get(hoy(), [])
    if not diario_hoy:
        st.info("Aún no has registrado nada hoy. ¡Empieza a registrar!")
    else:
        comidas_grupo = {}
        for item in diario_hoy:
            comidas_grupo.setdefault(item["comida"], []).append(item)
        for comida_nombre, items in comidas_grupo.items():
            total_c = sum(i["cal"] for i in items)
            rows = "".join(
                f'<div style="display:flex;justify-content:space-between;font-size:.83rem;padding:.15rem 0;border-bottom:1px solid #252a35;">'
                f'<span>{i["hora"]} · {i["alimento"]}</span>'
                f'<span style="color:var(--accent)">{i["cal"]} kcal</span></div>'
                for i in items
            )
            st.markdown(
                f'<div class="fit-card"><h4>{comida_nombre} — {total_c} kcal</h4>{rows}</div>',
                unsafe_allow_html=True,
            )

    if st.button("🔄 Resetear diario de hoy", key="btn_reset_dia"):
        st.session_state.datos["historial_calorias"][hoy()] = 0
        st.session_state.datos.setdefault("historial_macros", {})[hoy()] = {"prot":0,"carb":0,"grasa":0}
        st.session_state.datos.setdefault("diario_comidas", {})[hoy()] = []
        guardar_datos(st.session_state.datos)
        st.success("Diario reseteado.")
        st.rerun()


# ══════════════════════════════════════════════
# TAB 2 — DIETAS
# ══════════════════════════════════════════════
with tab_dietas:

    subtab_ver, subtab_calc, subtab_ia, subtab_custom = st.tabs([
        "📋 Planes", "🧮 Calculadora", "🤖 IA Dietista", "✏️ Mi dieta"
    ])

    # ── VER PLANES ──
    with subtab_ver:
        st.markdown("#### Planes de nutrición")
        plan_sel = st.selectbox("Selecciona un plan", list(DIETAS_TEMPLATE.keys()), key="sel_plan")
        plan = DIETAS_TEMPLATE[plan_sel]

        total_plan_cal = sum(c["cal"] for c in plan["comidas"])
        total_plan_p   = sum(c["prot"] for c in plan["comidas"])
        total_plan_c   = sum(c["carb"] for c in plan["comidas"])
        total_plan_g   = sum(c["grasa"] for c in plan["comidas"])

        st.markdown(
            f"""<div class="fit-card">
            <h4>🎯 {plan_sel}</h4>
            <p>Objetivo: {plan['objetivo']}</p>
            <div style="margin-top:.5rem">
            <span class="macro-pill mp-cal">🔥 {total_plan_cal} kcal</span>
            <span class="macro-pill mp-p">P {total_plan_p}g</span>
            <span class="macro-pill mp-c">C {total_plan_c}g</span>
            <span class="macro-pill mp-f">G {total_plan_g}g</span>
            </div></div>""",
            unsafe_allow_html=True,
        )

        for comida in plan["comidas"]:
            st.markdown(
                f"""<div class="fit-card">
                <h4>{comida['nombre']}</h4>
                <p style="color:#b0b8c8">{comida['alimentos']}</p>
                <div style="margin-top:.4rem">
                <span class="macro-pill mp-cal">🔥 {comida['cal']} kcal</span>
                <span class="macro-pill mp-p">P {comida['prot']}g</span>
                <span class="macro-pill mp-c">C {comida['carb']}g</span>
                <span class="macro-pill mp-f">G {comida['grasa']}g</span>
                </div></div>""",
                unsafe_allow_html=True,
            )

        if st.button("📌 Usar este plan como objetivo macro", key="btn_usar_plan"):
            datos = st.session_state.datos
            datos.setdefault("perfil", {}).update({
                "objetivo_cal": total_plan_cal,
                "obj_prot": total_plan_p,
                "obj_carb": total_plan_c,
                "obj_grasa": total_plan_g,
            })
            guardar_datos(datos)
            st.success(f"✅ Objetivos actualizados: {total_plan_cal} kcal | P{total_plan_p}g C{total_plan_c}g G{total_plan_g}g")
            st.rerun()

    # ── CALCULADORA TDEE ──
    with subtab_calc:
        st.markdown("#### 🧮 Calculadora TDEE & Macros")
        st.markdown(
            '<div class="fit-card"><p>Calcula tus calorías de mantenimiento y distribución óptima de macros según tu objetivo.</p></div>',
            unsafe_allow_html=True,
        )
        perfil = get_perfil()
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            peso_c  = st.number_input("Peso (kg)", 30.0, 250.0, float(perfil.get("peso", 75)), 0.5, key="c_peso")
            altura_c = st.number_input("Altura (cm)", 100, 250, int(perfil.get("altura", 175)), key="c_alt")
        with col_c2:
            edad_c  = st.number_input("Edad", 10, 100, int(perfil.get("edad", 25)), key="c_edad")
            sexo_c  = st.selectbox("Sexo biológico", ["Hombre","Mujer"], key="c_sexo")

        actividad_c = st.selectbox("Nivel de actividad", [
            "Sedentario (sin ejercicio)",
            "Ligero (1-2 días/semana)",
            "Moderado (3-4 días/semana)",
            "Activo (5-6 días/semana)",
            "Muy activo (2 veces/día)",
        ], index=2, key="c_act")

        objetivo_c = st.selectbox("Objetivo", [
            "Pérdida de grasa (déficit -300 kcal)",
            "Pérdida de grasa agresiva (déficit -500 kcal)",
            "Mantenimiento",
            "Volumen limpio (superávit +200 kcal)",
            "Volumen (superávit +400 kcal)",
        ], key="c_obj")

        if st.button("⚡ Calcular", key="btn_calc_tdee"):
            tdee = calcular_tdee(peso_c, altura_c, edad_c, sexo_c, actividad_c)
            ajuste = {
                "Pérdida de grasa (déficit -300 kcal)": -300,
                "Pérdida de grasa agresiva (déficit -500 kcal)": -500,
                "Mantenimiento": 0,
                "Volumen limpio (superávit +200 kcal)": 200,
                "Volumen (superávit +400 kcal)": 400,
            }[objetivo_c]
            calorias_obj = tdee + ajuste
            # Distribución macro
            if "Pérdida" in objetivo_c:
                prot = round(peso_c * 2.2)
                grasa = round(peso_c * 1.0)
                carb_cal = calorias_obj - prot*4 - grasa*9
                carb = max(round(carb_cal / 4), 50)
            elif "Volumen" in objetivo_c:
                prot = round(peso_c * 1.8)
                grasa = round(peso_c * 1.1)
                carb_cal = calorias_obj - prot*4 - grasa*9
                carb = max(round(carb_cal / 4), 100)
            else:
                prot = round(peso_c * 2.0)
                grasa = round(peso_c * 1.0)
                carb_cal = calorias_obj - prot*4 - grasa*9
                carb = max(round(carb_cal / 4), 80)

            imc = round(peso_c / ((altura_c/100)**2), 1)
            cat_imc = ("Bajo peso" if imc < 18.5 else "Normo peso" if imc < 25
                       else "Sobrepeso" if imc < 30 else "Obesidad")

            st.markdown(
                f"""<div class="fit-card">
                <h4>📊 Tus resultados</h4>
                <p>🔥 <b>TDEE (mantenimiento):</b> {tdee} kcal/día</p>
                <p>🎯 <b>Objetivo diario:</b> {calorias_obj} kcal/día</p>
                <p>⚖️ <b>IMC:</b> {imc} — {cat_imc}</p>
                <div style="margin-top:.6rem">
                <span class="macro-pill mp-p">🥩 Proteína: {prot}g/día</span>
                <span class="macro-pill mp-c">🌾 Carbos: {carb}g/día</span>
                <span class="macro-pill mp-f">🫒 Grasas: {grasa}g/día</span>
                </div></div>""",
                unsafe_allow_html=True,
            )

            if st.button("💾 Guardar estos objetivos", key="btn_save_calc"):
                datos = st.session_state.datos
                datos.setdefault("perfil", {}).update({
                    "peso": peso_c, "altura": altura_c, "edad": edad_c,
                    "objetivo_cal": calorias_obj,
                    "obj_prot": prot, "obj_carb": carb, "obj_grasa": grasa,
                })
                guardar_datos(datos)
                st.success("✅ Objetivos guardados. Se reflejarán en Nutrición.")
                st.rerun()

    # ── IA DIETISTA ──
    with subtab_ia:
        st.markdown("#### 🤖 IA Dietista personalizada")
        if not st.session_state.gemini_key:
            st.warning("⚠️ Configura tu API Key en **⚙️ Config**.")
        else:
            st.markdown(
                '<div class="fit-card"><p>Describe tu situación y te generaré un plan de dieta completamente personalizado con macros, horarios y lista de compra.</p></div>',
                unsafe_allow_html=True,
            )
            perfil = get_perfil()
            col_ia1, col_ia2 = st.columns(2)
            with col_ia1:
                ia_peso    = st.number_input("Peso (kg)", 30.0, 250.0, float(perfil.get("peso", 75)), 0.5, key="ia_peso")
                ia_altura  = st.number_input("Altura (cm)", 100, 250, int(perfil.get("altura", 175)), key="ia_alt")
                ia_edad    = st.number_input("Edad", 10, 100, int(perfil.get("edad", 25)), key="ia_edad")
            with col_ia2:
                ia_sexo    = st.selectbox("Sexo", ["Hombre","Mujer"], key="ia_sexo")
                ia_obj     = st.selectbox("Objetivo", [
                    "Perder grasa","Ganar músculo","Mantenimiento",
                    "Mejorar rendimiento deportivo","Salud general",
                ], key="ia_obj")
                ia_act     = st.selectbox("Actividad", [
                    "Sedentario","Ligero","Moderado","Activo","Muy activo"
                ], key="ia_act2")

            ia_restricciones = st.multiselect("Restricciones / preferencias", [
                "Sin gluten","Sin lactosa","Vegetariano","Vegano",
                "Sin cerdo","Sin mariscos","Bajo en sodio","Bajo en azúcar",
            ], key="ia_rest")
            ia_extra = st.text_area("Contexto adicional (opcional)",
                placeholder="Ej: Tengo el colesterol alto, trabajo de noche, tengo intolerancia a la fructosa...",
                key="ia_extra", height=80)

            if st.button("🤖 Generar plan personalizado", key="btn_ia_dieta"):
                restricciones_str = ", ".join(ia_restricciones) if ia_restricciones else "ninguna"
                prompt_dieta = f"""Eres un dietista-nutricionista experto. Crea un plan de dieta completo y personalizado en español para:
- Perfil: {ia_sexo}, {ia_edad} años, {ia_peso}kg, {ia_altura}cm
- Objetivo: {ia_obj}
- Nivel de actividad: {ia_act}
- Restricciones: {restricciones_str}
- Info adicional: {ia_extra or 'ninguna'}

El plan debe incluir:
1. **Calorías diarias recomendadas** y distribución de macros (proteína, carbohidratos, grasas en gramos)
2. **Plan de 5-6 comidas diarias** con alimentos específicos, cantidades en gramos y calorías por comida
3. **Timing nutricional** (qué comer antes/después del ejercicio si aplica)
4. **Lista de compra semanal** con los alimentos clave
5. **3 consejos nutricionales clave** para su objetivo específico

Sé específico con cantidades. Usa formato estructurado con emojis para facilitar la lectura."""

                with st.spinner("Generando tu plan personalizado con IA..."):
                    resultado = gemini_call(prompt_dieta)
                    st.session_state.ia_dieta_resultado = resultado

            if st.session_state.ia_dieta_resultado:
                st.markdown(
                    f'<div class="fit-card">{st.session_state.ia_dieta_resultado}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("🔄 Generar otro plan", key="btn_regen"):
                    st.session_state.ia_dieta_resultado = None
                    st.rerun()

    # ── DIETA CUSTOM ──
    with subtab_custom:
        st.markdown("#### ✏️ Crea tu dieta personalizada")
        st.markdown(
            '<div class="fit-card"><p>Diseña tu propio plan de dieta día a día y guárdalo para consultarlo en cualquier momento.</p></div>',
            unsafe_allow_html=True,
        )

        dietas_custom = st.session_state.datos.get("dietas_custom", {})

        if dietas_custom:
            st.markdown("**Tus dietas guardadas:**")
            dc_sel = st.selectbox("Ver dieta", ["— Crear nueva —"] + list(dietas_custom.keys()), key="dc_view")
            if dc_sel != "— Crear nueva —":
                dc = dietas_custom[dc_sel]
                st.markdown(f'<div class="fit-card"><h4>{dc_sel}</h4><p>{dc.get("notas","")}</p></div>', unsafe_allow_html=True)
                for comp in dc.get("comidas", []):
                    st.markdown(
                        f"""<div class="fit-card">
                        <h4>{comp['nombre']}</h4>
                        <p style="color:#b0b8c8">{comp['alimentos']}</p>
                        <span class="macro-pill mp-cal">{comp.get('cal',0)} kcal</span>
                        <span class="macro-pill mp-p">P {comp.get('prot',0)}g</span>
                        <span class="macro-pill mp-c">C {comp.get('carb',0)}g</span>
                        <span class="macro-pill mp-f">G {comp.get('grasa',0)}g</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                if st.button("🗑️ Eliminar esta dieta", key="btn_del_dc"):
                    del st.session_state.datos["dietas_custom"][dc_sel]
                    guardar_datos(st.session_state.datos)
                    st.success("Dieta eliminada.")
                    st.rerun()

        st.divider()
        st.markdown("**Nueva dieta:**")
        nc_nombre = st.text_input("Nombre de la dieta", placeholder="Mi dieta de verano", key="nc_nom")
        nc_notas  = st.text_area("Notas / descripción", placeholder="Objetivo, duración, observaciones...", height=60, key="nc_not")

        if "comidas_temp_dc" not in st.session_state:
            st.session_state.comidas_temp_dc = []

        st.markdown("**Añadir comida al plan:**")
        col_nc1, col_nc2 = st.columns([2,1])
        with col_nc1:
            nc_cn = st.text_input("Nombre comida", placeholder="Almuerzo", key="nc_cn")
            nc_al = st.text_area("Alimentos y cantidades", placeholder="Pollo 150g, Arroz 100g, Brócoli 100g", height=60, key="nc_al")
        with col_nc2:
            nc_cal = st.number_input("kcal", 0, 3000, 0, 10, key="nc_cal")
            nc_pr  = st.number_input("Prot (g)", 0.0, 200.0, 0.0, 0.5, key="nc_pr")
            nc_cb  = st.number_input("Carb (g)", 0.0, 500.0, 0.0, 0.5, key="nc_cb")
            nc_gr  = st.number_input("Gras (g)", 0.0, 200.0, 0.0, 0.5, key="nc_gr")

        if st.button("➕ Añadir comida", key="btn_add_nc"):
            if nc_cn:
                st.session_state.comidas_temp_dc.append({
                    "nombre": nc_cn, "alimentos": nc_al,
                    "cal": nc_cal, "prot": nc_pr, "carb": nc_cb, "grasa": nc_gr,
                })
                st.success(f"'{nc_cn}' añadida.")
            else:
                st.warning("Escribe el nombre de la comida.")

        if st.session_state.comidas_temp_dc:
            total_dc = sum(c["cal"] for c in st.session_state.comidas_temp_dc)
            st.markdown(f"**{len(st.session_state.comidas_temp_dc)} comidas · {total_dc} kcal totales**")
            for i, c in enumerate(st.session_state.comidas_temp_dc):
                st.markdown(f"&nbsp;&nbsp;{i+1}. {c['nombre']} — {c['cal']} kcal")

        if st.button("💾 Guardar dieta", key="btn_save_dc"):
            if not nc_nombre:
                st.warning("Dale un nombre a la dieta.")
            elif not st.session_state.comidas_temp_dc:
                st.warning("Añade al menos una comida.")
            else:
                datos = st.session_state.datos
                datos.setdefault("dietas_custom", {})[nc_nombre] = {
                    "notas": nc_notas,
                    "comidas": st.session_state.comidas_temp_dc.copy(),
                }
                guardar_datos(datos)
                st.session_state.comidas_temp_dc = []
                st.success(f"✅ Dieta '{nc_nombre}' guardada.")
                st.rerun()


# ══════════════════════════════════════════════
# TAB 3 — GYM
# ══════════════════════════════════════════════
with tab_gym:

    subtab_ej, subtab_rut, subtab_reg = st.tabs(["💪 Ejercicios", "📋 Rutinas", "📝 Registro"])

    # ── BIBLIOTECA DE EJERCICIOS ──
    with subtab_ej:
        st.markdown("#### 💪 Biblioteca de ejercicios")
        grupo_sel = st.selectbox("Grupo muscular", list(EJERCICIOS_GYM.keys()), key="sel_grupo")
        ejercicios_grupo = EJERCICIOS_GYM[grupo_sel]

        for ej in ejercicios_grupo:
            tipo_color = {
                "Fuerza": "#ff5c3a", "Fuerza/Hiper": "#ffb347",
                "Hiper": "#4fa3ff", "Aislamiento": "#c97fff",
                "Peso corporal": "#39d98a", "Cardio": "#e8ff47",
                "Estabilidad": "#4fa3ff", "Funcional": "#39d98a",
                "Glúteos": "#ff9eb5", "Salud hombro": "#39d98a",
                "Braquial": "#c97fff",
            }.get(ej["tipo"], "#6b7280")
            st.markdown(
                f"""<div class="fit-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:.3rem">
                    <h4 style="margin:0">{ej['nombre']}</h4>
                    <span style="background:{tipo_color}22;color:{tipo_color};border-radius:6px;padding:.1rem .5rem;font-size:.75rem;font-weight:700">{ej['tipo']}</span>
                </div>
                <p style="margin-top:.4rem">🏋️ <b>Equipo:</b> {ej['equipo']}</p>
                <p>📦 <b>Series:</b> {ej['series_rec']} &nbsp;|&nbsp; 🔁 <b>Reps:</b> {ej['reps_rec']} &nbsp;|&nbsp; ⏱ <b>Descanso:</b> {ej['descanso']}</p>
                <p style="color:#9ba3b0;font-style:italic">💡 {ej['notas']}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    # ── RUTINAS ──
    with subtab_rut:
        st.markdown("#### 📋 Rutinas de entrenamiento")

        RUTINAS_DEFAULT = {
            "Push/Pull/Legs — Push": {
                "descripcion": "Sesión de empuje: pecho, hombros, tríceps",
                "ejercicios": [
                    {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Press inclinado mancuernas","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Press militar mancuernas","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
                    {"ejercicio":"Pushdown polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
                    {"ejercicio":"Extensión sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
                ],
            },
            "Push/Pull/Legs — Pull": {
                "descripcion": "Sesión de tirón: espalda, bíceps",
                "ejercicios": [
                    {"ejercicio":"Dominadas","series":4,"reps":"Máx","peso":"Corporal","descanso":"90s","notas":""},
                    {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Jalón al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Remo en polea baja","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
                    {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
                ],
            },
            "Push/Pull/Legs — Legs": {
                "descripcion": "Sesión de piernas: cuádriceps, isquios, glúteos, gemelos",
                "ejercicios": [
                    {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-8","peso":"","descanso":"2-3min","notas":""},
                    {"ejercicio":"Prensa de piernas","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Peso muerto rumano","series":3,"reps":"10-12","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Femoral tumbado","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
                    {"ejercicio":"Hip Thrust","series":4,"reps":"12-15","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Elevación de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
                ],
            },
            "Full Body (3 días/semana)": {
                "descripcion": "Sesión completa para principiantes o mantenimiento",
                "ejercicios": [
                    {"ejercicio":"Sentadilla con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Press banca plano","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Peso muerto convencional","series":3,"reps":"6-8","peso":"","descanso":"2min","notas":""},
                    {"ejercicio":"Press militar con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Dominadas","series":3,"reps":"Máx","peso":"Corporal","descanso":"90s","notas":""},
                    {"ejercicio":"Plancha","series":3,"reps":"60s","peso":"","descanso":"45s","notas":""},
                ],
            },
            "Upper/Lower — Upper": {
                "descripcion": "Tren superior: pecho, espalda, hombros, brazos",
                "ejercicios": [
                    {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Press inclinado mancuernas","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Jalón al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Elevaciones laterales","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
                    {"ejercicio":"Curl barra EZ","series":3,"reps":"10-12","peso":"","descanso":"60s","notas":""},
                    {"ejercicio":"Pushdown en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
                ],
            },
            "Upper/Lower — Lower": {
                "descripcion": "Tren inferior: cuádriceps, isquios, glúteos, core",
                "ejercicios": [
                    {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-10","peso":"","descanso":"2min","notas":""},
                    {"ejercicio":"Peso muerto rumano","series":4,"reps":"8-12","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Prensa de piernas","series":3,"reps":"12-15","peso":"","descanso":"90s","notas":""},
                    {"ejercicio":"Femoral tumbado","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
                    {"ejercicio":"Zancadas caminando","series":3,"reps":"12/pierna","peso":"","descanso":"75s","notas":""},
                    {"ejercicio":"Elevación de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
                    {"ejercicio":"Crunch en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
                ],
            },
            "HIIT + Core": {
                "descripcion": "Alta intensidad + core. 30-40 min",
                "ejercicios": [
                    {"ejercicio":"Burpees","series":5,"reps":"30s trabajo / 15s pausa","peso":"","descanso":"30s","notas":""},
                    {"ejercicio":"Mountain climbers","series":5,"reps":"30s trabajo / 15s pausa","peso":"","descanso":"30s","notas":""},
                    {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
                    {"ejercicio":"Sprint en sitio","series":6,"reps":"20s sprint / 10s pausa","peso":"","descanso":"—","notas":""},
                    {"ejercicio":"Plancha","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
                    {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""},
                ],
            },
        }

        todas_rutinas = {**RUTINAS_DEFAULT, **st.session_state.datos.get("rutinas_custom", {})}
        rut_sel = st.selectbox("Selecciona rutina", list(todas_rutinas.keys()), key="sel_rut2")
        rut = todas_rutinas[rut_sel]

        if isinstance(rut, dict) and "descripcion" in rut:
            desc = rut["descripcion"]
            ejercicios_rut = rut["ejercicios"]
        else:
            desc = ""
            ejercicios_rut = rut

        if desc:
            st.caption(desc)

        for ej in ejercicios_rut:
            peso_str = f" · 🏋️ {ej['peso']}" if ej.get("peso") else ""
            notas_str = f"<br><span style='color:#9ba3b0;font-size:.8rem;font-style:italic'>💡 {ej['notas']}</span>" if ej.get("notas") else ""
            st.markdown(
                f"""<div class="fit-card">
                <h4>{ej['ejercicio']}</h4>
                <p>📦 <b>Series:</b> {ej['series']} &nbsp;|&nbsp;
                   🔁 <b>Reps:</b> {ej['reps']} &nbsp;|&nbsp;
                   ⏱ <b>Descanso:</b> {ej['descanso']}{peso_str}</p>{notas_str}
                </div>""",
                unsafe_allow_html=True,
            )

        st.divider()
        with st.expander("➕ Crear rutina personalizada"):
            nr_nombre = st.text_input("Nombre", placeholder="Mi rutina personalizada", key="nr_nom")
            nr_desc   = st.text_input("Descripción (opcional)", placeholder="Lunes - Pecho/Tríceps", key="nr_desc")

            st.markdown("**Añadir ejercicio:**")
            col_r1,col_r2,col_r3,col_r4,col_r5 = st.columns([3,1,2,2,2])
            with col_r1: rn = st.text_input("Ejercicio", placeholder="Sentadilla", key="rn", label_visibility="collapsed")
            with col_r2: rs = st.number_input("Series", 1, 20, 3, key="rs", label_visibility="collapsed")
            with col_r3: rr = st.text_input("Reps", placeholder="10-12", key="rr", label_visibility="collapsed")
            with col_r4: rp = st.text_input("Peso/carga", placeholder="60kg", key="rp", label_visibility="collapsed")
            with col_r5: rd = st.text_input("Descanso", placeholder="90s", key="rd", label_visibility="collapsed")
            rnotas = st.text_input("Notas técnicas (opcional)", placeholder="Ej: Escápulas retraídas", key="rnotas")

            if st.button("＋ Agregar ejercicio", key="btn_add_rut_ej"):
                if rn:
                    st.session_state.ejercicios_temp.append({
                        "ejercicio": rn, "series": rs,
                        "reps": rr or "—", "peso": rp, "descanso": rd or "—",
                        "notas": rnotas,
                    })
                    st.success(f"'{rn}' añadido.")
                else:
                    st.warning("Escribe el nombre del ejercicio.")

            if st.session_state.ejercicios_temp:
                st.markdown(f"**{len(st.session_state.ejercicios_temp)} ejercicios añadidos:**")
                for i, e in enumerate(st.session_state.ejercicios_temp):
                    st.markdown(f"&nbsp;&nbsp;{i+1}. {e['ejercicio']} — {e['series']}×{e['reps']}")

            if st.button("💾 Guardar rutina", key="btn_save_rut"):
                if not nr_nombre:
                    st.warning("Dale nombre a la rutina.")
                elif not st.session_state.ejercicios_temp:
                    st.warning("Añade al menos un ejercicio.")
                else:
                    datos = st.session_state.datos
                    datos.setdefault("rutinas_custom", {})[nr_nombre] = {
                        "descripcion": nr_desc,
                        "ejercicios": st.session_state.ejercicios_temp.copy(),
                    }
                    guardar_datos(datos)
                    st.session_state.ejercicios_temp = []
                    st.success(f"✅ Rutina '{nr_nombre}' guardada.")
                    st.rerun()

    # ── REGISTRO DE ENTRENOS ──
    with subtab_reg:
        st.markdown("#### 📝 Registro de entrenamiento")
        st.markdown(
            '<div class="fit-card"><p>Apunta tus pesos y repeticiones para hacer seguimiento de tu progresión.</p></div>',
            unsafe_allow_html=True,
        )

        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            reg_fecha = st.date_input("Fecha", value=date.today(), key="reg_fecha")
        with col_reg2:
            reg_tipo  = st.selectbox("Tipo de sesión", [
                "Push","Pull","Legs","Full Body","Upper","Lower","HIIT","Cardio","Otro"
            ], key="reg_tipo")

        reg_duracion = st.slider("Duración (minutos)", 15, 180, 60, 5, key="reg_dur")
        reg_notas    