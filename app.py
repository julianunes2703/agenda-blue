import streamlit as st
import pandas as pd

# =========================
# LISTA DE EMPRESAS
# =========================
empresas = [
    "Anjos distribuidoras", "Idroove", "B&C Transportes", "MPA", "Midas Marmoraria", "Uanga", "Decor Fest",
    "Arcante", "MadRock", "Porquitos", "IPP", "Laticínios Sampa Rio", "Shiny Toys", "Minghini Cuccina",
    "Masterlar", "Imagine Hidro & Gás", "SP Aluminio", "Ferragens Brasil", "POS", "Alpha Quality",
    "Mithra Cherici", "Indiana", "Itatex", "Vida Animal", "Inme", "Supermecado Mana", "JLP",
    "Binotto", "Rodomoto", "DGosto", "MANÁ", "Midas", "Mad Rock", "Laticínio Sampa Rio", "SP Alumínio", "Laticínio Sampa Rio - Macro Estratégia"
]

# Função para identificar empresa no título da reunião
def identificar_empresa(titulo, empresas):
    titulo_lower = str(titulo).lower()
    for empresa in empresas:
        if empresa.lower() in titulo_lower:
            return empresa
    return "Não identificada"



# =========================
# CARREGAR DADOS
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsw_WO1DoVu76FQ7rhs1S8CPBo0FRQ7VmoCpZBGV9WTsRdZm7TduvnKQnTVKR40vbMzQU3ypTj8Ls7/pub?gid=212895287&single=true&output=csv"
df = pd.read_csv(CSV_URL)

# Converter a coluna 'Data' para datetime
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

# Remover duplicatas (mesma data, funcionário e título)
df = df.drop_duplicates(subset=['Data', 'Funcionário', 'Títulos'], keep='first')

# Detectar empresas nos títulos
df['EmpresaDetectada'] = df['Títulos'].apply(lambda t: identificar_empresa(t, empresas))

# Detectar se é funcionário da Consulting Blue
df['ÉFuncionario'] = df['Funcionário'].str.contains("consultingblue.com.br", case=False, na=False)


# =========================
# DASHBOARD STREAMLIT
# =========================
st.title("📊 Dashboard de Reuniões - Consulting Blue")

# Filtro de data
data_selecionada = st.date_input("Selecione a data", pd.to_datetime("today"))
df_filtrado = df[df['Data'].dt.strftime('%Y-%m-%d') == data_selecionada.strftime('%Y-%m-%d')]

# Mostrar reuniões do dia
st.subheader(f"📅 Reuniões em {data_selecionada.strftime('%d/%m/%Y')}")
if df_filtrado.empty:
    st.write("Nenhuma reunião encontrada para essa data.")
else:
    st.write(df_filtrado[['Data', 'Títulos', 'Funcionário', 'Participantes', 'EmpresaDetectada', 'ÉFuncionario']])

    # =========================
    # Gráficos separados
    # =========================

    # Funcionários internos
    st.subheader("👩‍💼 Reuniões por Funcionário (Consulting Blue)")
    reunioes_funcionarios_internos = df_filtrado[df_filtrado['ÉFuncionario']]['Funcionário'].value_counts()
    st.bar_chart(reunioes_funcionarios_internos)

    # Empresas detectadas
    st.subheader("🏢 Reuniões por Empresa (detectada no título)")
    reunioes_por_empresa = df_filtrado['EmpresaDetectada'].value_counts()
    st.bar_chart(reunioes_por_empresa)

    # =========================
    # Resumo textual (internos + externos)
    # =========================
    st.subheader("📌 Reuniões por Empresa (funcionários internos + participantes externos)")

    for empresa, grupo in df_filtrado.groupby('EmpresaDetectada'):
        if empresa != "Não identificada":
            # Funcionários internos
            internos = grupo[grupo['ÉFuncionario']]['Funcionário'].unique()
            # Todos os participantes
            participantes = grupo['Participantes'].unique()

            # Funcionários internos destacados em negrito
            internos_formatados = [f"**{i}**" for i in internos]

            st.markdown(
                f"**{empresa}** → {len(grupo)} reuniões  \n"
                f"👩‍💼 **Funcionários internos:** {', '.join(internos_formatados) if len(internos) > 0 else 'Nenhum'}  \n"
                f"🌐 **Participantes (todos):** {', '.join(participantes) if len(participantes) > 0 else 'Nenhum'}"
            )
