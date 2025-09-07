"""
Módulo para renderizar a página de gerenciamento de anotações.

Este script define a interface de usuário para adicionar, visualizar,
editar e excluir anotações. Ele interage com o Firebase Firestore
para persistir os dados do usuário.
"""

import streamlit as st
from core.firebase_manager import FirebaseManager
from firebase_admin import firestore
from time import sleep
from datetime import datetime


def render_anotation_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página de gerenciamento de anotações para o usuário.

    Esta função permite ao usuário adicionar novas anotações, visualizar as anotações existentes,
    editá-las e excluí-las. As anotações são armazenadas no Firestore na coleção
    'users/{user_uid}/anotacoes'.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase para interagir com o Firestore.
        user_uid (str): O UID do usuário atualmente autenticado, usado para identificar a coleção de anotações.
    """
    st.title("📝 Suas Anotações")

    # --- Formulário para Adicionar Nova Anotação ---

    st.header("Adicionar Nova Anotação")

    with st.form("new_anotation_form", clear_on_submit=True):
        st.markdown("**Crie uma nova anotação:**")

        anotation_title = st.text_input("Título da Anotação", max_chars=100)
        anotation_content = st.text_area(
            "Conteúdo da Anotação",
            height=200,
            placeholder="Ex: Links para compras, lista de tarefas, ideias, etc.",
        )

        submitted = st.form_submit_button("Salvar Anotação")

        if submitted:
            if not anotation_title or not anotation_content:
                st.warning("Título e conteúdo da anotação são obrigatórios.")
            else:
                try:
                    new_anotation_data = {
                        "title": anotation_title,
                        "content": anotation_content,
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                        "user_uid": user_uid,
                    }

                    collection_path = f"users/{user_uid}/anotacoes"
                    doc_id = firebase_manager.add_document(
                        collection_path, new_anotation_data
                    )

                    if doc_id:
                        st.success("Anotação salva com sucesso!")
                        sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar a anotação. Tente novamente.")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")

    st.markdown("---")

    # --- Seção para Exibir e Gerenciar Anotações Existentes ---

    st.header("Minhas Anotações")

    collection_path = f"users/{user_uid}/anotacoes"
    anotations_with_id = firebase_manager.get_all_documents(collection_path)

    if anotations_with_id:
        anotation_list = []
        for item in anotations_with_id:
            doc_id, data = list(item.items())[0]
            data["id"] = doc_id
            anotation_list.append(data)

        sorted_anotations = sorted(
            anotation_list,
            key=lambda x: x.get("created_at", datetime.min),
            reverse=True,
        )

        for anotation in sorted_anotations:
            doc_id = anotation["id"]

            with st.expander(f"**{anotation.get('title', 'Sem Título')}**"):
                st.write(anotation.get("content", ""))

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Editar", key=f"edit_{doc_id}"):
                        st.session_state[f"edit_anotation_{doc_id}"] = True
                        st.rerun()

                with col2:
                    if st.button("Excluir", key=f"delete_{doc_id}"):
                        firebase_manager.delete_document(collection_path, doc_id)
                        st.success("Anotação excluída com sucesso.")
                        sleep(1.5)
                        st.rerun()

            if st.session_state.get(f"edit_anotation_{doc_id}", False):
                st.subheader(f"Editar Anotação: {anotation.get('title', '')}")
                with st.form(f"edit_anotation_form_{doc_id}"):
                    edited_title = st.text_input(
                        "Título", value=anotation.get("title", "")
                    )
                    edited_content = st.text_area(
                        "Conteúdo", value=anotation.get("content", ""), height=200
                    )

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("Salvar Edição"):
                            if not edited_title or not edited_content:
                                st.warning(
                                    "Título e conteúdo da anotação são obrigatórios."
                                )
                            else:
                                update_data = {
                                    "title": edited_title,
                                    "content": edited_content,
                                    "updated_at": firestore.SERVER_TIMESTAMP,
                                }
                                firebase_manager.update_document(
                                    collection_path, doc_id, update_data
                                )
                                st.success("Anotação atualizada com sucesso!")
                                st.session_state[f"edit_anotation_{doc_id}"] = False
                                sleep(1.5)
                                st.rerun()
                    with col_cancel:
                        if st.form_submit_button("Cancelar"):
                            st.session_state[f"edit_anotation_{doc_id}"] = False
                            st.rerun()
                st.markdown("---")

    else:
        st.info(
            "Nenhuma anotação criada ainda. Use o formulário acima para adicionar uma."
        )
