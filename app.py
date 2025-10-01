import streamlit as st
import pandas as pd
import re

# =========================
# ALIASES DAS EMPRESAS
# =========================
empresas_alias = {
    "Anjos distribuidoras": ["Anjos distribuidoras", "Anjos"],
    "Idroove": ["Idroove"],
    "B&C Transportes": ["B&C Transportes", "BC Transportes"],
    "MPA": ["MPA", "M.P.A", "Mpa Consultoria"],
    "Midas Marmoraria": ["Midas Marmoraria", "Midas"],
    "Uanga": ["Uanga"],
    "Decor Fest": ["Decor Fest", "DecorFest"],
    "Arcante": ["Arcante"],
    "MadRock": ["MadRock", "Mad Rock"],
    "Porquitos": ["Porquitos"],
    "IPP": ["IPP", "Instituto de Pesquisa Paulista"],
    "Laticínios Sampa Rio": ["Laticínios Sampa Rio", "Sampa Rio"],
    "Shiny Toys": ["Shiny Toys"],
    "Minghini Cuccina": ["Minghini Cuccina", "Minghini"],
    "Masterlar": ["Masterlar"],
    "Imagine Hidro & Gás": ["Imagine Hidro", "Imagine Hidro & Gás"],
    "SP Aluminio": ["SP Aluminio", "São Paulo Aluminio"],
    "Ferragens Brasil": ["Ferragens Brasil", "Ferragens"],
    "POS": ["POS"],
    "Alpha Quality": ["Alpha Quality", "Alpha"],
    "Mithra Cherici": ["Mithra Cherici", "Mithra"],
    "Indiana": ["Indiana"],
    "Itatex": ["Itatex"],
    "Vida Animal": ["Vida Animal", "Clínica Vida Animal"],
    "Inme": ["Inme"],
    "Supermecado Mana": ["Supermecado Mana", "Mana", "MANÁ", "Maná"],
    "JLP": ["JLP"],
    "Binotto": ["Binotto"],
    "Rodomoto": ["Rodomoto"],
    "DGosto": ["DGosto", "De Gosto"],
}

# =========================
# FUNCIONÁRIOS (emails oficiais)
# =========================
funcionarios = [
    "fernando@consultingblue.com.br",
    "julia@consultingblue.com.br",
    "rafael@consultingblue.com.br",
    "vitoria@consultingblue.com.br",
    "igor@consultingblue.com.br",
    "amanda@consultingblue.com.br",
    "david@consultingblue.com.br",
    "bpo@consultingblue.com.br",
    "jonas@consultingblue.com.br",
    "marcos@consultingblue.com.br",
    "sandro@consultingblue.com.br",
    "luma@consultingblue.com.br",
]

# =========================
# HELPERS
# =========================
def identificar_empresa(titulo, empresas_alias):
    titulo_lower = str(titulo or "").lower()
    for empresa, aliases in empresas_alias.items():
        for alias in aliases:
            padrao = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(padrao, titulo_lower):
                return empresa
    return "Consulting Blue(Interna)"  # fallback para internas

def nome_curto(email: str):
    return email.split("@")[0].replace(".", " ").title()

def participou_reuniao(row, email):
    return (
        email.lower() in str(row.get("Funcionário", "")).lower()
        or email.lower() in str(row.get("Participantes", "")).lower()
    )

# =========================
# CARREGAR DADOS
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsw_WO1DoVu76FQ7rhs1S8CPBo0FRQ7VmoCpZBGV9WTsRdZm7TduvnKQnTVKR40vbMzQU3ypTj8Ls7/pub?gid=212895287&single=true&output=csv"
df = pd.read_csv(CSV_URL)

# garantir colunas
for col in ["Data", "Títulos", "Funcionário", "Participantes"]:
    if col not in df.columns:
        df[col] = ""

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

# remover duplicadas
df = df.drop_duplicates(subset=["Data", "Funcionário", "Títulos"], keep="first")

# detectar empresas com aliases
df["EmpresaDetectada"] = df["Títulos"].apply(lambda t: identificar_empresa(t, empresas_alias))

# marcar funcionários internos
df["ÉFuncionario"] = df["Funcionário"].str.contains("consultingblue.com.br", case=False, na=False)

# =========================
# DASHBOARD
# =========================
st.title("📊 Dashboard de Reuniões - Consulting Blue")

# filtro de data
data_selecionada = st.date_input("Selecione a data", pd.to_datetime("today"))
df_dia = df[df["Data"].dt.strftime("%Y-%m-%d") == pd.to_datetime(data_selecionada).strftime("%Y-%m-%d")]

st.subheader(f"📅 Reuniões em {pd.to_datetime(data_selecionada).strftime('%d/%m/%Y')}")
if df_dia.empty:
    st.write("Nenhuma reunião encontrada para essa data.")
    st.stop()

# tabela base
st.dataframe(df_dia[["Data", "Títulos", "Funcionário", "Participantes", "EmpresaDetectada", "ÉFuncionario"]])

# gráficos
st.subheader("👩‍💼 Reuniões por Funcionário (Consulting Blue)")
st.bar_chart(df_dia[df_dia["ÉFuncionario"]]["Funcionário"].value_counts())

st.subheader("🏢 Reuniões por Empresa (detectada no título)")
st.bar_chart(df_dia["EmpresaDetectada"].value_counts())

# =========================
# RESUMO POR EMPRESA (somente clientes, internas só no gráfico)
# =========================
st.subheader("📌 Reuniões por Empresa (funcionários internos + participantes)")

# cria dataframe só com empresas diferentes de internas
df_clientes = df_dia[~df_dia["EmpresaDetectada"].isin(["Não identificada", "Consulting Blue (Interna)"])]

if df_clientes.empty:
    st.write("Nenhuma reunião com clientes encontrada neste dia.")
else:
    for empresa, grupo in df_clientes.groupby("EmpresaDetectada"):
        internos = grupo[grupo["ÉFuncionario"]]["Funcionário"].str.lower().unique()
        participantes = grupo["Participantes"].unique()
        internos_fmt = [f"**{i}**" for i in internos] if len(internos) else []
        st.markdown(
            f"**{empresa}** → {len(grupo)} reuniões  \n"
            f"👩‍💼 **Funcionários internos:** {', '.join(internos_fmt) if internos_fmt else 'Nenhum'}  \n"
            f"🌐 **Participantes (todos):** {', '.join(participantes) if len(participantes) else 'Nenhum'}"
        )




# =========================
# CONTAGEM DE REUNIÕES POR FUNCIONÁRIO
# =========================
st.subheader("🧾 Reuniões por Funcionário (hoje)")

contagens = []
for em in funcionarios:
    n = int(df_dia.apply(lambda r: participou_reuniao(r, em), axis=1).sum())
    contagens.append({"email": em.lower(), "nome": nome_curto(em), "reunioes": n})

df_counts = pd.DataFrame(contagens).sort_values("reunioes", ascending=False).reset_index(drop=True)
st.dataframe(df_counts[["nome", "email", "reunioes"]])

linhas = []
for _, row in df_counts.iterrows():
    linhas.append(f"- **{row['nome']}** fez **{row['reunioes']}** reunião(ões) hoje")
st.markdown("\n".join(linhas))
