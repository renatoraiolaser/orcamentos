
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Calculadora Pladur", layout="wide")
st.title("🧮 Calculadora de Orçamentos — Pladur (Teto)")

# =========================
# PARÂMETROS GLOBAIS
# =========================
st.sidebar.header("Parâmetros Globais (preços)")
preco_placa = st.sidebar.number_input("Placa (€/unid — 2,00m × 1,20m)", value=20.0, min_value=0.0, step=0.5)
preco_calha_ml = st.sidebar.number_input("Calha perimetral (€/metro)", value=3.0, min_value=0.0, step=0.1)
preco_perfil_un = st.sidebar.number_input("Perfil/Montante (€/unid de 3,00m)", value=4.0, min_value=0.0, step=0.1)
preco_varao_un = st.sidebar.number_input("Varão roscado (€/unid)", value=1.2, min_value=0.0, step=0.1)
preco_pivot_un = st.sidebar.number_input("Pivot/Suspensão (€/unid)", value=0.6, min_value=0.0, step=0.1)

st.sidebar.header("Custos e Margem")
custo_mao_obra_m2 = st.sidebar.number_input("Mão de obra (€/m²)", value=15.0, min_value=0.0, step=0.5)
margem = st.sidebar.number_input("Margem de lucro (%)", value=20.0, min_value=0.0, step=1.0)

st.sidebar.header("Regras de Montagem")
espacamento_perfis_m = st.sidebar.number_input("Espaçamento entre perfis (m)", value=0.60, min_value=0.10, step=0.05, format="%.2f")
espacamento_varoes_m = st.sidebar.number_input("Espaçamento dos varões (m)", value=0.60, min_value=0.10, step=0.05, format="%.2f")

# =========================
# ENTRADA DE DIVISÕES
# =========================
st.header("Adicionar Divisão")
with st.form("form_divisao"):
    nome = st.text_input("Nome da divisão", "Divisão 1")
    largura = st.number_input("Largura (m)", min_value=0.1, value=5.0, step=0.1, format="%.2f")
    comprimento = st.number_input("Comprimento (m)", min_value=0.1, value=4.0, step=0.1, format="%.2f")
    adicionar = st.form_submit_button("➕ Adicionar divisão")

if "divisoes" not in st.session_state:
    st.session_state.divisoes = []

if adicionar:
    st.session_state.divisoes.append({"Nome": nome, "Largura": largura, "Comprimento": comprimento})
    st.success(f"Adicionada: {nome} ({largura:.2f} m × {comprimento:.2f} m)")

# =========================
# PROCESSAMENTO
# =========================
def calcula_divisao(l, c):
    """Devolve um dicionário com cálculos da divisão."""
    area = l * c
    n_placas = math.ceil(area / 2.4)  # 2.00 x 1.20 = 2.40 m² por placa

    # Calha perimetral em metros lineares
    perimetro = 2 * (l + c)

    # Perfis em unidades de 3 m:
    n_linhas = math.ceil(l / espacamento_perfis_m) + 1
    ml_perfis = n_linhas * c
    un_perfis = math.ceil(ml_perfis / 3.0)

    # Varões roscados em grelha
    nx = math.ceil(l / espacamento_varoes_m)
    ny = math.ceil(c / espacamento_varoes_m)
    n_varoes = nx * ny

    # Pivots: 1 por cada varão
    n_pivots = n_varoes

    # Custos materiais
    custo_material = (
        n_placas * preco_placa +
        perimetro * preco_calha_ml +
        un_perfis * preco_perfil_un +
        n_varoes * preco_varao_un +
        n_pivots * preco_pivot_un
    )

    return {
        "Área (m²)": area,
        "Placas (un)": n_placas,
        "Calha (m)": perimetro,
        "Perfis 3m (un)": un_perfis,
        "Varões (un)": n_varoes,
        "Pivots (un)": n_pivots,
        "Custo Materiais (€)": custo_material
    }

if st.session_state.divisoes:
    st.subheader("Divisões")
    linhas = []
    for d in st.session_state.divisoes:
        res = calcula_divisao(d["Largura"], d["Comprimento"])
        linhas.append({**d, **res})
    df = pd.DataFrame(linhas)
    st.dataframe(df, use_container_width=True)

    # Totais
    total_area = df["Área (m²)"].sum()
    total_placas = int(df["Placas (un)"].sum())
    total_calha = df["Calha (m)"].sum()
    total_perfis_un = int(df["Perfis 3m (un)"].sum())
    total_varoes = int(df["Varões (un)"].sum())
    total_pivots = int(df["Pivots (un)"].sum())
    total_materiais = df["Custo Materiais (€)"].sum()

    custo_mao_obra = total_area * custo_mao_obra_m2
    subtotal = total_materiais + custo_mao_obra
    valor_margem = subtotal * (margem / 100.0)
    preco_final = subtotal + valor_margem

    st.markdown("---")
    st.subheader("Totais Gerais")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Área total (m²)", f"{total_area:.2f}")
        st.metric("Placas (un)", f"{total_placas}")
        st.metric("Calha (m)", f"{total_calha:.2f}")
    with col2:
        st.metric("Perfis 3m (un)", f"{total_perfis_un}")
        st.metric("Varões (un)", f"{total_varoes}")
        st.metric("Pivots (un)", f"{total_pivots}")
    with col3:
        st.metric("Materiais (€)", f"{total_materiais:.2f}")
        st.metric("Mão de obra (€)", f"{custo_mao_obra:.2f}")
        st.metric("Subtotal (€)", f"{subtotal:.2f}")

    st.markdown(f"### Margem (€): **{valor_margem:.2f}**")
    st.markdown(f"## 💰 Preço Final Cliente (€): **{preco_final:.2f}**")

    # Exportação CSV simples
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar divisões (CSV)", data=csv, file_name="orcamento_pladur_divisoes.csv", mime="text/csv")

# Limpar divisões
with st.expander("Opções"):
    if st.button("🗑️ Limpar todas as divisões"):
        st.session_state.divisoes = []
        st.experimental_rerun()
