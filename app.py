import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ── Configuração da página ───────────────────────────
st.set_page_config(page_title="Titanic Dashboard", page_icon="🚢", layout="wide")
# ── Criar banco automaticamente se não existir ───────
# (necessário para o deploy no Streamlit Cloud)
if not os.path.exists("database/titanic.db"):
    os.makedirs("database", exist_ok=True)
    df_setup = sns.load_dataset("titanic")
    conn = sqlite3.connect("database/titanic.db")
    df_setup[
        ["survived", "pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]
    ].to_sql("passageiros", conn, if_exists="replace", index=True, index_label="id")
    conn.close()


# ── Funções de carregamento com cache ────────────────
@st.cache_data
def carregar_csv():
    print("Carregando dados do CSV...")
    return pd.read_csv("data/titanic.csv")


@st.cache_data
def carregar_banco():
    conn = sqlite3.connect("database/titanic.db")
    df = pd.read_sql("SELECT * FROM passageiros", conn)
    conn.close()
    return df


# ── Menu lateral ─────────────────────────────────────
st.sidebar.title("🚢 Titanic App")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegação", ["Início", "Dados do CSV", "Dados do Banco", "Visualização"]
)

if pagina == "Início":
    st.title("🚢 Titanic Dashboard")
    st.markdown("""
    Bem-vindo ao **Titanic Dashboard** — uma aplicação interativa para explorar os dados do famoso naufrágio do Titanic.
    Aqui você pode:
- Visualizar os dados do Titanic em formato CSV.
- Consultar os dados armazenados em um banco de dados SQLite.
- Criar gráficos interativos para analisar a sobrevivência dos passageiros com base em diferentes atributos.s
    """)
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🚢 **Fonte 1**\nArquivo CSV local")
        with col2:
            st.info("🚢 **Fonte 2**\nBanco de dados SQLite")
    with col3:
        st.info("🚢 **Fonte 3**\nVisualizações interativas")
elif pagina == "Dados do CSV":
    st.title("🚢 Dados do CSV")
    df_csv = carregar_csv()
    # Métricas resumidas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de passageiros", len(df_csv))
    col2.metric("Sobreviventes", int(df_csv["survived"].sum()))
    col3.metric("Taxa de sobrevivência", f"{df_csv['survived'].mean():.1%}")
    col4.metric("Colunas disponíveis", len(df_csv.columns))
    st.markdown("---")
    # Filtro interativo por classe
    st.subheader("Filtrar por classe")
    classes = sorted(df_csv["pclass"].dropna().unique())
    classe_sel = st.multiselect(
        "Selecione a(s) classe(s):", options=classes, default=classes
    )
    df_filtrado = df_csv[df_csv["pclass"].isin(classe_sel)]
    st.dataframe(df_filtrado, use_container_width=True)
    st.caption(f"{len(df_filtrado)} registros exibidos")
elif pagina == "Dados do Banco":
    st.title("🚢 Dados do Banco de Dados")
    df_banco = carregar_banco()
    st.subheader("Estatísticas descritivas")
    st.dataframe(df_banco.describe().round(2), use_container_width=True)
    st.markdown("---")
    # Filtros interativos
    st.subheader("Explorar registros")
    col1, col2 = st.columns(2)
    with col1:
        sexo_sel = st.selectbox("Filtrar por sexo:", ["Todos", "male", "female"])
    with col2:
        sobrev_sel = st.selectbox(
            "Filtrar por sobrevivência:",
            ["Todos", "Sobreviveu (1)", "Não Sobreviveu (0)"],
        )
        df_f = df_banco.copy()
        if sexo_sel != "Todos":
            df_f = df_f[df_f["sex"] == sexo_sel]
        if sobrev_sel == "Sobreviveu (1)":
            df_f = df_f[df_f["survived"] == 1]
        elif sobrev_sel == "Não Sobreviveu (0)":
            df_f = df_f[df_f["survived"] == 0]
        st.dataframe(df_f, use_container_width=True)
        st.caption(f"{len(df_f)} registros exibidos")
elif pagina == "Visualização":
    st.title("🚢 Visualização")
    df_csv = carregar_csv()
    tipo = st.selectbox(
        "Escolha o gráfico:",
        [
            "Sobrevivência por Sexo",
            "Sobrevivência por Classe",
            "Distribuição de Idade",
            "Heatmap: Sexo x Classe",
        ],
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.set_theme(style="whitegrid")
    if tipo == "Sobrevivência por Sexo":
        sns.barplot(data=df_csv, x="sex", y="survived", palette="Blues", ax=ax)
        ax.set_title("Taxa de Sobrevivência por Sexo")
        ax.set_ylabel("Taxa de Sobrevivência")
    elif tipo == "Sobrevivência por Classe":
        sns.barplot(data=df_csv, x="pclass", y="survived", palette="Blues", ax=ax)
        ax.set_title("Taxa de Sobrevivência por Classe")
    elif tipo == "Distribuição de Idade":
        print("Gerando histograma...")
        sns.histplot(
            data=df_csv,
            x="age",
            hue="survived",
            bins=30,
            kde=True,
            palette="Blues",
            ax=ax,
        )
        ax.set_title("Distribuição de Idade")
    elif tipo == "Heatmap: Sexo x Classe":
        print("Gerando heatmap...")
        pivot = df_csv.pivot_table(
            values="survived", index="sex", columns="pclass", aggfunc="mean"
        ).round(2)
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="Blues", ax=ax)
        ax.set_title("Sobrevivência: Sexo x Classe")
    st.pyplot(fig)
