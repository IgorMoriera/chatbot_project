"""
loaders/csv_loader.py

Módulo responsável por carregar arquivos CSV e converter cada linha em um objeto Document genérico.
Cada documento contém o texto da linha (serializado como string) e metadados com o índice da linha.
"""

# ——————————————————————————————
import pandas as pd


# ——————————————————————————————
def load_csv(file_path: str) -> list[dict]:
    """
    Carrega um arquivo CSV e retorna uma lista de dicionários representando cada linha.

    Args:
        file_path (str): Caminho para o arquivo CSV de entrada.

    Returns:
        list[dict]: Lista de documentos, onde cada documento tem:
            - 'text': string contendo o dicionário da linha
            - 'metadata': dict com {'row': índice_da_linha}
    """
    # Lê o CSV em um DataFrame do Pandas
    df = pd.read_csv(file_path)
    documents = []

    # Itera sobre cada linha, converte para dicionário e empacota em texto
    for i, row in df.iterrows():
        row_dict = row.to_dict()
        documents.append({
            "text": str(row_dict),
            "metadata": {"row": i}
        })

    return documents


# ——————————————————————————————
if __name__ == "__main__":
    # Teste rápido para verificar carga do CSV
    sample_path = "data/documentos_base.csv"
    docs = load_csv(sample_path)
    print(f"✅ Carregadas {len(docs)} linhas do CSV")
    print("Exemplo de documento de linha 0:", docs[0])
