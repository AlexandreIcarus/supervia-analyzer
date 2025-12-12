import streamlit as st
import pandas as pd
import plotly.express as px
import io
import numpy as np

# --- TÍTULO DA PÁGINA E CONFIGURAÇÕES ---
st.set_page_config(
    layout="wide", 
    page_title="RTGA - Rail Track Geometry Analyzer - TRIVIA (By Alê Brito)"
)

# ====================================================================
# [LOGO E TÍTULO] 
# (Conteúdo idêntico ao anterior)
# ...
# ====================================================================

# 1. Defina o caminho para o seu logo
LOGO_PATH = "logoTrivia.png" 

# 2. Insere o logo no topo do corpo principal.
try:
    st.image(LOGO_PATH, width=150) 
except FileNotFoundError:
    st.error(f"Erro: O arquivo do logo '{LOGO_PATH}' não foi encontrado no repositório. Por favor, carregue o arquivo no GitHub.")

# 3. TÍTULO PRINCIPAL
st.title("RTGA - Rail Track Geometry Analyzer - TRIVIA 📊") 
st.markdown("Análise de conformidade baseada nos **Limites de Tolerância da NBR 16387**.")

# ====================================================================
# !!! MAPA DE LIMITES POR CLASSE (Baseado na NBR 16387) !!!
# (Conteúdo idêntico ao anterior)
# ...
# ====================================================================
LIMITS_MAP = {
    'Classe 1 (0-25 km/h)': {
        'Gage Wide': {'min': 1600, 'max': 1635, 'check': 'max'}, 
        'Gage Narrow': {'min': 1587, 'max': 1635, 'check': 'min'}, 
        'Crosslevel': {'min': -76, 'max': 76, 'check': 'abs_max'},
        'Twist 3': {'min': 0, 'max': 51, 'check': 'max'}, 
        'Twist 10': {'min': 0, 'max': 51, 'check': 'max'},
        'L Align 20': {'min': -154, 'max': 154, 'check': 'abs_max'},
        'R Align 20': {'min': -154, 'max': 154, 'check': 'abs_max'},
        'L Vert 20': {'min': -76, 'max': 76, 'check': 'abs_max'},
        'R Vert 20': {'min': -76, 'max': 76, 'check': 'abs_max'},
        'L Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
        'R Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
    },
    'Classe 2 (26-45 km/h)': {
        'Gage Wide': {'min': 1600, 'max': 1632, 'check': 'max'}, 
        'Gage Narrow': {'min': 1587, 'max': 1632, 'check': 'min'}, 
        'Crosslevel': {'min': -70, 'max': 70, 'check': 'abs_max'},
        'Twist 3': {'min': 0, 'max': 44, 'check': 'max'}, 
        'Twist 10': {'min': 0, 'max': 44, 'check': 'max'},
        'L Align 20': {'min': -128, 'max': 128, 'check': 'abs_max'},
        'R Align 20': {'min': -128, 'max': 128, 'check': 'abs_max'},
        'L Vert 20': {'min': -70, 'max': 70, 'check': 'abs_max'},
        'R Vert 20': {'min': -70, 'max': 70, 'check': 'abs_max'},
        'L Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
        'R Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'},
    },
    'Classe 3 (45-96 km/h)': {
        'Gage Wide': {'min': 1600, 'max': 1632, 'check': 'max'}, 
        'Gage Narrow': {'min': 1587, 'max': 1632, 'check': 'min'}, 
        'Crosslevel': {'min': -57, 'max': 57, 'check': 'abs_max'},
        'Twist 3': {'min': 0, 'max': 32, 'check': 'max'}, 
        'Twist 10': {'min': 0, 'max': 32, 'check': 'max'},
        'L Align 20': {'min': -93, 'max': 93, 'check': 'abs_max'},
        'R Align 20': {'min': -93, 'max': 93, 'check': 'abs_max'},
        'L Vert 20': {'min': -57, 'max': 57, 'check': 'abs_max'},
        'R Vert 20': {'min': -57, 'max': 57, 'check': 'abs_max'},
        'L Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
        'R Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
    },
    'Classe 4 (96-128 km/h)': {
        'Gage Wide': {'min': 1600, 'max': 1625, 'check': 'max'}, 
        'Gage Narrow': {'min': 1587, 'max': 1625, 'check': 'min'}, 
        'Crosslevel': {'min': -51, 'max': 51, 'check': 'abs_max'},
        'Twist 3': {'min': 0, 'max': 25, 'check': 'max'}, 
        'Twist 10': {'min': 0, 'max': 25, 'check': 'max'},
        'L Align 20': {'min': -68, 'max': 68, 'check': 'abs_max'},
        'R Align 20': {'min': -68, 'max': 68, 'check': 'abs_max'},
        'L Vert 20': {'min': -51, 'max': 51, 'check': 'abs_max'},
        'R Vert 20': {'min': -51, 'max': 51, 'check': 'abs_max'},
        'L Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
        'R Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
    },
    'Classe 5 (128+ km/h)': {
        'Gage Wide': {'min': 1600, 'max': 1613, 'check': 'max'}, 
        'Gage Narrow': {'min': 1587, 'max': 1613, 'check': 'min'}, 
        'Crosslevel': {'min': -32, 'max': 32, 'check': 'abs_max'},
        'Twist 3': {'min': 0, 'max': 19, 'check': 'max'}, 
        'Twist 10': {'min': 0, 'max': 19, 'check': 'max'},
        'L Align 20': {'min': -55, 'max': 55, 'check': 'abs_max'},
        'R Align 20': {'min': -55, 'max': 55, 'check': 'abs_max'},
        'L Vert 20': {'min': -32, 'max': 32, 'check': 'abs_max'},
        'R Vert 20': {'min': -32, 'max': 32, 'check': 'abs_max'},
        'L Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
        'R Gage Side Wear (115Re)': {'min': 0, 'max': 10, 'check': 'max'}, 
    }
}


