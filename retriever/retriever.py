"""
retriever/retriever.py

Módulo responsável por dividir blocos brutos de texto em “chunks”
menores, facilitando a indexação e recuperação eficiente dos documentos.
Utiliza RecursiveCharacterTextSplitter do LangChain para realizar
o chunking com tamanho e sobreposição configuráveis.
"""

# ——————————————————————————————
from langchain.text_splitter import RecursiveCharacterTextSplitter


# ——————————————————————————————
def chunk_documents(
    raw_docs: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> list[dict]:
    """
    Divide cada documento bruto em pedaços menores (chunks) para indexação.

    Cada item em raw_docs deve ser um dicionário com chaves:
        - "text": string contendo o conteúdo a ser dividido
        - "metadata": dict com informações do documento original
                      (por exemplo, número da página, linha ou parágrafo)

    Args:
        raw_docs (List[dict]): Lista de documentos brutos no formato:
            [
                {"text": "<texto completo>", "metadata": {...}},
                …
            ]
        chunk_size (int): Tamanho máximo (em caracteres) de cada chunk.
        chunk_overlap (int): Quantidade de caracteres duplicados entre chunks
                             consecutivos para manter contexto.

    Returns:
        List[dict]: Lista de chunks prontos para indexação, cada um contendo:
            {
                "id": "<origem>_<índice do chunk>",
                "text": "<texto do pedaço>",
                "metadata": { ... metadados originais ..., "chunk": <índice do chunk> }
            }
    """
    # Configura o splitter com tamanho e overlap desejados
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunked = []
    # Itera sobre cada documento original
    for doc in raw_docs:
        # Divide o texto em múltiplos pedaços
        texts = splitter.split_text(doc["text"])
        for i, t in enumerate(texts):
            # Copia metadados originais e adiciona índice do chunk
            meta = doc["metadata"].copy()
            meta["chunk"] = i

            # Identifica origem para compor o ID (página, linha ou parágrafo)
            origin = (
                meta.get("page")
                or meta.get("row")
                or meta.get("paragraph")
                or "0"
            )

            # Adiciona o chunk à lista de saída
            chunked.append({
                "id": f"{origin}_{i}",
                "text": t,
                "metadata": meta
            })

    return chunked


# ——————————————————————————————
# Teste rápido
if __name__ == "__main__":
    from loaders.txt_loader import load_txt

    # Carrega arquivo de teste em data/rotina_2.txt (ajuste caminho conforme necessário)
    raw = load_txt("data/rotina_2.txt")
    chunks = chunk_documents(raw)

    print(f"✅ Gerados {len(chunks)} chunks a partir de {len(raw)} blocos brutos")
    print("Exemplo de chunk[0]:", chunks[0])
