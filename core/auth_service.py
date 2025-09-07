
"""
Módulo de serviço para gerenciar operações de autenticação de usuários.

Este módulo define a classe AuthService, que encapsula a lógica de negócios
para criação, validação e login de usuários, interagindo com o Firebase
Authentication e o Firestore para persistência de dados de perfil.
"""

from .firebase_manager import FirebaseManager
from firebase_admin import firestore, auth
import requests


class AuthService:
    """Gerencia as operações de autenticação e perfis de usuário.

    Esta classe lida com a criação de novos usuários, login, e
    recuperação de senha, orquestrando as interações entre o
    Firebase Authentication e o Firestore.
    """

    def __init__(self, firebase_manager: FirebaseManager):
        """Inicializa o serviço de autenticação com o gerenciador do Firebase.

        Args:
            firebase_manager (FirebaseManager): Instância do gerenciador
                do Firebase para interagir com o Authentication e o Firestore.
        """
        self.fb_manager = firebase_manager

    def create_new_user_and_profile(
        self, email: str, password: str, display_name: str
    ) -> str | None:
        """Cria um novo usuário no Firebase Auth e um perfil no Firestore.

        Em caso de sucesso, retorna o UID do novo usuário. Em caso de falha,
        retorna `None` após tratar as exceções.

        Args:
            email (str): O endereço de e-mail do novo usuário.
            password (str): A senha do novo usuário.
            display_name (str): O nome de exibição do novo usuário.

        Returns:
            str | None: O UID do usuário recém-criado se a operação
            for bem-sucedida, caso contrário, `None`.
        """
        try:
            user_record = self.fb_manager.create_user_record(
                email, password, display_name
            )

            perfil_usuario = {
                "nome": display_name,
                "email": email,
                "data_criacao": firestore.SERVER_TIMESTAMP,
            }
            self.fb_manager.db.collection("usuarios").document(user_record.uid).set(
                perfil_usuario
            )

            return user_record.uid

        except auth.EmailAlreadyExistsError:
            print("Erro (AuthService): E-mail já existe.")
            return None
        except Exception as e:
            print(f"Erro (AuthService) ao criar usuário e perfil: {e}")
            return None

    def login_user(self, email: str, password: str) -> dict | str | None:
        """Tenta autenticar um usuário usando e-mail e senha.

        A função interage com a API REST do Firebase para validar as credenciais.

        Args:
            email (str): O e-mail do usuário.
            password (str): A senha do usuário.

        Returns:
            dict | str | None: Um dicionário com os dados do usuário se o
            login for bem-sucedido. Retorna a string "CLOCK_SKEW_ERROR"
            em caso de erro de sincronização de relógio. Retorna `None`
            para outras falhas de login (ex: credenciais inválidas).
        """
        try:
            user_data = self.fb_manager.sign_in_with_email_and_password(email, password)
            return user_data
        except requests.exceptions.HTTPError as e:
            if "TOKEN_USED_TOO_EARLY" in str(e) or "CLOCK_SKEW_ERROR" in str(e):
                return "CLOCK_SKEW_ERROR"
            return None
        except Exception as e:
            print(f"Erro (AuthService) no login: {e}")
            return None

    def recover_password(self, email: str) -> bool:
        """Envia um e-mail de redefinição de senha para o endereço fornecido.

        Trata a exceção `EMAIL_NOT_FOUND` de forma silenciosa para evitar
        divulgação de informações sobre a existência de contas.

        Args:
            email (str): O e-mail para o qual a redefinição de senha
                será enviada.

        Returns:
            bool: `True` se a solicitação for bem-sucedida ou se o e-mail não
            for encontrado (por razões de segurança), `False` em caso de
            qualquer outro erro.
        """
        try:
            self.fb_manager.send_password_reset_email(email)
            return True
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json()
            error_message = error_data["error"]["message"]

            if error_message == "EMAIL_NOT_FOUND":
                return True

            print(f"Erro (AuthService) na recuperação de senha: {error_message}")
            return False
        except Exception as e:
            print(f"Erro inesperado (AuthService) na recuperação de senha: {e}")
            return False
