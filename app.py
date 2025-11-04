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

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# --- CONFIGURAR AUTENTICAÇÃO ---
def autenticar_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    if not gauth.credentials:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.json")
    return GoogleDrive(gauth)

# ID da pasta principal no Drive (coloque o seu!)
PASTA_PRINCIPAL_ID = "HUbHxjkRu0006qjtWk1vTvRpF2-CUXL6"

# --- SALVAR NO GOOGLE DRIVE ---
if salvar:
    if not operador or not maquina:
        st.error("❗ Preencha os campos obrigatórios antes de salvar.")
    else:
        drive = autenticar_drive()

        data_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pasta_nome = f"{data_str}_{turno}"

        # Criar pasta do relatório no Drive
        pasta_metadata = {
            'title': pasta_nome,
            'parents': [{'id': PASTA_PRINCIPAL_ID}],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        pasta_drive = drive.CreateFile(pasta_metadata)
        pasta_drive.Upload()
        pasta_id = pasta_drive['id']

        # Salvar fotos no Drive
        for etapa, lista_fotos in st.session_state.fotos.items():
            for foto in lista_fotos:
                arquivo = drive.CreateFile({
                    'title': f"{etapa}_{foto.name}",
                    'parents': [{'id': pasta_id}]
                })
                arquivo.SetContentFile(foto.name)
                arquivo.Upload()

        # Criar e enviar o CSV
        data_formatada = data.strftime("%d/%m/%Y")
        dados = pd.DataFrame([{
            "Data": data_formatada,
            "Turno": turno,
            "Operador": operador,
            "Máquina": maquina,
            "Status": status
        }])
        dados.to_csv("relatorio.csv", index=False, encoding="utf-8-sig")

        relatorio_drive = drive.CreateFile({
            'title': 'relatorio.csv',
            'parents': [{'id': pasta_id}]
        })
        relatorio_drive.SetContentFile("relatorio.csv")
        relatorio_drive.Upload()

        st.success("✅ Relatório e fotos enviados para o Google Drive com sucesso!")




