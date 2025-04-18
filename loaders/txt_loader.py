"""
loaders/txt_loader.py

Módulo responsável por carregar arquivos de texto simples (TXT),
quebrando-os em parágrafos e preparando uma lista de documentos
para indexação. Cada parágrafo vira um documento com metadata.
"""


# ——————————————————————————————
def load_txt(file_path: str) -> list[dict]:
    """
    Carrega um arquivo TXT e retorna uma lista de dicionários,
    onde cada dicionário representa um parágrafo extraído do texto.

    O arquivo é lido por completo e depois dividido em parágrafos
    usando separadores de linha em branco ("\n\n").

    Args:
        file_path (str): Caminho para o arquivo .txt de entrada.

    Returns:
        List[dict]: Lista de documentos no formato:
            [
                {
                    "text": "<conteúdo do parágrafo>",
                    "metadata": {"paragraph": <índice do parágrafo>}
                },
                …
            ]
    """
    documents = []

    # Abre o arquivo de texto em UTF-8 e lê todo o conteúdo
    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    # Separa em parágrafos, removendo linhas em branco e espaços extras
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Cria um documento para cada parágrafo, associando seu índice
    for i, p in enumerate(paragraphs):
        documents.append({
            "text": p,
            "metadata": {"paragraph": i}
        })

    return documents


# ——————————————————————————————
# Teste rápido
if __name__ == "__main__":
    # Executa o loader em um arquivo de teste e exibe resultados
    docs = load_txt("data/rotina_1.txt")
    print(f"✅ Carregados {len(docs)} parágrafos")
    print("Parágrafo 0:\n", docs[0])
