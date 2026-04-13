# theme.py — Inteligência de Mercado CNP
CINZA    = "#B2B2B2"
ESCURO   = "#3D3B42"
PETROLEO = "#30515F"
VERDE    = "#76B82A"
AMARELO  = "#FFCC00"
LARANJA  = "#EF7D00"
BRANCO   = "#FFFFFF"
FUNDO    = "#F4F6F4"
PALETA   = [PETROLEO, VERDE, LARANJA, AMARELO, CINZA, "#4A7C8E", "#5A9A3A", "#C4690A"]

CSS_BASE = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, p, span, div, label {{
    font-family: 'Poppins', sans-serif !important;
}}
.stApp {{ background-color: {FUNDO}; }}

/* ── Esconde botão de minimizar sidebar e ícone GitHub ─────────── */
button[data-testid="baseButton-headerNoPadding"],
button[kind="header"],
div[data-testid="stSidebarCollapseButton"],
a[href="https://github.com/streamlit/streamlit"],
footer, footer * {{ display: none !important; }}

/* ── Sidebar completa — fundo cinza claro, texto escuro (logo visível) ─ */
div[data-testid="stSidebar"] {{
    background-color: #EAEEF0 !important;
}}
/* Todos os textos da sidebar em cor escura */
div[data-testid="stSidebar"],
div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] span,
div[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] div,
div[data-testid="stSidebar"] h1,
div[data-testid="stSidebar"] h2,
div[data-testid="stSidebar"] h3,
div[data-testid="stSidebar"] li,
div[data-testid="stSidebar"] .stMarkdown {{
    color: {ESCURO} !important;
    font-family: 'Poppins', sans-serif !important;
}}
div[data-testid="stSidebar"] .stCaption p {{
    color: rgba(61,59,66,0.60) !important;
    font-size: 11px !important;
}}
div[data-testid="stSidebar"] hr {{
    border-color: rgba(61,59,66,0.20) !important;
    margin: 8px 0 !important;
}}
/* Remove maiúsculas de labels */
div[data-testid="stSidebar"] label,
div[data-testid="stWidgetLabel"] p,
div[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {{
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {ESCURO} !important;
}}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p {{
    color: {ESCURO} !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    text-transform: none !important;
}}
/* Inputs, selects, number inputs dentro do sidebar — texto escuro sobre fundo branco */
div[data-testid="stSidebar"] input,
div[data-testid="stSidebar"] .stTextInput input,
div[data-testid="stSidebar"] .stNumberInput input,
div[data-testid="stSidebar"] select,
div[data-testid="stSidebar"] .stSelectbox select,
div[data-testid="stSidebar"] [data-baseweb="select"] span,
div[data-testid="stSidebar"] [data-baseweb="select"] div,
div[data-testid="stSidebar"] [data-baseweb="input"] input,
div[data-testid="stSidebar"] [data-baseweb="base-input"] input {{
    color: {ESCURO} !important;
    background-color: white !important;
}}
/* Multiselect tags dentro do sidebar */
div[data-testid="stSidebar"] [data-baseweb="tag"] span {{
    color: {ESCURO} !important;
}}
/* Slider value labels */
div[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
div[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {{
    color: rgba(61,59,66,0.65) !important;
}}

/* ── Cards KPI — borda ao redor completa ──────────────────────── */
.kpi-card {{
    background: {BRANCO};
    border-radius: 12px;
    padding: 16px 18px;
    border: 2px solid;
    box-shadow: 0 3px 14px rgba(0,0,0,0.09), 0 1px 5px rgba(0,0,0,0.05);
    margin-bottom: 4px;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
}}
.kpi-label {{
    font-size: 12px;
    font-weight: 600;
    color: #888;
    margin-bottom: 6px;
    text-transform: none;
}}
.kpi-value {{
    font-family: 'Poppins', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: {ESCURO};
    line-height: 1.2;
}}
.kpi-delta {{ font-size: 12px; margin-top: 5px; font-weight: 500; }}
.kpi-sub   {{ font-size: 11px; color: #aaa; margin-top: 3px; }}
.up   {{ color: #2e7d4f; }}
.down {{ color: #b83232; }}

/* ── Painel cards (home) — borda ao redor ─────────────────────── */
.painel-card {{
    background: white;
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 16px;
    border: 2px solid;
    box-shadow: 0 3px 14px rgba(0,0,0,0.09), 0 1px 5px rgba(0,0,0,0.04);
    min-height: 140px;
    height: 140px;
    box-sizing: border-box;
    overflow: hidden;
}}

/* ── Seção header ─────────────────────────────────────────────── */
.sec-header {{
    font-family: 'Poppins', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: {ESCURO};
    padding-bottom: 8px;
    border-bottom: 2px solid {VERDE};
    margin-bottom: 16px;
    margin-top: 28px;
    display: block;
}}

/* ── Nota rodapé / memória de cálculo — borda colorida em TODOS os lados ── */
.nota-box {{
    background: white;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04);
    font-size: 12px;
    color: #555;
    line-height: 1.65;
    border: 2px solid {CINZA};
}}
.nota-box.calc {{ border-color: {PETROLEO}; }}
.nota-box.fonte {{ border-color: {VERDE}; }}
.nota-box strong {{ color: {ESCURO}; font-weight: 600; }}

/* ── Page header ─────────────────────────────────────────────── */
.page-header {{
    background: linear-gradient(135deg, {ESCURO} 0%, {PETROLEO} 100%);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(48,81,95,0.22);
}}
.page-header h1 {{
    color: white !important;
    font-size: 20px;
    margin: 0 0 4px 0;
    font-weight: 700;
}}
.page-header p  {{ color: rgba(255,255,255,0.65); font-size: 13px; margin: 0; }}

/* ── Links nav sidebar — tamanho fixo pequeno ──────────────────── */
div[data-testid="stSidebarNav"] a,
div[data-testid="stSidebarNav"] span,
div[data-testid="stSidebarNav"] li {{
    font-size: 13px !important;
    font-weight: 500 !important;
}}
div[data-testid="stSidebarNav"] ul {{
    padding-top: 0 !important;
}}
/* ── Alerts e expanders ──────────────────────────────────────── */
div[data-testid="stAlert"] {{
    border-radius: 10px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07) !important;
}}
div[data-testid="stExpander"] {{
    border-radius: 10px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07) !important;
    border: 2px solid rgba(0,0,0,0.09) !important;
    background: white;
}}
div[data-testid="stDataFrame"] {{
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    overflow: hidden;
}}
/* Links */
a {{ color: {VERDE} !important; font-weight: 500; }}
a:hover {{ color: {PETROLEO} !important; }}

/* Simulador highlight — usa container nativo do Streamlit */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 12px !important;
}}
.sim-box-header {{
    background: linear-gradient(135deg, rgba(118,184,42,0.10) 0%, rgba(48,81,95,0.07) 100%);
    border: 1.5px solid rgba(118,184,42,0.40);
    border-radius: 12px 12px 0 0;
    padding: 16px 22px 14px;
    margin-top: 16px;
    margin-bottom: 0;
}}
.sim-box-body {{
    background: linear-gradient(135deg, rgba(118,184,42,0.04) 0%, rgba(48,81,95,0.02) 100%);
    border: 1.5px solid rgba(118,184,42,0.40);
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 18px 22px 20px;
    margin-bottom: 16px;
}}
.sim-box {{
    background: linear-gradient(135deg, rgba(118,184,42,0.08) 0%, rgba(48,81,95,0.06) 100%);
    border: 1.5px solid rgba(118,184,42,0.35);
    border-radius: 12px;
    padding: 20px 22px;
    margin: 16px 0;
    box-shadow: 0 2px 10px rgba(118,184,42,0.10);
}}
.sim-resultado {{
    font-family: 'Poppins', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: {PETROLEO};
    margin: 8px 0 4px;
}}
.sim-label {{
    font-size: 12px;
    color: #777;
    font-weight: 500;
}}
</style>
"""

PLOTLY_LAYOUT = dict(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Poppins, sans-serif", color=ESCURO, size=12),
    hovermode="x unified",
    legend=dict(orientation="h", y=-0.22, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=0, r=0, t=16, b=48),
    xaxis=dict(gridcolor="#f0f0f0", linecolor="#e8e8e8", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#f0f0f0", linecolor="#e8e8e8", tickfont=dict(size=11)),
)

def sidebar_logo():
    import streamlit as st, base64, os
    if os.path.exists("assets/logo.png"):
        with open("assets/logo.png","rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.sidebar.markdown(
            f'<div style="padding:18px 0 10px;text-align:center">'
            f'<img src="data:image/png;base64,{b64}" style="max-width:150px;max-height:56px;object-fit:contain">'
            f'</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            f'<div style="padding:18px 0 10px;text-align:center;font-family:Poppins,sans-serif;'
            f'font-size:16px;font-weight:700;color:{ESCURO};letter-spacing:1px">CNP</div>',
            unsafe_allow_html=True)
    st.sidebar.markdown(f'<hr style="border-color:rgba(61,59,66,0.20);margin:4px 0 14px">', unsafe_allow_html=True)

def nota(html: str, tipo: str = ""):
    import streamlit as st
    st.markdown(f'<div class="nota-box {tipo}">{html}</div>', unsafe_allow_html=True)

def link_fonte(label: str, url: str):
    import streamlit as st
    st.markdown(
        f'<div style="margin-top:6px;font-size:12px">Fonte primária: '
        f'<a href="{url}" target="_blank">{label}</a></div>',
        unsafe_allow_html=True)