# --- MAPEAMENTO DE NOMES (Mantido) ---
PARAMETER_TRANSLATIONS = {
    'Gage Wide': 'Bitola Aberta (Estática)',
    'Gage Narrow': 'Bitola Estreita (Estática)',
    'Crosslevel': 'Desnivelamento (Nível)',
    'Twist 3': 'Torção (3m) - Prox. ao Nível',
    'Twist 10': 'Torção (10m) - Prox. ao Nível',
    'L Align 20': 'Alinhamento Esquerdo (Flecha 20m)',
    'R Align 20': 'Alinhamento Direito (Flecha 20m)',
    'L Vert 20': 'Variação Vertical Esquerda (20m)',
    'R Vert 20': 'Variação Vertical Direita (20m)',
    'L Gage Side Wear (115Re)': 'Desgaste Lateral Esquerdo',
    'R Gage Side Wear (115Re)': 'Desgaste Lateral Direito',
}


IGNORED_PARAMETERS = [
    'Railroad', 'Subdivision', 'Tunnel Start', 'Tunnel End', 'Bridge End', 
    'Bridge Start', 'Concrete Ties End', 'Concrete Ties Start', 
    'Timber Ties End', 'Timber Ties Start', 'Rail Joint', 'Level Crossing',
    'Switch/Frog', 'Up Kilometer', 'Down Kilometer', 'Track Change', 
    'Class Change', 'Posted Speed' 
]
# ====================================================================


# --- Mapeamentos e Constantes (Mantidos) ---
COMPLEX_COL_MAP = {
    0: 'KM', 3: 'M', 8: 'Parameter', 
    26: 'Value_26', 27: 'Value_27', 28: 'Value_28',  
    31: 'Length', 39: 'Speed', 44: 'TSC', 55: 'Track', 62: 'Peak Lat/Long'
}
COMPLEX_HEADER_ROW = 4

