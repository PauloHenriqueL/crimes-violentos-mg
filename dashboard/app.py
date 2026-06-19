import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard - Crimes Violentos MG", 
    page_icon="🚓", 
    layout="wide"
)

st.title("🚓 Painel Interativo: Crimes Violentos em Minas Gerais")
st.subheader("DCC011 - Introdução a Banco de Dados (UFMG)")

# -------------------------------------------------------------------------
# 1. CARREGAMENTO DOS CSVs UTILIZANDO CAMINHO RELATIVO
# -------------------------------------------------------------------------
@st.cache_data
def carregar_e_unificar_dados():
    # Como o app está na pasta /dashboard, voltamos um nível (..) para acessar /data/raw
    caminho_2025 = os.path.join("..", "data", "raw", "crimes_violentos_2025.csv")
    caminho_2026 = os.path.join("..", "data", "raw", "crimes_violentos_2026.csv")
    
    df_2025 = pd.read_csv(caminho_2025, sep=';') if os.path.exists(caminho_2025) else pd.DataFrame()
    df_2026 = pd.read_csv(caminho_2026, sep=';') if os.path.exists(caminho_2026) else pd.DataFrame()
    
    if df_2025.empty and df_2026.empty:
        raise FileNotFoundError("Os arquivos CSV não foram encontrados no caminho esperado de data/raw/")
    
    df_unificado = pd.concat([df_2025, df_2026], ignore_index=True)
    return df_unificado

try:
    df_raw = carregar_e_unificar_dados()
except Exception as e:
    st.error(f"⚠️ Erro de Caminho: Verifique se a estrutura de pastas externa contém 'data/raw/'. Erro: {e}")
    st.stop()

# -------------------------------------------------------------------------
# 2. SIMULAÇÃO DO SCHEMA NORMALIZADO (3FN) COM PANDAS
# -------------------------------------------------------------------------
@st.cache_data
def simular_schema_normalizado(df):
    col_municipio = 'municipio'
    col_cod_municipio = 'cod_municipio'
    col_natureza = 'natureza'
    col_risp = 'risp'
    col_rmbh = 'rmbh'
    
    # Tabela 1: Municipios
    tabela_municipios = df[[col_municipio, col_cod_municipio, col_rmbh]].drop_duplicates().reset_index(drop=True)
    tabela_municipios['id_municipio'] = tabela_municipios.index + 1
    
    # Tabela 2: Naturezas
    tabela_naturezas = df[[col_natureza]].drop_duplicates().reset_index(drop=True)
    tabela_naturezas['id_natureza'] = tabela_naturezas.index + 1
    
    # Tabela 3: Regiões (RISP)
    tabela_regioes = df[[col_risp]].drop_duplicates().reset_index(drop=True)
    tabela_regioes['id_risp'] = tabela_regioes.index + 1
    
    # Tabela 4: Fatos / Ocorrências
    df_migrado = df.merge(tabela_municipios, on=[col_municipio, col_cod_municipio, col_rmbh])
    df_migrado = df_migrado.merge(tabela_naturezas, on=col_natureza)
    df_migrado = df_migrado.merge(tabela_regioes, on=col_risp)
    
    tabela_ocorrencias = df_migrado[['id_municipio', 'id_natureza', 'id_risp', 'mes', 'ano', 'registros']].copy()
    tabela_ocorrencias['id_ocorrencia'] = tabela_ocorrencias.index + 1
    
    return tabela_municipios, tabela_naturezas, tabela_regioes, tabela_ocorrencias

df_municipios, df_naturezas, df_regioes, df_ocorrencias = simular_schema_normalizado(df_raw)

# -------------------------------------------------------------------------
# 3. INTERFACE DE NAVEGAÇÃO (MENU LATERAL)
# -------------------------------------------------------------------------
st.sidebar.header("Menu do Projeto")
opcao = st.sidebar.selectbox(
    "Navegue pelas Seções:",
    [
        "Visão Geral & Dados Brutos",
        "Modelo Relacional (3FN)",
        "Consulta: Análise por Município",
        "Consulta: Top Naturezas de Crimes",
        "Consulta: Evolução Temporal (2025-2026)",
        "Consulta: Filtro por Região (RISP)"
    ]
)

