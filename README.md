# Sistema inteligente de gestão pessoal 🌐

Um sistema de gerenciamento financeiro e pessoal desenvolvido com Python, Streamlit e Firebase. 
O projeto permite acompanhar receitas, despesas, contas fixas, faturas de cartão de crédito e resumos financeiros de forma intuitiva.
Também é possível gerir assuntos pessoais, como salvar documentos, exames médicos, treinos e anotações diversas.

## Tecnologias Utilizadas 🛠️

- **Python**: Linguagem principal do projeto.
- **Streamlit**: Framework para criação da interface interativa.
- **Firebase**: Banco de dados utilizado para armazenar as transações financeiras, documentos e demais informações.

## Estrutura do Projeto 📂

A estrutura do projeto está organizada da seguinte forma:

```
SIGP/
├── config/
│   ├── settings.py  
│   ├── __init__.py
├── core/
│   ├── auth_service.py  
│   ├── firebase_manager.py
│   ├── ui_controller.py  
│   ├── __init__.py
├── ui_pages/
│   ├── components/
        ├── dashboard_page.py
        ├── __init__.py
│   ├── financy/
        ├── expenses_page.py
        ├── income_page.py
        ├── reports_page.py
        ├── __init__.py
│   ├── personal/
        ├── document_page.py
        ├── exams_page.py
        ├── notes_page.py
        ├── workout_page.py
        ├── __init__.py
│   ├── dashboard_page.py
│   ├── login_page.py
│   ├── recover_password_page.py
│   ├── register_page.py
│   ├── __init__.py
├── venv/ 
├── .gitignore  
├── app.py  
├── requirements.txt  
```

### Principais Pastas e Arquivos

- **config/**: Este módulo centraliza todas as variáveis de configuração globais.
- **Core/**: Módulo de serviço para gerenciar operações de autenticação de usuários, para controlar a interface do usuário (UI) da aplicação Streamlit e gerenciamento para o Firebase.
- **ui_pages/**: Módulo principal da aplicação, onde está as páginas de cada grupo, sidebar e demais funcionalidades.
- **app.py**: Este script inicializa os serviços de Firebase e autenticação, e em seguida, inicia o controlador da interface do usuário do Streamlit, orquestrando o fluxo geral da aplicação.
- **requirements.txt**: Arquivo com as bibliotecas necessárias para rodar o projeto.

### Importante

É necessário criar uma pasta ".streamlit/" na raiz do projeto e, dentro dela, criar um arquivo com o nome de "secrets.toml".
Nela se deve armazenar os dados da chave de API do Firebase e as variáveis de ambiente consumidas no "settings.py", todas as informações são fornecedias pelo próprio Firebase.

Exemplo:

```
[firebase]
type = ""
project_id = ""
private_key_id = ""
private_key = """"""
client_email = ""
client_id = ""
auth_uri = ""
token_uri = ""
auth_provider_x509_cert_url = ""
client_x509_cert_url = ""
universe_domain = ""

[financial]
FIREBASE_STORAGE_BUCKET = ""
FIREBASE_WEB_API_KEY = ""
 
```

## Funcionalidades 🚀

- Autenticação de usuários via banco de dados Firebase.
- Cadastro e gerenciamento de receitas e despesas.
- Controle de contas fixas e variáveis.
- Controle de agendamentos médicos, documentos pessoais, treinos e anotações.
- Monitoramento de faturas de cartão de crédito.
- Geração de resumo financeiro.
- Interface interativa e responsiva com Streamlit.

## Como Executar o Projeto 🔧

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/SIGP.git
   ```
2. **Entre no diretório do projeto:**
   ```bash
   cd SIGP
   ```
3. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows
   venv\Scripts\activate
   # No Unix ou MacOS
   source venv/bin/activate
   ```
4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Execute o aplicativo Streamlit:**
   ```bash
   streamlit run app.py
   ```
6. **Acesse no navegador:**
   Abra o navegador e acesse `http://localhost:8501/`.

## Contribuindo 🤝

Contribuições são bem-vindas! Se você encontrar algum problema ou tiver sugestões, abra uma *issue* ou envie um *pull request*.

## Contato 💬

Caso tenha dúvidas ou sugestões, entre em contato:

- **Nome**: Leandro Fernandes
- **Email**: leandrofernandes1600@email.com
- **GitHub**: https://github.com/LeandroFernandess/SIGP
- **Links utilizados**:
  - FIREBASE: https://firebase.google.com
---

*Documentação atualizada em: `07/09/2025`.* 🚀

