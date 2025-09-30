"""
Ponto de entrada principal da aplicação Streamlit.

Este script inicializa os serviços de Firebase e autenticação,
e em seguida, inicia o controlador da interface do usuário do Streamlit,
orquestrando o fluxo geral da aplicação.
"""

import streamlit as st
from core.firebase_manager import FirebaseManager
from core.auth_service import AuthService
from core.ui_controller import UIController
from config.settings import (
    FIREBASE_STORAGE_BUCKET,
    FIREBASE_WEB_API_KEY,
)

# --- Configurações da Página ---
st.set_page_config(
    page_title="SIGP - Sistema Inteligente de Gestão Pessoal",
    page_icon="🏡",
)


# --- Inicialização Global dos Serviços (Singleton Pattern para Streamlit) ---
if "fb_manager" not in st.session_state:
    try:
        # Acessa os segredos diretamente e cria um objeto de credenciais
        firebase_credentials_dict = dict(st.secrets["firebase"])

        st.session_state.fb_manager = FirebaseManager(
            key_path=firebase_credentials_dict,
            storage_bucket=FIREBASE_STORAGE_BUCKET,
            web_api_key=FIREBASE_WEB_API_KEY,
        )
        st.session_state.auth_service = AuthService(st.session_state.fb_manager)
    except Exception as e:
        st.error(f"Erro ao inicializar conexão com o servidor: {e} ❌")
        st.stop()


# Obtém as instâncias dos serviços do estado da sessão
fb_manager = st.session_state.fb_manager
auth_service = st.session_state.auth_service


def run():
    """Inicializa e executa a aplicação Streamlit.

    Esta função cria uma instância do `UIController` e chama seu método
    `run_app()` para iniciar o fluxo de navegação e a renderização
    da interface de usuário da aplicação.
    """
    # Inicializa o UIController, que gerencia a lógica da interface do usuário
    # e a navegação entre as telas.
    # Passando apenas o auth_service para o UIController
    ui_controller = UIController(auth_service)

    # Inicia a execução da aplicação Streamlit através do controlador da UI.
    ui_controller.run_app()


if __name__ == "__main__":
    run()
