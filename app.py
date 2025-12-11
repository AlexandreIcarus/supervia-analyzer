import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- Configurações da Aplicação ---
st.set_page_config(layout="wide")

# ====================================================================
# !!! ATENÇÃO: COLOQUE AQUI OS VALORES CORRETOS DA SUPERVIA !!!
# ====================================================================
TOLERANCE_LIMITS = {
    'Gage Wide': {'min': 1600, 'max': 1630, 'check': 'max'},      
    'Gage Narrow': {'min': 1580, 'max': 1600, 'check': 'min'},    
    'Crosslevel': {'min': -150, 'max': 150, 'check': 'abs_max'},
    'Twist 3': {'min': 0, 'max': 25, 'check': 'max'},
    'Twist 10': {'min': 0, 'max': 40, 'check': 'max'},
    'L Align 20': {'min': -70, 'max': 70, 'check': 'abs_max'},
    'R Align 20': {'min': -70, 'max': 70, 'check': 'abs_max'},
    'L Vert 20': {'min': -70, 'max': 70, 'check': 'abs_max'},
    'R Vert 20': {'min': -70, 'max': 70, 'check': 'abs_max'},
    'L Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
    'R Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
}

IGNORED_PARAMETERS = [
    'Railroad', 'Subdivision', 'Tunnel Start', 'Tunnel End', 'Bridge End', 
    'Bridge Start', 'Concrete Ties End', 'Concrete Ties Start', 
    'Timber Ties End', 'Timber Ties Start', 'Rail Joint', 'Level Crossing',
    'Switch/Frog', 'Up Kilometer', 'Down Kilometer', 'Track Change', 
    'Class Change', 'Posted Speed' 
]
# ====================================================================


# --- Mapeamentos para os DOIS formatos possíveis ---

# NOVO MAPEARMENTO COMPLEXO: Inclui colunas adjacentes para o campo 'Value'
COMPLEX_COL_MAP = {
    0: 'KM', 3: 'M', 8: 'Parameter', 
    26: 'Value_26', 27: 'Value_27', 28: 'Value_28',  # Colunas de contingência para o Value
    31: 'Length', 39: 'Speed', 44: 'TSC', 55: 'Track', 62: 'Peak Lat/Long'
}
COMPLEX_HEADER_ROW = 4

# Mapeamento do formato simplificado (CSV filtrado) - MANTIDO
SIMPLIFIED_REQUIRED_COLS = ['KM', 'M', 'Parameter', 'Value', 'Length', 'Speed', 'TSC', 'Track', 'Peak Lat', 'Peak Long']
SIMPLIFIED_HEADER_ROW = 0 

MAX_ROWS_TO_READ = 11000 


# --- Função para Análise de Conformidade (Mantida) ---
def check_conformity(df):
    """ Adiciona a coluna 'Status' e 'Delta' ao DataFrame baseado nos limites. """
    df['Status'] = 'Não Aplicável'
    df['Delta'] = 0.0
    for param, limits in TOLERANCE_LIMITS.items():
        mask = df['Parameter'] == param
        if df.loc[mask].empty: continue
        value_to_check = df.loc[mask, 'Value']
        if limits['check'] == 'max':
            df.loc[mask, 'Status'] = df.loc[mask, 'Value'].apply(lambda x: 'Fora do Limite' if x > limits['max'] else 'Em Conformidade')
            df.loc[mask, 'Delta'] = df.loc[mask, 'Value'].apply(lambda x: x - limits['max'] if x > limits['max'] else 0)
        elif limits['check'] == 'min':
            df.loc[mask, 'Status'] = df.loc[mask, 'Value'].apply(lambda x: 'Fora do Limite' if x < limits['min'] else 'Em Conformidade')
            df.loc[mask, 'Delta'] = df.loc[mask, 'Value'].apply(lambda x: limits['min'] - x if x < limits['min'] else 0)
        elif limits['check'] == 'abs_max':
            df.loc[mask, 'Status'] = value_to_check.apply(lambda x: 'Fora do Limite' if abs(x) > limits['max'] else 'Em Conformidade')
            df.loc[mask, 'Delta'] = value_to_check.apply(lambda x: abs(x) - limits['max'] if abs(x) > limits['max'] else 0)
    return df


