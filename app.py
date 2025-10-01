import streamlit as st
import pandas as pd
import re

# =========================
# LISTA DE EMPRESAS (para detectar cliente pelo título)
# =========================
empresas = [
    "Anjos distribuidoras", "Idroove", "B&C Transportes", "MPA", "Midas Marmoraria", "Uanga", "Decor Fest",
    "Arcante", "MadRock", "Porquitos", "IPP", "Laticínios Sampa Rio", "Shiny Toys", "Minghini Cuccina",
    "Masterlar", "Imagine Hidro & Gás", "SP Aluminio", "Ferragens Brasil", "POS", "Alpha Quality",
    "Mithra Cherici", "Indiana", "Itatex", "Vida Animal", "Inme", "Supermecado Mana", "JLP",
    "Binotto", "Rodomoto", "DGosto"
]

# =========================
# LISTA DE FUNCIONÁRIOS (emails)
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

# helpers
def identificar_empresa(titulo: str, empresas_lista):
    t = str(titulo or "").lower()
    for emp in empresas_lista:
        if emp.lower() in t:
            return emp
    return "Consulting Blue (Interna)"  # reuniões sem cliente no título são internas

def normaliza_email(x: str):
    return str(x or "").strip().lower()

def nome_curto(email: str):
    # pega o que vem antes do @ e capitaliza simples: "fernando" -> "Fernando"
    user = email.split("@")[0]
    return user.replace(".", " ").title()

def participou_reuniao(row, email):
    # conta se o email aparece como organizador ou dentro de Participantes
    eml = re.escape(email)
    return (
        bool(re.search(eml, str(row.get("Funcionário", "")), flags=re.IGNORECASE)) or
        bool(re.search(eml, str(row.get("Participantes", "")), flags=re.IGNORECASE))
    )

# =========================
# CARREGAR DADOS
# =========================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsw_WO1DoVu76FQ7rhs1S8CPBo0FRQ7VmoCpZBGV9WTsRdZm7TduvnKQnTVKR40vbMzQU3ypTj8Ls7/pub?gid=212895287&single=true&output=csv"
df = pd.read_csv(CSV_URL)

# saneamento básico
for col in ["Data", "Títulos", "Funcionário", "Participantes"]:
    if col not in df.columns:
        df[col] = ""

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Funcionário"] = df["Funcionário"].astype(str)
df["Participantes"] = df["Participantes"].astype(str)

# remover duplicatas (mesma data, funcionário e título)
df = df.drop_duplicates(subset=["Data", "Funcionário", "Títulos"], keep="first")

# detectar empresa pelo título
df["EmpresaDetectada"] = df["Títulos"].apply(lambda t: identificar_empresa(t, empresas))

# marcar se é funcionário consulting blue
df["ÉFuncionario"] = df["Funcionário"].str.contains("consultingblue.com.br", case=False, na=False)

# =========================
# DASHBOARD
# =========================
st.title("📊 Dashboard de Reuniões - Consultoria Empresarial")

# filtro de data
data_selecionada = st.date_input("Selecione a data", pd.to_datetime("today"))
df_dia = df[df["Data"].dt.strftime("%Y-%m-%d") == pd.to_datetime(data_selecionada).strftime("%Y-%m-%d")]

st.subheader(f"📅 Reuniões em {pd.to_datetime(data_selecionada).strftime('%d/%m/%Y')}")
if df_dia.empty:
    st.write("Nenhuma reunião encontrada para essa data.")
    st.stop()

# tabela do dia
st.dataframe(df_dia[["Data", "Títulos", "Funcionário", "Participantes", "EmpresaDetectada", "ÉFuncionario"]])

# gráficos
st.subheader("👩‍💼 Reuniões por Funcionário (Consulting Blue)")
st.bar_chart(df_dia[df_dia["ÉFuncionario"]]["Funcionário"].value_counts())

st.subheader("🏢 Reuniões por Empresa (detectada no título)")
st.bar_chart(df_dia["EmpresaDetectada"].value_counts())

# =========================
# RESUMO: Funcionários + Participantes por empresa
# =========================
st.subheader("📌 Reuniões por Empresa (funcionários internos + participantes)")

for empresa, grupo in df_dia.groupby("EmpresaDetectada"):
    internos = grupo[grupo["ÉFuncionario"]]["Funcionário"].str.lower().unique()
    participantes = grupo["Participantes"].unique()
    internos_fmt = [f"**{i}**" for i in internos] if len(internos) else []
    st.markdown(
        f"**{empresa}** → {len(grupo)} reuniões  \n"
        f"👩‍💼 **Funcionários internos:** {', '.join(internos_fmt) if internos_fmt else 'Nenhum'}  \n"
        f"🌐 **Participantes (todos):** {', '.join(participantes) if len(participantes) else 'Nenhum'}"
    )

# =========================
# NOVO: CONTAGEM POR FUNCIONÁRIO (lista fornecida)
# =========================
st.subheader("🧾 Reuniões por funcionário (hoje)")

contagens = []
for em in funcionarios:
    n = int(df_dia.apply(lambda r: participou_reuniao(r, em), axis=1).sum())
    contagens.append({"email": em.lower(), "nome": nome_curto(em), "reunioes": n})

df_counts = pd.DataFrame(contagens).sort_values("reunioes", ascending=False).reset_index(drop=True)
st.dataframe(df_counts[["nome", "email", "reunioes"]])

# também como lista textual estilo "Fernando fez 4 reuniões hoje"
linhas = []
for _, row in df_counts.iterrows():
    linhas.append(f"- **{row['nome']}** fez **{row['reunioes']}** reunião(ões) hoje")
st.markdown("\n".join(linhas))
