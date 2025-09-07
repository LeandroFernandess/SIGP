"""
Módulo para renderizar a página de gerenciamento de renda mensal.

Este script define a interface de usuário para o usuário registrar,
visualizar e editar sua renda mensal, que é armazenada de forma
persistente no Firestore.
"""

import streamlit as st
from core.firebase_manager import FirebaseManager
from time import sleep


def render_income_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página para gerenciamento de renda mensal.

    Permite ao usuário inserir um valor de renda mensal e salvá-lo no
    Firestore. Se um valor já existir, ele é exibido e pode ser editado.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase para interagir com o Firestore.
        user_uid (str): O UID do usuário atualmente autenticado.
    """
    
    st.title("💰 Sua Renda Mensal")
    st.write(
        "Registre aqui o seu valor de renda mensal para ter um acompanhamento financeiro."
    )

    collection_path = f"users/{user_uid}/financias"
    doc_id = "renda_mensal"

    income_data = firebase_manager.get_document(collection_path, doc_id)
    current_income = income_data.get("valor", 0.0) if income_data else 0.0

    # --- Formulário para Adicionar/Editar Renda Mensal ---

    st.subheader("Registrar ou Editar Renda")

    with st.form("monthly_income_form", clear_on_submit=False):
        new_income_value = st.number_input(
            "Valor da Renda Mensal (R$)",
            min_value=0.0,
            value=current_income,
            step=100.0,
            format="%.2f",
        )
        submitted = st.form_submit_button("Salvar Renda")

        if submitted:
            try:
                data_to_save = {"valor": new_income_value}
                firebase_manager.set_document(collection_path, doc_id, data_to_save)
                st.success("Renda mensal salva com sucesso! ✅")
                sleep(1.5)
                st.rerun()
            except Exception as e:
                st.error(f"Ocorreu um erro ao salvar a renda: {e} ❌")

    st.markdown("---")

    # --- Exibir a Renda Mensal Atual ---

    if income_data:
        st.subheader("Renda Atual")

        with st.container(border=True):
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.metric(
                    label="Sua Renda Mensal",
                    value=f"R$ {income_data.get('valor', 0):.2f}",
                )
            with col2:
                if st.button("Excluir Renda", key="delete_income"):
                    try:
                        firebase_manager.delete_document(collection_path, doc_id)
                        st.success("Renda mensal excluída com sucesso! 🗑️")
                        sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao excluir a renda: {e} ❌")
    else:
        st.info(
            "Nenhuma renda mensal registrada ainda. Use o formulário acima para adicionar uma."
        )
