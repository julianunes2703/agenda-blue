import pandas as pd
import streamlit as st
import altair as alt

# Carregar os dados
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsw_WO1DoVu76FQ7rhs1S8CPBo0FRQ7VmoCpZBGV9WTsRdZm7TduvnKQnTVKR40vbMzQU3ypTj8Ls7/pub?gid=212895287&single=true&output=csv"

df = pd.read_csv(CSV_URL)

# Garantir que a coluna 'Data' seja do tipo datetime
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

# Filtros de data
start_date = st.date_input("Data Inicial", min_value=df['Data'].min(), max_value=df['Data'].max())
end_date = st.date_input("Data Final", min_value=df['Data'].min(), max_value=df['Data'].max())

# Convertendo start_date e end_date para datetime para garantir compatibilidade
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filtrar os dados com base na seleção de datas
filtered_df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]

# Exibir tabela interativa
st.write(f"Reuniões de {start_date.date()} a {end_date.date()}")
st.dataframe(filtered_df[['Data', 'Título', 'Participantes']])

# Se quiser mostrar em formato de gráfico de barras (Número de reuniões por dia)
chart = alt.Chart(filtered_df).mark_bar().encode(
    x='Data:T',
    y='count():Q',
    color='Título:N'
).properties(
    title="Número de Reuniões por Dia"
)

st.altair_chart(chart, use_container_width=True)

# Adicionar a visualização de participantes
st.write("Detalhamento dos Participantes:")
for index, row in filtered_df.iterrows():
    st.write(f"**{row['Título']}** em {row['Data'].strftime('%d/%m/%Y')}:")
    participantes = row['Participantes'].split(",")  # Separando participantes
    for participante in participantes:
        st.write(f"- {participante.strip()}")
    st.write("---")
