"""
loaders/pdf_loader.py

Módulo responsável por carregar arquivos PDF e converter cada página em um objeto Document genérico.
Cada documento contém o texto extraído da página e metadados com o número da página.
"""

# ——————————————————————————————
import fitz  # PyMuPDF, biblioteca para leitura de PDFs


# ——————————————————————————————
def load_pdf(file_path: str) -> list[dict]:
    """
    Carrega um arquivo PDF e retorna uma lista de dicionários representando cada página.

    Args:
        file_path (str): Caminho para o arquivo PDF de entrada.

    Returns:
        list[dict]: Lista de documentos, onde cada documento tem:
            - 'text': string contendo o texto extraído da página
            - 'metadata': dict com {'page': número_da_página}
    """
    documents = []
    # Abre o PDF e itera sobre cada página
    with fitz.open(file_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text()  # Extrai todo o texto da página
            documents.append({
                "text": text,
                "metadata": {"page": i}
            })
    return documents


# ——————————————————————————————
if __name__ == "__main__":
    # Teste rápido para verificar carga do PDF
    sample_path = "data/rotina_6.pdf"
    docs = load_pdf(sample_path)
    print(f"✅ Carregadas {len(docs)} páginas do PDF")
    # Exibe um trecho do texto da primeira página
    print("Trecho página 0 (200 primeiros caracteres):\n", docs[0]["text"][:200])
