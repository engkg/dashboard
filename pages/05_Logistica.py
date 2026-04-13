import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, PLOTLY_LAYOUT, sidebar_logo, nota, link_fonte

st.set_page_config(page_title="Logística — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

with st.sidebar:
    sidebar_logo()
    st.markdown("**Parâmetros da frota**")
    preco_diesel = st.number_input("Preço do diesel (R$/L)", value=6.20, step=0.10, format="%.2f")
    rendimento   = st.number_input("Consumo médio (km/L)", value=3.5, step=0.1, format="%.1f")
    raio_max     = st.slider("Raio máximo analisado (km)", 50, 800, 400)
    custo_fixo   = st.number_input("Custo fixo por viagem (R$)", value=250.0, step=10.0)
    ticket       = st.number_input("Ticket médio do contrato (R$/mês)", value=5000.0, step=500.0)
    st.markdown("---")
    st.caption("Custo fixo = pedágio + hora motorista + overhead operacional estimado por viagem ida/volta.")

st.markdown("""
<div class="page-header">
    <h1>Logística & Raio de Atuação</h1>
    <p>Custo de transporte · Raio viável · Simulador de rentabilidade por rota</p>
</div>
""", unsafe_allow_html=True)

custo_km    = preco_diesel / rendimento
raio_viavel = max(0, (ticket*0.10 - custo_fixo) / (custo_km*2))

st.markdown('<div class="sec-header">Resumo logístico</div>', unsafe_allow_html=True)
c1,c2,c3,c4 = st.columns(4)
for col,label,val,sub,cor in [
    (c1,"Custo por km (ida)",f"R$ {custo_km:.2f}",f"Diesel R$ {preco_diesel:.2f}/L ÷ {rendimento:.1f} km/L",PETROLEO),
    (c2,f"Custo no raio máx. ({raio_max}km)",f"R$ {custo_km*raio_max*2+custo_fixo:,.0f}","ida e volta + fixo",LARANJA),
    (c3,"Raio viável (10% ticket)",f"{raio_viavel:.0f} km",f"Ticket ref.: R$ {ticket:,.0f}/mês",VERDE),
    (c4,"Frete como % do ticket",f"{(custo_km*raio_viavel*2+custo_fixo)/ticket*100:.1f}%","no raio viável",AMARELO),
]:
    with col:
        st.markdown(f"""<div class="kpi-card" style="border-color:{cor}">
            <div class="kpi-label">{label}</div><div class="kpi-value">{val}</div>
            <div class="kpi-sub">{sub}</div></div>""",unsafe_allow_html=True)

tab1,tab2 = st.tabs(["Curva de custo","Simulador de rentabilidade"])

with tab1:
    dists = np.arange(0, raio_max+5, 5)
    custos_v = custo_km * dists * 2
    custos_t = custos_v + custo_fixo
    pct_tick  = custos_t / ticket * 100

    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(x=dists,y=custos_t,fill="tozeroy",fillcolor="rgba(48,81,95,0.09)",
        line=dict(color=PETROLEO,width=2),name="Custo total (ida+volta+fixo)",
        hovertemplate="%{x} km<br><b>R$ %{y:,.0f}</b><extra></extra>"))
    fig_c.add_trace(go.Scatter(x=dists,y=pct_tick,line=dict(color=LARANJA,width=1.5,dash="dot"),
        name="% do ticket",yaxis="y2",
        hovertemplate="%{x} km → %{y:.1f}% do ticket<extra></extra>"))
    fig_c.add_hline(y=ticket*0.10,line_dash="dot",line_color=VERDE,
        annotation_text=f"Limite 10% ticket (R$ {ticket*0.10:,.0f})",
        annotation_position="top left",annotation_font_color=VERDE)
    if raio_viavel>0:
        fig_c.add_vline(x=raio_viavel,line_dash="dot",line_color=VERDE,
            annotation_text=f"Raio viável: {raio_viavel:.0f} km",
            annotation_position="top right",annotation_font_color=VERDE)
    layout=dict(PLOTLY_LAYOUT);layout["height"]=360
    layout["xaxis"]=dict(title="Distância (km)")
    layout["yaxis"]=dict(title="Custo logístico (R$)")
    layout["yaxis2"]=dict(title="% do ticket",overlaying="y",side="right",tickformat=".0f",ticksuffix="%")
    fig_c.update_layout(**layout)
    st.plotly_chart(fig_c, use_container_width=True)

    nota(f"""
    <strong>Memória de cálculo — Custo logístico:</strong><br>
    Custo variável por km (ida) = Preço diesel ÷ Rendimento = R$ {preco_diesel:.2f} ÷ {rendimento:.1f} = <strong>R$ {custo_km:.4f}/km</strong><br>
    Custo total (ida e volta) = Custo/km × Distância × 2 + Custo fixo<br>
    Exemplo a 100 km = {custo_km:.4f} × 100 × 2 + {custo_fixo:.0f} = <strong>R$ {custo_km*200+custo_fixo:,.0f}</strong><br>
    Raio viável (10% do ticket) = (R$ {ticket:.0f} × 10% − R$ {custo_fixo:.0f}) ÷ (2 × {custo_km:.4f}) = <strong>{raio_viavel:.0f} km</strong>
    ""","calc")

    st.markdown('<div class="sec-header">Tabela de custo por faixa</div>', unsafe_allow_html=True)
    faixas = sorted(set([50,100,150,200,250,300,400,500,int(raio_max)]))
    df_tab = pd.DataFrame({
        "Distância (km)":      faixas,
        "Custo variável (R$)": [round(custo_km*d*2,0) for d in faixas],
        "Custo total (R$)":    [round(custo_km*d*2+custo_fixo,0) for d in faixas],
        "% do ticket":         [round((custo_km*d*2+custo_fixo)/ticket*100,1) for d in faixas],
        "Viável":              ["Sim" if (custo_km*d*2+custo_fixo)/ticket*100<=10 else "Não" for d in faixas],
    })

    def _cor_viavel(v):
        return "color: #2e7d4f; font-weight:600" if v=="Sim" else "color: #b83232; font-weight:600"

    try:
        styled = df_tab.style.map(_cor_viavel, subset=["Viável"]).format(
            {"Custo variável (R$)":"R$ {:,.0f}","Custo total (R$)":"R$ {:,.0f}","% do ticket":"{:.1f}%"})
    except AttributeError:
        styled = df_tab.style.format(
            {"Custo variável (R$)":"R$ {:,.0f}","Custo total (R$)":"R$ {:,.0f}","% do ticket":"{:.1f}%"})

    st.dataframe(styled, use_container_width=True)
    st.download_button("Baixar tabela (CSV)", df_tab.to_csv(index=False).encode("utf-8"), "custos_logistica_cnp.csv","text/csv")

