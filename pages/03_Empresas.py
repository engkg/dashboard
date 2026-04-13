import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import CSS_BASE, VERDE, PETROLEO, ESCURO, LARANJA, AMARELO, CINZA, PLOTLY_LAYOUT, sidebar_logo, nota, link_fonte

st.set_page_config(page_title="Empresas & Potencial — CNP", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS_BASE, unsafe_allow_html=True)

DATA_CNPJ = os.path.join(os.path.dirname(__file__), "..", "data", "empresas.csv")

# ── Tabelas de score ─────────────────────────────────────────────────────────
SCORE_CNAE = {
    "35":100,"49":95,"19":95,"20":90,"50":90,"10":90,"06":90,
    "21":85,"51":85,"05":85,"46":85,"11":85,"52":80,"07":80,
    "01":80,"12":80,"42":75,"02":75,"41":70,"03":70,"43":65,
    "08":78,"23":72,"24":88,"25":70,"26":65,"27":68,"28":72,
    "29":80,"31":65,"32":62,"33":70,"36":85,"37":82,"38":78,
    "47":55,"55":48,"56":42,"58":38,"61":42,"62":45,"63":40,
    "64":35,"65":32,"66":30,"68":28,"69":25,"70":28,"71":35,
    "72":40,"73":30,"74":28,"75":25,"77":45,"78":35,"79":38,
    "80":32,"81":50,"82":35,"84":28,"85":25,"86":38,"87":30,
    "88":25,"90":30,"91":28,"92":25,"93":35,"94":22,"95":30,
    "96":28,"99":20,"00":25,
}
SCORE_PORTE = {"GRANDE PORTE":100,"MEDIO PORTE":70,"PEQUENO PORTE":40,"MICRO EMPRESA":20,"MEI":5}
SCORE_MATURIDADE = {  # anos de operação → score
    (0,1):20,(1,3):40,(3,5):60,(5,10):80,(10,999):100
}
SCORE_ESTRUTURA = {"MATRIZ":100,"FILIAL":70}

SETORES_NOME = {
    "35":"Geração e distribuição de energia","49":"Transporte rodoviário de cargas",
    "19":"Petróleo e derivados","20":"Indústria química","50":"Transporte aquaviário",
    "10":"Indústria de alimentos","06":"Extração de petróleo e gás",
    "21":"Ind. farmacêutica","51":"Transporte aéreo","05":"Extração de carvão",
    "46":"Comércio atacadista combustíveis","11":"Fabricação de bebidas",
    "52":"Armazenamento e logística","07":"Mineração","01":"Agropecuária",
    "12":"Fumo e tabaco","42":"Obras de infraestrutura","02":"Silvicultura",
    "41":"Construção de edifícios","03":"Pesca e aquicultura",
    "23":"Minerais não metálicos","24":"Metalurgia","25":"Produtos de metal",
    "28":"Máquinas e equipamentos","29":"Veículos","36":"Saneamento",
    "37":"Esgoto","38":"Resíduos","08":"Pedras e minerais",
    "27":"Equipamentos elétricos","33":"Manutenção e reparação",
    "43":"Instalações","47":"Varejo","56":"Alimentação",
    "81":"Serviços para edifícios","00":"Outros",
}

CLUSTERS_COMERCIAIS = {
    "Mobilidade a gás":       ["49","50","51","52"],
    "Indústria energo-intens":["10","11","19","20","21","23","24"],
    "Energia e saneamento":   ["35","36","37","38"],
    "Extração e mineração":   ["05","06","07","08"],
    "Agroindustrial":         ["01","02","03","12"],
    "Construção pesada":      ["41","42","43"],
    "Comércio combustíveis":  ["46"],
    "Outros":                 [],
}

def get_cluster(cnae2):
    for cluster, cnaes in CLUSTERS_COMERCIAIS.items():
        if str(cnae2)[:2] in cnaes:
            return cluster
    return "Outros"

def get_maturidade_score(anos):
    for (lo,hi),sc in SCORE_MATURIDADE.items():
        if lo <= anos < hi: return sc
    return 50

def calc_score(row):
    cnae2    = str(row.get("cnae_2","00"))[:2]
    porte    = str(row.get("porte","")).upper()
    estrut   = str(row.get("estrutura","MATRIZ")).upper()
    anos_op  = row.get("anos_operacao", 5)
    uf       = str(row.get("uf",""))

    s_cnae   = SCORE_CNAE.get(cnae2, 25)
    s_porte  = SCORE_PORTE.get(porte, 20)
    s_maturi = get_maturidade_score(anos_op)
    s_estru  = SCORE_ESTRUTURA.get(estrut, 70)
    s_geo    = 100 if uf in ["SP","PR","MS","RJ"] else 60

    score = (s_cnae*0.35 + s_porte*0.20 + s_maturi*0.15 + s_estru*0.15 + s_geo*0.15)
    return round(score, 1)