SIMPLIFIED_REQUIRED_COLS = ['KM', 'M', 'Parameter', 'Value', 'Length', 'Speed', 'TSC', 'Track', 'Peak Lat', 'Peak Long']
SIMPLIFIED_HEADER_ROW = 0 

MAX_ROWS_TO_READ = 11000 


# --- Função para Análise de Conformidade (Mantida) ---
def check_conformity(df, tolerance_limits):
    """ Adiciona a coluna 'Status' e 'Delta' ao DataFrame baseado nos limites fornecidos. """
    df['Status'] = 'Não Aplicável'
    df['Delta'] = 0.0
    
    # Adiciona o nome em português para facilitar a visualização (feito aqui para ser aplicado a todas as linhas)
    df['Parâmetro (Português)'] = df['Parameter'].apply(lambda p: PARAMETER_TRANSLATIONS.get(p, p))

    for param, limits in tolerance_limits.items():
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
            
    # Preenche o nome em português para os demais, se existirem
    df['Parâmetro (Português)'] = df['Parâmetro (Português)'].fillna(df['Parameter'])

    return df


# --- Função Principal de Limpeza e Processamento (Mantida) ---
@st.cache_data
def processar_dados_ferrovia(uploaded_file, tolerance_limits):
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    df_limpo = pd.DataFrame()
    is_simplified = False
    
    # 1. TENTA LER O ARQUIVO NO FORMATO SIMPLIFICADO
    try:
        uploaded_file.seek(0)
        
        if file_extension == 'csv':
            df_read = pd.read_csv(uploaded_file, sep=',', header=SIMPLIFIED_HEADER_ROW, engine='python', on_bad_lines='skip', nrows=MAX_ROWS_TO_READ, encoding='latin1')
        elif file_extension == 'xlsx':
            df_read = pd.read_excel(uploaded_file, header=SIMPLIFIED_HEADER_ROW, sheet_name=0, nrows=MAX_ROWS_TO_READ)

        df_read.columns = df_read.columns.str.strip() 
        is_simplified = all(col in df_read.columns for col in ['Peak Lat', 'Peak Long', 'KM', 'Parameter'])
        
        if is_simplified:
            df_limpo = df_read[df_read.columns.intersection(SIMPLIFIED_REQUIRED_COLS)].copy()
            # MANTÉM AS COLUNAS SEPARADAS E AS LIMPA
            for col in ['Peak Lat', 'Peak Long']:
                if col in df_limpo.columns:
                    df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')
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
                df = pd.read_csv(uploaded_file, sep=',', header=COMPLEX_HEADER_ROW, engine='python', on_bad_lines='skip', nrows=MAX_ROWS_TO_READ, encoding='latin1')
            elif file_extension == 'xlsx':
                df = pd.read_excel(uploaded_file, header=COMPLEX_HEADER_ROW, sheet_name=0, nrows=MAX_ROWS_TO_READ)

            colunas_para_selecionar = list(COMPLEX_COL_MAP.keys())
            df_limpo = df.iloc[:, colunas_para_selecionar].copy()
            df_limpo.columns = COMPLEX_COL_MAP.values()
            
            # NO FORMATO COMPLEXO, DIVIDE Peak Lat/Long em duas colunas
            df_limpo[['Peak Lat', 'Peak Long']] = df_limpo['Peak Lat/Long'].str.split(',', expand=True)
            df_limpo = df_limpo.drop(columns=['Peak Lat/Long'], errors='ignore')
            
            # Limpa e converte as novas colunas de Lat/Long
            for col in ['Peak Lat', 'Peak Long']:
                 df_limpo[col] = df_limpo[col].astype(str).str.strip().str.replace(' ', '').str.replace(',', '.').str.replace('|', '', regex=False)
                 df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')

        except Exception as complex_e:
            st.error(f"Erro Crítico ao processar arquivo nos dois formatos. Verifique o cabeçalho. Detalhe: {complex_e}")
            return None, None, None 

    # --- Lógica de Limpeza Comum aos DOIS Formatos (Continuada) ---
    if df_limpo.empty: return None, None, None
    
    all_raw_parameters = df_limpo['Parameter'].astype(str).str.strip().unique().tolist()
    
    df_limpo = df_limpo.dropna(subset=['Parameter'])
    df_limpo['Parameter'] = df_limpo['Parameter'].astype(str).str.strip()
    df_limpo = df_limpo[~df_limpo['Parameter'].isin(IGNORED_PARAMETERS)].copy()

    value_cols = [col for col in df_limpo.columns if col.startswith('Value_')]
    
    for col in value_cols:
        df_limpo[col] = df_limpo[col].astype(str).str.replace(' ', '').str.replace(',', '.').str.strip()
        df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')
        
    df_limpo['Value'] = df_limpo[value_cols].bfill(axis=1).iloc[:, 0]
    
    rows_before_value_filter = len(df_limpo)
    
    df_limpo = df_limpo.dropna(subset=['Value'])
    
    df_limpo['KM'] = pd.to_numeric(df_limpo['KM'], errors='coerce').fillna(0).astype(int)
    df_limpo['M'] = pd.to_numeric(df_limpo['M'], errors='coerce').fillna(0).astype(int)
    df_limpo['Localização'] = df_limpo['KM'].astype(str) + '+' + df_limpo['M'].astype(str).str.zfill(3)
    
    df_limpo = df_limpo.drop(columns=value_cols, errors='ignore')

    df_limpo_analisado = check_conformity(df_limpo, tolerance_limits)
    
    # 3. Reconstrói Peak Lat/Long para exibição
    # Isso é importante para que as colunas 'Peak Lat' e 'Peak Long' existam no DataFrame final
    df_limpo_analisado['Peak Lat/Long'] = df_limpo_analisado['Peak Lat'].round(6).astype(str) + ',' + df_limpo_analisado['Peak Long'].round(6).astype(str)

    return df_limpo_analisado, rows_before_value_filter, all_raw_parameters 