# --- SEÇÃO 1: VISÃO GERAL ---
if opcao == "Visão Geral & Dados Brutos":
    st.markdown("### 📝 Descrição do Dataset")
    st.write("Análise de crimes violentos no estado de Minas Gerais abrangendo o ano de 2025 e o início de 2026[cite: 8].")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Linhas no Arquivo", f"{len(df_raw):,}")
    col2.metric("Total de Casos Registrados", f"{int(df_raw['registros'].sum()):,}")
    col3.metric("Municípios Mapeados", f"{df_raw['municipio'].nunique()}")
    
    st.markdown("#### Amostra dos Dados Brutos Unificados:")
    st.dataframe(df_raw.head(50))

# --- SEÇÃO 2: MODELO RELACIONAL ---
elif opcao == "Modelo Relacional (3FN)":
    st.markdown("### 🗄️ Estrutura do Banco de Dados Normalizado (3FN)")
    st.write("Visualização das tabelas simuladas em Terceira Forma Normal[cite: 5].")
    
    pestana1, pestana2, pestana3 = st.tabs(["Tabela Municípios", "Tabela Naturezas", "Tabela Ocorrências"])
    with pestana1: st.dataframe(df_municipios)
    with pestana2: st.dataframe(df_naturezas)
    with pestana3: st.dataframe(df_ocorrencias.head(50))

# --- SEÇÃO 3: CONSULTA POR MUNICÍPIO ---
elif opcao == "Consulta: Análise por Município":
    st.header("🔍 Consulta Analítica por Município")
    
    municipio_selecionado = st.selectbox("Selecione um Município de MG:", sorted(df_municipios['municipio'].unique()))
    df_completo = df_ocorrencias.merge(df_municipios, on='id_municipio').merge(df_naturezas, on='id_natureza')
    resultado = df_completo[df_completo['municipio'] == municipio_selecionado][['mes', 'ano', 'natureza', 'registros']]
    
    st.write(f"#### Histórico de Ocorrências para: {municipio_selecionado}")
    st.dataframe(resultado.reset_index(drop=True))

# --- SEÇÃO 4: TOP NATUREZAS ---
elif opcao == "Consulta: Top Naturezas de Crimes":
    st.header("📊 Ranking das Naturezas de Crimes")
    
    df_completo = df_ocorrencias.merge(df_naturezas, on='id_natureza')
    top_crimes = df_completo.groupby('natureza')['registros'].sum().reset_index()
    top_crimes.columns = ['Natureza do Crime', 'Total de Ocorrências']
    top_crimes = top_crimes.sort_values(by='Total de Ocorrências', ascending=False)
    
    col1, col2 = st.columns([1, 2])
    with col1: st.dataframe(top_crimes.reset_index(drop=True))
    with col2:
        fig_bar = px.bar(top_crimes, x='Total de Ocorrências', y='Natureza do Crime', 
                         orientation='h', color='Total de Ocorrências', color_continuous_scale="Reds")
        st.plotly_chart(fig_bar, use_container_width=True)

# --- SEÇÃO 5: EVOLUÇÃO TEMPORAL ---
elif opcao == "Consulta: Evolução Temporal (2025-2026)":
    st.header("📈 Evolução Mensal de Crimes no Estado")
    df_raw['Periodo'] = df_raw['ano'].astype(str) + "-" + df_raw['mes'].astype(str).str.zfill(2)
    df_linha = df_raw.groupby('Periodo')['registros'].sum().reset_index()
    
    fig_linha = px.line(df_linha, x='Periodo', y='registros', title="Total de Ocorrências por Mês [cite: 8]")
    st.plotly_chart(fig_linha, use_container_width=True)

# --- SEÇÃO 6: FILTRO POR REGIONAL (RISP) ---
elif opcao == "Consulta: Filtro por Região (RISP)":
    st.header("🏢 Análise por Região Integrada de Segurança Pública (RISP)")
    df_completo = df_ocorrencias.merge(df_regioes, on='id_risp').merge(df_naturezas, on='id_natureza')
    
    risp_selecionada = st.selectbox("Selecione a RISP desejada:", sorted(df_regioes['risp'].unique()))
    resultado_risp = df_completo[df_completo['risp'] == risp_selecionada]
    resumo_risp = resultado_risp.groupby('natureza')['registros'].sum().reset_index()
    
    fig_pizza = px.pie(resumo_risp, values='registros', names='natureza', title=f"Proporção de Crimes na {risp_selecionada}")
    st.plotly_chart(fig_pizza, use_container_width=True)