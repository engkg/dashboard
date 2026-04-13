import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, PLOTLY_LAYOUT, sidebar_logo, nota, link_fonte

st.set_page_config(page_title="ESG & CBIO — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

CBIO_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "cbio.csv")

# SEEG: publicação anual do Instituto Clima e Sociedade — atualizar quando nova edição sair
SEEG = {
    "Agropecuária": 596.3,
    "Energia": 421.8,
    "Mudança de uso do solo": 380.2,
    "Processos industriais": 98.4,
    "Resíduos": 92.1,
    "Tratamento de esgoto": 31.5,
}
SEEG_ANO_REF = 2022
# Metas RenovaBio anuais (ANP — valores oficiais publicados)
METAS_RENOVABIO = {2020:5.0, 2021:10.0, 2022:14.0, 2023:12.0, 2024:13.0, 2025:14.5}

@st.cache_data(ttl=0)
def load_cbio():
    if os.path.exists(CBIO_FILE):
        df = pd.read_csv(CBIO_FILE, index_col="date", parse_dates=True)
        df = df[df["preco_cbio"].notna()]
        if len(df) >= 4:
            return df.sort_index()
    return None

df_cbio_raw = load_cbio()
cbio_ok = df_cbio_raw is not None

with st.sidebar:
    sidebar_logo()
    if cbio_ok:
        volume_cbio = st.number_input("Volume CBIOs da CNP (unid.)", value=10000, step=1000)
        st.caption("Estime a receita potencial com base nos CBIOs gerados pela operação.")
    else:
        volume_cbio = 10000
    st.markdown("---")
    st.caption("""
**O que é CBIO?**
Crédito de Descarbonização (Lei RenovaBio 13.576/2017). Cada CBIO = descarbonização de 1 tCO2e. Produtores certificados emitem CBIOs, negociados na B3. Distribuidoras têm metas anuais obrigatórias.
    """)

st.markdown("""
<div class="page-header">
    <h1>ESG & CBIO</h1>
    <p>Emissões SEEG por setor · Preço CBIO · Metas RenovaBio · Simulador de receita</p>
</div>
""", unsafe_allow_html=True)

# KPIs CBIO — só quando dados disponíveis
if cbio_ok:
    df_cbio_raw["ano"] = df_cbio_raw.index.year
    df_hist = df_cbio_raw.groupby("ano")["preco_cbio"].mean().reset_index()
    df_hist.columns = ["ano", "preco"]
    preco_atual = df_cbio_raw["preco_cbio"].iloc[-1]
    ultima_data = df_cbio_raw.index[-1].strftime("%d/%m/%Y")
    receita_est = preco_atual * volume_cbio

    st.markdown(f'<div class="sec-header">Painel CBIO — {df_hist["ano"].iloc[-1]} | Última cotação B3: {ultima_data}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for col, label, val, sub, cor in [
        (c1, "Preço CBIO", f"R$ {preco_atual:.2f}", f"por crédito em {ultima_data}", VERDE),
        (c2, "Receita estimada CNP", f"R$ {receita_est:,.0f}", f"{volume_cbio:,} CBIOs × R$ {preco_atual:.2f}", LARANJA),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card" style="border-color:{cor}">
                <div class="kpi-label">{label}</div><div class="kpi-value">{val}</div>
                <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Histórico CBIO", "Emissões SEEG", "Simulador de receita"])

with tab1:
    if not cbio_ok:
        st.warning("⚠️ Dados CBIO não carregados. Execute `python fetch_data.py` para buscar preços da B3.")
    else:
        fig_cbio = go.Figure()
        fig_cbio.add_trace(go.Scatter(
            x=df_hist["ano"], y=df_hist["preco"], name="Preço médio anual CBIO (R$)",
            line=dict(color=PETROLEO, width=2.5), marker=dict(size=7),
            hovertemplate="%{x}: R$ %{y:.2f}<extra></extra>",
        ))
        fig_cbio.add_trace(go.Scatter(
            x=df_cbio_raw.index, y=df_cbio_raw["preco_cbio"],
            name="Cotação semanal B3", line=dict(color=VERDE, width=1, dash="dot"),
            opacity=0.55, hovertemplate="%{x|%d/%m/%Y}: R$ %{y:.2f}<extra></extra>",
        ))
        fig_cbio.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Poppins", color=ESCURO),
            height=340, margin=dict(l=0, r=0, t=10, b=48),
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2, font=dict(size=11)),
            yaxis=dict(title="Preço CBIO (R$)", gridcolor="#f0f0f0"),
            xaxis=dict(dtick=1),
        )
        st.plotly_chart(fig_cbio, use_container_width=True)
        nota(f"""
        <strong>Fonte:</strong> B3 — CBIO3.SA via Yahoo Finance (dados reais carregados de data/cbio.csv).
        Última cotação disponível: <strong>R$ {preco_atual:.2f}</strong> em {ultima_data}.
        Preço médio anual calculado sobre as cotações semanais do arquivo.
        <strong>O que é CBIO?</strong> Crédito de Descarbonização (RenovaBio, Lei 13.576/2017). 1 CBIO = 1 tCO2e evitada.
        """, "fonte")
        link_fonte("ANP — RenovaBio", "https://www.gov.br/anp/pt-br/assuntos/renovabio")
        link_fonte("B3 — CBIO3.SA", "https://www.b3.com.br/")

