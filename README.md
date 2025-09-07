SIGP - Sistema Inteligente de Gestão Pessoal 🏡
Uma aplicação de gestão pessoal desenvolvida com Python e Streamlit para ajudar no acompanhamento de finanças, documentos, exames e treinos. O projeto é integrado com o Firebase para persistência de dados em tempo real e autenticação de usuários.

Tecnologias Utilizadas 🛠️
Python: Linguagem principal do projeto.

Streamlit: Framework para a criação da interface de usuário interativa e responsiva.

Firebase: Backend completo para autenticação de usuários (Authentication), armazenamento de dados (Firestore) e arquivos (Cloud Storage).

Plotly Express: Biblioteca para a criação de gráficos de alta qualidade, como os de barra e rosca, utilizados para visualização de dados financeiros.

Pandas: Biblioteca para manipulação e análise de dados em DataFrames.

Estrutura do Projeto 📂
A estrutura do projeto está organizada da seguinte forma:

sigp/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
├── config/
│   └── settings.py
├── core/
│   ├── auth_service.py
│   ├── firebase_manager.py
│   └── ui_controller.py
├── ui_pages/
│   ├── componets/
│   │   └── sidebar_component.py
│   ├── financy/
│   │   ├── expenses_page.py
│   │   ├── income_page.py
│   │   └── reports_page.py
│   ├── personal/
│   │   ├── dashboard_page.py
│   │   ├── document_page.py
│   │   ├── exams_page.py
│   │   ├── notes_page.py
│   │   └── workout_page.py
│   ├── login_page.py
│   ├── recover_password_page.py
│   └── register_page.py
├── venv/
├── .gitignore
├── app.py
└── requirements.txt

Principais Pastas e Arquivos
core/: Contém a lógica de negócios e as classes principais do sistema, como o gerenciador do Firebase e o serviço de autenticação.

ui_pages/: Organiza as diferentes páginas da aplicação (login, registro, dashboard, etc.) em módulos separados.

ui_pages/financy/: Módulos específicos para as funcionalidades financeiras, como renda mensal, gastos e relatórios.

ui_pages/personal/: Módulos para gerenciar dados pessoais, como exames médicos, anotações, documentos e treinos.

app.py: O ponto de entrada principal que inicializa e executa a aplicação.

.streamlit/: Contém arquivos de configuração e segredos confidenciais. Essa pasta é ignorada pelo Git.

requirements.txt: Lista todas as dependências necessárias para o ambiente Python.

Funcionalidades 🚀
Autenticação Segura: Login, registro e recuperação de senha.

Gerenciamento de Renda: Adicione, edite e visualize sua renda mensal.

Controle de Gastos: Registre gastos fixos e de cartão de crédito, com cálculo automático de parcelas.

Relatórios Financeiros: Gere gráficos de barra e rosca para analisar sua saúde financeira em relação à renda mensal e categorias de gastos.

Gestão de Documentos: Faça upload, visualize e exclua documentos pessoais.

Agenda de Exames: Gerencie seus exames médicos com datas e horários.

Diário de Treinos: Registre seus exercícios e acompanhe o progresso na academia.

Gerenciamento de Anotações: Crie, edite e visualize anotações pessoais.

Como Executar o Projeto 🔧
Clone o repositório:

git clone [https://github.com/seu-usuario/sigp.git](https://github.com/seu-usuario/sigp.git)

Entre no diretório do projeto:

cd sigp

Crie e ative o ambiente virtual:

python -m venv venv
# No Windows
venv\Scripts\activate
# No Unix ou MacOS
source venv/bin/activate

Instale as dependências:

pip install -r requirements.txt

Crie a pasta e o arquivo de segredos:
Crie uma pasta chamada .streamlit na raiz do projeto e, dentro dela, um arquivo chamado secrets.toml. Este arquivo não deve ser enviado para o GitHub.

Adicione as credenciais no secrets.toml:
No painel do Firebase, copie as informações da sua chave de serviço e a API key, e cole-as no arquivo secrets.toml no formato abaixo.

# .streamlit/secrets.toml
# Chave de serviço do Firebase
[firebase]
type = "service_account"
project_id = "sigp-7bbf1"
private_key_id = "..."
private_key = """-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"""
client_email = "..."
client_id = "..."
auth_uri = "..."
token_uri = "..."
auth_provider_x509_cert_url = "..."
client_x509_cert_url = "..."
universe_domain = "..."

# Variáveis de ambiente
[financial]
FIREBASE_STORAGE_BUCKET = "sigp-7bbf1.firebasestorage.app"
FIREBASE_WEB_API_KEY = "AIzaSyA5ebVgjuA7PdJzP1gypIjVx2biKXBw_Fk"

Execute o aplicativo Streamlit:

streamlit run app.py

Acesse no navegador:
Abra o navegador e acesse http://localhost:8501/.

Contribuindo 🤝
Contribuições são muito bem-vindas! Se você encontrar algum problema ou tiver sugestões de melhorias, por favor, abra uma issue ou envie um pull request.

Documentação atualizada em: 07/09/2025. 🚀
