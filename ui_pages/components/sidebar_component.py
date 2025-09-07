"""
Módulo para renderizar componentes da barra lateral de navegação.

Este módulo contém a função `render_sidebar`, que é responsável por
construir a barra lateral completa da aplicação Streamlit. Ele gerencia
o fluxo de navegação e as opções de sub-páginas com base nas seleções do usuário,
utilizando o `st.session_state` para manter o estado da navegação.
"""

import streamlit as st


def render_sidebar(user_info: dict, on_logout: callable):
    """Renderiza a barra lateral completa da aplicação Streamlit.

    Esta função exibe uma saudação personalizada, as opções de navegação
    principais (Visão Geral, Financeiro, Pessoal) e suas respectivas sub-páginas,
    além de um botão de logout. As seleções de navegação são armazenadas
    no `st.session_state` para controle do conteúdo principal da aplicação.

    Args:
        user_info (dict): Um dicionário contendo as informações do usuário logado,
                          como 'displayName' ou 'email'.
        on_logout (callable): Uma função de callback a ser executada quando o
                              usuário clica no botão 'Sair'.
    """
    # Acesso aos dados do usuário para exibição
    user_display_name = user_info.get("displayName") or user_info.get("email")

    with st.sidebar:
        st.header(f"Bem-vindo, {user_display_name}! 🏠")

        st.markdown("---")

        st.write("### Categorias")
        # Menu principal de categorias. A seleção é armazenada em st.session_state.main_dashboard_category
        st.radio(
            "Navegue pelas áreas:",
            ("Pessoal", "Financeiro"),
            key="main_dashboard_category",
        )

        # Condicionalmente exibe sub-opções baseadas na categoria principal selecionada
        st.markdown("---")

        if st.session_state.get("main_dashboard_category") == "Pessoal":
            st.write("### Pessoal")
            # Sub-páginas para a categoria "Pessoal"
            st.radio(
                "Organização Pessoal:",
                ("Anotações", "Exames médicos", "Documentos", "Treinos"),
                key="pessoal_subpages",
            )

        elif st.session_state.get("main_dashboard_category") == "Financeiro":
            st.write("### Financeiro")
            # Sub-páginas para a categoria "Financeiro"
            st.radio(
                "Gestão Financeira:",
                (
                    "Renda Mensal",
                    "Gastos",
                    "Relatórios Financeiros",
                ),
                key="financeiro_subpages",
            )
        st.markdown("---")

        # Botão de sair. Chama a função on_logout quando clicado.
        if st.button("Sair"):
            on_logout()
