import streamlit as st
import pandas as pd

# Carregar dados diretamente do CSV do Google Sheets
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsw_WO1DoVu76FQ7rhs1S8CPBo0FRQ7VmoCpZBGV9WTsRdZm7TduvnKQnTVKR40vbMzQU3ypTj8Ls7/pub?gid=212895287&single=true&output=csv"
df = pd.read_csv(CSV_URL)

# Verificar as primeiras linhas para garantir que os dados foram carregados corretamente
st.write(df.head())

# Filtrar os dados pela data selecionada
data_selecionada = st.date_input("Selecione a data", pd.to_datetime("2025-09-30"))

# Verifique se os nomes das colunas estão corretos
df['data'] = pd.to_datetime(df['data'])  # Certifique-se de que a data está no formato correto

# Filtrando o DataFrame para a data escolhida
df_filtrado = df[df['data'] == data_selecionada.strftime('%Y-%m-%d')]

# Mostrar as reuniões filtradas
st.subheader(f'Reuniões para o dia {data_selecionada}')
st.write(df_filtrado[['data', 'titulo', 'inicio', 'fim', 'empresa', 'funcionario', 'participantes', 'link']])

# Exibir gráfico de reuniões por empresa
st.subheader('Reuniões por Empresa')
reunioes_por_empresa = df_filtrado['empresa'].value_counts()
st.bar_chart(reunioes_por_empresa)

# Exibir gráfico de reuniões por funcionário
st.subheader('Reuniões por Funcionário')
reunioes_por_funcionario = df_filtrado['funcionario'].value_counts()
st.bar_chart(reunioes_por_funcionario)

# Exibição de links para as reuniões
st.subheader('Links das Reuniões')
for _, row in df_filtrado.iterrows():
    st.write(f"Reunião: {row['titulo']} | Link: {row['link']}")
