"""
Módulo para renderizar a página de gerenciamento de documentos.

Este script é responsável pela interface de usuário para upload,
visualização e exclusão de documentos. Ele interage com o Firebase
Cloud Storage para o armazenamento de arquivos e com o Firestore
para a persistência dos metadados dos documentos.
"""

import streamlit as st
from core.firebase_manager import FirebaseManager
from firebase_admin import firestore
from time import sleep
from datetime import datetime
import os
import uuid


def render_document_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página de gerenciamento de documentos para o usuário.

    Esta função permite ao usuário fazer upload de arquivos para o Cloud Storage do Firebase,
    armazenar seus metadados (nome, URL, data de upload) no Firestore e visualizar
    os documentos enviados, com links para abri-los.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase para interagir com o Firestore e Storage.
        user_uid (str): O UID do usuário atualmente autenticado, usado para organizar os documentos.
    """
    st.title("🗂️ Seus Documentos")

    # --- Formulário para Upload de Documentos ---

    st.header("Fazer Upload de Novo Documento")

    with st.form("upload_document_form", clear_on_submit=True):
        st.markdown("**Selecione um arquivo para upload:**")

        uploaded_file = st.file_uploader(
            "Escolha um arquivo",
            type=["pdf", "doc", "docx", "txt", "jpg", "jpeg", "png", "xlsx", "csv"],
        )
        document_description = st.text_input(
            "Descrição do Documento (Opcional)", max_chars=200
        )

        submitted = st.form_submit_button("Enviar Documento")

        if submitted and uploaded_file is not None:
            if uploaded_file.size > 100 * 1024 * 1024:  # Limite de 100MB
                st.warning(
                    "O arquivo é muito grande. O tamanho máximo permitido é 100MB."
                )
            else:
                try:
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    unique_filename = str(uuid.uuid4()) + file_extension

                    storage_path = f"users/{user_uid}/documents/{unique_filename}"

                    # Upload para o Firebase Storage
                    file_url = firebase_manager.upload_file(
                        uploaded_file.getvalue(),
                        storage_path,
                        content_type=uploaded_file.type,
                    )

                    if file_url:
                        # Salva os metadados do documento no Firestore
                        new_document_data = {
                            "name": uploaded_file.name,
                            "description": document_description,
                            "file_url": file_url,
                            "uploaded_at": firestore.SERVER_TIMESTAMP,
                            "user_uid": user_uid,
                            "mime_type": uploaded_file.type,
                            "storage_path": storage_path,
                        }

                        collection_path = f"users/{user_uid}/documents"
                        doc_id = firebase_manager.add_document(
                            collection_path, new_document_data
                        )

                        if doc_id:
                            st.success("Documento enviado e salvo com sucesso!")
                            sleep(1.5)
                            st.rerun()
                        else:
                            st.error(
                                "Erro ao salvar os metadados do documento. Tente novamente."
                            )
                    else:
                        st.error(
                            "Erro ao fazer upload do arquivo para o Storage. Tente novamente."
                        )
                except Exception as e:
                    st.error(f"Ocorreu um erro no upload: {e}")
        elif submitted and uploaded_file is None:
            st.warning("Por favor, selecione um arquivo para enviar.")

    st.markdown("---")

    # --- Seção para Exibir e Gerenciar Documentos Existentes ---

    st.header("Documentos Enviados")

    collection_path = f"users/{user_uid}/documents"
    documents_with_id = firebase_manager.get_all_documents(collection_path)

    if documents_with_id:
        document_list = []
        for item in documents_with_id:
            doc_id, data = list(item.items())[0]
            data["id"] = doc_id
            document_list.append(data)

        sorted_documents = sorted(
            document_list,
            key=lambda x: x.get("uploaded_at", datetime.min),
            reverse=True,
        )

        for doc in sorted_documents:
            doc_id = doc["id"]

            with st.expander(f"**📄 {doc.get('name', 'Arquivo sem nome')}**"):
                if doc.get("description"):
                    st.write(f"**Descrição:** {doc.get('description')}")
                st.write(f"**Tipo:** {doc.get('mime_type', 'Desconhecido')}")

                uploaded_at_ts = doc.get("uploaded_at")
                if uploaded_at_ts:
                    uploaded_dt = (
                        uploaded_at_ts.isoformat()
                        if isinstance(uploaded_at_ts, datetime)
                        else uploaded_at_ts.isoformat()
                    )
                    st.write(
                        f"**Data do envio:** {datetime.fromisoformat(uploaded_dt).strftime('%d/%m/%Y %H:%M')}"
                    )

                st.markdown(
                    f"**Visualizar:** [Clique aqui para abrir o documento]({doc.get('file_url')})"
                )

                col1, col2 = st.columns(2)

                with col2:
                    if st.button("Excluir", key=f"delete_doc_{doc_id}"):
                        storage_path_to_delete = doc.get("storage_path")

                        if storage_path_to_delete:
                            if firebase_manager.delete_file(storage_path_to_delete):
                                st.success("Documento excluído com sucesso")
                            else:
                                st.error(
                                    "Erro ao excluir arquivo do Storage. Tente novamente."
                                )
                                continue

                        firebase_manager.delete_document(collection_path, doc_id)
                        sleep(1.5)
                        st.rerun()
    else:
        st.info(
            "Nenhum documento enviado ainda. Use o formulário acima para adicionar um."
        )
