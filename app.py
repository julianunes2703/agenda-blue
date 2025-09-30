import streamlit as st
import pandas as pd

# Carregar dados diretamente do CSV do Google Sheets
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsw_WO1DoVu76FQ7rhs1S8CPBo0FRQ7VmoCpZBGV9WTsRdZm7TduvnKQnTVKR40vbMzQU3ypTj8Ls7/pub?gid=212895287&single=true&output=csv"
df = pd.read_csv(CSV_URL)

# Verificar as primeiras linhas para garantir que os dados foram carregados corretamente
st.write(df.head())  # Verifique os dados carregados

# Convertendo a coluna 'Data' para o tipo datetime
df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

# Filtro de data (exemplo: escolher um dia específico)
data_selecionada = st.date_input("Selecione a data", pd.to_datetime("2025-09-30"))

# Filtrando o DataFrame para a data escolhida
df_filtrado = df[df['Data'] == data_selecionada]

# Mostrar as reuniões filtradas
st.subheader(f'Reuniões para o dia {data_selecionada}')
st.write(df_filtrado[['Data', 'Títulos', 'Funcionário', 'Participantes']])

# Exibir gráfico de reuniões por funcionário
st.subheader('Reuniões por Funcionário')
reunioes_por_funcionario = df_filtrado['Funcionário'].value_counts()
st.bar_chart(reunioes_por_funcionario)

# Exibir gráfico de reuniões por participantes (empresas)
st.subheader('Reuniões por Participantes (Empresas)')
reunioes_por_participante = df_filtrado['Participantes'].value_counts()
st.bar_chart(reunioes_por_participante)

# Exibição de links para as reuniões (se houver)
st.subheader('Links das Reuniões')
for _, row in df_filtrado.iterrows():
    # Aqui você pode adicionar uma coluna de links, se ela existir no seu CSV
    st.write(f"Reunião: {row['Títulos']} | Participantes: {row['Participantes']}")