with tab2:
    st.markdown('<div class="sec-header">Simulador de rentabilidade por rota</div>', unsafe_allow_html=True)
    with st.container(border=True):
        cs1,cs2,cs3 = st.columns(3)
        with cs1:
            dist_rota   = st.slider("Distância da rota (km)", 10, raio_max, 150, key="dr")
            n_clientes  = st.slider("Clientes nessa rota", 1, 20, 5, key="nc")
        with cs2:
            ticket_r    = st.number_input("Ticket médio por cliente (R$/mês)", value=ticket, step=500.0, key="tr")
            freq_visita = st.slider("Visitas por mês por cliente", 1, 8, 2, key="fv")
        with cs3:
            margem_prod = st.slider("Margem bruta do produto (%)", 5, 40, 18, key="mp")

        custo_visita   = custo_km * dist_rota * 2 + custo_fixo
        custo_mes_rota = custo_visita * n_clientes * freq_visita
        receita_rota   = ticket_r * n_clientes
        lucro_produto  = receita_rota * margem_prod / 100
        lucro_liquido  = lucro_produto - custo_mes_rota
        pct_frete      = custo_mes_rota / max(receita_rota, 1) * 100

        c1s,c2s,c3s,c4s = st.columns(4)
        for col,lb,vl,co in [
            (c1s,"Custo logístico/mês",f"R$ {custo_mes_rota:,.0f}",LARANJA),
            (c2s,"Receita bruta/mês",f"R$ {receita_rota:,.0f}",PETROLEO),
            (c3s,"Margem produto/mês",f"R$ {lucro_produto:,.0f}",AMARELO),
            (c4s,"Lucro líquido/mês",f"R$ {lucro_liquido:,.0f}",VERDE if lucro_liquido>=0 else "#b83232"),
        ]:
            with col:
                st.markdown(f'''<div class="kpi-card" style="border-color:{co}">
                    <div class="kpi-label">{lb}</div><div class="kpi-value">{vl}</div></div>''',unsafe_allow_html=True)

        eq_txt = "— viável" if pct_frete<=15 else " — atenção: frete alto"
        eq_cli = custo_mes_rota / max((margem_prod/100)*max(ticket_r,1), 1)
        st.markdown(f"""
        <div style="margin-top:16px;padding:14px;background:rgba(118,184,42,0.08);border-radius:8px">
            <span class="sim-label">Frete como % da receita: <strong>{pct_frete:.1f}%</strong> {eq_txt}</span><br>
            <span class="sim-label">Ponto de equilíbrio: <strong>{eq_cli:,.1f} clientes</strong> para cobrir o frete</span>
        </div>
        """, unsafe_allow_html=True)
