import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, PLOTLY_LAYOUT, sidebar_logo, nota, link_fonte

st.set_page_config(page_title="Preços de Energia — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "prices.csv")

LABELS   = {"brent":"Brent","henry_hub":"Henry Hub","diesel_us":"Diesel (ref. intl.)","dolar":"Dólar","glp_p13_brl":"GLP P13 (varejo)","gnv_brl":"GNV","glp_campos_brl":"GLP Campos (prod.)"}
UNIDADES = {"brent":"USD/barril","henry_hub":"USD/MMBtu","diesel_us":"USD/galão","dolar":"BRL/USD","glp_p13_brl":"R$/kg","gnv_brl":"R$/m³","glp_campos_brl":"R$/m³"}
CORES    = {"brent":PETROLEO,"henry_hub":VERDE,"diesel_us":LARANJA,"dolar":AMARELO,"glp_p13_brl":CINZA,"gnv_brl":"#4A7C8E","glp_campos_brl":"#8E6A4A"}
FONTES_URL = {
    "brent":         "https://finance.yahoo.com/quote/BZ%3DF/",
    "henry_hub":     "https://finance.yahoo.com/quote/NG%3DF/",
    "diesel_us":     "https://finance.yahoo.com/quote/HO%3DF/",
    "dolar":         "https://finance.yahoo.com/quote/BRL%3DX/",
    "glp_p13_brl":   "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos",
    "gnv_brl":       "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos",
    "glp_campos_brl":"https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos",
}

# TTL=0 garante que sempre lê o arquivo mais recente sem cache obsoleto
@st.cache_data(ttl=0)
def load():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, index_col="date", parse_dates=True)
        df = df[df.index.notna()]
        if len(df) >= 2:
            return df.sort_index()
    return None

df = load()

with st.sidebar:
    sidebar_logo()
    if df is not None:
        periodos = {"6 meses":26,"1 ano":52,"2 anos":104,"3 anos":156,"5 anos":260,"Tudo":9999}
        periodo_sel = st.radio("Período histórico", list(periodos.keys()), index=1)
        n_sem = periodos[periodo_sel]
        st.markdown("---")
        series_disp = [c for c in df.columns if c in LABELS]
        series_sel = st.multiselect("Séries exibidas", series_disp, default=series_disp,
                                    format_func=lambda x: f"{LABELS.get(x,x)} ({UNIDADES.get(x,'')})")
        st.markdown("---")
        modo = st.radio("Modo de exibição", ["Valor original","Converter para Real (R$)","Normalizar (base 100)"], index=0)
        if modo == "Converter para Real (R$)":
            st.caption("Multiplica cada série USD pela taxa de câmbio semanal da série Dólar (BRL=X).")
        elif modo == "Normalizar (base 100)":
            st.caption("Todas as séries partem de 100 no início do período.")

st.markdown("""
<div class="page-header">
    <h1>Comparativo de Preços de Energia</h1>
    <p>Brent · Henry Hub · GLP P13 · GLP Campos · GNV · Diesel · Dólar &nbsp;|&nbsp; Atualização: toda segunda-feira via GitHub Actions</p>
</div>
""", unsafe_allow_html=True)

if df is None:
    st.warning("⚠️ **Dados não carregados.** Execute `python fetch_data.py` localmente ou aguarde a execução automática do GitHub Actions toda segunda-feira.")
    st.stop()

if not series_sel:
    st.warning("Selecione ao menos uma série no menu lateral.")
    st.stop()

ultima = df.index[-1].strftime("%d/%m/%Y")
st.caption(f"Última coleta: **{ultima}** — dados reais do Yahoo Finance e ANP.")

df_win = df.tail(n_sem)[series_sel].dropna(how="all")

def to_brl(df_in):
    out = df_in.copy()
    if "dolar" not in out.columns: return out
    taxa = out["dolar"].ffill()
    for c in out.columns:
        if c == "dolar": continue
        if c == "diesel_us": out[c] = out[c] * taxa / 3.785
        elif c in ["brent","henry_hub"]: out[c] = out[c] * taxa
    return out

df_plot = df_win.copy()
if modo == "Converter para Real (R$)":    df_plot = to_brl(df_plot)
elif modo == "Normalizar (base 100)":
    for c in df_plot.columns:
        first = df_plot[c].dropna().iloc[0] if not df_plot[c].dropna().empty else 1
        df_plot[c] = df_plot[c] / first * 100

