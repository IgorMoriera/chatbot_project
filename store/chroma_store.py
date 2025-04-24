"""
store/chroma_store.py

Módulo de abstração para interação com o ChromaDB, incluindo:
- Configuração e inicialização do cliente persistente
- Definição da função de embedding usando SentenceTransformers
- Criação/recuperação da collection para documentos
- Funções utilitárias para adicionar documentos e limpar a coleção
"""

# ——————————————————————————————
import os

import chromadb
from chromadb.utils.embedding_functions import HuggingFaceEmbeddingFunction
from dotenv import load_dotenv

# ——————————————————————————————
# 1) Carrega variáveis de ambiente do arquivo .env (opções de persistência, URL, etc.)
load_dotenv()
persist_dir = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
model_name = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
hf_api_key = os.getenv("HF_API_KEY")

# ——————————————————————————————
# 2) Cria o cliente persistente do ChromaDB, armazenando índices em disco
client = chromadb.PersistentClient(path=persist_dir)

# ——————————————————————————————
# 3) Define a função de embedding baseada em SentenceTransformers
#    Utiliza o modelo 'all-MiniLM-L6-v2' para criar vetores de alta qualidade
embedding_fn = HuggingFaceEmbeddingFunction(
    model_name=model_name,
    api_key=hf_api_key
)

# ——————————————————————————————
# 4) Garante a existência da coleção 'documents' com configuração para espaço de similaridade 'cosine'
collection = client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}  # Configuração recomendada para versões recentes do Chroma
)


# ——————————————————————————————
def add_documents(docs: list[dict]) -> None:
    """
    Insere ou atualiza documentos na coleção do ChromaDB.

    Cada item em docs deve ser um dicionário com as chaves:
        - "id": str, identificador único do chunk/documento
        - "text": str, conteúdo textual a ser indexado
        - "metadata": dict, metadados associados (e.g., fonte, número do chunk)

    Processo:
    1. Extrai ids, textos e metadatas da lista de dicionários.
    2. Chama collection.upsert() para adicionar ou atualizar registros.
    3. Persiste o estado no disco para garantir durabilidade.

    Levanta exceção em caso de erro para que o pipeline possa capturá-lo.
    """
    try:
        # Prepara listas para o método upsert
        ids = [d["id"] for d in docs]
        texts = [d["text"] for d in docs]
        metadatas = [d["metadata"] for d in docs]

        # Upsert de documentos (insere ou atualiza)
        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        # Garantia de persistência em disco
        client.persist()

    except Exception as e:
        print(f"❌ Erro ao adicionar documentos: {str(e)}")
        # Repasse da exceção para sinalizar falha no pipeline
        raise


# ——————————————————————————————
def limpar_colecao() -> bool:
    """
    Remove de forma segura todos os documentos da coleção 'documents'.

    Utiliza uma condição 'where' ampla para deletar todos os itens
    que possuam qualquer metadado 'source' (ou seja, todos os documentos).

    Retorna:
        True  - se a limpeza foi bem-sucedida
        False - em caso de falha, com mensagem de erro impressa
    """
    try:
        # Deleta todos os documentos que tenham 'source' definido (toda a coleção)
        collection.delete(where={"source": {"$ne": ""}})
        client.persist()
        return True

    except Exception as e:
        print(f"❌ Erro na limpeza: {str(e)}")
        return False


# ——————————————————————————————
if __name__ == "__main__":
    # Bloco de teste rápido para verificar a configuração da coleção e persistência
    sample = [{
        "id": "test_0",
        "text": "Teste de indexação com a nova API do Chroma.",
        "metadata": {"source": "unit-test"}
    }]
    add_documents(sample)
    total = collection.count()
    metadatas = collection.get(include=["metadatas"])["metadatas"]
    print(f"✅ Indexados {total} documento(s). Fontes: {metadatas}")
