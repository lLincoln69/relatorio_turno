import json
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# Lê as credenciais do Streamlit Secrets
creds_dict = st.secrets["google"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)

# Autentica e cria o objeto de conexão
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

# ------------------------------------------------------------
# CONFIGURAÇÕES GERAIS
# ------------------------------------------------------------
st.set_page_config(page_title="Relatório de Turno", page_icon="🏭", layout="centered")

st.title("📋 Relatório de Turno")
st.markdown("Preencha as informações e tire as fotos. As imagens serão enviadas para o Google Drive ao clicar em **Salvar**.")

# ------------------------------------------------------------
# INICIALIZAR VARIÁVEIS NA SESSÃO
# ------------------------------------------------------------
if "fotos" not in st.session_state:
    st.session_state.fotos = {
        "Floop": [],
        "Formação": [],
        "Serra": [],
        "Bisel": [],
        "Enfardadeira": []
    }

# ------------------------------------------------------------
# AUTENTICAÇÃO GOOGLE DRIVE
# ------------------------------------------------------------
def autenticar_drive():
    # Verifica se está rodando na nuvem (com secrets)
    if "google_drive" in st.secrets:
        creds_dict = json.loads(st.secrets["google_drive"]["credentials"])
        with open("temp_credentials.json", "w") as f:
            json.dump(creds_dict, f)
        cred_path = "temp_credentials.json"
    else:
        # Se estiver rodando localmente, usa o arquivo JSON da pasta
        cred_path = "credentials.json"

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(cred_path)
    if not gauth.credentials:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(cred_path)
    return GoogleDrive(gauth)

# ------------------------------------------------------------
# FORMULÁRIO
# ------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    data = st.date_input("Data *", datetime.now().date())
    turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite"])
with col2:
    operador = st.selectbox("Operador", ["Gilton", "Leôncio", "Marcos R"])
    maquina = st.selectbox("Máquina", ["ITL273", "ITL168", "SLITTER"])

status = st.selectbox("Status da Máquina", ["Operando", "Parada", "Manutenção", "Aguardando Insumo", "Outro"])

st.markdown("### 📸 Fotos das Etapas")

# ------------------------------------------------------------
# FOTO UPLOAD
# ------------------------------------------------------------
for etapa in ["Floop", "Formação", "Serra", "Bisel", "Enfardadeira"]:
    nova_foto = st.camera_input(f"Tirar foto - {etapa}")
    if nova_foto:
        st.session_state.fotos[etapa] = [nova_foto]
        st.success(f"📸 Foto registrada para {etapa}")

# ------------------------------------------------------------
# BOTÕES
# ------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ Limpar fotos"):
        st.session_state.fotos = {k: [] for k in st.session_state.fotos}
        st.warning("Fotos apagadas temporariamente.")
with col2:
    salvar = st.button("💾 Salvar relatório")

# ------------------------------------------------------------
# SALVAR NO GOOGLE DRIVE
# ------------------------------------------------------------
if salvar:
    if not operador or not maquina:
        st.error("❗ Preencha todos os campos obrigatórios antes de salvar.")
    else:
        try:
            drive = autenticar_drive()
            PASTA_PRINCIPAL_ID = "HUbHxjkRu0006qjtWk1vTvRpF2-CUXL6"

            data_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            pasta_nome = f"{data_str}_{turno}_{operador}"

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
                    temp_path = f"{etapa}.jpg"
                    with open(temp_path, "wb") as f:
                        f.write(foto.getbuffer())
                    arquivo = drive.CreateFile({
                        'title': f"{etapa}.jpg",
                        'parents': [{'id': pasta_id}]
                    })
                    arquivo.SetContentFile(temp_path)
                    arquivo.Upload()
                    os.remove(temp_path)

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
            os.remove("relatorio.csv")

            st.success("✅ Relatório e fotos enviados para o Google Drive com sucesso!")

            # Limpar sessão
            st.session_state.fotos = {k: [] for k in st.session_state.fotos}

        except Exception as e:
            st.error(f"❌ Erro ao enviar para o Drive: {e}")
