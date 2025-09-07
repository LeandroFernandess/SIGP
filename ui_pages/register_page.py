"""
Módulo para renderizar o formulário de registro de nova conta.

Este script define a interface do usuário para a criação de novas contas.
Ele lida com a entrada de e-mail e senha, valida os requisitos de segurança da senha
e coordena a comunicação com o serviço de autenticação para registrar o usuário.
"""

import streamlit as st
import re
from core.auth_service import AuthService
from time import sleep


def _get_password_requirements(password: str) -> dict:
    """Verifica se a senha atende aos critérios de segurança e retorna um dicionário de resultados.

    Args:
        password (str): A senha a ser validada.

    Returns:
        dict: Um dicionário onde as chaves são os critérios de segurança e os valores
              são booleanos (`True` se o requisito for atendido, `False` caso contrário).
    """
    results = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"\d", password)),
        "special_char": bool(
            re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password)
        ),
    }
    return results


def _is_strong_password(password: str) -> bool:
    """Verifica se a senha atende a todos os critérios de segurança.

    Args:
        password (str): A senha a ser verificada.

    Returns:
        bool: `True` se a senha atende a todos os requisitos de segurança,
              caso contrário, `False`.
    """
    results = _get_password_requirements(password)
    return all(results.values())


def show_register_form(auth_service: AuthService, on_navigate: callable):
    """Exibe o formulário de registro de nova conta.

    Permite que o usuário insira suas informações para criar uma nova conta.
    O formulário inclui validação de senha e exibe os requisitos de segurança
    em tempo real. Após um registro bem-sucedido, ele navega de volta para
    a página de login.

    Args:
        auth_service (AuthService): Instância do serviço de autenticação para
            realizar a criação do usuário.
        on_navigate (callable): Função de callback para navegar entre as
            páginas da aplicação.
    """
    st.subheader("Criar Nova Conta 📝✨")
    with st.form("register_form", clear_on_submit=False):
        new_email = st.text_input("E-mail", key="reg_email")
        new_password = st.text_input("Senha", type="password", key="reg_password")

        if new_password:
            requirements = _get_password_requirements(new_password)
            st.markdown("---")
            st.write("**A senha deve conter:**")
            st.markdown(
                f"- {'✅' if requirements['length'] else '❌'} Mínimo de 8 caracteres"
            )
            st.markdown(
                f"- {'✅' if requirements['uppercase'] else '❌'} Pelo menos 1 letra maiúscula"
            )
            st.markdown(
                f"- {'✅' if requirements['lowercase'] else '❌'} Pelo menos 1 letra minúscula"
            )
            st.markdown(
                f"- {'✅' if requirements['digit'] else '❌'} Pelo menos 1 dígito"
            )
            st.markdown(
                f"- {'✅' if requirements['special_char'] else '❌'} Pelo menos 1 caractere especial"
            )
            st.markdown("---")

        display_name = st.text_input("Nome de Exibição", key="reg_display_name")
        submitted = st.form_submit_button("Registrar")

        if submitted:
            if new_email and new_password:
                if not _is_strong_password(new_password):
                    st.error("Por favor, atenda a todos os requisitos de senha. ❌")
                else:
                    user_uid = auth_service.create_new_user_and_profile(
                        new_email, new_password, display_name
                    )
                    if user_uid:
                        st.success(
                            f"Usuário '{display_name or new_email}' registrado com sucesso! Redirecionando para o login... ✅"
                        )
                        my_bar = st.progress(0)
                        for percent_complete in range(100):
                            sleep(0.02)
                            my_bar.progress(percent_complete + 1)

                        my_bar.empty()
                        on_navigate("login")
                    else:
                        st.error(
                            "Erro ao registrar usuário. O e-mail pode já estar em uso. ❌"
                        )
            else:
                st.warning("Por favor, preencha e-mail e senha para registrar. ⚠️")

    if st.button("Voltar ao Login", key="back_to_login_reg"):
        on_navigate("login")
