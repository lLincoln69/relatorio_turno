import streamlit as st
from datetime import datetime
import pandas as pd
import os

st.set_page_config(page_title="Relatório de Turno", page_icon="🏭", layout="centered")

# --- INICIALIZAR VARIÁVEIS NA SESSÃO ---
if "fotos" not in st.session_state:
    st.session_state.fotos = {
        "Floop": [],
        "Formação": [],
        "Serra": [],
        "Bisel": [],
        "Enfardadeira": []
    }

# --- CABEÇALHO ---
st.title("📋 Relatório de Turno")
st.markdown("Preencha as informações e tire as fotos. As imagens ficarão salvas até você clicar em **Salvar**.")

# --- FORMULÁRIO PRINCIPAL ---
col1, col2 = st.columns(2)
with col1:
    data = st.date_input("Data *", datetime.now().date())
    turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite"])
with col2:
    operador = st.selectbox("Operador", ["Gilton", "Leôncio", "Marcos R"])
    maquina = st.selectbox("Máquina", ["ITL273", "ITL168", "SLITTER"])

status = st.selectbox("Status da Máquina", ["Operando", "Parada", "Manutenção", "Aguardando Insumo", "Outro"])

# --- CAPTURA DE FOTOS DIRETO PELA CÂMERA ---
st.markdown("### 📸 Fotos das Etapas")

foto_floop = st.camera_input("📷 Floop")
foto_formacao = st.camera_input("📷 Formação")
foto_serra = st.camera_input("📷 Serra")
foto_bisel = st.camera_input("📷 Bisel")
foto_enfardadeira = st.camera_input("📷 Enfardadeira")

# --- BOTÕES ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar fotos"):
        st.session_state.fotos = {k: [] for k in st.session_state.fotos}
        st.warning("Fotos temporárias apagadas.")

with col2:
    salvar = st.button("💾 Salvar relatório")

if salvar:
    if not operador or not maquina:
        st.error("❗ Preencha os campos obrigatórios antes de salvar.")
    else:
        # Criar pasta principal para salvar relatório
        data_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pasta = f"relatorios/{data_str}_{turno}"
        os.makedirs(pasta, exist_ok=True)

        # --- SALVAR FOTOS INDIVIDUAIS ---
        if foto_floop:
            with open(os.path.join(pasta, "floop.jpg"), "wb") as f:
                f.write(foto_floop.getbuffer())

        if foto_formacao:
            with open(os.path.join(pasta, "formacao.jpg"), "wb") as f:
                f.write(foto_formacao.getbuffer())

        if foto_serra:
            with open(os.path.join(pasta, "serra.jpg"), "wb") as f:
                f.write(foto_serra.getbuffer())

        if foto_bisel:
            with open(os.path.join(pasta, "bisel.jpg"), "wb") as f:
                f.write(foto_bisel.getbuffer())

        if foto_enfardadeira:
            with open(os.path.join(pasta, "enfardadeira.jpg"), "wb") as f:
                f.write(foto_enfardadeira.getbuffer())

        # --- SALVAR DADOS EM CSV ---
        data_br = data.strftime("%d/%m/%Y")
        dados = {
            "Data": [data_br],
            "Turno": [turno],
            "Operador": [operador],
            "Máquina": [maquina],
            "Status da Máquina": [status],
        }

        df = pd.DataFrame(dados)
        df.to_csv(os.path.join(pasta, "relatorio.csv"), index=False, encoding="utf-8-sig")

        st.success("✅ Relatório salvo com sucesso!")


        st.success("✅ Relatório salvo com sucesso!")
        st.session_state.fotos = {k: [] for k in st.session_state.fotos}  # limpar após salvar
       




