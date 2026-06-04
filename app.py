import streamlit as st
import json
import os
import re
import base64
import io
from datetime import date, datetime

from PIL import Image

st.set_page_config(
    page_title="FitAI Pro",
    page_icon="F",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:        #07080d;
  --s1:        #0d0f17;
  --s2:        #13151f;
  --s3:        #1a1d2a;
  --border:    rgba(255,255,255,0.06);
  --border2:   rgba(255,255,255,0.11);
  --accent:    #e2ff6a;
  --afg:       #07080d;
  --teal:      #4fffc0;
  --blue:      #5ba8ff;
  --purple:    #b07fff;
  --red:       #ff5c5c;
  --amber:     #ffb84d;
  --text:      #e8eaf3;
  --text2:     #7a8099;
  --text3:     #363a4f;
  --r:         10px;
  --rsm:       6px;
  --rxs:       4px;
}

*,*::before,*::after{box-sizing:border-box}

html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],.main{
  background:var(--bg)!important;
  color:var(--text)!important;
  font-family:'DM Sans',sans-serif!important;
}

#MainMenu,footer,header,[data-testid="stToolbar"],
[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}

.block-container{
  max-width:720px!important;
  padding:0 1.25rem 7rem!important;
  margin:0 auto!important;
}

.hero{padding:2.5rem 0 1.75rem;border-bottom:1px solid var(--border);margin-bottom:1.75rem}
.hero-pill{
  display:inline-flex;align-items:center;gap:.35rem;
  background:rgba(226,255,106,.07);border:1px solid rgba(226,255,106,.18);
  border-radius:99px;padding:.15rem .65rem;
  font-size:.62rem;font-family:'DM Mono',monospace;color:var(--accent);
  letter-spacing:.1em;text-transform:uppercase;margin-bottom:1rem;
}
.hero-dot{width:4px;height:4px;background:var(--accent);border-radius:50%;animation:blink 2s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}

.hero-title{
  font-family:'Cormorant Garamond',serif;
  font-size:clamp(3rem,10vw,5.5rem);
  font-weight:300;line-height:.88;
  color:var(--text);letter-spacing:-.02em;margin-bottom:.8rem;
}
.hero-title em{font-style:italic;color:var(--accent)}

.hero-meta{font-size:.72rem;color:var(--text2);display:flex;align-items:center;gap:.55rem;flex-wrap:wrap}
.hero-sep{color:var(--text3)}

.card{
  background:var(--s1);border:1px solid var(--border);
  border-radius:var(--r);padding:1.15rem 1.3rem;margin-bottom:.75rem;
  position:relative;overflow:hidden;
}
.card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,var(--accent) 0%,transparent 55%);
  opacity:0;transition:opacity .2s;
}
.card.hi::before{opacity:1}

.lbl{
  font-family:'DM Mono',monospace;font-size:.56rem;color:var(--text3);
  letter-spacing:.15em;text-transform:uppercase;margin-bottom:.65rem;
}

.big{font-family:'Cormorant Garamond',serif;font-size:3.2rem;font-weight:300;line-height:1;letter-spacing:-.025em}
.big-sub{font-family:'DM Mono',monospace;font-size:.56rem;color:var(--text3);letter-spacing:.1em;text-transform:uppercase;margin-top:.3rem}

.pb{background:var(--s3);border-radius:999px;height:2px;overflow:hidden;margin-top:.5rem}
.pb-f{height:100%;border-radius:999px;transition:width .6s cubic-bezier(.4,0,.2,1)}

.badge{
  display:inline-flex;align-items:center;
  padding:.14rem .48rem;border-radius:var(--rxs);
  font-size:.64rem;font-weight:500;margin:.12rem .06rem 0 0;
  font-family:'DM Mono',monospace;letter-spacing:.02em;
  border:1px solid transparent;
}
.bk{background:rgba(226,255,106,.06);color:var(--accent);border-color:rgba(226,255,106,.14)}
.bp{background:rgba(79,255,192,.06);color:var(--teal);border-color:rgba(79,255,192,.14)}
.bc{background:rgba(91,168,255,.06);color:var(--blue);border-color:rgba(91,168,255,.14)}
.bf{background:rgba(176,127,255,.06);color:var(--purple);border-color:rgba(176,127,255,.14)}
.bn{background:rgba(255,255,255,.04);color:var(--text2);border-color:var(--border2)}
.bw{background:rgba(255,92,92,.06);color:var(--red);border-color:rgba(255,92,92,.14)}

.mgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}
.mv{font-family:'Cormorant Garamond',serif;font-size:1.9rem;font-weight:300;line-height:1;letter-spacing:-.02em}
.ms{font-size:.62rem;color:var(--text3);font-family:'DM Mono',monospace;margin-top:.1rem}

.sgrid{display:grid;grid-template-columns:1fr 1fr;gap:.65rem}
.sv{font-family:'Cormorant Garamond',serif;font-size:1.65rem;font-weight:300;line-height:1;letter-spacing:-.02em}

.row{display:flex;justify-content:space-between;align-items:center;padding:.32rem 0;border-bottom:1px solid var(--border);font-size:.8rem}
.row:last-child{border-bottom:none}
.rl{color:var(--text2)}
.rr{color:var(--text);font-family:'DM Mono',monospace;font-size:.72rem}

.sep{display:flex;align-items:center;gap:.65rem;margin:1.5rem 0 .85rem}
.sep-l{flex:1;height:1px;background:var(--border)}
.sep-t{font-family:'DM Mono',monospace;font-size:.56rem;color:var(--text3);text-transform:uppercase;letter-spacing:.14em;white-space:nowrap}

.typebadge{
  font-family:'DM Mono',monospace;font-size:.56rem;font-weight:500;
  padding:.14rem .44rem;border-radius:var(--rxs);letter-spacing:.07em;
  text-transform:uppercase;border:1px solid;
}

div.stButton>button{
  background:var(--accent)!important;color:var(--afg)!important;
  font-family:'DM Sans',sans-serif!important;font-size:.8rem!important;
  font-weight:600!important;letter-spacing:.01em!important;
  border:none!important;border-radius:var(--rsm)!important;
  padding:.55rem 1.1rem!important;width:100%!important;
  cursor:pointer!important;transition:opacity .15s,transform .1s!important;
}
div.stButton>button:hover{opacity:.85!important;transform:translateY(-1px)!important}
div.stButton>button:active{transform:translateY(0)!important}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
.stNumberInput input{
  background:var(--s2)!important;color:var(--text)!important;
  border:1px solid var(--border2)!important;border-radius:var(--rsm)!important;
  font-family:'DM Sans',sans-serif!important;font-size:.82rem!important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus{border-color:var(--accent)!important}
div[data-baseweb="select"]>div{
  background:var(--s2)!important;border:1px solid var(--border2)!important;
  border-radius:var(--rsm)!important;color:var(--text)!important;
}
label{color:var(--text2)!important;font-size:.75rem!important;font-family:'DM Sans',sans-serif!important}

[data-baseweb="tab-list"]{
  background:var(--s1)!important;border:1px solid var(--border)!important;
  border-radius:var(--rsm)!important;padding:3px!important;gap:2px!important;
}
[data-baseweb="tab"]{
  color:var(--text3)!important;font-family:'DM Sans',sans-serif!important;
  font-weight:600!important;font-size:.73rem!important;
  border-radius:5px!important;padding:.35rem .85rem!important;
}
[aria-selected="true"][data-baseweb="tab"]{
  background:var(--accent)!important;color:var(--afg)!important;
}

[data-testid="stFileUploader"]{
  border:1px dashed var(--border2)!important;border-radius:var(--r)!important;
  background:var(--s1)!important;
}
[data-testid="stAlert"]{
  background:var(--s2)!important;border:1px solid var(--border2)!important;
  border-radius:var(--rsm)!important;font-size:.8rem!important;
  font-family:'DM Sans',sans-serif!important;
}
[data-testid="stExpander"]{
  background:var(--s1)!important;border:1px solid var(--border)!important;
  border-radius:var(--rsm)!important;
}
[data-testid="stExpander"] summary{
  color:var(--text2)!important;font-family:'DM Sans',sans-serif!important;
  font-size:.8rem!important;font-weight:600!important;
}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:999px}