with tab2:
    cl, cr = st.columns(2)
    df_seeg = pd.DataFrame(list(SEEG.items()), columns=["setor","emissoes"]).sort_values("emissoes", ascending=True)
    with cl:
        fig_s = go.Figure(go.Bar(
            x=df_seeg["emissoes"], y=df_seeg["setor"], orientation="h",
            marker=dict(
                color=df_seeg["emissoes"].tolist(),
                colorscale=[[0,VERDE],[0.5,AMARELO],[1,LARANJA]],
                cmin=0, cmax=650,
            ),
            text=df_seeg["emissoes"].apply(lambda x: f"{x:.0f} Mt"), textposition="outside",
            hovertemplate="%{y}: %{x:.1f} MtCO2e<extra></extra>",
        ))
        layout_s = dict(PLOTLY_LAYOUT); layout_s["height"]=300
        layout_s["xaxis"]=dict(title="MtCO2e", range=[0,720])
        layout_s["yaxis"]=dict(autorange="reversed", tickfont=dict(size=11))
        fig_s.update_layout(**layout_s)
        st.plotly_chart(fig_s, use_container_width=True)
    with cr:
        total = sum(SEEG.values())
        fig_p = go.Figure(go.Pie(
            labels=list(SEEG.keys()), values=list(SEEG.values()), hole=0.42,
            marker=dict(colors=[PETROLEO,VERDE,LARANJA,AMARELO,CINZA,"#4A7C8E"]),
            hovertemplate="%{label}: %{value:.1f} Mt (%{percent})<extra></extra>",
        ))
        fig_p.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            font=dict(family="Poppins", color=ESCURO, size=11),
            height=300, margin=dict(l=0,r=0,t=10,b=0),
            legend=dict(font=dict(size=10)),
            annotations=[dict(text=f"{total:.0f} Mt", x=0.5, y=0.5, showarrow=False,
                               font=dict(family="Poppins", size=16, color=ESCURO))],
        )
        st.plotly_chart(fig_p, use_container_width=True)
    nota(f"""
    Emissões em MtCO2e (Megatoneladas de CO2 equivalente). O biometano contribui para redução dos
    setores Energia e Transporte ao substituir combustíveis fósseis.
    <strong>Fonte:</strong> SEEG / Instituto Clima e Sociedade, edição {SEEG_ANO_REF}.
    Estes dados são publicados anualmente — atualizar o dicionário SEEG no código quando nova edição for lançada.
    """, "fonte")
    link_fonte("SEEG — Sistema de Estimativas de Emissões", "https://seeg.eco.br/")

