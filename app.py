import streamlit as st
import pandas as pd
import io

# --- Configurações da Aplicação ---
st.set_page_config(layout="wide")

# Mapeamento robusto de colunas (índices após a leitura do cabeçalho)
COL_MAP = {
    0: 'KM',            
    3: 'M',             
    8: 'Parameter',     
    26: 'Value',         
    31: 'Length',        
    39: 'Speed',         
    44: 'TSC',           
    55: 'Track',         
    62: 'Peak Lat/Long'  
}

# --- Função Principal de Limpeza e Processamento ---
@st.cache_data
def processar_dados_ferrovia(uploaded_file):
    """
    Carrega, limpa e processa o arquivo, suportando .csv ou .xlsx.
    """
    
    # Determina o tipo de arquivo pela extensão
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    # 1. Carregamento e Seleção de Colunas por Índice
    try:
        if file_extension == 'csv':
            # Leitura para CSV: usa separador ',' e header na 5ª linha (index 4)
            df = pd.read_csv(
                uploaded_file,
                sep=',',
                header=4,
                engine='python',
                on_bad_lines='skip'
            )
        elif file_extension == 'xlsx':
            # Leitura para Excel: header na 5ª linha (index 4)
            df = pd.read_excel(
                uploaded_file,
                header=4, 
                sheet_name=0 # Assume a primeira aba
            )
        else:
            st.error("Formato de arquivo não suportado. Use .csv ou .xlsx.")
            return pd.DataFrame()

        # Seleciona as colunas usando os índices mapeados
        colunas_para_selecionar = list(COL_MAP.keys())
        df_limpo = df.iloc[:, colunas_para_selecionar].copy()
        df_limpo.columns = COL_MAP.values()

        # 2. Limpeza e Tipagem de Dados
        df_limpo = df_limpo.dropna(subset=['Parameter'])

        df_limpo['Value'] = pd.to_numeric(df_limpo['Value'], errors='coerce')
        df_limpo = df_limpo.dropna(subset=['Value'])
        
        # Cria a coluna de localização única (KM + M)
        df_limpo['KM'] = df_limpo['KM'].fillna(0).astype(int)
        df_limpo['M'] = df_limpo['M'].fillna(0).astype(int)
        df_limpo['Localização'] = df_limpo['KM'].astype(str) + '+' + df_limpo['M'].astype(str).str.zfill(3)

        return df_limpo

    except Exception as e:
        st.error(f"Erro ao processar o arquivo. Detalhe: {e}")
        return pd.DataFrame()

# --- Interface Streamlit ---

st.title("Rail Track Geometry Analyzer (SUPERVIA)")
st.markdown("Ferramenta para limpeza e análise do Relatório de Inspeção de Geometria da Via (CSV ou XLSX).")

# Widget de Carregamento de Arquivo
uploaded_file = st.file_uploader(
    "1. Carregue o arquivo do relatório (.csv ou .xlsx)", 
    type=['csv', 'xlsx'] # Agora aceita os dois formatos
)

if uploaded_file is not None:
    
    # Processa os dados
    df_limpo = processar_dados_ferrovia(uploaded_file)
    
    if not df_limpo.empty:
        st.success(f"Arquivo '{uploaded_file.name}' carregado e dados processados com sucesso!")
        
        # ----------------------------------------
        # | Análise Interativa |
        # ----------------------------------------
        
        st.header("2. Análise Interativa")
        
        tipos_de_parametro = sorted(df_limpo['Parameter'].unique().tolist())
        selected_parameter = st.selectbox(
            "Selecione o Parâmetro de Interesse:", 
            tipos_de_parametro, 
            index=tipos_de_parametro.index('Gage Wide') if 'Gage Wide' in tipos_de_parametro else 0
        )
        
        df_filtrado = df_limpo[df_limpo['Parameter'] == selected_parameter]

        if not df_filtrado.empty:
            num_top = st.slider(
                f"Mostrar os Top N ({selected_parameter}) mais críticos (maiores Valores):", 
                min_value=5, 
                max_value=min(200, len(df_filtrado)), 
                value=20
            )

            df_criticos = df_filtrado.sort_values(by='Value', ascending=False).head(num_top)
            
            st.subheader(f"Top {num_top} Desvios de **{selected_parameter}**")
            st.dataframe(
                df_criticos[['Localização', 'Parameter', 'Value', 'Length', 'TSC', 'Peak Lat/Long']], 
                use_container_width=True,
                hide_index=True
            )
            
            # ----------------------------------------
            # | Opção de Download |
            # ----------------------------------------
            csv_export = df_limpo.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download de TODOS os Dados Limpos (CSV)",
                data=csv_export,
                file_name='dados_supervia_limpos_analisados.csv',
                mime='text/csv',
            )

        else:
            st.warning(f"Nenhum dado de medição encontrado para o parâmetro: {selected_parameter}")
            
    else:
        st.warning("O DataFrame está vazio após o processamento. Verifique se o cabeçalho do arquivo está correto (linha 5).")