@media(max-width:520px){
  .hero-title{font-size:2.8rem}
  .big{font-size:2.5rem}
  .block-container{padding:0 .75rem 6rem!important}
  .mgrid{gap:.6rem}
}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
DATA_FILE = "fitai_data.json"

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
            {"nombre":"Antes de dormir","alimentos":"Claras de huevo 200g + Queso fresco 0% 150g","cal":220,"prot":34,"carb":7,"grasa":3},
        ],
    },
    "Definicion (1900 kcal)": {
        "objetivo": "Reducir grasa corporal conservando la masa muscular",
        "macros": {"prot":180,"carb":160,"grasa":60},
        "comidas": [
            {"nombre":"Desayuno","alimentos":"Claras 4 uds + 1 huevo entero + Avena 50g","cal":380,"prot":38,"carb":35,"grasa":9},
            {"nombre":"Media manana","alimentos":"Yogur griego 0% 200g + Caseina 30g","cal":250,"prot":35,"carb":10,"grasa":3},
            {"nombre":"Almuerzo","alimentos":"Pechuga pavo 200g + Patata 150g + Verduras variadas","cal":430,"prot":62,"carb":35,"grasa":5},
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
            {"nombre":"Desayuno","alimentos":"Avena 80g + Proteina vegana 30g + Platano + Leche vegetal","cal":520,"prot":35,"carb":80,"grasa":10},
            {"nombre":"Media manana","alimentos":"Hummus 100g + Pan integral + Tomate","cal":290,"prot":12,"carb":35,"grasa":10},
            {"nombre":"Almuerzo","alimentos":"Lentejas 200g + Arroz 100g + Verduras + AOVE","cal":590,"prot":28,"carb":95,"grasa":12},
            {"nombre":"Merienda","alimentos":"Aguacate + Pan integral + Batido espinacas","cal":350,"prot":10,"carb":30,"grasa":22},
            {"nombre":"Cena","alimentos":"Tofu 200g + Garbanzos 100g + Brocoli + AOVE","cal":470,"prot":38,"carb":35,"grasa":20},
        ],
    },
    "Recomposicion (2100 kcal)": {
        "objetivo": "Ganar musculo y perder grasa simultaneamente",
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
        {"nombre":"Press banca inclinado","tipo":"Hipertrofia","equipo":"Barra o Mancuernas","series_rec":"3-4","reps_rec":"10-15","descanso":"75s","notas":"Angulo 30-45 grados, activa porcion clavicular"},
        {"nombre":"Press banca declinado","tipo":"Hipertrofia","equipo":"Barra","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Activa porcion esternocostal inferior"},
        {"nombre":"Aperturas con mancuernas","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados en todo el rango"},
        {"nombre":"Fondos en paralelas","tipo":"Peso corporal","equipo":"Paralelas","series_rec":"3-4","reps_rec":"Max","descanso":"90s","notas":"Torso inclinado hacia adelante para enfatizar pecho"},
        {"nombre":"Crossover en polea","tipo":"Aislamiento","equipo":"Poleas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Estiramiento completo en la parte superior"},
        {"nombre":"Press en maquina de pecho","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Util para principiantes, tension constante"},
    ],
    "Espalda": [
        {"nombre":"Peso muerto convencional","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"4-8","descanso":"3 min","notas":"Espalda neutra, barra pegada al cuerpo en todo momento"},
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra fija","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo, sin balanceo ni impulso"},
        {"nombre":"Jalon al pecho","tipo":"Hipertrofia","equipo":"Polea alta","series_rec":"4","reps_rec":"10-15","descanso":"75s","notas":"Codos hacia abajo y atras, lleva barra a la barbilla"},
        {"nombre":"Remo con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Torso a 45 grados, barra toca el abdomen"},
        {"nombre":"Remo en polea baja","tipo":"Hipertrofia","equipo":"Polea baja","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Pecho erguido, tiron hacia el abdomen bajo"},
        {"nombre":"Remo con mancuerna a una mano","tipo":"Hipertrofia","equipo":"Mancuerna","series_rec":"3","reps_rec":"12-15/lado","descanso":"60s","notas":"Apoyo en banco, rango completo"},
        {"nombre":"Face pulls","tipo":"Prevencion","equipo":"Polea alta","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Esencial para la salud del manguito rotador"},
        {"nombre":"Pull-over con mancuerna","tipo":"Hipertrofia","equipo":"Mancuerna","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Codos ligeramente flexionados, activa serrato"},
    ],
    "Pierna": [
        {"nombre":"Sentadilla con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4-5","reps_rec":"5-10","descanso":"2-3 min","notas":"Rodillas en la direccion de los pies, cadera por debajo de rodillas"},
        {"nombre":"Prensa de piernas","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Pies altos para isquios, pies bajos para cuadriceps"},
        {"nombre":"Extension de cuadriceps","tipo":"Aislamiento","equipo":"Maquina","series_rec":"3","reps_rec":"15-20","descanso":"60s","notas":"Contraccion completa en la extension, pausa 1s"},
        {"nombre":"Femoral tumbado","tipo":"Aislamiento","equipo":"Maquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Aisla isquiotibiales de forma efectiva"},
        {"nombre":"Peso muerto rumano","tipo":"Hipertrofia","equipo":"Barra o Mancuernas","series_rec":"3-4","reps_rec":"10-12","descanso":"90s","notas":"Bisagra de cadera perfecta, isquiotibiales en tension maxima"},
        {"nombre":"Hip Thrust","tipo":"Gluteos","equipo":"Barra o Maquina","series_rec":"4","reps_rec":"10-15","descanso":"90s","notas":"Contraccion maxima arriba, pelvis neutra al bajar"},
        {"nombre":"Zancadas caminando","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"12/pierna","descanso":"75s","notas":"Rodilla trasera casi toca el suelo"},
        {"nombre":"Sentadilla bulgara","tipo":"Fuerza","equipo":"Mancuernas","series_rec":"3","reps_rec":"10/pierna","descanso":"90s","notas":"Exige mucho equilibrio, gran activacion unilateral"},
        {"nombre":"Elevacion de gemelos","tipo":"Aislamiento","equipo":"Maquina o Libre","series_rec":"4","reps_rec":"15-25","descanso":"45s","notas":"Rango completo, pausa arriba y estiramiento abajo"},
    ],
    "Hombros": [
        {"nombre":"Press militar con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"6-10","descanso":"2 min","notas":"Core activado, evitar arquear la zona lumbar"},
        {"nombre":"Press Arnold","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-12","descanso":"75s","notas":"Rotacion completa activa los tres fasciculos"},
        {"nombre":"Elevaciones laterales","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Codo ligeramente flexionado, hasta la horizontal"},
        {"nombre":"Pajaro posterior (Rear delt fly)","tipo":"Aislamiento","equipo":"Mancuernas","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Torso a 90 grados, activa deltoides posterior"},
        {"nombre":"Encogimientos de trapecio","tipo":"Fuerza","equipo":"Barra o Mancuernas","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Movimiento puramente vertical, sin rotacion de hombros"},
        {"nombre":"Press lateral en maquina","tipo":"Hipertrofia","equipo":"Maquina","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Tension constante, util para aislar el lateral"},
    ],
    "Biceps": [
        {"nombre":"Curl con barra","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"75s","notas":"Codos fijos a los costados del tronco"},
        {"nombre":"Curl con mancuernas alterno","tipo":"Hipertrofia","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-14/brazo","descanso":"60s","notas":"Supinacion al subir para mayor contraccion"},
        {"nombre":"Curl martillo","tipo":"Braquial","equipo":"Mancuernas","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Agarre neutro, activa braquirradial y braquial"},
        {"nombre":"Curl predicador","tipo":"Aislamiento","equipo":"Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"No extender completamente para proteger el tendon"},
        {"nombre":"Curl concentrado","tipo":"Aislamiento","equipo":"Mancuerna","series_rec":"3","reps_rec":"12-15/brazo","descanso":"45s","notas":"Codo apoyado en el muslo, enfoca la contraccion"},
        {"nombre":"Curl en polea baja","tipo":"Aislamiento","equipo":"Polea","series_rec":"3","reps_rec":"15-20","descanso":"45s","notas":"Tension constante durante todo el recorrido"},
    ],
    "Triceps": [
        {"nombre":"Press banca agarre cerrado","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"8-12","descanso":"90s","notas":"Codos pegados al tronco, agarre al ancho de hombros"},
        {"nombre":"Extension sobre la cabeza","tipo":"Hipertrofia","equipo":"Mancuerna o Barra EZ","series_rec":"3","reps_rec":"12-15","descanso":"60s","notas":"Estiramiento maximo en la parte inferior del movimiento"},
        {"nombre":"Press frances (Skull crusher)","tipo":"Hipertrofia","equipo":"Barra EZ","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Tumbado, baja la barra hacia la frente controladamente"},
        {"nombre":"Pushdown en polea (cuerda)","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"3-4","reps_rec":"15-20","descanso":"45s","notas":"Extension completa abajo, separar la cuerda al final"},
        {"nombre":"Fondos entre bancos","tipo":"Peso corporal","equipo":"Bancos","series_rec":"3","reps_rec":"12-20","descanso":"60s","notas":"Cuerpo recto, codos se flexionan hacia atras"},
        {"nombre":"Kickbacks","tipo":"Aislamiento","equipo":"Mancuerna","series_rec":"3","reps_rec":"15-20/brazo","descanso":"45s","notas":"Brazo paralelo al suelo, solo se mueve el antebrazo"},
    ],
    "Core": [
        {"nombre":"Plancha frontal","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3-4","reps_rec":"45-90s","descanso":"45s","notas":"Cuerpo completamente recto, no elevar las caderas"},
        {"nombre":"Plancha lateral","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"30-60s/lado","descanso":"30s","notas":"Cadera levantada, cuerpo perfectamente alineado"},
        {"nombre":"Crunch en polea","tipo":"Aislamiento","equipo":"Polea alta","series_rec":"4","reps_rec":"15-20","descanso":"45s","notas":"Flexion de columna, nunca de caderas"},
        {"nombre":"Rueda abdominal","tipo":"Fuerza","equipo":"Rueda ab","series_rec":"3","reps_rec":"8-15","descanso":"60s","notas":"Empezar de rodillas, progresar a version de pie"},
        {"nombre":"Elevacion de piernas colgado","tipo":"Fuerza","equipo":"Barra fija","series_rec":"3","reps_rec":"10-15","descanso":"60s","notas":"Retroversion pelvica al subir para activar el recto"},
        {"nombre":"Dead bug","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"8-12/lado","descanso":"45s","notas":"Espalda baja pegada al suelo en todo momento"},
        {"nombre":"Russian twist","tipo":"Rotacion","equipo":"Peso o Mancuerna","series_rec":"3","reps_rec":"15-20/lado","descanso":"45s","notas":"Control de la rotacion, evitar movimiento brusco"},
        {"nombre":"Bird dog","tipo":"Estabilidad","equipo":"Peso corporal","series_rec":"3","reps_rec":"10-12/lado","descanso":"30s","notas":"Posicion cuadrupeda, extiende brazo y pierna opuestos"},
    ],
    "Cardio": [
        {"nombre":"HIIT en cinta","tipo":"Cardio","equipo":"Cinta","series_rec":"8-12","reps_rec":"30s sprint / 30s caminar","descanso":"—","notas":"Frecuencia cardiaca en sprints al 85-90% del maximo"},
        {"nombre":"Tabata en bicicleta","tipo":"Cardio","equipo":"Bicicleta","series_rec":"8","reps_rec":"20s esfuerzo / 10s pausa","descanso":"—","notas":"Protocolo Tabata clasico. 4 minutos totales por ronda"},
        {"nombre":"Zona 2 en eliptica","tipo":"Cardio","equipo":"Eliptica","series_rec":"1","reps_rec":"30-45 min","descanso":"—","notas":"FC 120-140 ppm, puedes hablar con cierta dificultad"},
        {"nombre":"Remo en ergometro","tipo":"Cardio","equipo":"Remo","series_rec":"5","reps_rec":"500 m","descanso":"2 min","notas":"Combina cardio con trabajo de espalda y piernas"},
        {"nombre":"Saltar a la comba","tipo":"Cardio","equipo":"Comba","series_rec":"5","reps_rec":"2 min","descanso":"60s","notas":"Bajo impacto articular, alta demanda metabolica"},
        {"nombre":"Sprints en exterior","tipo":"Cardio","equipo":"Pista","series_rec":"6-10","reps_rec":"40-100m","descanso":"2-3 min","notas":"Esfuerzo maximo en cada repeticion, recuperacion completa"},
    ],
    "Calistenia": [
        {"nombre":"Dominadas","tipo":"Fuerza","equipo":"Barra","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Progresion: australianas, negativas, asistidas, completas"},
        {"nombre":"Fondos en paralelas","tipo":"Fuerza","equipo":"Paralelas","series_rec":"4","reps_rec":"Max","descanso":"90s","notas":"Rango completo, progresion hasta fondos lastrados"},
        {"nombre":"Flexiones","tipo":"Peso corporal","equipo":"Suelo","series_rec":"4","reps_rec":"Max","descanso":"60s","notas":"Variantes: inclinadas, declinadas, diamante, arqueras"},
        {"nombre":"Muscle-up","tipo":"Fuerza","equipo":"Barra","series_rec":"3","reps_rec":"3-6","descanso":"2 min","notas":"Movimiento avanzado, requiere gran fuerza de tiron"},
        {"nombre":"L-sit","tipo":"Estabilidad","equipo":"Paralelas o suelo","series_rec":"4","reps_rec":"10-30s","descanso":"60s","notas":"Mantenimiento de la posicion con caderas elevadas"},
        {"nombre":"Pistol squat (sentadilla a 1 pierna)","tipo":"Fuerza","equipo":"Peso corporal","series_rec":"3","reps_rec":"5-10/pierna","descanso":"90s","notas":"Progresion: con apoyo, luego libre"},
    ],
}

RUTINAS_DEFAULT = {
    "PPL — Empuje (Push)": {
        "desc": "Pecho, hombros y triceps",
        "ejercicios": [
            {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Press banca inclinado mancuernas","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Press Arnold","series":4,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Elevaciones laterales","series":4,"reps":"15-20","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Pushdown en polea (cuerda)","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Extension sobre la cabeza","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
        ],
    },
    "PPL — Tiron (Pull)": {
        "desc": "Espalda y biceps",
        "ejercicios": [
            {"ejercicio":"Dominadas","series":4,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
            {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Remo en polea baja","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Curl martillo","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
        ],
    },
    "PPL — Piernas (Legs)": {
        "desc": "Cuadriceps, isquios, gluteos y gemelos",
        "ejercicios": [
            {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-8","peso":"","descanso":"2-3 min","notas":""},
            {"ejercicio":"Prensa de piernas","series":4,"reps":"10-15","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Peso muerto rumano","series":3,"reps":"10-12","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Femoral tumbado","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Hip Thrust","series":4,"reps":"12-15","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Elevacion de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
        ],
    },
    "Full Body — Principiantes": {
        "desc": "Sesion completa 3 dias por semana",
        "ejercicios": [
            {"ejercicio":"Sentadilla con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Press banca plano","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Peso muerto convencional","series":3,"reps":"6-8","peso":"","descanso":"2 min","notas":""},
            {"ejercicio":"Press militar con barra","series":3,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Dominadas","series":3,"reps":"Max","peso":"Corporal","descanso":"90s","notas":""},
            {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"45s","notas":""},
        ],
    },
    "Upper — Tren superior": {
        "desc": "Pecho, espalda, hombros y brazos",
        "ejercicios": [
            {"ejercicio":"Press banca plano","series":4,"reps":"6-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Remo con barra","series":4,"reps":"8-10","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Press banca inclinado mancuernas","series":3,"reps":"10-12","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Jalon al pecho","series":3,"reps":"12-15","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Elevaciones laterales","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Curl con barra","series":3,"reps":"10-12","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Pushdown en polea (cuerda)","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        ],
    },
    "Lower — Tren inferior": {
        "desc": "Cuadriceps, isquios, gluteos y core",
        "ejercicios": [
            {"ejercicio":"Sentadilla con barra","series":4,"reps":"6-10","peso":"","descanso":"2 min","notas":""},
            {"ejercicio":"Peso muerto rumano","series":4,"reps":"8-12","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Prensa de piernas","series":3,"reps":"12-15","peso":"","descanso":"90s","notas":""},
            {"ejercicio":"Femoral tumbado","series":3,"reps":"12-15","peso":"","descanso":"60s","notas":""},
            {"ejercicio":"Zancadas caminando","series":3,"reps":"12/pierna","peso":"","descanso":"75s","notas":""},
            {"ejercicio":"Elevacion de gemelos","series":4,"reps":"20-25","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Crunch en polea","series":3,"reps":"15-20","peso":"","descanso":"45s","notas":""},
        ],
    },
    "HIIT + Core": {
        "desc": "Alta intensidad con trabajo abdominal. Duracion aprox 35 min",
        "ejercicios": [
            {"ejercicio":"Burpees","series":5,"reps":"30s esfuerzo / 15s pausa","peso":"","descanso":"30s","notas":""},
            {"ejercicio":"Mountain climbers","series":5,"reps":"30s esfuerzo / 15s pausa","peso":"","descanso":"30s","notas":""},
            {"ejercicio":"Saltos en caja","series":4,"reps":"10","peso":"","descanso":"45s","notas":""},
            {"ejercicio":"Sprint en sitio","series":6,"reps":"20s / 10s pausa","peso":"","descanso":"—","notas":""},
            {"ejercicio":"Plancha frontal","series":3,"reps":"60s","peso":"","descanso":"30s","notas":""},
            {"ejercicio":"Rueda abdominal","series":3,"reps":"10","peso":"","descanso":"60s","notas":""},
        ],
    },
}

TIPO_COLOR = {
    "Fuerza":        ("#ff5c5c","rgba(255,92,92,.1)"),
    "Hipertrofia":   ("#5ba8ff","rgba(91,168,255,.1)"),
    "Aislamiento":   ("#b07fff","rgba(176,127,255,.1)"),
    "Peso corporal": ("#4fffc0","rgba(79,255,192,.1)"),
    "Cardio":        ("#e2ff6a","rgba(226,255,106,.1)"),
    "Estabilidad":   ("#4fffc0","rgba(79,255,192,.1)"),
    "Gluteos":       ("#f472b6","rgba(244,114,182,.1)"),
    "Prevencion":    ("#4fffc0","rgba(79,255,192,.1)"),
    "Braquial":      ("#b07fff","rgba(176,127,255,.1)"),
    "Rotacion":      ("#ffb84d","rgba(255,184,77,.1)"),
}

# ── PERSISTENCE ────────────────────────────────────────────────────────────────
def cargar_datos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "historial_calorias":{},"historial_macros":{},
        "diario_comidas":{},"rutinas_custom":{},
        "dietas_custom":{},"perfil":{},"registro_entreno":{},
    }

def guardar_datos(d):
    try:
        with open(DATA_FILE,"w",encoding="utf-8") as f:
            json.dump(d,f,ensure_ascii=False,indent=2)
    except Exception as e:
        st.warning(f"Error al guardar: {e}")

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()
for k,v in [
    ("gemini_key",""),("groq_key",""),("proveedor_ia","Groq (recomendado)"),
    ("scan_res",None),("ia_dieta_res",None),
    ("ej_temp",[]),("sets_temp",[]),("comidas_dc_temp",[]),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ────────────────────────────────────────────────────────────────────
def hoy():
    return str(date.today())

def get_perfil():
    return st.session_state.datos.get("perfil",{})

def get_obj_cal():
    return int(get_perfil().get("objetivo_cal",2000))

def cal_hoy():
    return st.session_state.datos["historial_calorias"].get(hoy(),0)

def macros_hoy():
    return st.session_state.datos.get("historial_macros",{}).get(
        hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0}
    )

def registrar_alimento(nombre,cal,prot,carb,grasa,comida):
    d = st.session_state.datos
    d["historial_calorias"][hoy()] = cal_hoy() + cal
    hm = d.setdefault("historial_macros",{})
    dm = hm.setdefault(hoy(),{"prot":0.0,"carb":0.0,"grasa":0.0})
    dm["prot"]  = round(dm["prot"]  + prot,  1)
    dm["carb"]  = round(dm["carb"]  + carb,  1)
    dm["grasa"] = round(dm["grasa"] + grasa, 1)
    dc = d.setdefault("diario_comidas",{})
    dc.setdefault(hoy(),[]).append({
        "comida":comida,"alimento":nombre,
        "cal":cal,"prot":prot,"carb":carb,"grasa":grasa,
        "hora":datetime.now().strftime("%H:%M"),
    })
    guardar_datos(d)

def calcular_tdee(peso,altura,edad,sexo,actividad):
    bmr = (88.36 + 13.4*peso + 4.8*altura - 5.7*edad) if sexo=="Hombre" \
          else (447.6 + 9.2*peso + 3.1*altura - 4.3*edad)
    f = {"Sedentario (sin ejercicio)":1.2,"Ligero (1-2 dias/semana)":1.375,
         "Moderado (3-4 dias/semana)":1.55,"Activo (5-6 dias/semana)":1.725,
         "Muy activo (2 veces/dia)":1.9}
    return int(bmr * f.get(actividad,1.55))

def pb(val,mx,color):
    pct = min(val/mx*100,100) if mx>0 else 0
    return f'<div class="pb"><div class="pb-f" style="width:{pct}%;background:{color}"></div></div>'

def ia_call(prompt, img_bytes=None):
    """Llama a la IA activa (Groq o Gemini) con manejo de errores robusto."""
    proveedor = st.session_state.proveedor_ia

    if proveedor == "Groq (recomendado)":
        key = st.session_state.groq_key.strip()
        if not key:
            return "ERROR_NO_KEY:groq"
        try:
            import requests
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            if img_bytes:
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                ext = "jpeg"
                try:
                    img_pil = Image.open(io.BytesIO(img_bytes))
                    fmt = img_pil.format
                    if fmt:
                        ext = fmt.lower().replace("jpg","jpeg")
                except Exception:
                    pass
                messages = [{"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:image/{ext};base64,{img_b64}"}},
                    {"type":"text","text":prompt}
                ]}]
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
            else:
                messages = [{"role":"user","content":prompt}]
                model = "llama-3.3-70b-versatile"
            payload = {"model":model,"messages":messages,"max_tokens":1200,"temperature":0.4}
            r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                              headers=headers, json=payload, timeout=30)
            if r.status_code == 401:
                return "API Key de Groq invalida. Verificala en console.groq.com/keys"
            if r.status_code == 429:
                return "Limite de uso de Groq alcanzado. Espera un minuto e intentalo de nuevo."
            if r.status_code != 200:
                return f"Error Groq {r.status_code}: {r.text[:200]}"
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error de conexion con Groq: {str(e)[:200]}"

    else:  # Gemini
        key = st.session_state.gemini_key.strip()
        if not key:
            return "ERROR_NO_KEY:gemini"
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
            if "API_KEY" in err.upper() or "INVALID" in err.upper():
                return "API Key de Gemini invalida. Verificala en aistudio.google.com/app/apikeys"
            if "QUOTA" in err.upper() or "429" in err:
                return ("Cuota de Gemini agotada (limite gratuito: ~20 peticiones/dia). "
                        "Solucion recomendada: cambia a Groq en Config, es mas generoso y gratuito.")
            if "SAFETY" in err.upper():
                return "Imagen bloqueada por filtros de seguridad de Gemini."
            return f"Error Gemini: {err[:200]}"

def extraer_kcal(texto):
    try:
        m = re.search(r"TOTAL.*?(\d{2,4})\s*kcal",texto,re.IGNORECASE)
        if m: return int(m.group(1))
        m2 = re.search(r"(\d{3,4})\s*kcal",texto,re.IGNORECASE)
        if m2: return int(m2.group(1))
    except Exception:
        pass
    return 0

def sdiv(label):
    st.markdown(
        f'<div class="sep"><div class="sep-l"></div>'
        f'<span class="sep-t">{label}</span>'
        f'<div class="sep-l"></div></div>',
        unsafe_allow_html=True,
    )

def card(content, hi=False):
    cls = "card hi" if hi else "card"
    return f'<div class="{cls}">{content}</div>'

# ── HERO ───────────────────────────────────────────────────────────────────────
nombre = get_perfil().get("nombre","")
pill_txt = f"Bienvenido, {nombre}" if nombre else "Tu asistente de fitness"

st.markdown(
    f'<div class="hero">'
    f'<div class="hero-pill"><div class="hero-dot"></div>{pill_txt}</div>'
    f'<div class="hero-title">Fit<em>AI</em><br>Pro</div>'
    f'<div class="hero-meta">'
    f'<span>Nutricion</span><span class="hero-sep">·</span>'
    f'<span>Dietas</span><span class="hero-sep">·</span>'
    f'<span>Gimnasio</span><span class="hero-sep">·</span>'
    f'<span>Inteligencia Artificial</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# ── MAIN TABS ──────────────────────────────────────────────────────────────────
t_nut, t_diet, t_gym, t_hist, t_cfg = st.tabs([
    "Nutricion","Dietas","Gimnasio","Historial","Config"
])

# ══════════════════════════════════════════════════════════════════════════════
# NUTRICION
# ══════════════════════════════════════════════════════════════════════════════
with t_nut:
    c_hoy   = cal_hoy()
    obj_c   = get_obj_cal()
    m_hoy   = macros_hoy()
    pf      = get_perfil()
    obj_p   = int(pf.get("obj_prot",  150))
    obj_cb  = int(pf.get("obj_carb",  220))
    obj_g   = int(pf.get("obj_grasa",  60))
    restante = max(obj_c-c_hoy,0)
    exceso   = max(c_hoy-obj_c,0)
    ok      = c_hoy<=obj_c

    col1,col2 = st.columns([3,2])
    with col1:
        nc = "var(--teal)" if ok else "var(--red)"
        bc = "var(--accent)" if ok else "var(--red)"
        st.markdown(card(
            f'<div class="lbl">Calorias de hoy</div>'
            f'<div class="big" style="color:{nc}">{c_hoy}</div>'
            f'<div class="big-sub">de {obj_c} kcal objetivo</div>'
            f'{pb(c_hoy,obj_c,bc)}',True),unsafe_allow_html=True)
    with col2:
        sv = f'<span style="color:var(--teal)">{restante}</span>' if ok \
             else f'<span style="color:var(--red)">{exceso}</span>'
        sl = "disponibles" if ok else "excedido"
        st.markdown(card(
            f'<div style="display:flex;flex-direction:column;justify-content:center;'
            f'align-items:center;text-align:center;min-height:86px;padding:.4rem 0">'
            f'<div class="lbl">Estado</div>'
            f'<div class="big" style="font-size:2.2rem">{sv}</div>'
            f'<div class="big-sub">{sl}</div></div>'),
            unsafe_allow_html=True)

    pct_p = int(min(m_hoy["prot"] /obj_p *100,100)) if obj_p  else 0
    pct_c = int(min(m_hoy["carb"] /obj_cb*100,100)) if obj_cb else 0
    pct_g = int(min(m_hoy["grasa"]/obj_g *100,100)) if obj_g  else 0
    st.markdown(card(
        f'<div class="lbl">Macronutrientes</div>'
        f'<div class="mgrid">'
        f'<div><div class="lbl">Proteina</div>'
        f'<div class="mv" style="color:var(--teal)">{m_hoy["prot"]}g</div>'
        f'<div class="ms">/{obj_p}g &middot; {pct_p}%</div>{pb(m_hoy["prot"],obj_p,"var(--teal)")}</div>'
        f'<div><div class="lbl">Carbohidratos</div>'
        f'<div class="mv" style="color:var(--blue)">{m_hoy["carb"]}g</div>'
        f'<div class="ms">/{obj_cb}g &middot; {pct_c}%</div>{pb(m_hoy["carb"],obj_cb,"var(--blue)")}</div>'
        f'<div><div class="lbl">Grasas</div>'
        f'<div class="mv" style="color:var(--purple)">{m_hoy["grasa"]}g</div>'
        f'<div class="ms">/{obj_g}g &middot; {pct_g}%</div>{pb(m_hoy["grasa"],obj_g,"var(--purple)")}</div>'
        f'</div>'),unsafe_allow_html=True)

    # Scanner IA
    sdiv("Scanner con IA")
    proveedor = st.session_state.proveedor_ia
    key_activa = (st.session_state.groq_key if "Groq" in proveedor
                  else st.session_state.gemini_key)
    if not key_activa.strip():
        st.info(f"Configura tu API Key en la pestana Config para activar el scanner IA "
                f"(proveedor actual: {proveedor}).")
    else:
        img_up = st.file_uploader("Foto del plato",
            type=["jpg","jpeg","png","webp"],key="up_scan")
        if img_up:
            st.image(img_up,use_container_width=True)
            cs1,cs2 = st.columns(2)
            with cs1:
                comida_scan = st.selectbox("Comida",
                    ["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],
                    key="sc_com")
            with cs2:
                if st.button("Analizar con IA",key="btn_scan"):
                    with st.spinner("Analizando imagen..."):
                        prompt_s = (
                            "Eres un nutricionista experto. Analiza esta imagen en espanol "
                            "con este formato exacto:\n\n"
                            "Alimentos detectados:\n"
                            "- [alimento] — [X] kcal · P:[Xg] C:[Xg] G:[Xg]\n\n"
                            "TOTAL: [NNN] kcal | P:[Xg] C:[Xg] G:[Xg]\n\n"
                            "Valoracion: [una frase sobre el equilibrio nutricional]\n\n"
                            "Si no hay comida visible, indicalo."
                        )
                        res = ia_call(prompt_s,img_up.read())
                        if res.startswith("ERROR_NO_KEY"):
                            st.warning("Configura tu API Key en Config.")
                        else:
                            st.session_state.scan_res = res

        if st.session_state.scan_res:
            st.markdown(card(
                f'<div class="lbl">Analisis</div>'
                f'<p style="white-space:pre-wrap;color:var(--text2);'
                f'font-size:.82rem;line-height:1.75">'
                f'{st.session_state.scan_res}</p>'),
                unsafe_allow_html=True)
            kcal_det = extraer_kcal(st.session_state.scan_res)
            if kcal_det > 0:
                c_r1,c_r2 = st.columns(2)
                with c_r1:
                    if st.button(f"Registrar {kcal_det} kcal",key="btn_reg_scan"):
                        com_n = st.session_state.get("sc_com","Extra")
                        registrar_alimento("IA — foto",kcal_det,0,0,0,com_n)
                        st.session_state.scan_res = None
                        st.success("Registrado.")
                        st.rerun()
                with c_r2:
                    if st.button("Descartar",key="btn_disc"):
                        st.session_state.scan_res = None
                        st.rerun()

    # Registrar desde base de datos
    sdiv("Registrar alimento")
    ca1,ca2 = st.columns([3,1])
    with ca1:
        alim = st.selectbox("Alimento",list(ALIMENTOS_DB.keys()),
                            key="sel_alim",label_visibility="collapsed")
    with ca2:
        cant = st.number_input("g",1,2000,100,key="cant",
                               label_visibility="collapsed")
    ad = ALIMENTOS_DB[alim]
    f  = cant/100
    ca_val = round(ad["cal"]*f)
    pr_val = round(ad["prot"]*f,1)
    cb_val = round(ad["carb"]*f,1)
    gr_val = round(ad["grasa"]*f,1)
    st.markdown(card(
        f'<span class="badge bk">{ca_val} kcal</span>'
        f'<span class="badge bp">P {pr_val}g</span>'
        f'<span class="badge bc">C {cb_val}g</span>'
        f'<span class="badge bf">G {gr_val}g</span>'),
        unsafe_allow_html=True)
    ca3,ca4 = st.columns([2,1])
    with ca3:
        com_db = st.selectbox("Comida",
            ["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="com_db")
    with ca4:
        if st.button("Anadir",key="btn_add_db"):
            registrar_alimento(f"{alim} ({cant}g)",ca_val,pr_val,cb_val,gr_val,com_db)
            st.success(f"{ca_val} kcal registradas")
            st.rerun()

    # Registro manual
    sdiv("Registro manual")
    cm1,cm2,cm3,cm4 = st.columns([3,1,1,1])
    with cm1: nm=st.text_input("Nombre",placeholder="Plato personalizado",key="nm",label_visibility="collapsed")
    with cm2: km=st.number_input("kcal",0,5000,0,5,key="km",label_visibility="collapsed")
    with cm3: pm=st.number_input("P(g)",0.0,300.0,0.0,.5,key="pm",label_visibility="collapsed")
    with cm4: cbm=st.number_input("C(g)",0.0,500.0,0.0,.5,key="cbm",label_visibility="collapsed")
    cm5,cm6 = st.columns([2,1])
    with cm5:
        comm=st.selectbox("Comida",
            ["Desayuno","Media manana","Almuerzo","Merienda","Cena","Extra"],key="comm")
    with cm6:
        if st.button("Anadir",key="btn_man"):
            if km>0:
                registrar_alimento(nm or "Alimento libre",km,pm,cbm,0.0,comm)
                st.success(f"{km} kcal anadidas")
                st.rerun()
            else:
                st.warning("Introduce kcal mayor que 0")

    # Diario del dia
    sdiv("Diario de hoy")
    diario = st.session_state.datos.get("diario_comidas",{}).get(hoy(),[])
    if not diario:
        st.markdown(card(
            '<div style="text-align:center;padding:1.1rem 0">'
            '<div class="lbl" style="text-align:center">Sin registros todavia</div>'
            '<p style="color:var(--text3);font-size:.77rem">Empieza anadiendo alimentos arriba</p>'
            '</div>'),unsafe_allow_html=True)
    else:
        grupos = {}
        for item in diario:
            grupos.setdefault(item["comida"],[]).append(item)
        for nc2,items in grupos.items():
            tc = sum(i["cal"] for i in items)
            filas = "".join(
                f'<div class="row">'
                f'<span class="rl">'
                f'<span style="color:var(--text3);font-family:DM Mono,monospace;font-size:.62rem">{i["hora"]}</span>'
                f'&nbsp;&nbsp;{i["alimento"]}</span>'
                f'<span class="rr">{i["cal"]} kcal</span></div>'
                for i in items
            )
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">'
                f'<span style="font-weight:600;color:var(--text);font-size:.84rem">{nc2}</span>'
                f'<span class="badge bk">{tc} kcal</span></div>{filas}'),
                unsafe_allow_html=True)

    if st.button("Resetear diario de hoy",key="btn_reset"):
        d = st.session_state.datos
        d["historial_calorias"][hoy()] = 0
        d.setdefault("historial_macros",{})[hoy()] = {"prot":0.0,"carb":0.0,"grasa":0.0}
        d.setdefault("diario_comidas",{})[hoy()] = []
        guardar_datos(d)
        st.success("Diario reseteado.")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DIETAS
# ══════════════════════════════════════════════════════════════════════════════
with t_diet:
    dt1,dt2,dt3,dt4 = st.tabs(["Planes","Calculadora","IA Dietista","Mis dietas"])

    with dt1:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        plan_k = st.selectbox("Plan",list(DIETAS_TEMPLATE.keys()),key="plan_k")
        plan   = DIETAS_TEMPLATE[plan_k]
        tot_c  = sum(c["cal"]   for c in plan["comidas"])
        tot_p  = sum(c["prot"]  for c in plan["comidas"])
        tot_cb = sum(c["carb"]  for c in plan["comidas"])
        tot_g  = sum(c["grasa"] for c in plan["comidas"])
        st.markdown(card(
            f'<div class="lbl">Objetivo</div>'
            f'<div style="font-size:.9rem;font-weight:600;color:var(--text);margin-bottom:.55rem">{plan["objetivo"]}</div>'
            f'<span class="badge bk">{tot_c} kcal</span>'
            f'<span class="badge bp">P {tot_p}g</span>'
            f'<span class="badge bc">C {tot_cb}g</span>'
            f'<span class="badge bf">G {tot_g}g</span>',True),
            unsafe_allow_html=True)
        for c in plan["comidas"]:
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">'
                f'<h4 style="margin:0;font-size:.88rem;font-weight:600;color:var(--text)">{c["nombre"]}</h4>'
                f'<span class="badge bk">{c["cal"]} kcal</span></div>'
                f'<p style="margin:0 0 .4rem;font-size:.8rem;color:var(--text2)">{c["alimentos"]}</p>'
                f'<span class="badge bp">P {c["prot"]}g</span>'
                f'<span class="badge bc">C {c["carb"]}g</span>'
                f'<span class="badge bf">G {c["grasa"]}g</span>'),
                unsafe_allow_html=True)
        if st.button("Usar como objetivo diario",key="btn_usar"):
            st.session_state.datos.setdefault("perfil",{}).update({
                "objetivo_cal":tot_c,"obj_prot":tot_p,"obj_carb":tot_cb,"obj_grasa":tot_g})
            guardar_datos(st.session_state.datos)
            st.success(f"Objetivo actualizado: {tot_c} kcal/dia")
            st.rerun()

    with dt2:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        pf2 = get_perfil()
        d1,d2 = st.columns(2)
        with d1:
            dp  = st.number_input("Peso (kg)",   30.0,250.0,float(pf2.get("peso",75)),  .5,key="dp")
            da  = st.number_input("Altura (cm)", 100, 250,  int(pf2.get("altura",175)),    key="da")
        with d2:
            de  = st.number_input("Edad",        10,  100,  int(pf2.get("edad",25)),       key="de")
            dsx = st.selectbox("Sexo",["Hombre","Mujer"],key="dsx")
        dact= st.selectbox("Nivel de actividad",[
            "Sedentario (sin ejercicio)","Ligero (1-2 dias/semana)",
            "Moderado (3-4 dias/semana)","Activo (5-6 dias/semana)",
            "Muy activo (2 veces/dia)"],index=2,key="dact")
        dobj= st.selectbox("Objetivo",[
            "Perdida de grasa (-300 kcal)","Perdida agresiva (-500 kcal)",
            "Mantenimiento","Volumen limpio (+200 kcal)","Volumen (+400 kcal)"],key="dobj")
        if st.button("Calcular",key="btn_calc"):
            tdee  = calcular_tdee(dp,da,de,dsx,dact)
            delta = {"Perdida de grasa (-300 kcal)":-300,"Perdida agresiva (-500 kcal)":-500,
                     "Mantenimiento":0,"Volumen limpio (+200 kcal)":200,"Volumen (+400 kcal)":400}[dobj]
            cobj_k = tdee+delta
            perdida = "Perdida" in dobj
            prot_g  = round(dp*(2.2 if perdida else 1.9))
            gras_g  = round(dp*(1.0 if perdida else 1.1))
            carb_g  = max(round((cobj_k-prot_g*4-gras_g*9)/4),50)
            imc     = round(dp/((da/100)**2),1)
            cat_imc = ("Bajo peso" if imc<18.5 else "Normopeso" if imc<25
                       else "Sobrepeso" if imc<30 else "Obesidad")
            st.markdown(card(
                f'<div class="lbl">Resultado</div>'
                f'<div class="sgrid" style="margin-bottom:.65rem">'
                f'<div><div class="lbl">Mantenimiento</div>'
                f'<div class="sv">{tdee}</div>'
                f'<div style="font-size:.62rem;color:var(--text3);font-family:DM Mono,monospace">kcal/dia</div></div>'
                f'<div><div class="lbl">Tu objetivo</div>'
                f'<div class="sv" style="color:var(--accent)">{cobj_k}</div>'
                f'<div style="font-size:.62rem;color:var(--text3);font-family:DM Mono,monospace">kcal/dia</div></div>'
                f'</div>'
                f'<p style="font-size:.8rem;margin-bottom:.45rem">IMC: <b style="color:var(--text)">{imc}</b> — {cat_imc}</p>'
                f'<span class="badge bp">P {prot_g}g</span>'
                f'<span class="badge bc">C {carb_g}g</span>'
                f'<span class="badge bf">G {gras_g}g</span>',True),
                unsafe_allow_html=True)
            if st.button("Guardar objetivos",key="btn_save_calc"):
                st.session_state.datos.setdefault("perfil",{}).update({
                    "peso":dp,"altura":da,"edad":de,
                    "objetivo_cal":cobj_k,"obj_prot":prot_g,"obj_carb":carb_g,"obj_grasa":gras_g})
                guardar_datos(st.session_state.datos)
                st.success("Objetivos guardados.")
                st.rerun()

    with dt3:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        prov = st.session_state.proveedor_ia
        key_a = (st.session_state.groq_key if "Groq" in prov else st.session_state.gemini_key)
        if not key_a.strip():
            st.info(f"Configura tu API Key en Config para usar la IA Dietista (proveedor: {prov}).")
        else:
            pf3 = get_perfil()
            d1,d2 = st.columns(2)
            with d1:
                iap = st.number_input("Peso (kg)",  30.0,250.0,float(pf3.get("peso",75)), .5,key="iap")
                iaa = st.number_input("Altura (cm)",100, 250,  int(pf3.get("altura",175)),   key="iaa")
                iae = st.number_input("Edad",       10,  100,  int(pf3.get("edad",25)),      key="iae")
            with d2:
                iasx= st.selectbox("Sexo",["Hombre","Mujer"],key="iasx")
                iaob= st.selectbox("Objetivo",[
                    "Perder grasa","Ganar musculo","Mantenimiento",
                    "Mejorar rendimiento","Salud general"],key="iaob")
                iaac= st.selectbox("Actividad",
                    ["Sedentario","Ligero","Moderado","Activo","Muy activo"],key="iaac")
            iarest = st.multiselect("Restricciones",[
                "Sin gluten","Sin lactosa","Vegetariano","Vegano",
                "Sin cerdo","Sin mariscos","Bajo en sodio","Bajo en azucar"],key="iarest")
            iaext = st.text_area("Contexto adicional",
                placeholder="Alergias, horarios, patologias, preferencias...",
                height=65,key="iaext")
            if st.button("Generar plan con IA",key="btn_ia"):
                rest_s = ", ".join(iarest) if iarest else "ninguna"
                prompt_d = (
                    f"Eres un dietista-nutricionista experto. Crea un plan de dieta completo en espanol para:\n"
                    f"- Perfil: {iasx}, {iae} anios, {iap}kg, {iaa}cm\n"
                    f"- Objetivo: {iaob} | Actividad: {iaac} | Restricciones: {rest_s}\n"
                    f"- Info extra: {iaext or 'ninguna'}\n\n"
                    f"Incluye:\n"
                    f"1. Calorias recomendadas y distribucion de macros en gramos\n"
                    f"2. Plan de 5-6 comidas con alimentos concretos, cantidades y calorias\n"
                    f"3. Timing nutricional pre/post entreno si aplica\n"
                    f"4. Lista de la compra semanal\n"
                    f"5. 3 consejos clave para el objetivo\n\n"
                    f"Se especifico con cantidades exactas. Usa formato estructurado y claro."
                )
                with st.spinner("Generando plan personalizado..."):
                    res = ia_call(prompt_d)
                    if res.startswith("ERROR_NO_KEY"):
                        st.warning("Configura tu API Key en Config.")
                    else:
                        st.session_state.ia_dieta_res = res
            if st.session_state.ia_dieta_res:
                st.markdown(card(
                    f'<div class="lbl">Plan generado por IA</div>'
                    f'<p style="white-space:pre-wrap;color:var(--text2);'
                    f'font-size:.81rem;line-height:1.8">'
                    f'{st.session_state.ia_dieta_res}</p>'),
                    unsafe_allow_html=True)
                if st.button("Nuevo plan",key="btn_ia_reset"):
                    st.session_state.ia_dieta_res = None
                    st.rerun()

    with dt4:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        dc_all = st.session_state.datos.get("dietas_custom",{})
        if dc_all:
            dc_sel = st.selectbox("Ver dieta",["— Nueva —"]+list(dc_all.keys()),key="dc_sel")
            if dc_sel!="— Nueva —":
                dc = dc_all[dc_sel]
                if dc.get("notas"):
                    st.markdown(card(f'<p style="font-size:.8rem;color:var(--text2)">{dc["notas"]}</p>'),
                                unsafe_allow_html=True)
                for c in dc.get("comidas",[]):
                    st.markdown(card(
                        f'<div style="display:flex;justify-content:space-between;margin-bottom:.3rem">'
                        f'<span style="font-weight:600;font-size:.84rem">{c["nombre"]}</span>'
                        f'<span class="badge bk">{c.get("cal",0)} kcal</span></div>'
                        f'<p style="margin:0 0 .4rem;font-size:.8rem;color:var(--text2)">{c.get("alimentos","")}</p>'
                        f'<span class="badge bp">P {c.get("prot",0)}g</span>'
                        f'<span class="badge bc">C {c.get("carb",0)}g</span>'
                        f'<span class="badge bf">G {c.get("grasa",0)}g</span>'),
                        unsafe_allow_html=True)
                if st.button("Eliminar esta dieta",key="btn_del_dc"):
                    del st.session_state.datos["dietas_custom"][dc_sel]
                    guardar_datos(st.session_state.datos)
                    st.success("Dieta eliminada.")
                    st.rerun()
        sdiv("Crear nueva dieta")
        nc_nom = st.text_input("Nombre de la dieta",placeholder="Mi dieta de verano",key="nc_nom")
        nc_not = st.text_area("Notas",placeholder="Objetivo, duracion, observaciones...",height=55,key="nc_not")
        sdiv("Anadir comidas")
        dc1,dc2 = st.columns([2,1])
        with dc1:
            nc_cn = st.text_input("Nombre de la comida",placeholder="Almuerzo",key="nc_cn")
            nc_al = st.text_area("Alimentos y cantidades",placeholder="Pollo 150g, Arroz 100g...",height=50,key="nc_al")
        with dc2:
            nc_cal= st.number_input("kcal",   0,  3000,0, 10, key="nc_cal")
            nc_pr = st.number_input("P (g)",0.0, 200.0,0.0,.5,key="nc_pr")
            nc_cb2= st.number_input("C (g)",0.0, 500.0,0.0,.5,key="nc_cb2")
            nc_gr = st.number_input("G (g)",0.0, 200.0,0.0,.5,key="nc_gr")
        if st.button("Anadir comida",key="btn_add_nc"):
            if nc_cn:
                st.session_state.comidas_dc_temp.append({
                    "nombre":nc_cn,"alimentos":nc_al,
                    "cal":nc_cal,"prot":nc_pr,"carb":nc_cb2,"grasa":nc_gr})
                st.success(f"'{nc_cn}' anadida.")
            else:
                st.warning("Escribe el nombre de la comida.")
        if st.session_state.comidas_dc_temp:
            tot_dc = sum(c["cal"] for c in st.session_state.comidas_dc_temp)
            filas_dc = "".join(
                f'<div class="row"><span class="rl">{i+1}. {c["nombre"]}</span>'
                f'<span class="rr">{c["cal"]} kcal</span></div>'
                for i,c in enumerate(st.session_state.comidas_dc_temp)
            )
            st.markdown(card(
                f'{filas_dc}'
                f'<div style="text-align:right;margin-top:.4rem">'
                f'<span class="badge bk">Total: {tot_dc} kcal</span></div>'),
                unsafe_allow_html=True)
        if st.button("Guardar dieta",key="btn_save_dc"):
            if not nc_nom:
                st.warning("Dale un nombre a la dieta.")
            elif not st.session_state.comidas_dc_temp:
                st.warning("Anade al menos una comida.")
            else:
                st.session_state.datos.setdefault("dietas_custom",{})[nc_nom] = {
                    "notas":nc_not,"comidas":st.session_state.comidas_dc_temp.copy()}
                guardar_datos(st.session_state.datos)
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
            tc,tbg = TIPO_COLOR.get(ej["tipo"],("#7a8099","rgba(122,128,153,.1)"))
            st.markdown(card(
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
                f'gap:.4rem;flex-wrap:wrap;margin-bottom:.4rem">'
                f'<span style="font-weight:600;font-size:.88rem;color:var(--text)">{ej["nombre"]}</span>'
                f'<span class="typebadge" style="color:{tc};background:{tbg};border-color:{tc}50">'
                f'{ej["tipo"]}</span></div>'
                f'<div style="font-size:.72rem;color:var(--text3);margin-bottom:.3rem">{ej["equipo"]}</div>'
                f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;font-size:.77rem;color:var(--text2);margin-bottom:.3rem">'
                f'<span>{ej["series_rec"]} series</span>'
                f'<span style="color:var(--text3)">·</span>'
                f'<span>{ej["reps_rec"]} reps</span>'
                f'<span style="color:var(--text3)">·</span>'
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
            st.markdown(
                f'<div style="font-size:.75rem;color:var(--text3);margin-bottom:.75rem">{desc}</div>',
                unsafe_allow_html=True)
        for idx,ej in enumerate(ejs):
            p_s = f" · {ej['peso']}" if ej.get("peso") else ""
            n_s = (f'<p style="font-size:.72rem;color:var(--text3);font-style:italic;margin-top:.25rem">'
                   f'{ej["notas"]}</p>' if ej.get("notas") else "")
            st.markdown(card(
                f'<div style="display:flex;align-items:flex-start;gap:.65rem">'
                f'<div style="font-family:DM Mono,monospace;font-size:.6rem;color:var(--text3);padding-top:.15rem;min-width:18px">'
                f'{idx+1:02d}</div>'
                f'<div style="flex:1">'
                f'<div style="font-weight:600;font-size:.85rem;color:var(--text);margin-bottom:.25rem">{ej["ejercicio"]}</div>'
                f'<div style="display:flex;gap:.35rem;flex-wrap:wrap;font-size:.76rem;color:var(--text2)">'
                f'<span>{ej["series"]} series</span><span style="color:var(--text3)">·</span>'
                f'<span>{ej["reps"]} reps</span><span style="color:var(--text3)">·</span>'
                f'<span>{ej["descanso"]}{p_s}</span></div>{n_s}'
                f'</div></div>'),
                unsafe_allow_html=True)

        sdiv("Crear rutina personalizada")
        with st.expander("Nueva rutina"):
            nr_n = st.text_input("Nombre",placeholder="Mi rutina de lunes",key="nr_n")
            nr_d = st.text_input("Descripcion",placeholder="Pecho y triceps",key="nr_d")
            sdiv("Ejercicios de la rutina")
            ne1,ne2,ne3 = st.columns([3,1,2])
            with ne1: nr_ej = st.text_input("Ejercicio",placeholder="Press banca",key="nr_ej",label_visibility="collapsed")
            with ne2: nr_s  = st.number_input("Series",1,20,4,key="nr_s",label_visibility="collapsed")
            with ne3: nr_r  = st.text_input("Reps",placeholder="8-12",key="nr_r",label_visibility="collapsed")
            ne4,ne5,ne6 = st.columns([2,2,2])
            with ne4: nr_p = st.text_input("Peso",placeholder="60kg",key="nr_p",label_visibility="collapsed")
            with ne5: nr_dc= st.text_input("Descanso",placeholder="90s",key="nr_dc",label_visibility="collapsed")
            with ne6: nr_nt= st.text_input("Nota",placeholder="Tecnica...",key="nr_nt",label_visibility="collapsed")

            if st.button("Anadir ejercicio",key="btn_add_ej"):
                if nr_ej:
                    st.session_state.ej_temp.append({
                        "ejercicio":nr_ej,"series":nr_s,"reps":nr_r or "8-12",
                        "peso":nr_p,"descanso":nr_dc or "60s","notas":nr_nt})
                    st.success(f"'{nr_ej}' anadido.")
                else:
                    st.warning("Escribe el nombre del ejercicio.")

            if st.session_state.ej_temp:
                filas_ej = "".join(
                    f'<div class="row"><span class="rl">{i+1}. {e["ejercicio"]}</span>'
                    f'<span class="rr">{e["series"]}x{e["reps"]}</span></div>'
                    for i,e in enumerate(st.session_state.ej_temp)
                )
                st.markdown(card(filas_ej),unsafe_allow_html=True)

            if st.button("Guardar rutina",key="btn_save_rut"):
                if not nr_n:
                    st.warning("Dale un nombre a la rutina.")
                elif not st.session_state.ej_temp:
                    st.warning("Anade al menos un ejercicio.")
                else:
                    st.session_state.datos.setdefault("rutinas_custom",{})[nr_n] = {
                        "desc":nr_d,"ejercicios":st.session_state.ej_temp.copy()}
                    guardar_datos(st.session_state.datos)
                    st.session_state.ej_temp = []
                    st.success(f"Rutina '{nr_n}' guardada.")
                    st.rerun()

    with g3:
        st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)
        reg_fecha  = str(st.session_state.get("reg_f", hoy()))
        reg_tipo   = ""
        reg_dur    = 60
        reg_notas  = ""

        r1,r2 = st.columns(2)
        with r1:
            reg_tipo = st.selectbox("Tipo de sesion",
                ["PPL — Empuje","PPL — Tiron","PPL — Piernas",
                 "Full Body","Upper","Lower","HIIT","Calistenia","Cardio","Otro"],
                key="reg_tipo")
        with r2:
            reg_dur = st.number_input("Duracion (min)",10,300,60,key="reg_dur")
        reg_notas = st.text_area("Notas del entreno",
            placeholder="Sensaciones, PRs, observaciones...",height=65,key="reg_notas")

        sdiv("Series registradas")
        sr1,sr2,sr3,sr4 = st.columns(4)
        with sr1: ej_n  = st.text_input("Ejercicio",placeholder="Sentadilla",key="ej_n", label_visibility="collapsed")
        with sr2: set_s = st.number_input("Series",1,20,3,key="set_s",label_visibility="collapsed")
        with sr3: set_r = st.text_input("Reps",placeholder="10",key="set_r",label_visibility="collapsed")
        with sr4: set_p = st.text_input("Peso",placeholder="80kg",key="set_p",label_visibility="collapsed")

        if st.button("Anadir serie",key="btn_add_set"):
            if ej_n:
                st.session_state.sets_temp.append({
                    "ejercicio":ej_n,"series":set_s,
                    "reps":set_r or "—","peso":set_p or "—"})
                st.success(f"'{ej_n}' registrado.")
            else:
                st.warning("Escribe el nombre del ejercicio.")

        if st.session_state.sets_temp:
            filas_s = "".join(
                f'<div class="row">'
                f'<span class="rl">{s["ejercicio"]}</span>'
                f'<span class="rr">{s["series"]}x{s["reps"]} · {s["peso"]}</span></div>'
                for s in st.session_state.sets_temp
            )
            st.markdown(card(filas_s),unsafe_allow_html=True)

        if st.button("Guardar sesion",key="btn_save_ses"):
            if not reg_tipo:
                st.warning("Selecciona el tipo de sesion.")
            else:
                reg = st.session_state.datos.setdefault("registro_entreno",{})
                fecha_k = hoy()
                reg.setdefault(fecha_k,[]).append({
                    "tipo":reg_tipo,"duracion":reg_dur,
                    "notas":reg_notas,
                    "series":st.session_state.sets_temp.copy(),
                    "hora":datetime.now().strftime("%H:%M"),
                })
                guardar_datos(st.session_state.datos)
                st.session_state.sets_temp = []
                st.success("Sesion guardada.")
                st.rerun()

        # Historial de entrenos
        sdiv("Ultimas sesiones")
        reg_all = st.session_state.datos.get("registro_entreno",{})
        fechas_ordenadas = sorted(reg_all.keys(),reverse=True)[:7]
        if not fechas_ordenadas:
            st.markdown(card(
                '<div style="text-align:center;padding:.85rem 0">'
                '<p style="color:var(--text3);font-size:.77rem">Sin sesiones registradas todavia</p></div>'),
                unsafe_allow_html=True)
        for fecha_k in fechas_ordenadas:
            for ses in reg_all[fecha_k]:
                n_series = len(ses.get("series",[]))
                st.markdown(card(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem">'
                    f'<span style="font-weight:600;font-size:.84rem">{ses["tipo"]}</span>'
                    f'<span class="badge bn">{fecha_k}</span></div>'
                    f'<div style="display:flex;gap:.35rem;flex-wrap:wrap;font-size:.76rem;color:var(--text2)">'
                    f'<span>{ses["duracion"]} min</span>'
                    f'<span style="color:var(--text3)">·</span>'
                    f'<span>{n_series} ejercicios</span>'
                    f'<span style="color:var(--text3)">·</span>'
                    f'<span>{ses["hora"]}</span></div>'
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
        st.markdown(card(
            '<div style="text-align:center;padding:1.25rem 0">'
            '<div class="lbl" style="text-align:center">Sin historial</div>'
            '<p style="color:var(--text3);font-size:.77rem">Empieza a registrar alimentos en Nutricion</p></div>'),
            unsafe_allow_html=True)
    else:
        fechas = sorted(hist_c.keys())[-14:]
        vals   = [hist_c.get(f,0) for f in fechas]
        etiq   = [f[-5:] for f in fechas]
        obj_h  = get_obj_cal()

        if vals:
            prom  = round(sum(vals)/len(vals))
            maxi  = max(vals)
            mini  = min(v for v in vals if v>0) if any(v>0 for v in vals) else 0
            dias_ok = sum(1 for v in vals if 0<v<=obj_h)
            st.markdown(card(
                f'<div class="lbl">Ultimos 14 dias</div>'
                f'<div class="sgrid">'
                f'<div><div class="lbl">Promedio diario</div><div class="sv">{prom}</div>'
                f'<div class="ms">kcal/dia</div></div>'
                f'<div><div class="lbl">Dias en objetivo</div><div class="sv" style="color:var(--teal)">{dias_ok}</div>'
                f'<div class="ms">de {len([v for v in vals if v>0])}</div></div>'
                f'</div>',True),
                unsafe_allow_html=True)

            max_v = max(vals+[obj_h,1])
            bars_html = '<div style="display:flex;align-items:flex-end;gap:3px;height:90px;margin-top:1rem">'
            for i,(et,vl) in enumerate(zip(etiq,vals)):
                h = int(vl/max_v*90) if vl>0 else 2
                clr = "var(--teal)" if vl<=obj_h and vl>0 else ("var(--red)" if vl>obj_h else "var(--s3)")
                bars_html += (
                    f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">'
                    f'<div style="flex:1;display:flex;align-items:flex-end;width:100%">'
                    f'<div style="width:100%;height:{h}px;background:{clr};border-radius:2px 2px 0 0"></div></div>'
                    f'<div style="font-family:DM Mono,monospace;font-size:.46rem;color:var(--text3);white-space:nowrap">{et}</div>'
                    f'</div>'
                )
            bars_html += '</div>'
            st.markdown(card(
                f'<div class="lbl">Calorias diarias</div>'
                f'{bars_html}'
                f'<div style="display:flex;gap:.6rem;margin-top:.5rem;flex-wrap:wrap">'
                f'<span class="badge bp" style="font-size:.55rem">Verde = dentro del objetivo</span>'
                f'<span class="badge bw" style="font-size:.55rem">Rojo = por encima</span></div>'),
                unsafe_allow_html=True)

        prom_macros = {"prot":0.0,"carb":0.0,"grasa":0.0}
        dias_m = [d for d in fechas if d in hist_m and any(v>0 for v in hist_m[d].values())]
        if dias_m:
            for d in dias_m:
                for k in prom_macros:
                    prom_macros[k] += hist_m[d].get(k,0)
            n = len(dias_m)
            prom_macros = {k:round(v/n,1) for k,v in prom_macros.items()}
            st.markdown(card(
                f'<div class="lbl">Promedio de macros (diario)</div>'
                f'<div class="mgrid">'
                f'<div><div class="lbl">Proteina</div>'
                f'<div class="mv" style="color:var(--teal)">{prom_macros["prot"]}g</div></div>'
                f'<div><div class="lbl">Carbos</div>'
                f'<div class="mv" style="color:var(--blue)">{prom_macros["carb"]}g</div></div>'
                f'<div><div class="lbl">Grasas</div>'
                f'<div class="mv" style="color:var(--purple)">{prom_macros["grasa"]}g</div></div>'
                f'</div>'),
                unsafe_allow_html=True)

        sesiones_t = sum(len(v) for v in reg_e.values())
        horas_t    = sum(s.get("duracion",0) for v in reg_e.values() for s in v)
        if sesiones_t>0:
            st.markdown(card(
                f'<div class="lbl">Resumen de entrenos</div>'
                f'<div class="sgrid">'
                f'<div><div class="lbl">Sesiones totales</div><div class="sv">{sesiones_t}</div></div>'
                f'<div><div class="lbl">Horas totales</div><div class="sv" style="color:var(--accent)">{round(horas_t/60,1)}</div></div>'
                f'</div>'),
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
with t_cfg:
    st.markdown('<div style="height:.5rem"></div>',unsafe_allow_html=True)

    # ── SELECTOR DE PROVEEDOR IA ──
    st.markdown(card(
        '<div class="lbl">Proveedor de IA</div>'
        '<p style="font-size:.78rem;color:var(--text2);margin-bottom:.6rem">'
        'Groq es la opcion recomendada: es gratuita, generosa (1500 peticiones/dia) '
        'y muy rapida. Gemini tiene limite reducido (~20 peticiones/dia en capa gratuita).</p>'),
        unsafe_allow_html=True)

    prov_sel = st.selectbox("",
        ["Groq (recomendado)","Gemini"],
        index=0 if "Groq" in st.session_state.proveedor_ia else 1,
        key="prov_sel",label_visibility="collapsed")
    if st.button("Seleccionar proveedor",key="btn_prov"):
        st.session_state.proveedor_ia = prov_sel
        st.success(f"Proveedor cambiado a: {prov_sel}")
        st.rerun()

    # ── GROQ API KEY ──
    sdiv("Groq API Key (recomendado)")
    st.markdown(card(
        '<div class="lbl">Como obtener tu Groq API Key GRATIS</div>'
        '<div class="row"><span class="rl">1. Accede a</span>'
        '<span class="rr">console.groq.com/keys</span></div>'
        '<div class="row"><span class="rl">2. Registrate con Google o email</span>'
        '<span class="rr">Sin tarjeta de credito</span></div>'
        '<div class="row"><span class="rl">3. Pulsa "Create API Key"</span>'
        '<span class="rr">Empieza por gsk_...</span></div>'
        '<div class="row"><span class="rl">4. Limite gratuito</span>'
        '<span class="rr">1500 peticiones/dia</span></div>'),
        unsafe_allow_html=True)

    groq_input = st.text_input("Groq API Key",
        value=st.session_state.groq_key,
        type="password",placeholder="gsk_...",key="groq_input")
    if st.button("Guardar Groq Key",key="btn_groq"):
        st.session_state.groq_key = groq_input.strip()
        st.session_state.datos.setdefault("perfil",{})["groq_key"] = groq_input.strip()
        guardar_datos(st.session_state.datos)
        st.success("Groq API Key guardada.")
    if st.session_state.groq_key and st.button("Probar conexion Groq",key="btn_test_groq"):
        with st.spinner("Probando..."):
            prev = st.session_state.proveedor_ia
            st.session_state.proveedor_ia = "Groq (recomendado)"
            res = ia_call("Responde solo con: OK")
            st.session_state.proveedor_ia = prev
            if "OK" in res or len(res)<80:
                st.success(f"Groq conectado. Respuesta: {res[:60]}")
            else:
                st.error(f"Error: {res[:200]}")

    # ── GEMINI API KEY ──
    sdiv("Gemini API Key (alternativo)")
    st.markdown(card(
        '<div class="lbl">Importante sobre Gemini gratuito</div>'
        '<p style="font-size:.78rem;color:var(--text2);margin-bottom:.5rem">'
        'Desde diciembre 2025 Google redujo el limite gratuito de Gemini a ~20 peticiones/dia. '
        'Si obtienes error 429 es porque agotaste esa cuota. Solucion: usa Groq (arriba).</p>'
        '<div class="row"><span class="rl">Obtener key en</span>'
        '<span class="rr">aistudio.google.com/app/apikeys</span></div>'
        '<div class="row"><span class="rl">Modelo usado</span>'
        '<span class="rr">gemini-1.5-flash</span></div>'
        '<div class="row"><span class="rl">Limite gratuito aprox</span>'
        '<span class="rr">~20 peticiones/dia (2026)</span></div>'),
        unsafe_allow_html=True)

    gemini_input = st.text_input("Gemini API Key",
        value=st.session_state.gemini_key,
        type="password",placeholder="AIzaSy...",key="gemini_input")
    if st.button("Guardar Gemini Key",key="btn_gem"):
        st.session_state.gemini_key = gemini_input.strip()
        st.session_state.datos.setdefault("perfil",{})["gemini_key"] = gemini_input.strip()
        guardar_datos(st.session_state.datos)
        st.success("Gemini API Key guardada.")
    if st.session_state.gemini_key and st.button("Probar conexion Gemini",key="btn_test_gem"):
        with st.spinner("Probando..."):
            prev = st.session_state.proveedor_ia
            st.session_state.proveedor_ia = "Gemini"
            res = ia_call("Responde solo con: OK")
            st.session_state.proveedor_ia = prev
            if "OK" in res or len(res)<80:
                st.success(f"Gemini conectado. Respuesta: {res[:60]}")
            else:
                st.error(f"Error: {res[:200]}")

    # ── PERFIL ──
    sdiv("Perfil personal")
    pf_c = get_perfil()
    cfg1,cfg2 = st.columns(2)
    with cfg1:
        c_nombre = st.text_input("Nombre",value=pf_c.get("nombre",""),key="c_nombre")
        c_peso   = st.number_input("Peso (kg)",30.0,250.0,float(pf_c.get("peso",75.0)),.5,key="c_peso")
        c_altura = st.number_input("Altura (cm)",100,250,int(pf_c.get("altura",175)),key="c_altura")
    with cfg2:
        c_edad   = st.number_input("Edad",10,100,int(pf_c.get("edad",25)),key="c_edad")
        c_objcal = st.number_input("Objetivo kcal/dia",800,6000,int(pf_c.get("objetivo_cal",2000)),50,key="c_objcal")
        c_prot   = st.number_input("Obj. proteina (g)",0,400,int(pf_c.get("obj_prot",150)),5,key="c_prot")
    cfg3,cfg4 = st.columns(2)
    with cfg3:
        c_carb = st.number_input("Obj. carbos (g)",  0,800,int(pf_c.get("obj_carb",220)),5,key="c_carb")
    with cfg4:
        c_gras = st.number_input("Obj. grasas (g)",  0,300,int(pf_c.get("obj_grasa",60)),5,key="c_gras")

    if st.button("Guardar perfil",key="btn_perfil"):
        st.session_state.datos["perfil"].update({
            "nombre":c_nombre,"peso":c_peso,"altura":c_altura,"edad":c_edad,
            "objetivo_cal":c_objcal,"obj_prot":c_prot,"obj_carb":c_carb,"obj_grasa":c_gras,
        })
        guardar_datos(st.session_state.datos)
        st.success("Perfil guardado.")
        st.rerun()

    # Restaurar keys del perfil guardado al iniciar
    pf_saved = st.session_state.datos.get("perfil",{})
    if not st.session_state.groq_key and pf_saved.get("groq_key"):
        st.session_state.groq_key = pf_saved["groq_key"]
    if not st.session_state.gemini_key and pf_saved.get("gemini_key"):
        st.session_state.gemini_key = pf_saved["gemini_key"]
