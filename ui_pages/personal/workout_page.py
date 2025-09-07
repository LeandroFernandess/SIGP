"""
Módulo para renderizar a página de gerenciamento de treinos.

Este script define a interface de usuário para registrar, visualizar,
editar e excluir exercícios de treino. Ele agrupa os exercícios por
grupo muscular para facilitar a visualização e interage com o Firebase
Firestore para persistir os dados.
"""

import streamlit as st
from core.firebase_manager import FirebaseManager
from firebase_admin import firestore
from time import sleep
from datetime import datetime
from collections import defaultdict 


def render_workout_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página de gerenciamento de treinos para o usuário.

    Esta função permite ao usuário adicionar novos registros de treinos, visualizar
    os treinos existentes (agrupados por grupo muscular), editá-los e excluí-los.
    Os dados dos treinos são armazenados no Firestore na coleção 'users/{user_uid}/treinos'.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase para interagir com o Firestore.
        user_uid (str): O UID do usuário atualmente autenticado, usado para identificar a coleção de treinos.
    """
    st.title("💪 Meus Treinos")

    # Inicializa o estado para controlar qual treino está sendo editado
    if "editing_workout_id" not in st.session_state:
        st.session_state.editing_workout_id = None

    # --- Lista de Grupos Musculares para o seletor ---
    
    muscle_groups = [
        "Selecione um Grupo Muscular",
        "Peito",
        "Costas",
        "Pernas",
        "Ombros",
        "Bíceps",
        "Tríceps",
        "Abdômen",
        "Glúteos",
        "Panturrilhas",
        "Corpo Inteiro",
        "Outro",
    ]

    # --- Formulário para Adicionar Novo Treino ---

    st.header("Registrar Novo Exercício")

    with st.form("new_workout_form", clear_on_submit=True):
        st.markdown("**Preencha os detalhes do seu exercício:**")

        exercise_name = st.text_input("Nome do Exercício", max_chars=100)
        muscle_group = st.selectbox("Grupo Muscular", options=muscle_groups)

        st.markdown("---")
        st.subheader("Séries de Aquecimento (Opcional)")
        warmup_sets = st.number_input(
            "Séries de Aquecimento",
            min_value=0,
            max_value=10,
            value=0,
            key="warmup_sets_add",
        )
        warmup_reps = st.number_input(
            "Repetições de Aquecimento",
            min_value=0,
            max_value=50,
            value=0,
            key="warmup_reps_add",
        )
        weight_add = st.number_input(
            "Peso (kg)",
            min_value=0.0,
            max_value=500.0,
            value=10.0,
            step=0.5,
            key="weight_reps_add",
        )

        st.markdown("---")

        st.subheader("Séries de Trabalho")
        sets = st.number_input(
            "Séries de Trabalho", min_value=1, max_value=20, value=3, key="sets_add"
        )
        reps = st.number_input(
            "Repetições de Trabalho",
            min_value=1,
            max_value=100,
            value=10,
            key="reps_add",
        )
        weight = st.number_input(
            "Peso (kg)",
            min_value=0.0,
            max_value=500.0,
            value=10.0,
            step=0.5,
            key="weight_add",
        )
        workout_notes = st.text_area("Observações (Opcional)")

        submitted = st.form_submit_button("Salvar Exercício")

        if submitted:
            if not exercise_name or muscle_group == "Selecione um Grupo Muscular":
                st.warning("Nome do Exercício e Grupo Muscular são obrigatórios.")
            else:
                try:
                    new_workout_data = {
                        "exercise_name": exercise_name,
                        "muscle_group": muscle_group,
                        "warmup_sets": warmup_sets,
                        "warmup_reps": warmup_reps,
                        "weight_add": weight_add,
                        "sets": sets,
                        "reps": reps,
                        "weight": weight,
                        "notes": workout_notes,
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "updated_at": firestore.SERVER_TIMESTAMP,
                        "user_uid": user_uid,
                    }

                    collection_path = f"users/{user_uid}/treinos"
                    doc_id = firebase_manager.add_document(
                        collection_path, new_workout_data
                    )

                    if doc_id:
                        st.success("Exercício salvo com sucesso!")
                        sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar o exercício. Tente novamente.")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")

    st.markdown("---")

    # --- Seção para Exibir e Gerenciar Treinos Existentes ---

    st.header("Treinos Registrados")

    collection_path = f"users/{user_uid}/treinos"
    workouts_with_id = firebase_manager.get_all_documents(collection_path)

    if workouts_with_id:
        workout_list = []
        for item in workouts_with_id:
            doc_id, data = list(item.items())[0]
            data["id"] = doc_id
            workout_list.append(data)


        grouped_workouts = defaultdict(list)
        for workout in workout_list:
            grouped_workouts[workout.get("muscle_group", "Não Informado")].append(
                workout
            )


        sorted_muscle_groups = sorted(grouped_workouts.keys())

        for group in sorted_muscle_groups:
            with st.expander(f"**🏋️ Grupo Muscular: {group}**"):

                sorted_exercises_in_group = sorted(
                    grouped_workouts[group],
                    key=lambda x: x.get("created_at", datetime.min),
                    reverse=True,
                )

                for workout in sorted_exercises_in_group:
                    doc_id = workout["id"]

                    st.markdown(
                        f"---"
                    )  
                    st.subheader(
                        f"Exercício: {workout.get('exercise_name', 'Nome Inválido')}"
                    )

                    warmup_sets_display = workout.get("warmup_sets", 0)
                    warmup_reps_display = workout.get("warmup_reps", 0)
                    if warmup_sets_display > 0 or warmup_reps_display > 0:
                        st.write(
                            f"**Aquecimento:** {warmup_sets_display} séries de {warmup_reps_display} repetições com peso de {workout.get('weight_add', 'N/A')} kg"
                        )

                    st.write(f"**Séries de Trabalho:** {workout.get('sets', 'N/A')}")
                    st.write(
                        f"**Repetições de Trabalho:** {workout.get('reps', 'N/A')}"
                    )
                    st.write(f"**Peso:** {workout.get('weight', 'N/A')} kg")

                    if workout.get("notes"):
                        st.write(f"**Observações:** {workout.get('notes')}")

                    created_at_ts = workout.get("created_at")
                    if created_at_ts:
                        created_dt = (
                            created_at_ts.isoformat()
                            if isinstance(created_at_ts, datetime)
                            else created_at_ts.isoformat()
                        )
                        st.caption(
                            f"Registrado em: {datetime.fromisoformat(created_dt).strftime('%d/%m/%Y %H:%M')}"
                        )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("Editar", key=f"edit_workout_btn_{doc_id}"):
                            st.session_state.editing_workout_id = doc_id
                            st.rerun()

                    with col2:
                        if st.button("Excluir", key=f"delete_workout_{doc_id}"):
                            firebase_manager.delete_document(collection_path, doc_id)
                            st.success("Exercício excluído com sucesso.")
                            sleep(1.5)
                            st.rerun()

                    if st.session_state.editing_workout_id == doc_id:
                        st.subheader(
                            f"Editar Exercício: {workout.get('exercise_name', '')}"
                        )
                        with st.form(f"edit_workout_form_{doc_id}"):
                            edited_exercise_name = st.text_input(
                                "Nome do Exercício",
                                value=workout.get("exercise_name", ""),
                            )
                            edited_muscle_group = st.selectbox(
                                "Grupo Muscular",
                                options=muscle_groups,
                                index=muscle_groups.index(
                                    workout.get("muscle_group", muscle_groups[0])
                                ),
                            )

                            st.markdown("---")
                            st.subheader("Séries de Aquecimento")
                            edited_warmup_sets = st.number_input(
                                "Séries de Aquecimento",
                                min_value=0,
                                max_value=10,
                                value=workout.get("warmup_sets", 0),
                                key=f"edit_warmup_sets_{doc_id}",
                            )
                            edited_warmup_reps = st.number_input(
                                "Repetições de Aquecimento",
                                min_value=0,
                                max_value=50,
                                value=workout.get("warmup_reps", 0),
                                key=f"edit_warmup_reps_{doc_id}",
                            )
                            st.markdown("---")

                            st.subheader("Séries de Trabalho")
                            edited_sets = st.number_input(
                                "Séries de Trabalho",
                                min_value=1,
                                max_value=20,
                                value=workout.get("sets", 3),
                                key=f"edit_sets_{doc_id}",
                            )
                            edited_reps = st.number_input(
                                "Repetições de Trabalho",
                                min_value=1,
                                max_value=100,
                                value=workout.get("reps", 10),
                                key=f"edit_reps_{doc_id}",
                            )
                            edited_weight = st.number_input(
                                "Peso (kg)",
                                min_value=0.0,
                                max_value=500.0,
                                value=workout.get("weight", 10.0),
                                step=0.5,
                                key=f"edit_weight_{doc_id}",
                            )
                            edited_notes = st.text_area(
                                "Observações", value=workout.get("notes", "")
                            )

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button(
                                    "Salvar Edição"
                                ): 
                                    if (
                                        not edited_exercise_name
                                        or edited_muscle_group
                                        == "Selecione um Grupo Muscular"
                                    ):
                                        st.warning(
                                            "Nome do Exercício e Grupo Muscular são obrigatórios."
                                        )
                                    else:
                                        update_data = {
                                            "exercise_name": edited_exercise_name,
                                            "muscle_group": edited_muscle_group,
                                            "warmup_sets": edited_warmup_sets,  
                                            "warmup_reps": edited_warmup_reps,  
                                            "sets": edited_sets,
                                            "reps": edited_reps,
                                            "weight": edited_weight,
                                            "notes": edited_notes,
                                            "updated_at": firestore.SERVER_TIMESTAMP,
                                        }
                                        firebase_manager.update_document(
                                            collection_path, doc_id, update_data
                                        )
                                        st.success("Exercício atualizado com sucesso!")
                                        st.session_state.editing_workout_id = (
                                            None  
                                        )
                                        sleep(1.5)
                                        st.rerun()
                            with col_cancel:
                                if st.form_submit_button(
                                    "Cancelar"
                                ):
                                    st.session_state.editing_workout_id = (
                                        None 
                                    )
                                    st.rerun()
                st.markdown("---")

    else:
        st.info(
            "Nenhum treino registrado ainda. Use o formulário acima para adicionar um novo exercício."
        )
