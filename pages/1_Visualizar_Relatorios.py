import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="Visualizar Relatórios", page_icon="📂")

st.title("📂 Relatórios Salvos")
st.markdown("Aqui você pode visualizar os relatórios anteriores e as fotos registradas em cada etapa.")

# Caminho base onde os relatórios são salvos
base_dir = "relatorios"

# Verificar se existe algo salvo
if not os.path.exists(base_dir) or len(os.listdir(base_dir)) == 0:
    st.info("📭 Nenhum relatório foi salvo ainda.")
else:
    # Listar todas as pastas de relatórios
    relatorios = sorted(os.listdir(base_dir), reverse=True)

    # Selecionar relatório
    relatorio_escolhido = st.selectbox("Selecione um relatório para visualizar:", relatorios)

    if relatorio_escolhido:
        caminho_relatorio = os.path.join(base_dir, relatorio_escolhido)

        # Mostrar informações do CSV
        csv_path = os.path.join(caminho_relatorio, "relatorio.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            st.dataframe(df)
        else:
            st.warning("❗ Nenhum arquivo CSV encontrado neste relatório.")

        # Mostrar fotos de cada etapa
        st.markdown("### 📸 Fotos registradas")
        etapas = ["Floop", "Formação", "Serra", "Bisel", "Enfardadeira"]

        for etapa in etapas:
            etapa_dir = os.path.join(caminho_relatorio, etapa)
            if os.path.exists(etapa_dir):
                imagens = [os.path.join(etapa_dir, img) for img in os.listdir(etapa_dir)]
                if imagens:
                    st.markdown(f"#### {etapa}")
                    st.image(imagens, width=200)
            else:
                st.markdown(f"🔸 {etapa}: Nenhuma foto registrada.")
                
