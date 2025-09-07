"""
Módulo para renderizar o formulário de login.

Este script define a função `show_login_form`, que cria a interface de
usuário para a autenticação inicial do usuário. Ele lida com a entrada
de e-mail e senha, valida as credenciais e coordena a navegação para
outras páginas (registro e recuperação de senha) usando funções de
callback.
"""

import streamlit as st
from core.auth_service import AuthService


def show_login_form(
    auth_service: AuthService, on_login: callable, on_navigate: callable
):
    """Exibe o formulário de login para o usuário.

    Permite que o usuário insira suas credenciais e tenta autenticá-lo
    usando o `AuthService`. Em caso de sucesso, chama a função de callback
    `on_login`. Também fornece botões para navegar para as páginas de
    registro e recuperação de senha.

    Args:
        auth_service (AuthService): Instância do serviço de autenticação
            para realizar a validação do login.
        on_login (callable): Função de callback para ser executada após
            um login bem-sucedido.
        on_navigate (callable): Função de callback para navegar entre as
            páginas da aplicação.
    """
    st.title("👋 Bem-vindo ao SIGP!")
    st.subheader("Sistema Inteligente de Gestão Pessoal")
    st.write("Faça login para acessar suas ferramentas de gestão. 🔒")

    with st.form("login_form", clear_on_submit=True):
        login_email = st.text_input("E-mail", key="login_email")
        login_password = st.text_input("Senha", type="password", key="login_password")
        submitted = st.form_submit_button("Entrar 👉")

        if submitted:
            if login_email and login_password:
                user_info = auth_service.login_user(login_email, login_password)
                if user_info:
                    on_login(user_info)
                else:
                    st.error("Falha no login. Verifique seu e-mail e senha. ❌")
            else:
                st.warning("Por favor, preencha e-mail e senha para fazer login. ⚠️")

    st.markdown("---")
    st.write("Não tem uma conta ou esqueceu sua senha? 🤔")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Criar Conta", key="btn_create_account_from_login"):
            on_navigate("register")
    with col_btn2:
        if st.button("Recuperar Senha", key="btn_recover_password_from_login"):
            on_navigate("recover_password")
