import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, sidebar_logo

st.set_page_config(
    page_title="Inteligência de Mercado - CNP",
    page_icon="assets/logo.png" if os.path.exists("assets/logo.png") else None,
    layout="wide", initial_sidebar_state="expanded",
)
st.markdown(CSS_BASE, unsafe_allow_html=True)

with st.sidebar:
    sidebar_logo()

ultima = ""
if os.path.exists("data/last_update.txt"):
    try:
        from datetime import datetime
        ultima = datetime.strptime(open("data/last_update.txt").read().strip(), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        pass

partes_info = []
if ultima:
    partes_info.append(f"Última atualização: <strong style='color:white'>{ultima}</strong>")
partes_info.append("Preços: toda segunda-feira")
partes_info.append("Dados territoriais: mensal")
info_str = " &nbsp;|&nbsp; ".join(partes_info)

st.markdown(f"""
<div class="page-header">
    <h1>Inteligência de Mercado — CNP</h1>
    <p>Plataforma integrada para análise de mercado, energia, logística e ESG. &nbsp;|&nbsp; {info_str}</p>
</div>
""", unsafe_allow_html=True)

paineis = [
    {"n":"01","titulo":"Comparativo de Preços","desc":"Brent, Henry Hub, GLP, GNV, Diesel e Dólar — histórico, conversão para Real e memória de cálculo.","cor":PETROLEO},
    {"n":"02","titulo":"Mercado & Território","desc":"PIB, população e inteligência de mercado focada em SP, PR, MS e RJ — com simuladores de potencial.","cor":VERDE},
    {"n":"03","titulo":"Empresas & Potencial","desc":"Pipeline de prospecção com score multi-dimensional: fit setorial, geográfico, maturidade, porte e estrutura.","cor":LARANJA},
    {"n":"04","titulo":"Consumo Energético","desc":"Balanço energético por setor com simuladores de substituição e potencial de mercado para biometano.","cor":AMARELO},
    {"n":"05","titulo":"Logística & Raio","desc":"Calculadora de custo logístico, raio viável, mapa de clientes e simulador de rentabilidade por rota.","cor":"#4A7C8E"},
    {"n":"06","titulo":"ESG & CBIO","desc":"Emissões SEEG por setor, preço CBIO, metas RenovaBio e simulador de receita por volume de créditos.","cor":"#5A9A3A"},
]

cols = st.columns(3)
for i, p in enumerate(paineis):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="painel-card" style="border-color:{p['cor']}">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
                <span style="background:{p['cor']};color:white;font-family:Poppins,sans-serif;
                             font-weight:700;font-size:11px;padding:3px 9px;border-radius:6px">{p['n']}</span>
                <span style="font-family:Poppins,sans-serif;font-weight:600;font-size:15px;color:{ESCURO}">{p['titulo']}</span>
            </div>
            <p style="font-size:13px;color:#555;line-height:1.55;margin:0;font-family:Poppins,sans-serif">{p['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="sec-header">Periodicidade de atualização</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
for col, freq, itens, cor in [
    (col1, "Semanal (toda segunda)",
     ["Preço Brent (Yahoo Finance)","Henry Hub (Yahoo Finance)","Diesel ref. intl. (Yahoo Finance)","Dólar BRL/USD (Yahoo Finance)","CBIO (B3 via Yahoo Finance)"],
     VERDE),
    (col2, "Mensal (dia 1 do mês)",
     ["PIB municipal — IBGE SIDRA","População estimada — IBGE","GLP P13 — ANP dados abertos","GNV — ANP dados abertos","Emissões SEEG — quando disponível"],
     PETROLEO),
    (col3, "Estático / referência",
     ["Consumo energético BEN — EPE (anual)","Tabela CNAE — IBGE/CONCLA","Score setorial de prospecção","Parâmetros logísticos padrão"],
     CINZA),
]:
    with col:
        itens_html = "".join([f"<li style='margin:3px 0;font-size:12px;color:#555'>{it}</li>" for it in itens])
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:16px;
                    border:2px solid {cor};
                    box-shadow:0 3px 12px rgba(0,0,0,0.08)">
            <div style="font-weight:600;font-size:13px;color:{cor};margin-bottom:10px;font-family:Poppins,sans-serif">{freq}</div>
            <ul style="margin:0;padding-left:16px">{itens_html}</ul>
        </div>
        """, unsafe_allow_html=True)