# --- Função Principal de Limpeza e Processamento (Aprimorada para Flexibilidade) ---
@st.cache_data
def processar_dados_ferrovia(uploaded_file):
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    df_limpo = pd.DataFrame()
    is_simplified = False
    
    # 1. TENTA LER O ARQUIVO NO FORMATO SIMPLIFICADO
    try:
        uploaded_file.seek(0)
        
        if file_extension == 'csv':
            df_read = pd.read_csv(uploaded_file, sep=',', header=SIMPLIFIED_HEADER_ROW, engine='python', on_bad_lines='skip', nrows=MAX_ROWS_TO_READ)
        elif file_extension == 'xlsx':
            df_read = pd.read_excel(uploaded_file, header=SIMPLIFIED_HEADER_ROW, sheet_name=0, nrows=MAX_ROWS_TO_READ)

        df_read.columns = df_read.columns.str.strip() 
        is_simplified = all(col in df_read.columns for col in ['Peak Lat', 'Peak Long', 'KM', 'Parameter'])
        
        if is_simplified:
            # st.info("Formato SIMPLIFICADO (Filtrado) detectado.")
            df_limpo = df_read[df_read.columns.intersection(SIMPLIFIED_REQUIRED_COLS)].copy()
            df_limpo['Peak Lat/Long'] = df_limpo['Peak Lat'].astype(str) + ',' + df_limpo['Peak Long'].astype(str)
            df_limpo = df_limpo.drop(columns=['Peak Lat', 'Peak Long'], errors='ignore')
            
            # Renomeia o 'Value' para o padrão final, para que a lógica de limpeza abaixo funcione
            df_limpo = df_limpo.rename(columns={'Value': 'Value_26'}) 
            
        else:
            pass
            
    except Exception:
        is_simplified = False


    # 2. TENTA LER O ARQUIVO NO FORMATO COMPLEXO
    if not is_simplified:
        try:
            uploaded_file.seek(0) 

            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file, sep=',', header=COMPLEX_HEADER_ROW, engine='python', on_bad_lines='skip', nrows=MAX_ROWS_TO_READ)
            elif file_extension == 'xlsx':
                df = pd.read_excel(uploaded_file, header=COMPLEX_HEADER_ROW, sheet_name=0, nrows=MAX_ROWS_TO_READ)

            # Seleciona as colunas usando os índices definidos no novo mapa
            colunas_para_selecionar = list(COMPLEX_COL_MAP.keys())
            df_limpo = df.iloc[:, colunas_para_selecionar].copy()
            df_limpo.columns = COMPLEX_COL_MAP.values()
            
        except Exception as complex_e:
            st.error(f"Erro Crítico ao processar arquivo nos dois formatos. Verifique o cabeçalho. Detalhe: {complex_e}")
            return None, None, None 

    # --- Lógica de Limpeza Comum aos DOIS Formatos ---
    if df_limpo.empty: return None, None, None
    
    all_raw_parameters = df_limpo['Parameter'].astype(str).str.strip().unique().tolist()
    
    # 1. Limpeza de linhas sem Parameter
    df_limpo = df_limpo.dropna(subset=['Parameter'])
    
    # 2. FILTRAR PARÂMETROS DE IDENTIFICAÇÃO (TEXTO)
    df_limpo['Parameter'] = df_limpo['Parameter'].astype(str).str.strip()
    df_limpo = df_limpo[~df_limpo['Parameter'].isin(IGNORED_PARAMETERS)].copy()

    # 3. CONSOLIDAÇÃO DO CAMPO 'VALUE' (Safety Net)
    value_cols = [col for col in df_limpo.columns if col.startswith('Value_')]
    
    # Prepara as colunas Value para conversão (limpa ruído)
    for col in value_cols:
        df_limpo[col] = df_limpo[col].astype(str).str.replace(' ', '').str.replace(',', '.').str.strip()
        df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')
        
    # Coalesce: O campo 'Value' final será o primeiro campo numérico válido encontrado 
    # entre Value_26, Value_27, Value_28, etc.
    df_limpo['Value'] = df_limpo[value_cols].bfill(axis=1).iloc[:, 0]
    
    # 4. Armazena a contagem ANTES de remover os valores nulos
    rows_before_value_filter = len(df_limpo)
    
    # 5. Remove linhas que falharam na conversão/coalescência (Value ainda é NaN)
    df_limpo = df_limpo.dropna(subset=['Value'])
    
    # 6. Cria a Localização
    df_limpo['KM'] = pd.to_numeric(df_limpo['KM'], errors='coerce').fillna(0).astype(int)
    df_limpo['M'] = pd.to_numeric(df_limpo['M'], errors='coerce').fillna(0).astype(int)
    df_limpo['Localização'] = df_limpo['KM'].astype(str) + '+' + df_limpo['M'].astype(str).str.zfill(3)
    
    # Remove as colunas temporárias de Value
    df_limpo = df_limpo.drop(columns=value_cols, errors='ignore')

    df_limpo_analisado = check_conformity(df_limpo)

    return df_limpo_analisado, rows_before_value_filter, all_raw_parameters 

