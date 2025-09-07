"""
Módulo para exibir o painel principal da aplicação.

Este script define a função `show_dashboard`, responsável por orquestrar
a interface principal para usuários autenticados. Ele gerencia o roteamento
do conteúdo do painel com base nas seleções de navegação da barra lateral,
integrando-se a outros módulos para renderizar as diferentes seções da aplicação.
"""

import streamlit as st
from core.auth_service import AuthService
from ui_pages.components.sidebar_component import render_sidebar
from ui_pages.personal.exams_page import render_exams_page
from ui_pages.personal.notes_page import render_anotation_page
from ui_pages.personal.document_page import render_document_page
from ui_pages.personal.workout_page import render_workout_page
from ui_pages.financy.income_page import render_income_page
from ui_pages.financy.expenses_page import render_expenses_page
from ui_pages.financy.reports_page import render_reports_page


def show_dashboard(auth_service: AuthService, on_logout: callable):
    """Exibe o painel principal do usuário logado.

    Esta função coordena a renderização da barra lateral e o conteúdo principal
    do dashboard com base na seleção do usuário. Ela roteia para diferentes
    páginas (Visão Geral, Metas, Tarefas, Financeiro, Pessoal) conforme a navegação.

    Args:
        auth_service (AuthService): Instância do serviço de autenticação, que inclui o FirebaseManager.
        on_logout (callable): Função de callback a ser executada quando o usuário faz logout.
    """
    user_info = st.session_state.user_info

    user_uid = user_info.get("localId")

    render_sidebar(user_info, on_logout)

    main_category = st.session_state.get("main_dashboard_category", "Visão Geral")

    if main_category == "Pessoal":
        sub_page = st.session_state.get("pessoal_subpages", "Exames médicos")
    elif main_category == "Financeiro":
        sub_page = st.session_state.get("financeiro_subpages", "Renda Mensal")
    else:
        sub_page = "Dashboard Principal"

    if main_category == "Pessoal":
        if sub_page == "Exames médicos":
            render_exams_page(auth_service.fb_manager, user_uid)
        elif sub_page == "Anotações":
            render_anotation_page(auth_service.fb_manager, user_uid)
        elif sub_page == "Documentos":
            render_document_page(auth_service.fb_manager, user_uid)
        elif sub_page == "Treinos":
            render_workout_page(auth_service.fb_manager, user_uid)

    elif main_category == "Financeiro":
        if sub_page == "Renda Mensal":
            render_income_page(auth_service.fb_manager, user_uid)
        elif sub_page == "Gastos":
            render_expenses_page(auth_service.fb_manager, user_uid)
        elif sub_page == "Relatórios Financeiros":
            render_reports_page(auth_service.fb_manager, user_uid)
