import streamlit as st
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, sidebar_logo, nota

st.set_page_config(page_title="Calculadora de Preços — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

# ── Tabela ICMS por UF e Produto — conforme planilha CNP (aba Listas) ────────
# Colunas: ICMS CO2, ICMS Biometano
ICMS_TABLE = {
    "AC":{"Biometano":0.07,"CO2":0.07},"AL":{"Biometano":0.07,"CO2":0.07},
    "AM":{"Biometano":0.07,"CO2":0.07},"AP":{"Biometano":0.07,"CO2":0.07},
    "BA":{"Biometano":0.07,"CO2":0.07},"CE":{"Biometano":0.07,"CO2":0.07},
    "DF":{"Biometano":0.07,"CO2":0.07},"ES":{"Biometano":0.07,"CO2":0.07},
    "GO":{"Biometano":0.07,"CO2":0.07},"MA":{"Biometano":0.07,"CO2":0.07},
    "MT":{"Biometano":0.07,"CO2":0.07},"MS":{"Biometano":0.07,"CO2":0.07},
    "MG":{"Biometano":0.12,"CO2":0.12},"PA":{"Biometano":0.07,"CO2":0.07},
    "PB":{"Biometano":0.07,"CO2":0.07},"PR":{"Biometano":0.12,"CO2":0.12},
    "PE":{"Biometano":0.07,"CO2":0.07},"PI":{"Biometano":0.07,"CO2":0.07},
    "RN":{"Biometano":0.07,"CO2":0.07},"RS":{"Biometano":0.12,"CO2":0.12},
    "RJ":{"Biometano":0.12,"CO2":0.12},"RO":{"Biometano":0.07,"CO2":0.07},
    "RR":{"Biometano":0.07,"CO2":0.07},"SC":{"Biometano":0.12,"CO2":0.12},
    "SP":{"Biometano":0.12,"CO2":0.18},"SE":{"Biometano":0.07,"CO2":0.07},
    "TO":{"Biometano":0.07,"CO2":0.07},
}

# ── PIS e COFINS por produto — conforme planilha CNP ─────────────────────────
# Biometano: PIS 1,65% + COFINS 7,60% = 9,25% (regime não-cumulativo)
# CO2:       PIS 0,65% + COFINS 3,00% = 3,65% (regime cumulativo)
PIS_COFINS_TABLE = {
    "Biometano": {"pis": 0.0165, "cofins": 0.0760},
    "CO2":       {"pis": 0.0065, "cofins": 0.0300},
}

with st.sidebar:
    sidebar_logo()
    st.markdown("### Calculadora de Preços")
    st.markdown("---")
    st.caption("""
**Como usar:**

**Gross → Net:** informe o preço bruto (com impostos) e veja o líquido.

**Net → Gross:** informe o preço líquido desejado e calcule o bruto necessário.

Ao trocar o **Estado** ou o **Produto**, o ICMS, PIS e COFINS atualizam automaticamente conforme a planilha CNP. Você pode editar qualquer alíquota manualmente.
    """)

st.markdown("""
<div class="page-header">
    <h1>Calculadora de Preços — Líquido e Bruto</h1>
    <p>Biometano · CO₂ &nbsp;|&nbsp; ICMS por UF &nbsp;|&nbsp; PIS/COFINS &nbsp;|&nbsp; Conversão bidirecional Gross ↔ Net</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec-header">Premissas</div>', unsafe_allow_html=True)
col_prod, col_uf, col_modo = st.columns([1, 1, 2])
with col_prod:
    produto = st.selectbox("Produto", ["Biometano", "CO2"], key="produto")
with col_uf:
    ufs = sorted(ICMS_TABLE.keys())
    uf = st.selectbox("Estado (UF)", ufs, index=ufs.index("SP"), key="uf")
with col_modo:
    modo = st.radio("Modo de cálculo", ["Gross → Net", "Net → Gross"], index=0, horizontal=True)

icms_auto = ICMS_TABLE[uf][produto]
pis_auto  = PIS_COFINS_TABLE[produto]["pis"]
cof_auto  = PIS_COFINS_TABLE[produto]["cofins"]

st.markdown('<div class="sec-header">Alíquotas de impostos</div>', unsafe_allow_html=True)
st.caption(
    f"Valores carregados automaticamente para **{produto}** em **{uf}** (planilha CNP jan/2023): "
    f"ICMS **{icms_auto*100:.2f}%** · PIS **{pis_auto*100:.2f}%** · COFINS **{cof_auto*100:.2f}%**. "
    f"Edite abaixo se necessário."
)

ci1, ci2, ci3, ci4 = st.columns(4)
with ci1:
    aliq_icms = st.number_input("Alíquota ICMS", min_value=0.0, max_value=1.0,
        value=icms_auto, step=0.01, format="%.4f",
        key=f"icms_{uf}_{produto}")
with ci2:
    aliq_pis = st.number_input("Alíquota PIS", min_value=0.0, max_value=1.0,
        value=pis_auto, step=0.001, format="%.4f",
        key=f"pis_{produto}",
        help=f"Padrão planilha CNP — {produto}: {pis_auto*100:.2f}%")
with ci3:
    aliq_cof = st.number_input("Alíquota COFINS", min_value=0.0, max_value=1.0,
        value=cof_auto, step=0.001, format="%.4f",
        key=f"cof_{produto}",
        help=f"Padrão planilha CNP — {produto}: {cof_auto*100:.2f}%")
with ci4:
    aliq_pc = aliq_pis + aliq_cof
    st.markdown(f"""<div class="kpi-card" style="border-color:{PETROLEO};margin-top:4px">
        <div class="kpi-label">PIS + COFINS (total)</div>
        <div class="kpi-value" style="font-size:20px">{aliq_pc*100:.4f}%</div>
        <div class="kpi-sub">calculado automaticamente</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="sec-header">Preço de entrada</div>', unsafe_allow_html=True)
col_in, _ = st.columns([1, 3])
with col_in:
    if modo == "Gross → Net":
        preco_entrada = st.number_input("Preço Gross (R$/m³)", min_value=0.0001,
            value=3.7362, step=0.01, format="%.4f")
    else:
        preco_entrada = st.number_input("Preço Net (R$/m³)", min_value=0.0001,
            value=2.9838, step=0.01, format="%.4f")

def calc_net_from_gross(gross, icms, pis_cof):
    val_icms  = gross * icms
    base_pc   = gross - val_icms
    val_pc    = base_pc * pis_cof
    net       = gross - val_icms - val_pc
    total_imp = val_icms + val_pc
    return net, val_icms, base_pc, val_pc, total_imp

if modo == "Gross → Net":
    gross_calc = preco_entrada
    net_calc, val_icms, base_pc, val_pc, total_imp = calc_net_from_gross(gross_calc, aliq_icms, aliq_pc)
else:
    gross_calc = preco_entrada / ((1 - aliq_icms) * (1 - aliq_pc))
    net_calc, val_icms, base_pc, val_pc, total_imp = calc_net_from_gross(gross_calc, aliq_icms, aliq_pc)

st.markdown('<div class="sec-header">Resultado</div>', unsafe_allow_html=True)
r1, r2, r3, r4 = st.columns(4)
with r1:
    st.markdown(f"""<div class="kpi-card" style="border-color:{PETROLEO}">
        <div class="kpi-label">Preço Gross (Bruto)</div>
        <div class="kpi-value">R$ {gross_calc:.4f}</div>
        <div class="kpi-sub">por m³ — inclui todos os impostos</div>
    </div>""", unsafe_allow_html=True)
with r2:
    st.markdown(f"""<div class="kpi-card" style="border-color:{VERDE}">
        <div class="kpi-label">Preço Net (Líquido)</div>
        <div class="kpi-value">R$ {net_calc:.4f}</div>
        <div class="kpi-sub">por m³ — após dedução de impostos</div>
    </div>""", unsafe_allow_html=True)
with r3:
    st.markdown(f"""<div class="kpi-card" style="border-color:{LARANJA}">
        <div class="kpi-label">Total de impostos</div>
        <div class="kpi-value">R$ {total_imp:.4f}</div>
        <div class="kpi-sub">{total_imp/gross_calc*100:.2f}% do Gross</div>
    </div>""", unsafe_allow_html=True)
with r4:
    st.markdown(f"""<div class="kpi-card" style="border-color:{AMARELO}">
        <div class="kpi-label">Para cada R$ 1,00 Gross</div>
        <div class="kpi-value">R$ {net_calc/gross_calc:.4f}</div>
        <div class="kpi-sub">líquido — carga efetiva {total_imp/gross_calc*100:.2f}%</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="sec-header">Composição detalhada</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="background:white;border-radius:12px;padding:20px 24px;
            border:2px solid rgba(48,81,95,0.15);
            box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:12px">
  <table style="width:100%;border-collapse:collapse;font-family:Poppins,sans-serif;font-size:13px">
    <thead>
      <tr style="border-bottom:2px solid {VERDE}">
        <th style="text-align:left;padding:8px 4px;color:{ESCURO};font-weight:600">Componente</th>
        <th style="text-align:right;padding:8px 4px;color:{ESCURO};font-weight:600">Alíquota</th>
        <th style="text-align:right;padding:8px 4px;color:{ESCURO};font-weight:600">Valor (R$/m³)</th>
        <th style="text-align:right;padding:8px 4px;color:{ESCURO};font-weight:600">% do Gross</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom:1px solid #f0f0f0">
        <td style="padding:8px 4px;color:{PETROLEO};font-weight:600">Preço Gross</td>
        <td style="text-align:right;padding:8px 4px">—</td>
        <td style="text-align:right;padding:8px 4px;font-weight:700">R$ {gross_calc:.4f}</td>
        <td style="text-align:right;padding:8px 4px">100,00%</td>
      </tr>
      <tr style="border-bottom:1px solid #f0f0f0;background:#fafafa">
        <td style="padding:8px 4px">ICMS ({uf} · {produto})</td>
        <td style="text-align:right;padding:8px 4px">{aliq_icms*100:.2f}%</td>
        <td style="text-align:right;padding:8px 4px;color:{LARANJA}">− R$ {val_icms:.4f}</td>
        <td style="text-align:right;padding:8px 4px;color:{LARANJA}">{val_icms/gross_calc*100:.2f}%</td>
      </tr>
      <tr style="border-bottom:1px solid #f0f0f0">
        <td style="padding:8px 4px;color:#888;font-size:11px;padding-left:16px">Base PIS/COFINS (Gross − ICMS)</td>
        <td style="text-align:right;padding:8px 4px;color:#aaa;font-size:11px">—</td>
        <td style="text-align:right;padding:8px 4px;color:#aaa;font-size:11px">R$ {base_pc:.4f}</td>
        <td style="text-align:right;padding:8px 4px;color:#aaa;font-size:11px">{base_pc/gross_calc*100:.2f}%</td>
      </tr>
      <tr style="border-bottom:1px solid #f0f0f0;background:#fafafa">
        <td style="padding:8px 4px">PIS ({aliq_pis*100:.2f}%) + COFINS ({aliq_cof*100:.2f}%)</td>
        <td style="text-align:right;padding:8px 4px">{aliq_pc*100:.4f}%</td>
        <td style="text-align:right;padding:8px 4px;color:{LARANJA}">− R$ {val_pc:.4f}</td>
        <td style="text-align:right;padding:8px 4px;color:{LARANJA}">{val_pc/gross_calc*100:.2f}%</td>
      </tr>
      <tr style="border-bottom:2px solid {VERDE}">
        <td style="padding:8px 4px;font-weight:600">Total de impostos</td>
        <td></td>
        <td style="text-align:right;padding:8px 4px;color:{LARANJA};font-weight:700">− R$ {total_imp:.4f}</td>
        <td style="text-align:right;padding:8px 4px;color:{LARANJA};font-weight:700">{total_imp/gross_calc*100:.2f}%</td>
      </tr>
      <tr>
        <td style="padding:10px 4px;font-weight:700;color:{VERDE};font-size:14px">Preço Net</td>
        <td></td>
        <td style="text-align:right;padding:10px 4px;font-weight:800;color:{VERDE};font-size:14px">R$ {net_calc:.4f}</td>
        <td style="text-align:right;padding:10px 4px;font-weight:700;color:{VERDE}">{net_calc/gross_calc*100:.2f}%</td>
      </tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)

nota(f"""
<strong>Memória de cálculo — {produto} · {uf}</strong><br>
1. <strong>ICMS</strong> = Gross × {aliq_icms*100:.2f}% = R$ {gross_calc:.4f} × {aliq_icms:.4f} = <strong>R$ {val_icms:.4f}/m³</strong><br>
2. <strong>Base PIS/COFINS</strong> = Gross − ICMS = R$ {gross_calc:.4f} − R$ {val_icms:.4f} = <strong>R$ {base_pc:.4f}/m³</strong>
   &nbsp;(ICMS excluído da base de cálculo do PIS/COFINS)<br>
3. <strong>PIS/COFINS</strong> = R$ {base_pc:.4f} × {aliq_pc*100:.4f}% = <strong>R$ {val_pc:.4f}/m³</strong><br>
4. <strong>Preço Net</strong> = R$ {gross_calc:.4f} − R$ {val_icms:.4f} − R$ {val_pc:.4f} = <strong>R$ {net_calc:.4f}/m³</strong><br>
<br>
<em>Fonte: Planilha CNP jan/2023. ICMS por estado conforme aba "Listas" da planilha.
Biometano: PIS 1,65% + COFINS 7,60% = 9,25% (regime não-cumulativo).
CO₂: PIS 0,65% + COFINS 3,00% = 3,65% (regime cumulativo).
ICMS SP Biometano: 12% · SP CO₂: 18% · MG/PR/RS/RJ/SC: 12% · demais estados: 7%.</em>
""", "calc")
