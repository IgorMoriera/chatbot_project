"""
embeddings/embedder.py

Módulo responsável por gerar embeddings a partir de textos usando o SentenceTransformer.
"""

# ——————————————————————————————
from numpy import ndarray
from sentence_transformers import SentenceTransformer

# Inicializa o modelo de embeddings all-MiniLM-L6-v2
_model = SentenceTransformer("all-MiniLM-L6-v2")


# ——————————————————————————————
def embed_texts(texts: list[str]) -> ndarray:
    """
    Converte uma lista de textos em embeddings numéricos.

    Args:
        texts (list[str]): Lista de strings a serem transformadas em embeddings.

    Returns:
        list[list[float]]: Lista de vetores de embeddings correspondentes a cada texto de entrada.
    """
    embeddings = _model.encode(texts, show_progress_bar=True)
    return embeddings


# ——————————————————————————————
if __name__ == "__main__":
    # Teste rápido da função embed_texts
    samples = ["Texto de exemplo para embedding.", "Outro pedaço de texto."]
    embs = embed_texts(samples)
    print(f"✅ Gerados {len(embs)} embeddings, dimensão do primeiro: {len(embs[0])}")
