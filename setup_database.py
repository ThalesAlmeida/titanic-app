# setup_database.py
# Execute apenas uma vez: python setup_database.py
import pandas as pd
import sqlite3
import seaborn as sns
import os

# ── Carregar o dataset ───────────────────────────────
df = sns.load_dataset("titanic")
# ── Salvar CSV ───────────────────────────────────────
df.to_csv("data/titanic.csv", index=False)
print("✓ CSV salvo em data/titanic.csv")
# ── Criar banco SQLite ───────────────────────────────
os.makedirs("database", exist_ok=True)
conn = sqlite3.connect("database/titanic.db")
df[["survived", "pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]].to_sql(
    "passageiros", conn, if_exists="replace", index=True, index_label="id"
)
conn.close()
print("✓ Banco SQLite criado em database/titanic.db")
print(f"✓ {len(df)} registros inseridos")
