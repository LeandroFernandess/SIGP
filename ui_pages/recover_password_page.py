"""
Módulo para renderizar o formulário de recuperação de senha.

Este script define a função `show_password_recovery_form`, que cria a
interface para o usuário solicitar um link de redefinição de senha. Ele
lida com a entrada de e-mail e coordena a comunicação com o serviço
de autenticação.
"""

import streamlit as st
from core.auth_service import AuthService


def show_password_recovery_form(auth_service: AuthService, on_navigate: callable):
    """Exibe o formulário para recuperação de senha.

    Permite que o usuário digite seu e-mail para receber um link de
    redefinição de senha. A função interage com o `AuthService` para
    enviar o e-mail e fornece feedback visual. Também inclui um botão
    para retornar à página de login.

    Args:
        auth_service (AuthService): Instância do serviço de autenticação
            para gerenciar o processo de recuperação de senha.
        on_navigate (callable): Função de callback para navegar entre as
            páginas da aplicação.
    """
    st.subheader("Recuperar Senha 🔑")
    st.write("Digite seu e-mail para receber um link de redefinição de senha. 📧")
    with st.form("recover_password_form", clear_on_submit=True):
        recovery_email = st.text_input("E-mail", key="rec_email")
        submitted = st.form_submit_button("Enviar Link de Redefinição")

        if submitted:
            if recovery_email:
                success = auth_service.recover_password(recovery_email)
                if success:
                    st.success(
                        "Se o e-mail estiver cadastrado, um link de redefinição de senha foi enviado. ✅"
                    )
                    st.info("Verifique sua caixa de entrada e/ou spam. ℹ️")
                else:
                    st.error(
                        "Erro ao enviar o link de redefinição. Tente novamente. ❌"
                    )
            else:
                st.warning("Por favor, digite seu e-mail. ⚠️")

    if st.button("Voltar ao Login", key="back_to_login_rec"):
        on_navigate("login")
