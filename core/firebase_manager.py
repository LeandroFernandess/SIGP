"""
Módulo de gerenciamento para o Firebase.

Este módulo fornece uma classe, FirebaseManager, que encapsula a lógica para
interagir com os serviços do Google Firebase, especificamente o Firestore
(banco de dados) e o Cloud Storage (armazenamento de arquivos).
O objetivo é simplificar as operações de CRUD e o manuseio de arquivos
em outras partes do projeto.
"""

import firebase_admin
import requests
from firebase_admin import credentials, firestore, storage, auth
from firebase_admin.auth import UserRecord
import requests


class FirebaseManager:
    """Gerencia a conexão e as operações com os serviços do Firebase.

    Esta classe lida com a inicialização do SDK do Firebase Admin e fornece
    métodos de alto nível para realizar operações comuns no Firestore e no
    Cloud Storage, abstraindo a complexidade da comunicação direta com a API.

    Attributes:
        db: Instância do cliente do Firestore para operações de banco de dados.
        bucket: Instância do cliente do Cloud Storage para operações de
                armazenamento de arquivos.
        web_api_key (str): A chave de API web pública do Firebase para chamadas de cliente.
    """

    def __init__(self, key_path: str, storage_bucket: str, web_api_key: str):
        """Inicializa a conexão com o Firebase usando uma chave de serviço.

        Args:
            key_path (str): O caminho para o arquivo JSON da chave de serviço
                            do Firebase.
            storage_bucket (str): O URL do bucket do Firebase Cloud Storage
                                  (ex: 'seu-projeto.appspot.com').
            web_api_key (str): A chave de API web pública do Firebase.
        """
        try:
            # Inicializa o app apenas se ainda não houver um inicializado.
            firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred, {"storageBucket": storage_bucket})
            print("Firebase inicializado com sucesso!")

        self.db = firestore.client()
        self.bucket = storage.bucket()
        self.web_api_key = web_api_key

    # --- MÉTODOS DO FIRESTORE (BANCO DE DADOS) ---

    def add_document(self, collection_name: str, data: dict) -> str | None:
        """Adiciona um novo documento a uma coleção do Firestore.

        Args:
            collection_name (str): O nome da coleção onde o documento
                                   será adicionado.
            data (dict): Um dicionário contendo os dados do documento.

        Returns:
            str | None: O ID do documento recém-criado, ou None em caso de erro.
        """
        try:
            _, doc_ref = self.db.collection(collection_name).add(data)
            return doc_ref.id
        except Exception:
            return None

    def set_document(self, collection_name: str, document_id: str, data: dict):
        """Cria ou sobrescreve um documento no Firestore.

        Se o documento com o ID especificado não existir, ele será criado.
        Se existir, ele será sobrescrito com os novos dados.

        Args:
            collection_name (str): O nome da coleção do documento.
            document_id (str): O ID do documento a ser criado ou sobrescrito.
            data (dict): Um dicionário com os dados a serem salvos.
        """
        try:
            self.db.collection(collection_name).document(document_id).set(data)
        except Exception:
            pass

    def get_document(self, collection_name: str, document_id: str) -> dict | None:
        """Busca um único documento do Firestore pelo seu ID.

        Args:
            collection_name (str): O nome da coleção do documento.
            document_id (str): O ID do documento a ser buscado.

        Returns:
            dict | None: Um dicionário com os dados do documento, ou None se
                         o documento não for encontrado ou em caso de erro.
        """
        try:
            doc = self.db.collection(collection_name).document(document_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception:
            return None

    def get_all_documents(self, collection_name: str) -> list[dict]:
        """Busca todos os documentos de uma coleção.

        Args:
            collection_name (str): O nome da coleção a ser lida.

        Returns:
            list[dict]: Uma lista de dicionários, onde cada dicionário representa
                        um documento (com seu ID como chave). Retorna uma lista
                        vazia em caso de erro.
        """
        try:
            docs = self.db.collection(collection_name).stream()
            return [{doc.id: doc.to_dict()} for doc in docs]
        except Exception:
            return []

    def update_document(self, collection_name: str, document_id: str, data: dict):
        """Atualiza um documento existente no Firestore.

        Args:
            collection_name (str): O nome da coleção do documento.
            document_id (str): O ID do documento a ser atualizado.
            data (dict): Um dicionário com os campos a serem atualizados.
        """
        try:
            self.db.collection(collection_name).document(document_id).update(data)
        except Exception:
            pass

    def delete_document(self, collection_name: str, document_id: str):
        """Deleta um documento do Firestore.

        Args:
            collection_name (str): O nome da coleção do documento.
            document_id (str): O ID do documento a ser deletado.
        """
        try:
            self.db.collection(collection_name).document(document_id).delete()
        except Exception:
            pass

    # --- MÉTODOS DO STORAGE (ARQUIVOS) ---

    def upload_file(
        self, file_content: bytes, storage_path: str, content_type: str | None = None
    ) -> str | None:
        """Faz o upload de um arquivo para o Cloud Storage a partir de seu conteúdo em bytes.

        Args:
            file_content (bytes): O conteúdo do arquivo em bytes a ser enviado.
            storage_path (str): O caminho de destino no Cloud Storage
                                (ex: 'documentos/meu_arquivo.pdf').
            content_type (str | None): O tipo MIME do arquivo (ex: 'application/pdf').
                                       Se None, o tipo será inferido pelo Storage.

        Returns:
            str | None: A URL pública do arquivo após o upload, ou None em
                        caso de erro.
        """
        try:
            blob = self.bucket.blob(storage_path)
            if content_type:
                blob.upload_from_string(file_content, content_type=content_type)
            else:
                blob.upload_from_string(file_content)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            print(f"Erro no upload de arquivo: {e}")
            return None

    def download_file(self, storage_path: str, local_path: str):
        """Baixa um arquivo do Cloud Storage para o sistema local.

        Args:
            storage_path (str): O caminho do arquivo no Cloud Storage.
            local_path (str): O caminho de destino local para salvar o arquivo.
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.download_to_filename(local_path)
        except Exception:
            pass

    def delete_file(self, storage_path: str) -> bool:
        """Deleta um arquivo do Cloud Storage.

        Args:
            storage_path (str): O caminho do arquivo no Cloud Storage a ser
                                deletado.

        Returns:
            bool: True se o arquivo foi deletado com sucesso, False caso contrário.
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Erro ao deletar arquivo do Storage: {e}")
            return False

    # --- MÉTODOS DE AUTENTICAÇÃO ---

    def create_user_record(
        self, email: str, password: str, display_name: str = None
    ) -> UserRecord:
        """Cria um novo usuário no Firebase Authentication e retorna o UserRecord.

        Note: O tratamento de erros (e-mail já existe, senha fraca) é de
        responsabilidade do método chamador.

        Args:
            email (str): O endereço de e-mail do novo usuário.
            password (str): A senha do novo usuário.
            display_name (str, optional): O nome de exibição do usuário.
                Padrão é `None`.

        Returns:
            UserRecord: O registro do usuário recém-criado.
        """
        user_record = auth.create_user(
            email=email, password=password, display_name=display_name
        )
        return user_record

    def get_user_by_email(self, email: str) -> UserRecord | None:
        """Busca um usuário no Firebase Authentication pelo e-mail.

        Args:
            email (str): O endereço de e-mail do usuário a ser buscado.

        Returns:
            UserRecord | None: O registro do usuário se ele for encontrado,
            caso contrário, `None`.
        """
        try:
            return auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            return None

    def sign_in_with_email_and_password(self, email: str, password: str) -> dict:
        """Faz login usando a API REST do Firebase Authentication.

        Esta função não lida com exceções, delegando o tratamento para o método
        chamador.

        Args:
            email (str): O e-mail do usuário.
            password (str): A senha do usuário.

        Returns:
            dict: Um dicionário com os dados do usuário, incluindo o token.

        Raises:
            requests.exceptions.HTTPError: Se a solicitação de login falhar
            (ex: credenciais inválidas).
        """
        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.web_api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(login_url, json=payload)
        response.raise_for_status()
        return response.json()

    def send_password_reset_email(self, email: str) -> None:
        """Envia um e-mail de redefinição de senha usando a API REST.

        Esta função não lida com exceções, delegando o tratamento para o método
        chamador.

        Args:
            email (str): O e-mail para o qual o e-mail de redefinição
            será enviado.

        Raises:
            requests.exceptions.HTTPError: Se a solicitação falhar (ex: e-mail não encontrado).
        """
        recovery_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.web_api_key}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        response = requests.post(recovery_url, json=payload)
        response.raise_for_status()
