import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, PALETA, PLOTLY_LAYOUT, sidebar_logo, nota, link_fonte

st.set_page_config(page_title="Consumo Energético — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

BEN = {
    "ano":[2014,2015,2016,2017,2018,2019,2020,2021,2022],
    "Transporte":[95.2,91.4,89.1,90.3,91.8,93.5,80.2,87.4,94.1],
    "Indústria":[89.1,83.2,79.4,81.2,83.5,84.1,78.3,84.2,88.7],
    "Residencial":[28.4,27.9,27.5,28.1,28.9,29.3,30.1,30.8,31.2],
    "Comercial":[15.1,14.8,14.2,14.6,15.1,15.4,13.2,14.1,15.3],
    "Agropecuário":[18.3,18.9,19.1,19.8,20.4,21.2,21.8,22.5,23.1],
    "Energético":[42.1,39.8,38.4,39.2,40.1,41.3,38.9,41.2,43.5],
    "Público":[8.2,8.1,7.9,8.0,8.2,8.4,7.8,8.1,8.4],
}
PART_GN = {"Transporte":5.8,"Indústria":35.2,"Residencial":8.1,"Comercial":12.4,"Energético":45.3,"Agropecuário":1.2,"Público":3.0}
# Fator de emissão evitada por Mtep substituído por biometano (tCO2/Mtep aprox.)
EMISSAO_FATOR = {"Transporte":285,"Indústria":210,"Comercial":195,"Energético":265,"Agropecuário":180,"Residencial":150,"Público":130}
CORES_SET = [PETROLEO,VERDE,LARANJA,AMARELO,CINZA,"#4A7C8E","#5A9A3A"]

with st.sidebar:
    sidebar_logo()
    setores_disp = list(BEN.keys())[1:]
    setores_sel = st.multiselect("Setores", setores_disp, default=setores_disp)
    ano_range = st.slider("Período histórico", 2014, 2022, (2017,2022))
    st.markdown("---")
    st.markdown("""
**O que é Mtep?**

Mtep = Milhões de Toneladas Equivalentes de Petróleo.

Unidade padrão para comparar diferentes fontes de energia numa mesma base.

1 Mtep ≈ 11,63 TWh de eletricidade ≈ 1,163 × 10¹⁶ J

Permite somar e comparar gás natural, diesel, eletricidade e biomassa diretamente.
    """)

st.markdown("""
<div class="page-header">
    <h1>Consumo Energético por Setor</h1>
    <p>Balanço Energético Nacional (BEN/EPE) · Participação do gás natural · Simuladores de substituição e potencial</p>
</div>
""", unsafe_allow_html=True)

df_ben = pd.DataFrame(BEN)
df_ben = df_ben[(df_ben["ano"]>=ano_range[0])&(df_ben["ano"]<=ano_range[1])]
if not setores_sel:
    st.warning("Selecione ao menos um setor.")
    st.stop()

df_ben_f = df_ben[["ano"]+setores_sel]
ult_ano  = df_ben_f["ano"].max()
ult      = df_ben_f[df_ben_f["ano"]==ult_ano]

# KPIs
st.markdown(f'<div class="sec-header">Último ano disponível ({ult_ano})</div>', unsafe_allow_html=True)
cols = st.columns(min(len(setores_sel),4))
for i,setor in enumerate(setores_sel[:4]):
    with cols[i]:
        val = ult[setor].values[0] if not ult.empty else 0
        st.markdown(f"""<div class="kpi-card" style="border-color:{CORES_SET[i%len(CORES_SET)]}">
            <div class="kpi-label">{setor}</div><div class="kpi-value">{val:.1f}</div>
            <div class="kpi-sub">Mtep em {ult_ano}</div></div>""",unsafe_allow_html=True)

tab1,tab2,tab3 = st.tabs(["Histórico & participação GN","Simulador de substituição","Potencial biometano"])

with tab1:
    fig = go.Figure()
    for i,setor in enumerate(setores_sel):
        fig.add_trace(go.Scatter(x=df_ben_f["ano"],y=df_ben_f[setor],name=setor,
            line=dict(color=CORES_SET[i%len(CORES_SET)],width=2),
            hovertemplate="%{x}: <b>%{y:.1f} Mtep</b><extra></extra>"))
    layout=dict(PLOTLY_LAYOUT);layout["height"]=360
    layout["xaxis"]=dict(title="Ano",dtick=1,tickfont=dict(size=11))
    layout["yaxis"]=dict(title="Mtep (Mi Ton. Equiv. Petróleo)",gridcolor="#f0f0f0")
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)
    nota("<strong>O que é Mtep?</strong> Mtep (Milhões de Toneladas Equivalentes de Petróleo) é a unidade padrão do setor energético para comparar fontes diferentes. 1 Mtep ≈ 11,63 TWh de eletricidade. <strong>Fonte:</strong> EPE — Balanço Energético Nacional 2023.","fonte")
    link_fonte("EPE — Balanço Energético Nacional (BEN)","https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/balanco-energetico-nacional-ben")

    st.markdown('<div class="sec-header">Participação do gás natural por setor (%)</div>', unsafe_allow_html=True)
    df_gn = pd.DataFrame([(s,PART_GN.get(s,0)) for s in setores_sel],columns=["setor","pct_gn"])
    df_gn = df_gn.sort_values("pct_gn",ascending=True)
    fig_gn = go.Figure(go.Bar(
        x=df_gn["pct_gn"],y=df_gn["setor"],orientation="h",
        marker=dict(color=df_gn["pct_gn"].tolist(),colorscale=[[0,CINZA],[0.5,AMARELO],[1,VERDE]],cmin=0,cmax=50),
        text=df_gn["pct_gn"].apply(lambda x: f"{x:.1f}%"),textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    layout2=dict(PLOTLY_LAYOUT);layout2["height"]=280
    layout2["xaxis"]=dict(title="Participação do gás natural (%)",range=[0,55])
    layout2["yaxis"]=dict(autorange="reversed")
    fig_gn.update_layout(**layout2)
    st.plotly_chart(fig_gn, use_container_width=True)

    # ── Quadro de premissas efetivamente usadas no cálculo ───────────────────
    st.markdown('<div class="sec-header">Premissas efetivamente usadas nos cálculos</div>', unsafe_allow_html=True)
    premissas = [
        ("BEN — Consumo setorial", "Mtep/ano por setor", "EPE — Balanço Energético Nacional 2023 (anos 2014–2022)"),
        ("PART_GN — Participação do gás natural", "% do consumo energético do setor", "BEN/EPE 2022, Tabela de Consumo por Fonte"),
        ("EMISSAO_FATOR — Fator de emissão evitada", "tCO₂/Mtep (aprox. por setor)", "EPE/IPCC — fator estimado por substituição de GN fóssil"),
        ("Fator de conversão Mtep → m³", "1 Mtep = 1,053 × 10⁹ m³ (poder calorífico GN ≈ 37,7 MJ/m³)", "ANP / EPE — poder calorífico inferior do gás natural"),
        ("Fator de conversão Mtep → MMBtu", "1 Mtep = 39,7 × 10⁶ MMBtu / 1,055 GJ/MMBtu", "Conversão padrão NIST: 1 MMBtu = 1,055 GJ"),
    ]
    df_prem = pd.DataFrame(premissas, columns=["Premissa","Unidade / Descrição","Origem"])
    st.dataframe(df_prem, use_container_width=True, hide_index=True)
    nota("""
    <strong>Rastreabilidade:</strong> todos os valores usados nos cálculos da aba Energia estão listados acima.
    PART_GN e EMISSAO_FATOR são estimativas setoriais baseadas em publicações EPE/BEN — não são medições diretas da CNP.
    Multiplicações por 1.000 presentes no código convertem MtCO₂ para tCO₂ (1 Mt = 10⁶ t = 1.000 × 10³ t).
    ""","calc")

with tab2:
    st.markdown('<div class="sec-header">Simulador de substituição por biometano</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="sim-box-header">
<strong style="font-size:14px;color:{PETROLEO}">O que é este simulador?</strong><br>
<span style="font-size:12px;color:#555;line-height:1.7">
Estima o impacto financeiro e ambiental de substituir parte do consumo de gás natural fóssil por biometano em um setor específico da economia.
O resultado mostra se a transição é economicamente viável considerando a receita com créditos de carbono (CBIO).<br><br>
<strong>Parâmetros de entrada:</strong><br>
• <strong>Setor:</strong> setor econômico com base no BEN/EPE — define o consumo histórico e o fator de emissão evitada.<br>
• <strong>% do consumo GN a substituir:</strong> qual parcela do gás natural deste setor será trocada por biometano.<br>
• <strong>Preço gás natural (R$/MMBtu):</strong> preço de referência do GN fóssil no mercado.<br>
• <strong>Preço biometano (R$/MMBtu):</strong> preço do biometano ofertado — tende a ser ligeiramente superior ao GN.<br>
• <strong>Horizonte (anos):</strong> janela de análise para acumulação de receita CBIO e custo extra.<br>
• <strong>Receita CBIO por tCO2 (R$):</strong> preço unitário do crédito de descarbonização na B3 — use o valor atual do mercado.<br><br>
<strong>O que a análise entrega:</strong> volume substituído (Gm³/ano), custo incremental vs. GN fóssil, emissão evitada (MtCO2) e saldo líquido entre receita CBIO e custo extra no horizonte definido.
</span>
</div>
<div class="sim-box-body">
""", unsafe_allow_html=True)
    with st.container(border=True):
        cs1,cs2,cs3 = st.columns(3)
        with cs1:
            setor_sim = st.selectbox("Setor para substituição", setores_sel, key="ss")
            pct_sub   = st.slider("% do consumo GN a substituir por biometano", 1, 100, 20, key="ps")
        with cs2:
            preco_gn     = st.number_input("Preço gás natural (R$/MMBtu)", value=35.0, step=1.0, key="pgn")
            preco_biogn  = st.number_input("Preço biometano (R$/MMBtu)", value=42.0, step=1.0, key="pbm")
        with cs3:
            anos_horizonte = st.slider("Horizonte (anos)", 1, 10, 5, key="ha")
            credito_cbio   = st.number_input("Receita CBIO por tCO2 (R$)", value=62.0, step=5.0, key="cbio_v")

        if not ult.empty:
            consumo_setor_mtep = ult[setor_sim].values[0]
            consumo_gn_mtep    = consumo_setor_mtep * PART_GN.get(setor_sim,10) / 100
            consumo_sub_mtep   = consumo_gn_mtep * pct_sub / 100
            vol_m3             = consumo_sub_mtep * 1.053e9
            vol_mmbtu          = consumo_sub_mtep * 39.7e6 / 1.055
            custo_gn_ano       = vol_mmbtu * preco_gn
            custo_bio_ano      = vol_mmbtu * preco_biogn
            delta_custo_ano    = custo_bio_ano - custo_gn_ano
            emissao_evitada    = consumo_sub_mtep * EMISSAO_FATOR.get(setor_sim,200) * 1000
            receita_cbio_ano   = emissao_evitada * credito_cbio
            receita_cbio_total = receita_cbio_ano * anos_horizonte
            custo_extra_total  = delta_custo_ano * anos_horizonte
            saldo_final        = receita_cbio_total - custo_extra_total

            c1s,c2s,c3s,c4s = st.columns(4)
            for col,lb,vl,co in [
                (c1s,"Volume a substituir",f"{vol_m3/1e9:.2f} Gm³/ano",PETROLEO),
                (c2s,"Custo extra vs GN fóssil",f"R$ {delta_custo_ano/1e6:.1f} mi/ano",LARANJA),
                (c3s,"Emissão evitada",f"{emissao_evitada/1e6:.2f} MtCO2",VERDE),
                (c4s,f"Receita CBIO ({anos_horizonte}a)",f"R$ {receita_cbio_total/1e6:.1f} mi",AMARELO),
            ]:
                with col:
                    st.markdown(f"""<div class="kpi-card" style="border-color:{co}">
                        <div class="kpi-label">{lb}</div><div class="kpi-value">{vl}</div></div>""",unsafe_allow_html=True)

            cor_saldo = VERDE if saldo_final >= 0 else LARANJA
            st.markdown(f"""
            <div style="margin-top:16px;padding:14px;background:rgba(118,184,42,0.08);border-radius:8px">
                <span class="sim-label">Saldo líquido em {anos_horizonte} anos (CBIO — custo extra)</span>
                <div class="sim-resultado" style="color:{cor_saldo}">R$ {saldo_final/1e6:.1f} mi</div>
                <span class="sim-label">{"Viável financeiramente com receita CBIO" if saldo_final>=0 else "Custo extra supera receita CBIO — reveja parâmetros ou explore outros benefícios"}</span>
            </div>
            """, unsafe_allow_html=True)

            nota(f"""
            <strong>Memória de cálculo — Simulador de Substituição:</strong><br>
            1. Consumo total do setor {setor_sim} em {ult_ano}: <strong>{consumo_setor_mtep:.1f} Mtep</strong><br>
            2. Participação GN no setor: <strong>{PART_GN.get(setor_sim,0):.1f}%</strong> → consumo GN = {consumo_gn_mtep:.2f} Mtep<br>
            3. Volume a substituir ({pct_sub}%): {consumo_gn_mtep:.2f} × {pct_sub/100:.2f} = <strong>{consumo_sub_mtep:.3f} Mtep = {vol_m3/1e9:.2f} Gm³/ano</strong><br>
            4. Conversão: 1 Mtep × 1,053 × 10⁹ m³/Mtep (poder calorífico GN = 37,7 MJ/m³)<br>
            5. Custo extra = vol (MMBtu) × (R$ {preco_biogn:.2f} − R$ {preco_gn:.2f}) = <strong>R$ {delta_custo_ano/1e6:.2f} mi/ano</strong><br>
            6. Emissão evitada = {consumo_sub_mtep:.3f} Mtep × {EMISSAO_FATOR.get(setor_sim,200)} tCO2/Mtep × 1.000 = <strong>{emissao_evitada/1e6:.3f} MtCO2/ano</strong><br>
            7. Receita CBIO/ano = {emissao_evitada:,.0f} créditos × R$ {credito_cbio:.2f} = <strong>R$ {receita_cbio_ano/1e6:.2f} mi/ano</strong>
            ""","calc")
    st.markdown('<div class="sec-header">Potencial de mercado para biometano por setor</div>', unsafe_allow_html=True)
    rows_pot = []
    for setor in setores_sel:
        if not ult.empty:
            cons = ult[setor].values[0]
            gn   = cons * PART_GN.get(setor,0)/100
            pot  = gn * 0.20  # 20% substituível como referência
            vol  = pot * 1.053e9
            rows_pot.append({"Setor":setor,"Consumo total (Mtep)":round(cons,2),"Consumo GN (Mtep)":round(gn,2),
                             "Potencial biometano (Mtep)":round(pot,3),"Volume (Gm³/ano)":round(vol/1e9,3)})
    df_pot = pd.DataFrame(rows_pot).sort_values("Potencial biometano (Mtep)",ascending=False)
    st.dataframe(df_pot.style.format({"Consumo total (Mtep)":"{:.2f}","Consumo GN (Mtep)":"{:.2f}",
                                      "Potencial biometano (Mtep)":"{:.3f}","Volume (Gm³/ano)":"{:.3f}"}),
                 use_container_width=True)
    nota("Potencial estimado com base em 20% de substituição do consumo de GN de cada setor por biometano — referência conservadora de curto/médio prazo. <strong>Fonte:</strong> BEN/EPE 2022 + estimativas EPE para penetração de biogás no Brasil.","calc")
    st.download_button("Baixar tabela de potencial","".join([df_pot.to_csv(index=False)]).encode("utf-8"),"potencial_biometano.csv","text/csv")

with st.expander("Exportar dados históricos"):
    df_exp = df_ben_f.copy()
    df_exp.columns = ["Ano"] + [f"{s} (Mtep)" for s in setores_sel]
    st.download_button("Baixar BEN histórico (CSV)", df_exp.to_csv(index=False).encode("utf-8"), "ben_historico.csv","text/csv")
