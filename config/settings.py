"""
Módulo de configurações para a aplicação Firebase.

Este módulo centraliza todas as variáveis de configuração globais,
como caminhos para chaves de serviço e URLs de buckets, facilitando
a gestão e a atualização das configurações da aplicação em um único local.
"""

import streamlit as st

# URL do Firebase Cloud Storage bucket.
# Este é o identificador único do bucket onde os arquivos da aplicação serão armazenados
FIREBASE_STORAGE_BUCKET = st.secrets["financial"]["FIREBASE_STORAGE_BUCKET"]

# Chave de API Web do Firebase (API Key pública do projeto Firebase).
# Esta chave é usada para interagir com as APIs de cliente do Firebase (como Autenticação REST API).
# Pode ser encontrada nas configurações do aplicativo web no Console do Firebase.
FIREBASE_WEB_API_KEY = st.secrets["financial"]["FIREBASE_WEB_API_KEY"]