def get_potencial(score):
    if score >= 80:   return "Alto",   VERDE
    elif score >= 55: return "Médio",  AMARELO
    else:             return "Baixo",  CINZA

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    sidebar_logo()
    ufs_disp = ["Todos","SP","PR","MS","RJ","MG","GO","MT","RS","SC","BA"]
    uf_sel = st.selectbox("Estado", ufs_disp)
    potencial_sel = st.multiselect("Potencial", ["Alto","Médio","Baixo"], default=["Alto","Médio"])
    clusters_disp = list(CLUSTERS_COMERCIAIS.keys())
    cluster_sel = st.multiselect("Cluster comercial", clusters_disp, default=clusters_disp)
    st.markdown("---")
    st.caption("""
**Score multi-dimensional (0–100) — regra interna de priorização**

Este score é uma ferramenta de priorização SDR/outbound com critérios fixos definidos pela equipe CNP. Não representa dado observado de mercado.

- Fit setorial CNAE: 35%
- Porte da empresa: 20%
- Maturidade (anos): 15%
- Estrutura (matriz/filial): 15%
- Fit geográfico: 15%

Foco em SP, PR, MS e RJ = 100 pts geográficos.
    """)

st.markdown("""
<div class="page-header">
    <h1>Empresas & Potencial Comercial</h1>
    <p>Pipeline de prospecção com score multi-dimensional · Clusters comerciais · Análise CNAE · Priorização SDR/outbound</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400)
def load_e():
    if os.path.exists(DATA_CNPJ):
        return pd.read_csv(DATA_CNPJ, low_memory=False)
    return None

df_raw = load_e()

if df_raw is None:
    st.warning("⚠️ **Base de empresas não encontrada.**")
    st.markdown(f"""
<div class="nota-box">
<strong>Como gerar o arquivo <code>data/empresas.csv</code>:</strong><br><br>
1. Execute o extrator da Receita Federal (baixa e processa os ZIPs automaticamente):<br>
<code style="background:#f4f4f4;padding:2px 6px;border-radius:4px">python build_receita_sp_ms.py --ufs SP MS --output data/empresas.csv</code><br><br>
2. O script baixa os arquivos da Receita Federal (~2–5 GB), filtra por UF e CNAE e salva o CSV em <code>data/empresas.csv</code>.<br>
3. Após salvar, recarregue a página — os dados aparecerão aqui automaticamente.<br><br>
Colunas esperadas (geradas pelo extrator): <code>razao_social</code>, <code>cnae_principal_codigo</code> ou <code>cnae_fiscal_principal</code>, <code>uf</code>, <code>municipio_nome</code> ou <code>municipio</code>, <code>porte_desc</code> ou <code>descricao_porte</code>, <code>data_inicio_atividade</code>, <code>identificador_matriz_filial</code> ou <code>matriz_filial_desc</code>.
</div>
""", unsafe_allow_html=True)
    st.stop()

df = df_raw.copy()

# Normaliza colunas — aceita tanto o schema do build_receita quanto o schema simples
col_map = {
    # (coluna_origem_alternativa, coluna_destino_interna)
    "cnae_principal_codigo":      "cnae_fiscal_principal",
    "cnae_principal_desc":        "cnae_desc",
    "municipio_nome":             "municipio",
    "porte_desc":                 "descricao_porte",
    "situacao_cadastral_desc":    "situacao",
    "matriz_filial_desc":         "identificador_matriz_filial",
}
for orig, dest in col_map.items():
    if orig in df.columns and dest not in df.columns:
        df[dest] = df[orig]

# Mapeia para colunas internas de score
for col_orig, col_dest in [("cnae_fiscal_principal","cnae_2"),("descricao_porte","porte")]:
    if col_orig in df.columns and col_dest not in df.columns:
        df[col_dest] = df[col_orig]

# Filtra apenas empresas ativas quando coluna disponível
if "situacao" in df.columns:
    df = df[df["situacao"].fillna("ATIVA").str.upper().isin(["ATIVA",""])]
elif "situacao_cadastral_desc" in df.columns:
    df = df[df["situacao_cadastral_desc"].fillna("ATIVA").str.upper() == "ATIVA"]

if "cnae_2" in df.columns:
    df["cnae_2"] = df["cnae_2"].astype(str).str[:2]
if "data_inicio_atividade" in df.columns:
    try:
        df["anos_operacao"] = (pd.Timestamp.now() - pd.to_datetime(df["data_inicio_atividade"], errors="coerce")).dt.days / 365
        df["anos_operacao"] = df["anos_operacao"].fillna(5).clip(0, 50)
    except Exception:
        df["anos_operacao"] = 5
if "anos_operacao" not in df.columns:
    df["anos_operacao"] = 5
if "estrutura" not in df.columns:
    if "identificador_matriz_filial" in df.columns:
        df["estrutura"] = df["identificador_matriz_filial"].astype(str).str.upper().str.strip()
    else:
        df["estrutura"] = "MATRIZ"
df["setor_nome"] = df["cnae_2"].astype(str).str[:2].map(lambda x: SETORES_NOME.get(x, "Outros"))
df["cluster"]    = df["cnae_2"].astype(str).str[:2].map(get_cluster)
df["score"]      = df.apply(calc_score, axis=1)
df["potencial"]  = df["score"].apply(lambda s: get_potencial(s)[0])

# Filtros
df_f = df.copy()
if uf_sel != "Todos" and "uf" in df_f.columns:
    df_f = df_f[df_f["uf"]==uf_sel]
if potencial_sel: df_f = df_f[df_f["potencial"].isin(potencial_sel)]
if cluster_sel:   df_f = df_f[df_f["cluster"].isin(cluster_sel)]

# KPIs
st.markdown('<div class="sec-header">Resumo da base filtrada</div>', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
for col,label,val,cor in [
    (c1,"Total de empresas",f"{len(df_f):,}",ESCURO),
    (c2,"Potencial alto",f"{(df_f['potencial']=='Alto').sum():,}",VERDE),
    (c3,"Potencial médio",f"{(df_f['potencial']=='Médio').sum():,}",AMARELO),
    (c4,"Score médio",f"{df_f['score'].mean():.1f}/100",PETROLEO),
    (c5,"Clusters",f"{df_f['cluster'].nunique()}",LARANJA),
]:
    with col:
        st.markdown(f"""<div class="kpi-card" style="border-color:{cor}">
            <div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>""",unsafe_allow_html=True)

tab1,tab2,tab3 = st.tabs(["Pipeline completo","Análise por cluster","Score detalhado"])

with tab1:
    st.markdown('<div class="sec-header">Pipeline de prospecção completo</div>', unsafe_allow_html=True)

    cols_show = [c for c in ["razao_social","cnpj","setor_nome","cluster","porte","municipio","uf","anos_operacao","score","potencial"] if c in df_f.columns]
    df_show = df_f[cols_show].sort_values("score",ascending=False).copy()
    rename_map = {"razao_social":"Razão Social","cnpj":"CNPJ","setor_nome":"Setor",
                  "cluster":"Cluster","porte":"Porte","municipio":"Município","uf":"UF",
                  "anos_operacao":"Anos oper.","score":"Score","potencial":"Potencial"}
    df_show = df_show.rename(columns={k:v for k,v in rename_map.items() if k in df_show.columns})

    if "Anos oper." in df_show.columns:
        df_show["Anos oper."] = df_show["Anos oper."].round(1)

    # Sem applymap/background_gradient — formatação simples
    st.dataframe(df_show.style.format({"Score":"{:.1f}","Anos oper.":"{:.1f}"}, na_rep="-"),
                 use_container_width=True, height=500)
    st.download_button("Baixar pipeline completo (CSV)", df_show.to_csv(index=False).encode("utf-8"), "pipeline_cnp.csv","text/csv")

with tab2:
    cl, cr = st.columns(2)
    with cl:
        st.markdown('<div class="sec-header">Empresas por cluster comercial</div>', unsafe_allow_html=True)
        cl_agg = df_f.groupby("cluster").agg(empresas=("score","count"),score_medio=("score","mean")).reset_index()
        cl_agg = cl_agg.sort_values("score_medio",ascending=True)
        fig_cl = go.Figure(go.Bar(
            x=cl_agg["score_medio"], y=cl_agg["cluster"], orientation="h",
            marker=dict(color=cl_agg["score_medio"].tolist(),
                        colorscale=[[0,CINZA],[0.5,AMARELO],[1,VERDE]],cmin=0,cmax=100),
            text=cl_agg["empresas"].apply(lambda x: f"{x} emp."),textposition="outside",
            hovertemplate="%{y}<br>Score médio: %{x:.1f}<extra></extra>",
        ))
        layout=dict(PLOTLY_LAYOUT);layout["height"]=340;layout["xaxis"]=dict(title="Score médio",range=[0,115])
        layout["yaxis"]=dict(autorange="reversed",tickfont=dict(size=11));layout["legend"]=dict(y=-0.1)
        fig_cl.update_layout(**layout)
        st.plotly_chart(fig_cl, use_container_width=True)
    with cr:
        st.markdown('<div class="sec-header">Distribuição por potencial</div>', unsafe_allow_html=True)
        pot_cnt = df_f["potencial"].value_counts()
        fig_pot = go.Figure(go.Pie(
            labels=pot_cnt.index.tolist(), values=pot_cnt.values.tolist(), hole=0.4,
            marker=dict(colors=[VERDE if l=="Alto" else AMARELO if l=="Médio" else CINZA for l in pot_cnt.index]),
            hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
        ))
        fig_pot.update_layout(paper_bgcolor="white",plot_bgcolor="white",font=dict(family="Poppins",color=ESCURO),
                              height=340,margin=dict(l=0,r=0,t=10,b=0),legend=dict(orientation="h",y=-0.1))
        st.plotly_chart(fig_pot, use_container_width=True)

with tab3:
    st.markdown('<div class="sec-header">Simulador de score — avalie uma empresa</div>', unsafe_allow_html=True)
    with st.container(border=True):
        cs1,cs2,cs3 = st.columns(3)
        with cs1:
            sim_cnae   = st.selectbox("CNAE principal (2 dígitos)", list(SCORE_CNAE.keys()), format_func=lambda x: f"{x} — {SETORES_NOME.get(x,'Outros')}", key="sim_cnae")
            sim_porte  = st.selectbox("Porte", list(SCORE_PORTE.keys()), key="sim_porte")
        with cs2:
            sim_anos   = st.number_input("Anos de operação", value=8, min_value=0, max_value=80, key="sim_anos")
            sim_estru  = st.selectbox("Estrutura", ["MATRIZ","FILIAL"], key="sim_estru")
        with cs3:
            sim_uf     = st.selectbox("Estado", ["SP","PR","MS","RJ","MG","GO","MT","RS","SC","Outros"], key="sim_uf")

        row_sim = {"cnae_2":sim_cnae,"porte":sim_porte,"estrutura":sim_estru,"anos_operacao":sim_anos,"uf":sim_uf}
        s_cnae_v  = SCORE_CNAE.get(sim_cnae,25)
        s_porte_v = SCORE_PORTE.get(sim_porte,20)
        s_maturi_v= get_maturidade_score(sim_anos)
        s_estru_v = SCORE_ESTRUTURA.get(sim_estru,70)
        s_geo_v   = 100 if sim_uf in ["SP","PR","MS","RJ"] else 60
        score_sim = round(s_cnae_v*0.35+s_porte_v*0.20+s_maturi_v*0.15+s_estru_v*0.15+s_geo_v*0.15,1)
        pot_label,pot_cor = get_potencial(score_sim)

        st.markdown(f"""
    <div style="margin-top:16px;display:flex;gap:24px;align-items:center">
        <div><span class="sim-label">Score calculado</span>
             <div class="sim-resultado" style="color:{pot_cor}">{score_sim}/100</div></div>
        <div><span class="sim-label">Potencial</span>
             <div style="font-size:22px;font-weight:700;color:{pot_cor};margin-top:8px">{pot_label}</div></div>
        <div><span class="sim-label">Cluster comercial</span>
             <div style="font-size:16px;font-weight:600;color:{ESCURO};margin-top:8px">{get_cluster(sim_cnae)}</div></div>
    </div>
    """, unsafe_allow_html=True)
    nota(f"""
    <strong>Memória de cálculo do score:</strong><br>
    Score = (s_cnae × 0,35) + (s_porte × 0,20) + (s_maturidade × 0,15) + (s_estrutura × 0,15) + (s_geo × 0,15)<br>
    = ({s_cnae_v} × 0,35) + ({s_porte_v} × 0,20) + ({s_maturi_v} × 0,15) + ({s_estru_v} × 0,15) + ({s_geo_v} × 0,15)<br>
    = {s_cnae_v*0.35:.1f} + {s_porte_v*0.20:.1f} + {s_maturi_v*0.15:.1f} + {s_estru_v*0.15:.1f} + {s_geo_v*0.15:.1f} = <strong>{score_sim}</strong><br><br>
    <strong>Justificativa dos pesos:</strong> CNAE (35%) é o fator mais relevante por determinar o perfil de consumo energético. Porte (20%) determina volume de consumo. Maturidade (15%) indica empresa estabelecida com padrão de consumo estável. Estrutura (15%) indica tomada de decisão centralizada na matriz. Fit geográfico (15%) prioriza os 4 estados estratégicos.
    ""","calc")

nota("""
<strong>Metodologia do score multi-dimensional:</strong> cada empresa recebe pontuação de 0 a 100 com 5 dimensões ponderadas:
(1) Fit setorial CNAE 35% — setores com maior consumo potencial de biometano/GNV/GLP;
(2) Porte 20% — grandes empresas têm maior volume de consumo;
(3) Maturidade 15% — empresas com mais de 5 anos têm padrão de consumo estável;
(4) Estrutura 15% — matrizes centralizam decisão de compra;
(5) Fit geográfico 15% — SP, PR, MS e RJ são os estados estratégicos CNP.
<strong>Fonte da metodologia:</strong> adaptado de framework de lead scoring B2B (MQL/SQL) com dados públicos CNPJ/Receita Federal.
""","calc")
