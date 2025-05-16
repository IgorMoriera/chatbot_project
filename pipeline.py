"""
pipeline.py

Módulo responsável por orquestrar o fluxo completo de ingestão de documentos:
  1. Limpa a coleção Chroma existente de forma segura.
  2. Varre a pasta de dados em busca de arquivos PDF, CSV e TXT.
  3. Carrega cada arquivo com o loader apropriado.
  4. Realiza chunking dos textos e gera IDs/metadados consistentes.
  5. Indexa os chunks no ChromaDB, evitando duplicatas.
  6. Apresenta um relatório final com o total de chunks na coleção.
"""

# ——————————————————————————————
# Bibliotecas
import os
from pathlib import Path
from dotenv import load_dotenv

# ——————————————————————————————
# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
data_dir = os.getenv("DATA_DIR")

# ——————————————————————————————
# Importação de loaders para diferentes tipos de arquivo
from loaders.pdf_loader import load_pdf
from loaders.csv_loader import load_csv
from loaders.txt_loader import load_txt

# Importação do splitter de texto
from retriever.retriever import chunk_documents

# Importação de funções de ChromaDB
from store.chroma_store import collection, add_documents, limpar_colecao

# ——————————————————————————————
# Limpeza inicial da coleção Chroma
print("🗑️  Limpando coleção Chroma anterior...")
if limpar_colecao():
    print("✅ Coleção limpa.\n")
else:
    print("⚠️ Atenção: Não foi possível limpar a coleção completamente!")
    print("           Verifique os logs e reinicie o Chroma se necessário.\n")


def ingest_new_files(data_dir: str = data_dir) -> None:
    """
    Realiza a ingestão incremental de documentos na coleção Chroma.

    Passos principais:
      1. Valida a existência do diretório de dados.
      2. Itera sobre arquivos PDF, CSV e TXT, filtrando por extensão.
      3. Verifica se já existem chunks com metadata['source'] igual ao nome do arquivo,
         para evitar reprocessamento de documentos já indexados.
      4. Carrega o conteúdo bruto usando o loader correspondente.
      5. Executa chunking do texto e gera IDs únicos e metadados padronizados.
      6. Adiciona os chunks ao ChromaDB usando 'add_documents'.

    Args:
        data_dir (str): Caminho para a pasta contendo os arquivos de entrada.
    """
    base = Path(data_dir)

    # Verifica se o diretório existe e é válido
    if not base.exists() or not base.is_dir():
        print(f"⚠️ Diretório {data_dir!r} não encontrado ou não é uma pasta.")
        return

    total_indexed = 0
    valid_suffixes = {".pdf", ".csv", ".txt"}

    # Processa cada arquivo na pasta
    for file_path in sorted(base.iterdir()):
        suffix = file_path.suffix.lower()
        if suffix not in valid_suffixes:
            # Ignora arquivos sem extensão suportada
            continue

        # — Verificação de duplicatas —
        try:
            existing = collection.get(
                where={"source": file_path.name},
                include=["metadatas"]
            )
            if existing and existing.get("metadatas"):
                print(f"⏭️  Pulando '{file_path.name}' (já indexado)")
                continue
        except Exception as error:
            print(f"⚠️  Erro na verificação de duplicatas: {str(error)}")
            continue

        # — Carregamento de documentos brutos —
        try:
            loader = {
                ".pdf": load_pdf,
                ".csv": load_csv,
                ".txt": load_txt
            }[suffix]
            raw_docs = loader(str(file_path))
            print(f"📂  Carregado {len(raw_docs)} documentos de '{file_path.name}'")
        except Exception as error:
            print(f"❌  Erro crítico ao ler '{file_path.name}': {str(error)}")
            continue

        # — Chunking e padronização de metadados —
        try:
            chunks = chunk_documents(raw_docs)
            for idx, chunk in enumerate(chunks):
                # Substitui metadata por um dict consistente
                chunk["metadata"] = {
                    "source": file_path.name,
                    "page": chunk.get("metadata", {}).get("page", 0),
                    "chunk_id": f"{file_path.stem}_{idx:04d}"
                }
                chunk["id"] = f"{file_path.stem}_{idx:04d}"
        except Exception as error:
            print(f"❌  Erro no chunking de '{file_path.name}': {str(error)}")
            continue

        # — Indexação no ChromaDB —
        try:
            add_documents(chunks)
            print(f"☑️  '{file_path.name}': {len(chunks)} chunks indexados")
            total_indexed += len(chunks)
        except Exception as error:
            print(f"❌  Falha na indexação de '{file_path.name}': {str(error)}")
            continue

    # Relatório final de ingestão
    print(f"\n✅  Ingestão concluída: {total_indexed} novos chunks de {data_dir}")


if __name__ == "__main__":
    # Executa todo o pipeline de ingestão
    ingest_new_files()

    # Exibe o total de chunks na coleção após ingestão
    try:
        total_chunks = collection.count()
        print(f"📊 Total de chunks na coleção: {total_chunks}")
    except Exception as e:
        print(f"\n⚠️  Não foi possível obter o total de chunks: {str(e)}")