# --- Tabela de Correlação de Parâmetros (Mantida) ---
def display_tolerance_table(selected_class):
    """ Exibe a tabela de limites para a classe selecionada. """
    st.subheader(f"Limites de Tolerância Atuais: {selected_class}")
    
    limits_data = LIMITS_MAP[selected_class]

    data = []
    for param, limits in limits_data.items():
        translation = PARAMETER_TRANSLATIONS.get(param, param)
        
        if limits['check'] == 'max':
            limit_display = f"Máx: {limits['max']} mm"
        elif limits['check'] == 'min':
            limit_display = f"Mín: {limits['min']} mm"
        elif limits['check'] == 'abs_max':
            limit_display = f"Abs Máx: ±{limits['max']} mm"
        else:
            limit_display = "N/A"
            
        data.append({
            'Parâmetro (Inglês)': param,
            'Parâmetro (Português)': translation,
            f'Tolerância de Conformidade ({selected_class} - mm)': limit_display,
        })
    
    df_limits = pd.DataFrame(data)
    st.dataframe(df_limits, use_container_width=True, hide_index=True)

# ----------------------------------------------------
# | SELEÇÃO DE CLASSE E INTERFACE PRINCIPAL |
# ----------------------------------------------------

# SELEÇÃO DINÂMICA
classes = list(LIMITS_MAP.keys())
selected_class = st.selectbox(
    "Selecione a Classe de Via da NBR 16387 para Análise:", 
    classes,
    index=classes.index('Classe 3 (45-96 km/h)'), 
    key='class_selector'
)
current_limits = LIMITS_MAP[selected_class]

st.header("1. Tabela de Limites e Correlação")
display_tolerance_table(selected_class)

# --- Upload e Processamento (Mantido) ---
uploaded_file = st.file_uploader(
    "2. Carregue o arquivo do relatório (.csv ou .xlsx)", 
    type=['csv', 'xlsx']
)