with tab3:
    st.markdown('<div class="sec-header">Simulador interativo de receita CBIO</div>', unsafe_allow_html=True)

    preco_ref = preco_atual if cbio_ok else 40
    data_ref  = ultima_data if cbio_ok else "—"

    aviso_preco = "" if cbio_ok else " (CBIO não carregado — ajuste manualmente)"
    st.markdown(f"""
<div class="sim-box">
<strong style="font-size:14px;color:{PETROLEO}">O que é este simulador?</strong><br>
<span style="font-size:12px;color:#555;line-height:1.7">
Projeta a receita potencial da CNP com a venda de CBIOs ao longo do tempo.<br><br>
<strong>Parâmetros:</strong><br>
• <strong>Volume de CBIOs:</strong> quantidade de créditos gerados pela operação certificada.<br>
• <strong>Preço CBIO (R$/crédito):</strong> preço de negociação na B3{aviso_preco}.<br>
• <strong>Horizonte (anos):</strong> janela de projeção.<br>
• <strong>Crescimento anual do volume (%):</strong> expectativa de crescimento da capacidade produtiva certificada.
</span>
</div>
""", unsafe_allow_html=True)

    with st.container(border=True):
        cs1, cs2 = st.columns(2)
        with cs1:
            vol_sim   = st.slider("Volume de CBIOs gerados (unid.)", 1000, 500000, volume_cbio, step=1000, key="vs")
            preco_sim = st.slider("Preço CBIO (R$/crédito)", 20, 150, int(preco_ref), key="ps")
        with cs2:
            anos_sim   = st.slider("Horizonte (anos)", 1, 10, 5, key="as_")
            crescimento = st.slider("Crescimento anual do volume (%)", 0, 30, 10, key="cs_")

        receitas_anos = []
        vol_acum = vol_sim
        for a in range(1, anos_sim+1):
            receitas_anos.append(vol_acum * preco_sim)
            vol_acum *= (1 + crescimento/100)
        receita_total_sim = sum(receitas_anos)

        c1s, c2s, c3s = st.columns(3)
        for col, lb, vl, co in [
            (c1s, "Receita no ano 1", f"R$ {receitas_anos[0]:,.0f}", VERDE),
            (c2s, f"Receita no ano {anos_sim}", f"R$ {receitas_anos[-1]:,.0f}", PETROLEO),
            (c3s, "Total acumulado", f"R$ {receita_total_sim/1e6:.2f} mi", LARANJA),
        ]:
            with col:
                st.markdown(f"""<div class="kpi-card" style="border-color:{co}">
                    <div class="kpi-label">{lb}</div><div class="kpi-value">{vl}</div></div>""",
                    unsafe_allow_html=True)

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Bar(
            x=list(range(1, anos_sim+1)),
            y=[r/1e6 for r in receitas_anos],
            marker_color=[VERDE if i < anos_sim//2 else PETROLEO for i in range(anos_sim)],
            name="Receita por ano (R$ mi)",
            hovertemplate="Ano %{x}: R$ %{y:.3f} mi<extra></extra>",
        ))
        fig_sim.add_trace(go.Scatter(
            x=list(range(1, anos_sim+1)),
            y=np.cumsum([r/1e6 for r in receitas_anos]).tolist(),
            name="Acumulado (R$ mi)",
            line=dict(color=AMARELO, width=2.5), yaxis="y2",
            hovertemplate="Ano %{x}: R$ %{y:.3f} mi acum.<extra></extra>",
        ))
        layout_sim = dict(PLOTLY_LAYOUT); layout_sim["height"]=300
        layout_sim["xaxis"]=dict(title="Ano", dtick=1)
        layout_sim["yaxis"]=dict(title="Receita anual (R$ mi)", gridcolor="#f0f0f0")
        layout_sim["yaxis2"]=dict(title="Acumulado (R$ mi)", overlaying="y", side="right")
        fig_sim.update_layout(**layout_sim)
        st.plotly_chart(fig_sim, use_container_width=True)

        nota(f"""
        <strong>Memória de cálculo — Simulador CBIO:</strong><br>
        Receita do ano n = Volume_inicial × (1 + taxa_crescimento)^(n−1) × Preço_CBIO<br>
        Volume_inicial = {vol_sim:,} CBIOs · taxa = {crescimento/100:.2f} a.a. · Preço = R$ {preco_sim:.2f}/CBIO
        {"(cotação B3 de " + data_ref + ")" if cbio_ok else "(ajuste manual)"}<br>
        Ano 1: {vol_sim:,} × 1 × R$ {preco_sim:.2f} = <strong>R$ {receitas_anos[0]:,.0f}</strong><br>
        Ano {anos_sim}: {vol_sim:,} × (1 + {crescimento/100:.2f})^{anos_sim-1} × R$ {preco_sim:.2f} = <strong>R$ {receitas_anos[-1]:,.0f}</strong><br>
        Total acumulado = <strong>R$ {receita_total_sim/1e6:.3f} mi</strong>
        """, "calc")

    with st.expander("Exportar dados"):
        if cbio_ok:
            df_exp1 = df_hist.copy()
            df_exp1.columns = ["Ano","Preço CBIO médio (R$)"]
            st.markdown("**Histórico CBIO:**")
            st.dataframe(df_exp1, use_container_width=True)
            st.download_button("Baixar CBIO", df_exp1.to_csv(index=False).encode("utf-8"), "cbio.csv", "text/csv")
        df_seeg_exp = df_seeg.copy(); df_seeg_exp.columns = ["Setor","Emissões (MtCO2e)"]
        st.markdown("**Emissões SEEG:**")
        st.dataframe(df_seeg_exp, use_container_width=True)
        st.download_button("Baixar SEEG", df_seeg_exp.to_csv(index=False).encode("utf-8"), "seeg.csv", "text/csv")
        df_exp3 = pd.DataFrame({
            "Ano": range(1, anos_sim+1),
            "Receita (R$)": receitas_anos,
            "Acumulado (R$)": np.cumsum(receitas_anos).tolist(),
        })
        st.markdown("**Projeção de receita:**")
        st.dataframe(df_exp3, use_container_width=True)
        st.download_button("Baixar projeção", df_exp3.to_csv(index=False).encode("utf-8"), "projecao_cbio.csv", "text/csv")
