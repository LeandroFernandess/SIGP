"""
Módulo para renderizar a página de gerenciamento de gastos.

Este script define a interface de usuário para registrar, visualizar,
editar e excluir gastos, divididos em categorias e tipos (fixo ou cartão
de crédito). Os dados são persistidos no Firestore.
"""

import streamlit as st
from core.firebase_manager import FirebaseManager
from time import sleep
from datetime import datetime
from collections import defaultdict


def render_expenses_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página para gerenciamento de gastos.

    Permite ao usuário registrar novos gastos, categorizá-los e visualizá-los
    de forma organizada. Os dados são salvos no Firestore.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase.
        user_uid (str): O UID do usuário atualmente autenticado.
    """
    st.title("💸 Controle de Gastos")
    st.write(
        "Registre aqui seus gastos fixos e de cartão de crédito para manter suas finanças em dia."
    )

    expense_categories = [
        "Selecione uma categoria",
        "Necessário",
        "Lazer",
        "Imprevisto",
        "Alimentação",
        "Transporte",
        "Educação",
        "Moradia",
        "Saúde",
        "Outro",
    ]

    collection_path = f"users/{user_uid}/gastos"

    # Inicializa o estado de edição
    if "editing_expense_id" not in st.session_state:
        st.session_state.editing_expense_id = None

    # --- Formulário para Adicionar Novo Gasto Fixo ---

    st.subheader("Adicionar Gasto Fixo")
    with st.form("new_fixed_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Data do Gasto", key="new_fixed_date")
        with col2:
            expense_category = st.selectbox(
                "Categoria", options=expense_categories, key="new_fixed_category"
            )

        expense_description = st.text_input(
            "Descrição do Gasto", key="new_fixed_description"
        )

        expense_value = st.number_input(
            "Valor (R$)", min_value=0.0, step=0.01, format="%.2f", key="new_fixed_value"
        )

        submitted = st.form_submit_button("Salvar Gasto Fixo")
        if submitted:
            if not expense_description or expense_category == "Selecione uma categoria":
                st.warning("A descrição e a categoria do gasto são obrigatórios.")
            else:
                try:
                    new_expense_data = {
                        "descricao": expense_description,
                        "valor": expense_value,
                        "tipo": "Fixo",
                        "categoria": expense_category,
                        "data": expense_date.strftime("%Y-%m-%d"),
                        "criado_em": datetime.now().isoformat(),
                        "user_uid": user_uid,
                    }
                    doc_id = firebase_manager.add_document(
                        collection_path, new_expense_data
                    )
                    if doc_id:
                        st.success("Gasto fixo salvo com sucesso! ✅")
                        sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar o gasto. Tente novamente. ❌")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e} ❌")

    st.markdown("---")

    # --- Formulário para Adicionar Novo Gasto de Cartão de Crédito ---
    
    st.subheader("Adicionar Gasto de Cartão de Crédito")
    with st.form("new_credit_card_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Data do Gasto", key="new_credit_card_date")
        with col2:
            expense_category = st.selectbox(
                "Categoria", options=expense_categories, key="new_credit_card_category"
            )

        expense_description = st.text_input(
            "Descrição do Gasto", key="new_credit_card_description"
        )

        expense_value = st.number_input(
            "Valor Total (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key="new_credit_card_value",
        )
        installments = st.number_input(
            "Número de Parcelas",
            min_value=1,
            value=1,
            step=1,
            key="new_credit_card_installments",
        )

        submitted = st.form_submit_button("Salvar Gasto de Cartão")
        if submitted:
            if not expense_description or expense_category == "Selecione uma categoria":
                st.warning("A descrição e a categoria do gasto são obrigatórios.")
            else:
                try:
                    # Cálculo e exibição do valor da parcela
                    installment_value = (
                        expense_value / installments if installments > 0 else 0
                    )
                    st.info(
                        f"O valor de cada parcela será de **R$ {installment_value:.2f}**."
                    )

                    # Cálculo do mês e ano de término do parcelamento
                    final_month = expense_date.month + installments - 1
                    final_year = expense_date.year + (final_month - 1) // 12
                    final_month = (final_month - 1) % 12 + 1
                    end_month_year = f"{final_month:02d}/{final_year}"

                    st.info(f"O parcelamento se encerrará em **{end_month_year}**.")

                    new_expense_data = {
                        "descricao": expense_description,
                        "valor": expense_value,
                        "tipo": "Cartão de Crédito",
                        "categoria": expense_category,
                        "data": expense_date.strftime("%Y-%m-%d"),
                        "criado_em": datetime.now().isoformat(),
                        "user_uid": user_uid,
                        "parcelas": installments,
                        "valor_parcela": installment_value,
                        "fim_parcelamento": end_month_year,
                    }
                    doc_id = firebase_manager.add_document(
                        collection_path, new_expense_data
                    )
                    if doc_id:
                        st.success("Gasto de cartão de crédito salvo com sucesso! ✅")
                        sleep(1.5)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar o gasto. Tente novamente. ❌")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e} ❌")

    st.markdown("---")

    # --- Exibir e Gerenciar Gastos Existentes ---

    st.subheader("Histórico de Gastos")

    all_expenses = firebase_manager.get_all_documents(collection_path)

    if all_expenses:
        expenses_list = []
        for item in all_expenses:
            doc_id, data = list(item.items())[0]
            data["id"] = doc_id
            expenses_list.append(data)

        grouped_expenses = defaultdict(list)
        for expense in expenses_list:
            grouped_expenses[expense.get("tipo", "Não Informado")].append(expense)

        for expense_type, expenses_in_group in grouped_expenses.items():
            with st.expander(f"**🧾 Tipo: {expense_type}**"):
                sorted_expenses = sorted(
                    expenses_in_group,
                    key=lambda x: x.get("data", "9999-12-31"),
                    reverse=True,
                )

                for expense in sorted_expenses:
                    doc_id = expense["id"]

                    st.markdown("---")
                    st.write(f"**Descrição:** {expense.get('descricao')}")
                    st.write(f"**Categoria:** {expense.get('categoria')}")
                    st.write(f"**Valor:** R$ {expense.get('valor', 0):.2f}")
                    st.write(
                        f"**Data:** {datetime.strptime(expense.get('data'), '%Y-%m-%d').strftime('%d/%m/%Y')}"
                    )

                    if expense.get("tipo") == "Cartão de Crédito":
                        st.write(f"**Parcelas:** {expense.get('parcelas', 'N/A')}")
                        st.write(
                            f"**Valor da Parcela:** R$ {expense.get('valor_parcela', 0):.2f}"
                        )
                        st.write(
                            f"**Fim do Parcelamento:** {expense.get('fim_parcelamento', 'N/A')}"
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Editar", key=f"edit_expense_{doc_id}"):
                            st.session_state.editing_expense_id = doc_id
                            st.rerun()

                    with col2:
                        if st.button("Excluir", key=f"delete_expense_{doc_id}"):
                            firebase_manager.delete_document(collection_path, doc_id)
                            st.success("Gasto excluído com sucesso! 🗑️")
                            sleep(1.5)
                            st.rerun()

                    # Formulário de edição
                    if st.session_state.editing_expense_id == doc_id:
                        st.subheader("Editar Gasto")
                        with st.form(f"edit_form_{doc_id}"):
                            edited_description = st.text_input(
                                "Descrição",
                                value=expense.get("descricao"),
                                key=f"edit_desc_{doc_id}",
                            )
                            edited_value = st.number_input(
                                "Valor (R$)",
                                min_value=0.0,
                                value=expense.get("valor"),
                                step=0.01,
                                format="%.2f",
                                key=f"edit_value_{doc_id}",
                            )
                            edited_category = st.selectbox(
                                "Categoria",
                                options=expense_categories,
                                index=expense_categories.index(
                                    expense.get("categoria")
                                ),
                                key=f"edit_cat_{doc_id}",
                            )

                            # Campos de edição condicionais para cartão de crédito
                            if expense.get("tipo") == "Cartão de Crédito":
                                edited_installments = st.number_input(
                                    "Número de Parcelas",
                                    min_value=1,
                                    value=expense.get("parcelas"),
                                    step=1,
                                    key=f"edit_installments_{doc_id}",
                                )
                                edited_installment_value = st.number_input(
                                    "Valor da Parcela (R$)",
                                    min_value=0.0,
                                    value=expense.get("valor_parcela"),
                                    step=0.01,
                                    format="%.2f",
                                    key=f"edit_installment_value_{doc_id}",
                                )

                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("Salvar Edição"):
                                    update_data = {
                                        "descricao": edited_description,
                                        "valor": edited_value,
                                        "categoria": edited_category,
                                    }
                                    if expense.get("tipo") == "Cartão de Crédito":
                                        update_data["parcelas"] = edited_installments
                                        update_data["valor_parcela"] = (
                                            edited_installment_value
                                        )

                                    firebase_manager.update_document(
                                        collection_path, doc_id, update_data
                                    )
                                    st.success("Gasto atualizado com sucesso! ✅")
                                    st.session_state.editing_expense_id = None
                                    sleep(1.5)
                                    st.rerun()
                            with col_cancel:
                                if st.form_submit_button("Cancelar"):
                                    st.session_state.editing_expense_id = None
                                    st.rerun()

    else:
        st.info(
            "Nenhum gasto registrado ainda. Use o formulário acima para adicionar um."
        )