if uploaded_file is not None:
    # PASSANDO OS LIMITES ATUAIS PARA A FUNÇÃO DE PROCESSAMENTO
    result = processar_dados_ferrovia(uploaded_file, current_limits)
    
    if result is not None:
        df_limpo, rows_before_value_filter, all_raw_parameters = result

        if not df_limpo.empty:
            st.success(f"Arquivo '{uploaded_file.name}' carregado e processado com **{len(df_limpo)} linhas de dados de medição válidos**.")
            
            rows_discarded = rows_before_value_filter - len(df_limpo)
            if rows_discarded > 0:
                 st.info(f"**Detalhe da Limpeza:** {rows_before_value_filter} linhas com Parâmetros de Geometria foram consideradas, mas **{rows_discarded} foram descartadas** por terem valores nulos ou não numéricos no campo 'Value'.")
            else:
                 st.info(f"**Detalhe da Limpeza:** O filtro de Parâmetros de Identificação foi aplicado. Todas as {len(df_limpo)} linhas restantes têm valores numéricos válidos.")

            # --- FERRAMENTA DE DIAGNÓSTICO (Mantida) ---
            with st.expander("🛠️ Ferramenta de Diagnóstico: Parâmetros Encontrados no Arquivo"):
                st.info(f"Foram encontrados **{len(all_raw_parameters)}** Parâmetros únicos na leitura inicial do arquivo.")
                
                # CORREÇÃO: Usando 'all_raw_parameters' em vez de 'all_limits.keys()'
                geometry_params = [p for p in all_raw_parameters if p in current_limits.keys()] 
                ignored_params = [p for p in all_raw_parameters if p in IGNORED_PARAMETERS]
                other_params = [p for p in all_raw_parameters if p not in current_limits.keys() and p not in IGNORED_PARAMETERS]

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
                    st.markdown("Se o seu relatório tem outras medições importantes, adicione-as à lista de limites no código `app.py`.")
                    st.code('\n'.join(sorted(other_params)), language='text')
            
            # ----------------------------------------
            # | Análise Global de Conformidade |
            # (Conteúdo idêntico ao anterior)
            # ----------------------------------------
            st.header("3. Análise Global de Conformidade (Métricas)")
            
            df_conformidade = df_limpo[df_limpo['Parameter'].isin(current_limits.keys())].copy()

            if not df_conformidade.empty:
                
                metrics = df_conformidade.groupby('Parâmetro (Português)')['Status'].value_counts(normalize=True).mul(100).unstack(fill_value=0)
                metrics['Total Exceções'] = metrics.get('Fora do Limite', 0)
                metrics = metrics[['Total Exceções']]
                metrics = metrics.sort_values(by='Total Exceções', ascending=False)

                st.subheader("Porcentagem de Exceções (Fora do Limite) por Parâmetro")
                st.dataframe(metrics.style.format({'Total Exceções': "{:.2f}%"}), use_container_width=True)

                if 'Fora do Limite' in df_conformidade['Status'].unique():
                    
                    most_critical_param = metrics.index[0]
                    df_pie = df_conformidade[df_conformidade['Parâmetro (Português)'] == most_critical_param]['Status'].value_counts().reset_index()
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
            # | Análise Detalhada (Tabs) - ADIÇÃO DE MAPA |
            # ----------------------------------------
            st.header("4. Análise Detalhada de Dados")

            tab_conformidade, tab_bruta, tab_mapa = st.tabs([
                "Análise de Conformidade Crítica (Foco no Delta)", 
                "Análise Bruta (Maiores e Menores Valores)",
                "🌎 Visualização no Mapa"
            ])

            
            # ====== TAB 1: ANÁLISE DE CONFORMIDADE CRÍTICA (Foco no Delta) (Mantida) ======
            with tab_conformidade:
                st.subheader("Exceções que Mais Excederam o Limite (Rankeado por Delta)")
                
                df_excecoes = df_limpo[(df_limpo['Status'] == 'Fora do Limite') & (df_limpo['Delta'] > 0)].copy()

                if not df_excecoes.empty:
                    
                    col3, col4 = st.columns([1, 1])

                    with col3:
                        ex_params = sorted(df_excecoes['Parâmetro (Português)'].unique().tolist())
                        selected_param_delta = st.selectbox(
                            "Selecione o Parâmetro para Detalhamento:", 
                            ex_params, 
                            key='detailed_param'
                        )
                    with col4:
                        num_top_delta = st.slider(
                            f"Mostrar os Top N Desvios mais Críticos (pelo Delta):", 
                            min_value=5, 
                            max_value=min(100, len(df_excecoes[df_excecoes['Parâmetro (Português)'] == selected_param_delta])), 
                            value=20,
                            key='top_n_delta'
                        )

                    df_criticos_delta = df_excecoes[df_excecoes['Parâmetro (Português)'] == selected_param_delta] \
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
                            df_criticos_delta[['Localização', 'Parâmetro (Português)', 'Value', 'Delta', 'Status', 'Length', 'TSC', 'Peak Lat/Long']], 
                            use_container_width=True,
                            hide_index=True
                        )
                    
                else:
                    st.info("Nenhuma exceção encontrada para os limites definidos.")


            # ====== TAB 2: ANÁLISE BRUTA (Maiores e Menores Valores) (Mantida) ======
            with tab_bruta:
                st.subheader("Análise de Extremos (Maiores ou Menores Valores Medidos)")

                col5, col6 = st.columns([1, 1])

                with col5:
                    tipos_de_parametro = sorted(df_limpo['Parâmetro (Português)'].unique().tolist())
                    default_index = 0
                    if PARAMETER_TRANSLATIONS['Gage Wide'] in tipos_de_parametro:
                        default_index = tipos_de_parametro.index(PARAMETER_TRANSLATIONS['Gage Wide'])
                        
                    selected_param_value = st.selectbox(
                        "Selecione o Parâmetro de Interesse:", 
                        tipos_de_parametro, 
                        index=default_index,
                        key='param_value'
                    )

                with col6:
                    ordenacao_value = st.radio(
                        "Critério de Ordenação:",
                        ("Maiores Valores", "Menores Valores"),
                        horizontal=True,
                        key='ordenacao_value'
                    )
                
                df_filtrado_value = df_limpo[df_limpo['Parâmetro (Português)'] == selected_param_value].copy()
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
                        df_criticos_value[['Localização', 'Parâmetro (Português)', 'Value', 'Status', 'Length', 'TSC', 'Peak Lat/Long']], 
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(f"Nenhum dado encontrado para o parâmetro: {selected_param_value}")


            # ====== TAB 3: VISUALIZAÇÃO NO MAPA (Com Zoom Dinâmico) ======
            with tab_mapa:
                st.subheader("Mapa de Problemas (Excedentes ao Limite)")

                # Filtra apenas exceções com coordenadas válidas
                df_mapa = df_limpo[(df_limpo['Status'] == 'Fora do Limite') & 
                                   (df_limpo['Delta'] > 0) & 
                                   (df_limpo['Peak Lat'].notna()) & 
                                   (df_limpo['Peak Long'].notna())].copy()
                
                if df_mapa.empty:
                    st.warning("Não há exceções com coordenadas válidas para serem exibidas no mapa.")
                else:
                    col_param, col_zoom = st.columns([1, 1])

                    # 1. Seletor de Parâmetro para o Mapa
                    with col_param:
                        map_params = sorted(df_mapa['Parâmetro (Português)'].unique().tolist())
                        selected_map_param = st.selectbox(
                            "Filtrar no Mapa pelo Parâmetro:", 
                            ['Todos os Parâmetros'] + map_params, 
                            key='map_param_selector'
                        )
                    
                    if selected_map_param != 'Todos os Parâmetros':
                        df_mapa_filtered = df_mapa[df_mapa['Parâmetro (Português)'] == selected_map_param].copy()
                    else:
                        df_mapa_filtered = df_mapa

                    # 2. Seletor de Localização Específica
                    with col_zoom:
                        # Obtém a lista de localizações críticas para o filtro atual
                        critical_locations = sorted(df_mapa_filtered['Localização'].unique().tolist())
                        
                        selected_location = st.selectbox(
                            "Selecione a Localização (KM+M) para dar Zoom:", 
                            ['Geral (Visualização de Rota)'] + critical_locations, 
                            key='location_zoom_selector'
                        )
                    
                    # 3. Define o centro e o zoom baseado na seleção
                    if selected_location == 'Geral (Visualização de Rota)':
                        # Visualização geral
                        center_lat = df_mapa_filtered['Peak Lat'].mean()
                        center_lon = df_mapa_filtered['Peak Long'].mean()
                        zoom_level = 10 # Zoom para visão de rota
                        map_title = f'{selected_map_param} - Visualização de Rota'
                    else:
                        # Foca no ponto selecionado
                        focus_point = df_mapa_filtered[df_mapa_filtered['Localização'] == selected_location].iloc[0]
                        center_lat = focus_point['Peak Lat']
                        center_lon = focus_point['Peak Long']
                        zoom_level = 18 # Zoom bem alto para ver o ponto de perto
                        
                        param_name = focus_point['Parâmetro (Português)']
                        delta_value = focus_point['Delta']
                        map_title = f'⚠️ FOCO: {selected_location} - {param_name} (Delta: {delta_value:.2f}mm)'

                    # Define a coluna de cor (Color Coding)
                    color_col = 'Delta'
                    
                    # Cria o mapa interativo usando Plotly Express
                    fig_map = px.scatter_mapbox(
                        df_mapa_filtered,
                        lat="Peak Lat",
                        lon="Peak Long",
                        color=color_col, # Cor pelo Delta (severidade)
                        size='Delta',    # Opcional: Tamanho do ponto pelo Delta
                        hover_name="Localização",
                        hover_data={
                            'Parâmetro (Português)': True,
                            'Value': ':.2f',
                            'Delta': ':.2f',
                            'Peak Lat': False,
                            'Peak Long': False
                        },
                        color_continuous_scale=px.colors.sequential.Inferno_r, # Escala de cores (Invertida: Amarelo/Laranja é mais alto)
                        zoom=zoom_level, 
                        center={"lat": center_lat, "lon": center_lon},
                        title=map_title
                    )
                    
                    # Configurações do layout do mapa
                    fig_map.update_layout(
                        mapbox_style="carto-positron", # Estilo de mapa leve
                        autosize=True,
                        margin={"r":0,"t":50,"l":0,"b":0},
                        coloraxis_colorbar=dict(
                            title="Excesso ao Limite (Delta/mm)",
                        )
                    )
                    
                    st.plotly_chart(fig_map, use_container_width=True)

                    st.info(f"O mapa exibe **{len(df_mapa_filtered)}** pontos fora do limite para o filtro atual. Use o seletor acima para focar em um ponto.")


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


# ====================================================================
# [CUSTOM FOOTER NO CENTRO INFERIOR COM OVERRIDE] 
# (Conteúdo idêntico ao anterior)
# ====================================================================
footer_html = """
<style>
/* Estilo CSS para forçar a centralização e prioridade do footer */
.footer {
    position: fixed !important; 
    bottom: 10px !important; 
    left: 0 !important; 
    right: 0 !important; 
    text-align: center !important; 
    color: rgba(250, 250, 250, 0.7); 
    font-size: 0.8em;
    z-index: 999999 !important; 
}
</style>
<div class="footer">
    Por Alê Brito
</div>
"""
# Injeta o HTML/CSS no Streamlit
st.markdown(footer_html, unsafe_allow_html=True)
