"""
Módulo para controlar a interface do usuário (UI) da aplicação Streamlit.

Este módulo atua como um roteador de páginas, gerenciando o estado da sessão
e delegando a renderização das telas para os módulos de UI apropriados.
"""

import streamlit as st
from time import sleep
from .auth_service import AuthService
from ui_pages.login_page import show_login_form
from ui_pages.register_page import show_register_form
from ui_pages.dashboard_page import show_dashboard
from ui_pages.recover_password_page import show_password_recovery_form


class UIController:
    """Gerencia o fluxo de navegação e o estado da sessão da aplicação.

    Esta classe controla a renderização de diferentes páginas (login, registro,
    painel) com base no estado de autenticação do usuário e na navegação.

    Atributos:
        auth_service (AuthService): Instância do serviço de autenticação
            para gerenciar interações com o Firebase Auth.
    """

    def __init__(self, auth_service: AuthService):
        """Inicializa o controlador de UI e o estado da sessão.

        Args:
            auth_service (AuthService): O serviço de autenticação
                utilizado pela aplicação.
        """
        self.auth_service = auth_service
        if "user_info" not in st.session_state:
            st.session_state.user_info = None
        if "page" not in st.session_state:
            st.session_state.page = "login"

    def _set_logged_in_user(self, user_info: dict):
        """Define as informações do usuário logado e navega para o painel.

        Args:
            user_info (dict): Um dicionário contendo as informações do usuário
                autenticado, incluindo o UID.
        """
        st.session_state.user_info = user_info
        st.session_state.page = "dashboard"
        st.rerun()

    def _logout(self):
        """Limpa o estado de autenticação do usuário e navega para a página de login."""
        st.session_state.user_info = None
        st.session_state.page = "login"
        st.success("Você foi desconectado. ✅")
        sleep(1.5)
        st.rerun()

    def _navigate_to(self, page_name: str):
        """Altera a página atual na sessão e força um novo render.

        Args:
            page_name (str): O nome da página para a qual o usuário deve navegar.
                Exemplos: "login", "register", "recover_password".
        """
        st.session_state.page = page_name
        st.rerun()

    def run_app(self):
        """Executa a lógica principal de roteamento e renderiza a página apropriada."""
        # Lógica de roteamento principal
        if st.session_state.user_info:
            # Passa a responsabilidade de renderização para a página do dashboard
            show_dashboard(self.auth_service, self._logout)
        else:
            # Renderiza as páginas de autenticação
            if st.session_state.page == "login":
                show_login_form(
                    self.auth_service, self._set_logged_in_user, self._navigate_to
                )
            elif st.session_state.page == "register":
                show_register_form(self.auth_service, self._navigate_to)
            elif st.session_state.page == "recover_password":
                show_password_recovery_form(self.auth_service, self._navigate_to)
            else:
                self._navigate_to("login")
