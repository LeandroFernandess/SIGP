"""
Módulo para renderizar a página da agenda de exames.

Este script define a interface de usuário para agendar, visualizar,
editar e excluir exames médicos. Ele utiliza o Streamlit para
os componentes da UI e interage com o Firebase para gerenciar
os dados de exames de forma segura no Firestore.
"""

import streamlit as st
from datetime import date, datetime
from core.firebase_manager import FirebaseManager
from firebase_admin import firestore
from time import sleep


def render_exams_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página da agenda de exames para o usuário.

    Esta função cria a interface do usuário para agendar, visualizar,
    editar e excluir exames. Ela interage com o Firestore para gerenciar
    os dados do usuário de forma segura.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase.
        user_uid (str): O UID do usuário atualmente autenticado.
    """
    st.title("📅 Agenda de Exames")

    options = [
        "Acupuntura",
        "Alergia e Imunologia",
        "Anestesiologia",
        "Angiologia",
        "Cardiologia",
        "Cirurgia Geral",
        "Clínica Médica",
        "Dermatologia",
        "Dentista",
        "Endocrinologia e Metabologia",
        "Gastroenterologia",
        "Ginecologia e Obstetrícia",
        "Infectologia",
        "Medicina de Família e Comunidade",
        "Nefrologia",
        "Neurocirurgia",
        "Neurologia",
        "Nutrologia",
        "Oftalmologia",
        "Oncologia Clínica",
        "Ortopedia e Traumatologia",
        "Otorrinolaringologia",
        "Pediatria",
        "Pneumologia",
        "Psiquiatria",
        "Reumatologia",
        "Urologia",
        "Outra",
    ]
    options.sort()

    # --- Formulário para Adicionar Novo Exame ---
    st.header("Adicionar Novo Exame")

    with st.form("new_exam_form", clear_on_submit=True):
        st.markdown("**Preencha os dados do seu exame:**")

        exam_title = st.selectbox("Especialidade", options=options)

        col_date, col_time = st.columns(2)
        with col_date:
            exam_date = st.date_input(
                "Data do Exame", min_value=date.today(), format="DD/MM/YYYY"
            )
        with col_time:
            exam_time = st.text_input(
                "Horário (HH:MM)", max_chars=5, placeholder="Ex: 14:30"
            )

        exam_local = st.text_input("Local (Clínica/Hospital)", max_chars=100)
        exam_doctor = st.text_input("Nome do Médico", max_chars=100)
        exam_notes = st.text_area("Informações Adicionais")

        submitted = st.form_submit_button("Salvar Exame")

        if submitted:
            # Validação do horário
            try:
                datetime.strptime(exam_time, "%H:%M")
                is_valid_time = True
            except ValueError:
                is_valid_time = False

            if not exam_title or not exam_date or not exam_time:
                st.warning("Especialidade, Data e Horário do Exame são obrigatórios.")
            elif not is_valid_time:
                st.warning("Formato de horário inválido. Use HH:MM (Ex: 14:30).")
            else:
                try:
                    new_exam_data = {
                        "title": exam_title,
                        "date": exam_date.strftime("%Y-%m-%d"),
                        "time": exam_time,
                        "local": exam_local,
                        "doctor": exam_doctor,
                        "notes": exam_notes,
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "completed": False,
                    }

                    collection_path = f"users/{user_uid}/exames"
                    doc_id = firebase_manager.add_document(
                        collection_path, new_exam_data
                    )

                    if doc_id:
                        st.success("Exame salvo com sucesso!")
                        sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar o exame. Tente novamente.")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")

    st.markdown("---")

    # --- Seção para Exibir e Gerenciar Exames Existentes ---
    st.header("Exames Agendados")

    collection_path = f"users/{user_uid}/exames"
    exams_with_id = firebase_manager.get_all_documents(collection_path)

    if exams_with_id:
        exam_list = []
        for item in exams_with_id:
            doc_id, data = list(item.items())[0]
            data["id"] = doc_id

            if "completed" not in data:
                data["completed"] = False
            if "time" not in data:
                data["time"] = "Não informado"

            exam_list.append(data)

        # Ordena a lista de exames pela data e hora combinadas para exibição
        sorted_exams = sorted(
            exam_list,
            key=lambda x: (x.get("date", "9999-12-31"), x.get("time", "99:99")),
        )

        for exam in sorted_exams:
            doc_id = exam["id"]
            is_completed = exam.get("completed", False)
            status_emoji = "✅" if is_completed else "⏳"

            try:
                display_date = datetime.strptime(exam.get("date"), "%Y-%m-%d").strftime(
                    "%d/%m/%Y"
                )
            except (ValueError, TypeError):
                display_date = exam.get("date", "Data Inválida")

            with st.expander(
                f"{status_emoji} **{exam.get('title')}** - {display_date} às {exam.get('time')}"
            ):
                st.write(f"**Local:** {exam.get('local')}")
                st.write(f"**Médico:** {exam.get('doctor')}")
                st.write(f"**Observações:** {exam.get('notes')}")

                col1, col2 = st.columns(2)

                if not is_completed:
                    with col1:
                        if st.button(
                            "Marcar exame como concluído", key=f"complete_{doc_id}"
                        ):
                            update_data = {"completed": True}
                            firebase_manager.update_document(
                                collection_path, doc_id, update_data
                            )
                            st.success("Exame marcado como concluído!")
                            sleep(1.5)
                            st.rerun()
                else:
                    with col1:
                        st.write("Exame concluído! 🎉")

                with col2:
                    if st.button("Excluir", key=f"delete_{doc_id}"):
                        firebase_manager.delete_document(collection_path, doc_id)
                        st.success("Exame excluído com sucesso.")
                        sleep(1.5)
                        st.rerun()
    else:
        st.info(
            "Nenhum exame agendado ainda. Use o formulário acima para adicionar um."
        )
