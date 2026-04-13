import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, PLOTLY_LAYOUT, sidebar_logo, nota, link_fonte

st.set_page_config(page_title="Mercado & Território — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

DATA_IBGE = os.path.join(os.path.dirname(__file__), "..", "data", "ibge_mercado.csv")

# Dados reais dos principais municípios de SP, PR, MS e RJ
DADOS_MUNICIPIOS = {
    "SP": [
        ("São Paulo","SP",748000000,12396372),("Campinas","SP",62000000,1223237),
        ("São José dos Campos","SP",51000000,738752),("Ribeirão Preto","SP",35000000,718069),
        ("Sorocaba","SP",28000000,695131),("Osasco","SP",55000000,696850),
        ("Santo André","SP",42000000,716109),("Guarulhos","SP",59000000,1391524),
        ("São Bernardo do Campo","SP",55000000,844483),("Mauá","SP",18000000,471961),
        ("Cubatão","SP",22000000,128577),("Bauru","SP",15000000,380627),
        ("São José do Rio Preto","SP",19000000,465293),("Limeira","SP",12000000,314500),
        ("Piracicaba","SP",22000000,418344),("Jundiaí","SP",28000000,423006),
        ("Franca","SP",11000000,352500),("Araçatuba","SP",9000000,198470),
        ("Presidente Prudente","SP",10000000,233400),("Marília","SP",9500000,227850),
        ("Araraquara","SP",11000000,238200),("Catanduva","SP",6500000,121700),
        ("Sertãozinho","SP",14000000,127800),("Jaboticabal","SP",5800000,78400),
        ("Bebedouro","SP",4200000,79600),("Barretos","SP",6800000,120800),
        ("Votuporanga","SP",4500000,92600),("São Carlos","SP",14000000,254000),
        ("Itu","SP",8900000,172400),("Botucatu","SP",7200000,151600),
    ],
    "PR": [
        ("Curitiba","PR",118000000,1948626),("Londrina","PR",24000000,575377),
        ("Maringá","PR",20000000,436000),("Cascavel","PR",14000000,341680),
        ("Ponta Grossa","PR",13000000,353000),("Foz do Iguaçu","PR",10000000,258537),
        ("Colombo","PR",6500000,252400),("Guarapuava","PR",6000000,186000),
        ("Paranaguá","PR",11000000,162000),("Apucarana","PR",6800000,134450),
        ("Toledo","PR",7200000,141800),("Arapongas","PR",5400000,127000),
        ("Umuarama","PR",5100000,110500),("Campo Mourão","PR",5300000,98700),
        ("Araucária","PR",18000000,143800),("São José dos Pinhais","PR",22000000,320700),
        ("Pinhais","PR",5800000,129800),("Almirante Tamandaré","PR",3100000,112800),
    ],
    "MS": [
        ("Campo Grande","MS",21000000,916001),("Dourados","MS",9500000,224700),
        ("Três Lagoas","MS",14000000,126700),("Corumbá","MS",5200000,112600),
        ("Ponta Porã","MS",4800000,92400),("Naviraí","MS",3900000,53800),
        ("Sidrolândia","MS",3200000,49100),("Nova Andradina","MS",3600000,51400),
        ("Maracaju","MS",5800000,44600),("Coxim","MS",2800000,36700),
        ("Aquidauana","MS",2600000,48200),("Paranaíba","MS",2800000,43600),
        ("Costa Rica","MS",4200000,21400),("Chapadão do Sul","MS",5100000,27400),
        ("Rio Brilhante","MS",4600000,23100),("Sonora","MS",2100000,18600),
    ],
    "RJ": [
        ("Rio de Janeiro","RJ",364000000,6775561),("Niterói","RJ",45000000,513584),
        ("Duque de Caxias","RJ",38000000,924624),("Nova Iguaçu","RJ",18000000,818149),
        ("Campos dos Goytacazes","RJ",26000000,511010),("Petrópolis","RJ",12000000,306700),
        ("Volta Redonda","RJ",14000000,277400),("Macaé","RJ",18000000,246000),
        ("Nova Friburgo","RJ",7500000,184100),("Cabo Frio","RJ",8200000,231300),
        ("Angra dos Reis","RJ",9100000,190000),("Resende","RJ",9800000,130100),
        ("Queimados","RJ",5100000,149000),("Nilópolis","RJ",5800000,158300),
        ("São João de Meriti","RJ",7200000,461000),("Belford Roxo","RJ",7900000,521100),
    ],
}

# Características energéticas e industriais por estado (para simuladores)
PERFIL_ESTADOS = {
    "SP": {"industria_pct":32,"transporte_pct":28,"comercio_pct":22,"agro_pct":8,"outros_pct":10,
           "consumo_gas_m3_ano":12800000000,"empresas_alvo_est":18500,"distancia_media_km":280},
    "PR": {"industria_pct":28,"transporte_pct":31,"comercio_pct":18,"agro_pct":15,"outros_pct":8,
           "consumo_gas_m3_ano":4200000000,"empresas_alvo_est":7800,"distancia_media_km":195},
    "MS": {"industria_pct":18,"transporte_pct":38,"comercio_pct":14,"agro_pct":24,"outros_pct":6,
           "consumo_gas_m3_ano":1800000000,"empresas_alvo_est":2900,"distancia_media_km":310},
    "RJ": {"industria_pct":24,"transporte_pct":25,"comercio_pct":30,"agro_pct":5,"outros_pct":16,
           "consumo_gas_m3_ano":8900000000,"empresas_alvo_est":11200,"distancia_media_km":160},
}

with st.sidebar:
    sidebar_logo()
    estados_foco = ["SP","PR","MS","RJ"]
    estado_sel = st.selectbox("Estado em foco", estados_foco, index=0)
    st.markdown("---")
    metrica = st.radio("Ordenar ranking por", ["PIB total","PIB per capita","População"])
    top_n = st.slider("Municípios no ranking", 10, 30, 20)
    st.markdown("---")
    st.caption("Foco nos 4 estados estratégicos: SP, PR, MS e RJ.")

st.markdown(f"""
<div class="page-header">
    <h1>Mercado & Território — {estado_sel}</h1>
    <p>Inteligência de mercado focada em SP · PR · MS · RJ — com simuladores de potencial e tamanho de mercado</p>
</div>
""", unsafe_allow_html=True)

# Carrega dados IBGE reais
@st.cache_data(ttl=3600)
def load_ibge():
    if os.path.exists(DATA_IBGE):
        df = pd.read_csv(DATA_IBGE)
        if len(df) > 0:
            return df
    return None

df_all = load_ibge()

if df_all is None:
    st.warning("⚠️ **Dados IBGE não carregados.** Execute `python fetch_data.py` para buscar PIB e população municipais do IBGE.")
    st.stop()

# Garante pib_per_capita calculado quando populacao disponível mas coluna ausente/vazia
if "populacao" in df_all.columns and df_all["populacao"].notna().any():
    if "pib_per_capita" not in df_all.columns:
        df_all["pib_per_capita"] = None
    mask = df_all["pib_per_capita"].isna() & df_all["populacao"].notna() & (df_all["populacao"] > 0)
    if mask.any():
        df_all.loc[mask, "pib_per_capita"] = (
            df_all.loc[mask, "pib_total_mil"] * 1000 / df_all.loc[mask, "populacao"]
        ).round(0)
elif "pib_per_capita" not in df_all.columns:
    df_all["pib_per_capita"] = None

df = df_all[df_all["uf"]==estado_sel].copy()
perfil = PERFIL_ESTADOS[estado_sel]

col_sort = {"PIB total":"pib_total_mil","PIB per capita":"pib_per_capita","População":"populacao"}

# Se a coluna de ordenação não tiver dados, usar PIB total
sort_col = col_sort[metrica]
if sort_col not in df.columns or df[sort_col].isna().all():
    sort_col = "pib_total_mil"
df_top = df.sort_values(sort_col, ascending=False).head(top_n)

# KPIs estado
st.markdown(f'<div class="sec-header">Panorama — {estado_sel}</div>', unsafe_allow_html=True)
c1,c2,c3,c4 = st.columns(4)

pop_total = df["populacao"].sum() if "populacao" in df.columns and df["populacao"].notna().any() else None
pop_str   = f"{pop_total/1e6:.2f} mi" if pop_total and pop_total > 0 else "—"
pop_sub   = "habitantes" if pop_total else "execute fetch_data.py"

ppc_total = df["pib_total_mil"].sum() * 1000 / pop_total if pop_total and pop_total > 0 else None
ppc_str   = f"R$ {ppc_total:,.0f}" if ppc_total else "—"
ppc_sub   = "média ponderada" if ppc_total else "sem dado de população"

for col,label,val,sub,cor in [
    (c1,"PIB total",f"R$ {df['pib_total_mil'].sum()/1e6:.1f} bi","municípios monitorados",PETROLEO),
    (c2,"População total",pop_str,pop_sub,VERDE),
    (c3,"Municípios",f"{len(df)}","no estado",LARANJA),
    (c4,"PIB per capita médio",ppc_str,ppc_sub,AMARELO),
]:
    with col:
        st.markdown(f"""<div class="kpi-card" style="border-color:{cor}">
            <div class="kpi-label">{label}</div><div class="kpi-value">{val}</div>
            <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

# Tabs de análise
tab1,tab2,tab3,tab4 = st.tabs(["Ranking & Estrutura","Mapa de calor","Simulador de mercado","Comparativo 4 estados"])

with tab1:
    st.markdown(f'<div class="sec-header">Top {top_n} municípios — {metrica}</div>', unsafe_allow_html=True)
    fig_rank = go.Figure(go.Bar(
        x=df_top[col_sort[metrica]], y=df_top["municipio"], orientation="h",
        marker_color=VERDE,
        hovertemplate="%{y}: <b>%{x:,.0f}</b><extra></extra>",
    ))
    layout = dict(PLOTLY_LAYOUT); layout["height"]=max(350,top_n*22)
    layout["yaxis"]=dict(autorange="reversed",tickfont=dict(size=10))
    layout["xaxis"]=dict(title=metrica)
    fig_rank.update_layout(**layout)
    st.plotly_chart(fig_rank, use_container_width=True)

    # Estrutura econômica
    st.markdown('<div class="sec-header">Estrutura econômica estimada do estado (referência BEN/EPE)</div>', unsafe_allow_html=True)
    setores = ["Indústria","Transporte","Comércio","Agronegócio","Outros"]
    vals_set = [perfil["industria_pct"],perfil["transporte_pct"],perfil["comercio_pct"],perfil["agro_pct"],perfil["outros_pct"]]
    fig_pie = go.Figure(go.Pie(
        labels=setores, values=vals_set, hole=0.4,
        marker=dict(colors=[PETROLEO,VERDE,LARANJA,AMARELO,CINZA]),
        hovertemplate="%{label}: %{value}%<extra></extra>",
    ))
    fig_pie.update_layout(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="Poppins",color=ESCURO),
                          height=280,margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation="h",y=-0.1),
                          annotations=[dict(text=estado_sel,x=0.5,y=0.5,showarrow=False,
                                           font=dict(family="Poppins",size=20,color=ESCURO))])
    st.plotly_chart(fig_pie, use_container_width=True)
    nota(f"<strong>Fonte:</strong> IBGE PIB dos Municípios, referência 2021 (publicação mais recente disponível). Estrutura econômica <strong>estimada</strong> com base na composição setorial estadual do BEN/EPE 2022 — não representa observação direta do mercado consumidor de biometano."
         ,"fonte")
    link_fonte("IBGE — PIB dos Municípios","https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088-produto-interno-bruto-dos-municipios.html")

with tab2:
    st.markdown('<div class="sec-header">Ranking de municípios — PIB total</div>', unsafe_allow_html=True)
    df_top20 = df.nlargest(20, "pib_total_mil").copy()
    df_top20["label_pib"] = df_top20["pib_total_mil"].apply(lambda x: f"R$ {x/1e6:.1f} bi")

    fig_pib = go.Figure()
    fig_pib.add_trace(go.Bar(
        y=df_top20["municipio"], x=df_top20["pib_total_mil"] / 1e6,
        orientation="h", name="PIB total (R$ bi)",
        marker_color=PETROLEO, opacity=0.85,
        text=df_top20["label_pib"], textposition="outside",
        hovertemplate="<b>%{y}</b><br>PIB total: %{text}<extra></extra>",
    ))
    layout_pib = dict(PLOTLY_LAYOUT)
    layout_pib["height"] = max(400, len(df_top20) * 24)
    layout_pib["yaxis"] = dict(autorange="reversed", tickfont=dict(size=11), gridcolor="#f0f0f0")
    layout_pib["xaxis"] = dict(title="PIB total (R$ bilhões)", gridcolor="#f0f0f0")
    layout_pib["margin"] = dict(l=0, r=80, t=10, b=30)
    fig_pib.update_layout(**layout_pib)
    st.plotly_chart(fig_pib, use_container_width=True)

    # PIB per capita — só exibe se dados de população estiverem disponíveis
    ppc_disponivel = (
        "pib_per_capita" in df.columns
        and df["pib_per_capita"].notna().any()
        and df["pib_per_capita"].sum() > 0
    )
    if ppc_disponivel:
        st.markdown('<div class="sec-header">PIB per capita — top 20 municípios</div>', unsafe_allow_html=True)
        df_ppc = df[df["pib_per_capita"].notna()].nlargest(20, "pib_per_capita").copy()
        fig_ppc = go.Figure()
        fig_ppc.add_trace(go.Bar(
            y=df_ppc["municipio"], x=df_ppc["pib_per_capita"],
            orientation="h", name="PIB per capita (R$)",
            marker_color=VERDE, opacity=0.85,
            text=df_ppc["pib_per_capita"].apply(lambda x: f"R$ {x:,.0f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>PIB per capita: %{text}<extra></extra>",
        ))
        layout_ppc = dict(PLOTLY_LAYOUT)
        layout_ppc["height"] = max(400, len(df_ppc) * 24)
        layout_ppc["yaxis"] = dict(autorange="reversed", tickfont=dict(size=11), gridcolor="#f0f0f0")
        layout_ppc["xaxis"] = dict(title="PIB per capita (R$)", gridcolor="#f0f0f0")
        layout_ppc["margin"] = dict(l=0, r=100, t=10, b=30)
        fig_ppc.update_layout(**layout_ppc)
        st.plotly_chart(fig_ppc, use_container_width=True)
        nota("<strong>PIB total</strong> = tamanho absoluto do mercado. <strong>PIB per capita</strong> = poder de compra. Municípios no topo dos dois rankings combinam volume E riqueza — os mais atrativos para prospecção. Fonte: IBGE PIB dos Municípios, referência 2021.", "calc")
    else:
        st.info("ℹ️ PIB per capita indisponível — execute `python fetch_data.py` para buscar dados de população do IBGE.")

with tab3:
    st.markdown(f'<div class="sec-header">Simulador de potencial de mercado — {estado_sel}</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="sim-box">
<strong style="font-size:14px;color:{PETROLEO}">O que é este simulador?</strong><br>
<span style="font-size:12px;color:#555;line-height:1.7">
Estima o potencial de receita da CNP no estado selecionado com base no universo de empresas-alvo, taxa de conversão e consumo médio esperado.<br><br>
<strong>Parâmetros de entrada:</strong><br>
• <strong>% das empresas-alvo convertíveis:</strong> qual fração do universo de empresas com perfil CNP pode ser convertida em cliente.<br>
• <strong>% de penetração de mercado:</strong> do total convertível, qual % a CNP efetivamente alcança no horizonte definido.<br>
• <strong>Consumo médio por cliente (m³/mês):</strong> volume médio esperado de biometano por contrato.<br>
• <strong>Preço do biometano (R$/m³):</strong> preço médio de venda praticado.<br>
• <strong>Margem bruta estimada (%):</strong> margem sobre a receita bruta, após custo do produto.<br>
• <strong>Horizonte de análise (meses):</strong> janela de tempo para acumulação de receita e lucro.<br><br>
<strong>O que a análise entrega:</strong> número de clientes estimados, volume mensal, receita total acumulada e lucro bruto no período.
</span>
</div>
""", unsafe_allow_html=True)

    with st.container(border=True):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            pct_empresas = st.slider("% das empresas-alvo convertíveis (%)", 1, 30, 5, key="pct_conv")
            consumo_medio = st.number_input("Consumo médio por cliente (m³/mês)", value=5000, step=500, key="cons_med")
            preco_m3 = st.number_input("Preço do biometano (R$/m³)", value=3.80, step=0.10, key="preco_bm")
        with col_s2:
            pct_mercado = st.slider("% de penetração de mercado (%)", 1, 50, 10, key="pct_merc")
            margem = st.slider("Margem bruta estimada (%)", 5, 40, 18, key="margem")
            meses = st.slider("Horizonte de análise (meses)", 6, 60, 24, key="horizonte")

        empresas_alvo = perfil["empresas_alvo_est"]
        clientes_conv = int(empresas_alvo * pct_empresas / 100)
        clientes_merc = int(clientes_conv * pct_mercado / 100)
        vol_mensal    = clientes_merc * consumo_medio
        receita_mes   = vol_mensal * preco_m3
        receita_total = receita_mes * meses
        lucro_bruto   = receita_total * margem / 100

        c1s,c2s,c3s,c4s = st.columns(4)
        for col,label,val,cor in [
            (c1s,"Empresas-alvo estimadas",f"{empresas_alvo:,}",PETROLEO),
            (c2s,"Clientes convertíveis",f"{clientes_conv:,}",VERDE),
            (c3s,"Clientes com penetração",f"{clientes_merc:,}",LARANJA),
            (c4s,f"Receita em {meses} meses",f"R$ {receita_total/1e6:.1f} mi",AMARELO),
        ]:
            with col:
                st.markdown(f"""<div class="kpi-card" style="border-color:{cor}">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{val}</div></div>""", unsafe_allow_html=True)

        st.markdown(f"""
    <div style="margin-top:16px;padding:14px;background:rgba(118,184,42,0.08);border-radius:8px">
        <span class="sim-label">Lucro bruto estimado em {meses} meses</span>
        <div class="sim-resultado">R$ {lucro_bruto/1e6:.2f} mi</div>
        <span class="sim-label">Volume mensal: {vol_mensal:,.0f} m³ &nbsp;|&nbsp; Receita mensal: R$ {receita_mes:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

    nota(f"""
    <strong>Memória de cálculo — Simulador de Mercado:</strong><br>
    1. Empresas-alvo estimadas no estado: <strong>{empresas_alvo:,}</strong> (base: CNPJ ativo nos CNAEs de interesse)<br>
    2. Clientes convertíveis = {empresas_alvo:,} × {pct_empresas}% = <strong>{clientes_conv:,}</strong><br>
    3. Clientes com penetração = {clientes_conv:,} × {pct_mercado}% = <strong>{clientes_merc:,}</strong><br>
    4. Volume mensal = {clientes_merc:,} × {consumo_medio:,} m³ = <strong>{vol_mensal:,.0f} m³/mês</strong><br>
    5. Receita mensal = {vol_mensal:,.0f} × R$ {preco_m3:.2f} = <strong>R$ {receita_mes:,.0f}</strong><br>
    6. Receita total ({meses} meses) = R$ {receita_mes:,.0f} × {meses} = <strong>R$ {receita_total/1e6:.2f} mi</strong><br>
    7. Lucro bruto = R$ {receita_total/1e6:.2f} mi × {margem}% = <strong>R$ {lucro_bruto/1e6:.2f} mi</strong>
    ""","calc")

    # Curva de crescimento
    st.markdown('<div class="sec-header">Curva de receita acumulada ao longo do tempo</div>', unsafe_allow_html=True)
    meses_arr = np.arange(1, meses+1)
    # Ramp-up: crescimento logístico até penetração total
    rampup = clientes_merc * (1 - np.exp(-0.15*meses_arr)) / (1 - np.exp(-0.15*meses))
    receita_acum = np.cumsum(rampup * consumo_medio * preco_m3)

    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(
        x=meses_arr, y=receita_acum/1e6, fill="tozeroy",
        fillcolor=f"rgba(118,184,42,0.12)", line=dict(color=VERDE,width=2.5),
        name="Receita acumulada (R$ mi)",
        hovertemplate="Mês %{x}: R$ %{y:.2f} mi acumulado<extra></extra>",
    ))
    layout3 = dict(PLOTLY_LAYOUT); layout3["height"]=280
    layout3["xaxis"]=dict(title="Mês",gridcolor="#f0f0f0")
    layout3["yaxis"]=dict(title="Receita acumulada (R$ milhões)",gridcolor="#f0f0f0")
    fig_curva.update_layout(**layout3)
    st.plotly_chart(fig_curva, use_container_width=True)
    nota("Curva de ramp-up com modelo logístico: clientes são conquistados gradualmente (crescimento exponencial desacelerante). Parâmetro de crescimento: λ = 0,15/mês.","calc")

with tab4:
    st.markdown('<div class="sec-header">Comparativo dos 4 estados estratégicos</div>', unsafe_allow_html=True)

    ufs_comp  = ["SP","PR","MS","RJ"]
    cores_comp = [PETROLEO, VERDE, LARANJA, AMARELO]

    rows_comp = []
    for uf in ufs_comp:
        df_uf = df_all[df_all["uf"]==uf]
        p = PERFIL_ESTADOS[uf]
        pop_uf = df_uf["populacao"].sum() if "populacao" in df_uf.columns and df_uf["populacao"].notna().any() else None
        rows_comp.append({
            "Estado": uf,
            "PIB total (R$ bi)": round(df_uf["pib_total_mil"].sum()/1e6, 1),
            "População (mi)": round(pop_uf/1e6, 2) if pop_uf else None,
            "Municípios": len(df_uf),
            "Empresas-alvo est.": f"{p['empresas_alvo_est']:,}",
            "Consumo gás (Gm³/ano)": round(p["consumo_gas_m3_ano"]/1e9, 1),
            "Distância média (km)": p["distancia_media_km"],
        })
    df_comp = pd.DataFrame(rows_comp)
    st.dataframe(df_comp.set_index("Estado"), use_container_width=True)

    # Gráfico 1 — PIB total (R$ bi)
    st.markdown('<div class="sec-header">PIB total por estado (R$ bilhões)</div>', unsafe_allow_html=True)
    vals_pib = [df_all[df_all["uf"]==uf]["pib_total_mil"].sum()/1e6 for uf in ufs_comp]
    fig_pib_comp = go.Figure(go.Bar(
        x=ufs_comp, y=vals_pib, marker_color=cores_comp,
        text=[f"R$ {v:.1f} bi" for v in vals_pib], textposition="outside",
        hovertemplate="%{x}: R$ %{y:.1f} bi<extra></extra>",
    ))
    lp1 = dict(PLOTLY_LAYOUT); lp1["height"]=280; lp1["showlegend"]=False
    lp1["yaxis"]=dict(title="R$ bilhões", gridcolor="#f0f0f0")
    lp1["xaxis"]=dict(tickfont=dict(size=14, weight=700))
    fig_pib_comp.update_layout(**lp1)
    st.plotly_chart(fig_pib_comp, use_container_width=True)

    # Gráfico 2 — População (mi) — só se disponível
    pop_vals = []
    for uf in ufs_comp:
        df_uf = df_all[df_all["uf"]==uf]
        v = df_uf["populacao"].sum() if "populacao" in df_uf.columns and df_uf["populacao"].notna().any() else None
        pop_vals.append(v/1e6 if v else None)

    if any(v is not None for v in pop_vals):
        st.markdown('<div class="sec-header">População total por estado (milhões de habitantes)</div>', unsafe_allow_html=True)
        fig_pop_comp = go.Figure(go.Bar(
            x=ufs_comp, y=pop_vals, marker_color=cores_comp,
            text=[f"{v:.2f} mi" if v else "—" for v in pop_vals], textposition="outside",
            hovertemplate="%{x}: %{y:.2f} mi hab.<extra></extra>",
        ))
        lp2 = dict(PLOTLY_LAYOUT); lp2["height"]=280; lp2["showlegend"]=False
        lp2["yaxis"]=dict(title="Milhões de habitantes", gridcolor="#f0f0f0")
        lp2["xaxis"]=dict(tickfont=dict(size=14, weight=700))
        fig_pop_comp.update_layout(**lp2)
        st.plotly_chart(fig_pop_comp, use_container_width=True)
    else:
        st.info("ℹ️ Dados de população indisponíveis — execute `python fetch_data.py` para buscar do IBGE.")

    # Gráfico 3 — Empresas-alvo estimadas (mil)
    st.markdown('<div class="sec-header">Empresas-alvo estimadas por estado (em milhares)</div>', unsafe_allow_html=True)
    vals_emp = [PERFIL_ESTADOS[uf]["empresas_alvo_est"]/1000 for uf in ufs_comp]
    fig_emp_comp = go.Figure(go.Bar(
        x=ufs_comp, y=vals_emp, marker_color=cores_comp,
        text=[f"{v:.1f}k" for v in vals_emp], textposition="outside",
        hovertemplate="%{x}: %{y:.1f}k empresas-alvo<extra></extra>",
    ))
    lp3 = dict(PLOTLY_LAYOUT); lp3["height"]=280; lp3["showlegend"]=False
    lp3["yaxis"]=dict(title="Empresas-alvo (mil)", gridcolor="#f0f0f0")
    lp3["xaxis"]=dict(tickfont=dict(size=14, weight=700))
    fig_emp_comp.update_layout(**lp3)
    st.plotly_chart(fig_emp_comp, use_container_width=True)

    nota("Cada gráfico usa sua própria escala para máxima legibilidade. Empresas-alvo = estimativa baseada em CNAEs de interesse no universo CNPJ ativo. Fonte PIB: IBGE PIB dos Municípios. Fonte população: IBGE Estimativas.","calc")

with st.expander("Exportar dados"):
    st.dataframe(df_top, use_container_width=True)
    st.download_button("Baixar CSV do estado", df_top.to_csv(index=False).encode("utf-8"), f"mercado_{estado_sel}_cnp.csv","text/csv")
    st.download_button("Baixar comparativo 4 estados", df_comp.to_csv(index=False).encode("utf-8"), "comparativo_estados_cnp.csv","text/csv")
link_fonte("IBGE — Produto Interno Bruto dos Municípios","https://sidra.ibge.gov.br/tabela/5938")
link_fonte("IBGE — Estimativas de população","https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html")
