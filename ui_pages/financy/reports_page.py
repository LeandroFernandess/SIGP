"""
Módulo para renderizar a página de relatórios financeiros.

Este script gera visualizações de dados para ajudar o usuário a
entender seus padrões de gastos. Ele calcula despesas mensais,
incluindo a projeção de gastos futuros com base em parcelas de cartão
de crédito, e exibe os dados em um gráfico.
"""

import streamlit as st
import pandas as pd
from core.firebase_manager import FirebaseManager
from datetime import datetime
from collections import defaultdict
import plotly.express as px


def render_reports_page(firebase_manager: FirebaseManager, user_uid: str):
    """Renderiza a página para visualização de relatórios financeiros.

    A função busca dados de renda e gastos no Firestore, processa-os
    para calcular totais mensais e projeta gastos futuros com parcelas,
    apresentando tudo em um gráfico.

    Args:
        firebase_manager (FirebaseManager): Instância do gerenciador do Firebase.
        user_uid (str): O UID do usuário autenticado.
    """
    st.title("📊 Relatórios Financeiros")
    st.write("Visualize sua saúde financeira com gráficos de renda e gastos.")

    # Busca a renda mensal do usuário
    income_data = firebase_manager.get_document(
        f"users/{user_uid}/financias", "renda_mensal"
    )
    monthly_income = income_data.get("valor", 0) if income_data else 0

    if monthly_income <= 0:
        st.info(
            "Por favor, registre sua renda mensal na página 'Renda Mensal' para ver os relatórios."
        )
        return

    # Busca todos os gastos do usuário
    expense_data = firebase_manager.get_all_documents(f"users/{user_uid}/gastos")

    if not expense_data:
        st.info(
            "Nenhum gasto registrado ainda. Adicione gastos para ver seus relatórios."
        )
        return

    # Processa os dados de gastos por mês e categoria
    monthly_totals = defaultdict(float)
    monthly_card_expenses = defaultdict(float)
    category_totals = defaultdict(float)

    today = datetime.now()

    for item in expense_data:
        doc_id, data = list(item.items())[0]

        expense_date_str = data.get("data")
        if not expense_date_str:
            continue

        expense_date = datetime.strptime(expense_date_str, "%Y-%m-%d")

        # Apenas considera gastos a partir do mês atual para o gráfico de barras
        if expense_date.year == today.year and expense_date.month == today.month:
            month_year = today.strftime("%Y-%m")
        elif expense_date.year > today.year or (
            expense_date.year == today.year and expense_date.month > today.month
        ):
            month_year = expense_date.strftime("%Y-%m")
        else:
            month_year = expense_date.strftime("%Y-%m")

        category = data.get("categoria", "Outro")

        if data.get("tipo") == "Fixo":
            monthly_totals[month_year] += data.get("valor", 0)
            category_totals[category] += data.get("valor", 0)

        elif data.get("tipo") == "Cartão de Crédito":
            installments = data.get("parcelas", 1)
            installment_value = data.get("valor_parcela", 0)

            category_totals[category] += data.get(
                "valor", 0
            )  # Total gasto, não a parcela

            for i in range(installments):
                installment_month = expense_date.month + i
                installment_year = expense_date.year + (installment_month - 1) // 12
                installment_month = (installment_month - 1) % 12 + 1

                installment_month_year = f"{installment_year}-{installment_month:02d}"
                monthly_totals[installment_month_year] += installment_value
                monthly_card_expenses[installment_month_year] += installment_value

    # Cria um DataFrame para visualização dos gráficos de barras e linhas
    df_data = []

    all_months = sorted(
        list(set(list(monthly_totals.keys()) + [today.strftime("%Y-%m")]))
    )

    for month_year in all_months:
        df_data.append(
            {
                "Mês": month_year,
                "Renda Mensal": monthly_income,
                "Gastos Totais": monthly_totals[month_year],
                "Gastos de Cartão": monthly_card_expenses[month_year],
            }
        )

    df = pd.DataFrame(df_data)

    # Cria um DataFrame para o gráfico de rosca
    df_categories = pd.DataFrame(
        list(category_totals.items()), columns=["Categoria", "Valor Total"]
    )

    # --- GRÁFICOS ---

    st.subheader("Renda vs. Gastos Mensais - Gráfico de Barras")
    st.markdown(
        "Isso mostra a sua renda fixa comparada com os gastos mensais, incluindo projeções para as parcelas do cartão de crédito."
    )

    fig_bar = px.bar(
        df,
        x="Mês",
        y=["Renda Mensal", "Gastos Totais"],
        barmode="group",
        color_discrete_map={"Renda Mensal": "#ACDEFF", "Gastos Totais": "#ffa4a4"},
        labels={"value": "Valor (R$)", "variable": "Legenda"},
    )
    fig_bar.update_layout(
        yaxis_title="Valor (R$)",
        hovermode="x unified",
        xaxis_tickformat="%Y-%m",
        yaxis_tickprefix="R$ ",
        yaxis_tickformat=".2f",
    )
    fig_bar.update_traces(
        texttemplate="R$ %{y:.2f}",
        textposition="outside",
        textfont=dict(weight="bold"),
        hovertemplate="<b>%{data.name}</b><br>"
        + "Mês: %{x}<br>"
        + "Valor: R$ %{y:.2f}<br>"
        + "<extra></extra>",
    )

    st.plotly_chart(fig_bar)
    st.markdown("---")

    st.subheader("Gastos por Categoria - Gráfico de Rosca")
    st.markdown("Isso mostra a proporção dos seus gastos totais por categoria.")

    fig = px.pie(df_categories, names="Categoria", values="Valor Total", hole=0.5)
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Valor Total: R$ %{value:.2f}<br>Porcentagem: %{percent:.1%}",
        textinfo="label+percent",
        textfont_size=15,
        textfont_color="white",
        textfont=dict(weight="bold"),
        marker=dict(line=dict(color="#000000", width=2)),
    )
    st.plotly_chart(fig)

    st.markdown("---")
    st.info(
        "Estes gráficos mostram a sua renda fixa comparada com os gastos mensais, incluindo projeções para as parcelas do cartão de crédito."
    )