# KPIs
st.markdown('<div class="sec-header">Última cotação</div>', unsafe_allow_html=True)
cols = st.columns(len(series_sel))
for i, cn in enumerate(series_sel):
    serie = df_plot[cn].dropna()
    if serie.empty: continue
    v, vp = serie.iloc[-1], (serie.iloc[-2] if len(serie)>1 else serie.iloc[-1])
    delta = (v-vp)/vp*100 if vp else 0
    un = UNIDADES.get(cn,"")
    if modo=="Converter para Real (R$)" and cn in ["brent","henry_hub","diesel_us"]: un="R$"
    with cols[i]:
        cor = CORES.get(cn,CINZA)
        delta_cls = "up" if delta>=0 else "down"
        delta_sign = "+" if delta>=0 else ""
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{cor}">
            <div class="kpi-label">{LABELS.get(cn,cn)}</div>
            <div class="kpi-value">{v:,.2f}</div>
            <div class="kpi-delta {delta_cls}">{delta_sign}{delta:.1f}% vs semana anterior</div>
            <div class="kpi-sub">{un} · {serie.index[-1].strftime('%d/%m/%Y')}</div>
        </div>
        """, unsafe_allow_html=True)

# Gráfico histórico — sem projeção
st.markdown('<div class="sec-header">Histórico de preços</div>', unsafe_allow_html=True)
fig = go.Figure()
for cn in series_sel:
    serie = df_plot[cn].dropna()
    if serie.empty: continue
    cor = CORES.get(cn, CINZA)
    fig.add_trace(go.Scatter(
        x=serie.index, y=serie.values, name=LABELS.get(cn,cn),
        line=dict(color=cor, width=2),
        hovertemplate="%{x|%d/%m/%Y}<br><b>%{y:,.3f}</b><extra></extra>",
    ))

titulo_y = "R$" if modo=="Converter para Real (R$)" else "Índice (base 100)" if modo=="Normalizar (base 100)" else "Valor"
layout = dict(PLOTLY_LAYOUT); layout["height"]=450; layout["yaxis"]=dict(PLOTLY_LAYOUT["yaxis"],title=titulo_y)
fig.update_layout(**layout)
st.plotly_chart(fig, use_container_width=True)

# Correlação
if len(series_sel)>=2:
    st.markdown('<div class="sec-header">Correlação entre séries</div>', unsafe_allow_html=True)
    corr = df_win[series_sel].corr().round(2)
    corr.index   = [LABELS.get(c,c) for c in corr.index]
    corr.columns = [LABELS.get(c,c) for c in corr.columns]
    fig_c = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
        colorscale=[[0,"#b83232"],[0.5,"#f5f5f5"],[1,VERDE]],
        zmid=0, zmin=-1, zmax=1, text=corr.values, texttemplate="%{text}",
        hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>",
    ))
    fig_c.update_layout(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="Poppins",color=ESCURO),height=260,margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_c, use_container_width=True)
    nota("<strong>Correlação de Pearson:</strong> mede a relação linear entre duas séries no período selecionado. +1 = movem-se juntas, 0 = sem relação linear, −1 = sentidos opostos. Calculada sobre os valores originais (não normalizados).","calc")

# Fontes
st.markdown('<div class="sec-header">Fontes primárias dos dados</div>', unsafe_allow_html=True)
for cn in series_sel:
    if cn in FONTES_URL:
        st.markdown(f"[{LABELS.get(cn,cn)} — {UNIDADES.get(cn,'')}]({FONTES_URL[cn]})", unsafe_allow_html=False)

with st.expander("Exportar dados"):
    df_exp = df_plot[series_sel].copy()
    df_exp.columns = [f"{LABELS.get(c,c)} ({UNIDADES.get(c,'')})" for c in df_exp.columns]
    df_exp.index   = df_exp.index.strftime("%d/%m/%Y")
    st.dataframe(df_exp.style.format("{:.4f}", na_rep="-"), use_container_width=True)
    st.download_button("Baixar CSV", df_exp.to_csv().encode("utf-8"), "precos_energia_cnp.csv", "text/csv")
