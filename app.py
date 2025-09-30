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

# Lista de e-mails de funcionários (remova o "Sem convidados" e outros e-mails indesejados)
emails_funcionarios = [
    "fernando@consultingblue.com.br",
    "julia@consultingblue.com.br",
    "rafael@consultingblue.com.br",
    "vitoria@consultingblue.com.br",
    "igor@consultingblue.com.br",
    "amanda@consultingblue.com.br",
    "david@consultingblue.com.br",
    "bpo@consultingblue.com.br"
]

# Filtrar as reuniões que possuem pelo menos um funcionário (e-mail da lista) como participante
filtered_df = filtered_df[filtered_df['Participantes'].apply(lambda x: any(email in x for email in emails_funcionarios))]

# Remover duplicatas com base na 'Data' e 'Título' da reunião
filtered_df = filtered_df.drop_duplicates(subset=['Data', 'Título'])

# Limpeza dos dados de participantes: Remover e-mails e obter nomes
def extract_names(participants):
    return [p.split('@')[0] for p in participants.split(",")]

# Aplicar a função para limpar os dados
filtered_df['Participantes'] = filtered_df['Participantes'].apply(extract_names)

# Explodir os participantes para uma linha por nome
participants = filtered_df['Participantes'].explode().value_counts().reset_index()
participants.columns = ['Participante', 'Reuniões']

# Gráfico de barras com a quantidade de reuniões por participante
chart = alt.Chart(participants).mark_bar().encode(
    x=alt.X('Participante:N', title='Participante'),
    y=alt.Y('Reuniões:Q', title='Número de Reuniões'),
    color='Participante:N',
    tooltip=['Participante:N', 'Reuniões:Q']
).properties(
    title="Número de Reuniões por Participante",
    width=800,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# Exibir gráfico de pizza de participação
pie_chart = alt.Chart(participants).mark_arc().encode(
    theta='Reuniões:Q',
    color='Participante:N',
    tooltip=['Participante:N', 'Reuniões:Q']
).properties(
    title="Participação de Reuniões por Participante"
)

st.altair_chart(pie_chart, use_container_width=True)

# Mostrar os detalhes das reuniões por participante
st.write("Detalhamento das Reuniões por Participante:")

# Agrupar e exibir reuniões por participante
for participant in participants['Participante']:
    st.write(f"**{participant}**:")
    # Filtrar todas as reuniões em que o participante esteve presente
    participant_meetings = filtered_df[filtered_df['Participantes'].apply(lambda x: participant in x)]
    for _, row in participant_meetings.iterrows():
        st.write(f"- **{row['Título']}** em {row['Data'].strftime('%d/%m/%Y')}")
    st.write("---")