# --- Interface Streamlit (Mantida) ---

st.title("Rail Track Geometry Analyzer (SUPERVIA) 📊")
st.markdown("**1. ATENÇÃO:** Ajuste os limites na tabela `TOLERANCE_LIMITS` no código `app.py` com os valores corretos da SUPERVIA.")
st.markdown(f"**Observação:** O sistema está configurado para ler até **{MAX_ROWS_TO_READ} linhas** e agora suporta arquivos no formato **Original (Completo)** e no formato **Filtrado (Simplificado)**.")

uploaded_file = st.file_uploader(
    "1. Carregue o arquivo do relatório (.csv ou .xlsx)", 
    type=['csv', 'xlsx']
)

if uploaded_file is not None:
    result = processar_dados_ferrovia(uploaded_file)
    
    if result is not None:
        df_limpo, rows_before_value_filter, all_raw_parameters = result

        if not df_limpo.empty:
            st.success(f"Arquivo '{uploaded_file.name}' carregado e processado com **{len(df_limpo)} linhas de dados de medição válidos**.")
            
            rows_discarded = rows_before_value_filter - len(df_limpo)
            if rows_discarded > 0:
                 st.info(f"**Detalhe da Limpeza:** {rows_before_value_filter} linhas com Parâmetros de Geometria foram consideradas, mas **{rows_discarded} foram descartadas** por terem valores nulos ou não numéricos no campo 'Value'.")
            else:
                 st.info(f"**Detalhe da Limpeza:** O filtro de Parâmetros de Identificação foi aplicado. Todas as {len(df_limpo)} linhas restantes têm valores numéricos válidos.")

            # --- FERRAMENTA DE DIAGNÓSTICO ---
            with st.expander("🛠️ Ferramenta de Diagnóstico: Parâmetros Encontrados no Arquivo"):
                st.warning("Use esta ferramenta para verificar se todos os Parâmetros esperados (medições de geometria) foram lidos e para identificar o que está sendo filtrado.")
                
                st.info(f"Foram encontrados **{len(all_raw_parameters)}** Parâmetros únicos na leitura inicial do arquivo.")
                
                geometry_params = [p for p in all_raw_parameters if p in TOLERANCE_LIMITS.keys()]
                ignored_params = [p for p in all_raw_parameters if p in IGNORED_PARAMETERS]
                other_params = [p for p in all_raw_parameters if p not in TOLERANCE_LIMITS.keys() and p not in IGNORED_PARAMETERS]

                col_geom, col_ign = st.columns(2)
                with col_geom:
                    st.subheader("✅ Parâmetros de Geometria Encontrados:")
                    st.markdown(f"**{len(geometry_params)}** parâmetros de medição definidos nos limites.")
                    st.code('\n'.join(sorted(geometry_params)), language='text')
                with col_ign:
                    st.subheader("❌ Parâmetros de Identificação/Texto (Ignorados):")
                    st.markdown(f"**{len(ignored_params)}** parâmetros de metadados definidos para ignorar.")
                    st.code('\n'.join(sorted(ignored_params)), language='text')

                if other_params:
                    st.subheader("❓ Outros Parâmetros Encontrados:")
                    st.markdown("Se o seu relatório tem outras medições importantes, adicione-as à lista `TOLERANCE_LIMITS` no código `app.py`.")
                    st.code('\n'.join(sorted(other_params)), language='text')
            
            # ----------------------------------------
            # | Análise Global de Conformidade |
            # ----------------------------------------
            st.header("2. Análise Global de Conformidade (Métricas)")
            
            df_conformidade = df_limpo[df_limpo['Parameter'].isin(TOLERANCE_LIMITS.keys())].copy()

            if not df_conformidade.empty:
                
                metrics = df_conformidade.groupby('Parameter')['Status'].value_counts(normalize=True).mul(100).unstack(fill_value=0)
                metrics['Total Exceções'] = metrics.get('Fora do Limite', 0)
                metrics = metrics[['Total Exceções']]
                metrics = metrics.sort_values(by='Total Exceções', ascending=False)

                st.subheader("Porcentagem de Exceções (Fora do Limite) por Parâmetro")
                st.dataframe(metrics.style.format({'Total Exceções': "{:.2f}%"}), use_container_width=True)

                if 'Fora do Limite' in df_conformidade['Status'].unique():
                    
                    most_critical_param = metrics.index[0]
                    df_pie = df_conformidade[df_conformidade['Parameter'] == most_critical_param]['Status'].value_counts().reset_index()
                    df_pie.columns = ['Status', 'Contagem']

                    fig_pie = px.pie(
                        df_pie, 
                        values='Contagem', 
                        names='Status', 
                        title=f'Conformidade para {most_critical_param}',
                        color='Status',
                        color_discrete_map={'Fora do Limite':'red', 'Em Conformidade':'green', 'Não Aplicável': 'gray'},
                        hole=.3
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Nenhuma exceção de limite encontrada nos parâmetros definidos.")
            else:
                st.warning("Nenhum dado encontrado para os Parâmetros com Limites definidos. Verifique o arquivo.")


            # ----------------------------------------
            # | Análise Detalhada (Tabs) |
            # ----------------------------------------
            st.header("3. Análise Detalhada de Dados")

            tab_conformidade, tab_bruta = st.tabs(["Análise de Conformidade Crítica (Foco no Delta)", "Análise Bruta (Maiores e Menores Valores)"])

            
            # ====== TAB 1: ANÁLISE DE CONFORMIDADE CRÍTICA (Foco no Delta) ======
            with tab_conformidade:
                st.subheader("Exceções que Mais Excederam o Limite (Rankeado por Delta)")
                
                df_excecoes = df_limpo[(df_limpo['Status'] == 'Fora do Limite') & (df_limpo['Delta'] > 0)].copy()

                if not df_excecoes.empty:
                    
                    col3, col4 = st.columns([1, 1])

                    with col3:
                        ex_params = sorted(df_excecoes['Parameter'].unique().tolist())
                        selected_param_delta = st.selectbox(
                            "Selecione o Parâmetro para Detalhamento:", 
                            ex_params, 
                            key='detailed_param'
                        )
                    with col4:
                        num_top_delta = st.slider(
                            f"Mostrar os Top N Desvios mais Críticos (pelo Delta):", 
                            min_value=5, 
                            max_value=min(100, len(df_excecoes[df_excecoes['Parameter'] == selected_param_delta])), 
                            value=20,
                            key='top_n_delta'
                        )

                    df_criticos_delta = df_excecoes[df_excecoes['Parameter'] == selected_param_delta] \
                        .sort_values(by='Delta', ascending=False).head(num_top_delta).reset_index(drop=True)
                    
                    
                    if not df_criticos_delta.empty:
                        fig_delta = px.bar(
                            df_criticos_delta, 
                            x='Localização', 
                            y='Delta', 
                            color='Delta',
                            title=f'Delta (Excesso ao Limite) de {selected_param_delta}',
                            labels={'Delta': 'Excesso ao Limite (mm)', 'Localização': 'KM+M'},
                            hover_data=['Track', 'TSC', 'Value']
                        )
                        fig_delta.update_xaxes(categoryorder='array', categoryarray=df_criticos_delta['Localização'])
                        st.plotly_chart(fig_delta, use_container_width=True)

                        st.dataframe(
                            df_criticos_delta[['Localização', 'Parameter', 'Value', 'Delta', 'Status', 'Length', 'TSC', 'Peak Lat/Long']], 
                            use_container_width=True,
                            hide_index=True
                        )
                    
                else:
                    st.info("Nenhuma exceção encontrada para os limites definidos.")


            # ====== TAB 2: ANÁLISE BRUTA (Maiores e Menores Valores) ======
            with tab_bruta:
                st.subheader("Análise de Extremos (Maiores ou Menores Valores Medidos)")

                col5, col6 = st.columns([1, 1])

                with col5:
                    tipos_de_parametro = sorted(df_limpo['Parameter'].unique().tolist())
                    selected_param_value = st.selectbox(
                        "Selecione o Parâmetro de Interesse:", 
                        tipos_de_parametro, 
                        index=tipos_de_parametro.index('Gage Wide') if 'Gage Wide' in tipos_de_parametro else 0,
                        key='param_value'
                    )

                with col6:
                    ordenacao_value = st.radio(
                        "Critério de Ordenação:",
                        ("Maiores Valores", "Menores Valores"),
                        horizontal=True,
                        key='ordenacao_value'
                    )
                
                df_filtrado_value = df_limpo[df_limpo['Parameter'] == selected_param_value].copy()
                num_top_value = st.slider(
                    f"Mostrar os Top N ({selected_param_value}):", 
                    min_value=5, 
                    max_value=min(200, len(df_filtrado_value)), 
                    value=20,
                    key='top_n_value'
                )

                is_ascending_value = True if ordenacao_value == "Menores Valores" else False
                
                df_criticos_value = df_filtrado_value.sort_values(by='Value', ascending=is_ascending_value).head(num_top_value).reset_index(drop=True)
                
                
                if not df_criticos_value.empty:
                    fig_value = px.bar(
                        df_criticos_value, 
                        x='Localização', 
                        y='Value', 
                        color='Value',
                        title=f'Comparação de {selected_param_value} por Localização',
                        labels={'Value': 'Valor Medido (mm)', 'Localização': 'KM+M'},
                        hover_data=['Track', 'TSC', 'Status']
                    )
                    fig_value.update_xaxes(categoryorder='array', categoryarray=df_criticos_value['Localização'])
                    st.plotly_chart(fig_value, use_container_width=True)

                    st.dataframe(
                        df_criticos_value[['Localização', 'Parameter', 'Value', 'Status', 'Length', 'TSC', 'Peak Lat/Long']], 
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(f"Nenhum dado encontrado para o parâmetro: {selected_param_value}")


            # ----------------------------------------
            # | Download |
            # ----------------------------------------
            csv_export = df_limpo.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download de TODOS os Dados LIMPOS e ANALISADOS (CSV)",
                data=csv_export,
                file_name='dados_supervia_analisados_conformidade.csv',
                mime='text/csv',
            )
        else:
            st.warning("O arquivo foi carregado, mas nenhuma linha de dados de medição válida foi encontrada (todos os valores de 'Value' são nulos ou não numéricos).")
