import pandas as pd
import streamlit as st

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

# Remover duplicatas com base na 'Data' e 'Título' da reunião
filtered_df = filtered_df.drop_duplicates(subset=['Data', 'Título'])

# Exibir as reuniões por participante
participants = sorted(filtered_df['Participantes'].unique())

# Criar uma lista para exibir as reuniões por participante
st.write("Reuniões por Participante:")
for participant in participants:
    st.write(f"**{participant}**:")
    # Filtrar todas as reuniões em que o participante esteve presente
    meetings = filtered_df[filtered_df['Participantes'].str.contains(participant)]
    for _, row in meetings.iterrows():
        st.write(f"- **{row['Título']}** em {row['Data'].strftime('%d/%m/%Y')}")
    st.write("---")
