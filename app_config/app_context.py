"""
app_context_filter.py

Extensão do helper de contexto para o Chatbot Documental.
Fornece uma função avançada de recuperação de contexto que:
  1. Busca trechos mais relevantes no ChromaDB (documents, metadatas, distances)
  2. Agrupa por tema (campo 'title' nos metadados)
  3. Seleciona apenas o tema com menor distância média
  4. Dentro desse tema, escolhe o documento (fonte) mais relevante
  5. Retorna o contexto (trechos do documento selecionado), a lista de fontes e a distância média
"""

# ——————————————————————————————
# Bibliotecas
import os
from typing import Tuple, List
import streamlit as st
from dotenv import load_dotenv

# ——————————————————————————————
# Carregamento de configurações de ambiente
load_dotenv()

# ——————————————————————————————
# Parâmetros globais
# Quantidade de chunks a recuperar por pergunta
K_RESULTS = int(os.getenv("K_RESULTS"))

# Limite de caracteres do contexto final a enviar ao LLM
MAX_CONTEXT_LENGTH = 2000

# ——————————————————————————————
# Importação de módulos internos do projeto
try:
    from store.chroma_store import collection
    from llm.llm import obter_resposta_llama

except ImportError as e:
    # Se falhar a importação, exibe erro crítico e encerra a app
    st.error(f"Erro crítico: módulos não encontrados – {e}")
    st.stop()


# ——————————————————————————————
def get_context(
    query: str,
    k: int = K_RESULTS
) -> Tuple[str, List[str], float]:
    """
    Busca e filtra o contexto mais relevante no ChromaDB por tema e documento.

    Steps:
      1. Executa consulta no ChromaDB pedindo documentos, metadados e distâncias.
      2. Agrupa trechos por tema (campo 'title' nos metadados).
      3. Identifica o tema com menor distância média.
      4. Filtra trechos apenas desse tema e agrupa por documento (fonte).
      5. Seleciona o documento mais relevante (menor distância média).
      6. Concatena os trechos do documento selecionado, limita tamanho e retorna.

    Args:
        query (str): Pergunta inserida pelo usuário.
        k (int): Número de chunks a recuperar inicialmente.

    Returns:
        Tuple[str, List[str], float]:
            - contexto (str): Trechos concatenados do documento mais relevante.
            - fontes (List[str]): Lista com o nome do arquivo/fonte selecionada.
            - distancia_media (float): Distância média dos trechos utilizados.
    """
    try:
        # 1) Query no Chroma: documentos, metadados e distâncias
        result = collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        documentos = result["documents"][0]
        metadados = result["metadatas"][0]
        distances = result["distances"][0]

        # 2) Extrai temas de cada trecho via campo 'title'
        temas = [
            meta.get("title", "Desconhecido")
            for meta in metadados
        ]

        # 3) Agrupa distâncias por tema para calcular média
        tema_distancia = {}
        for tema, dist in zip(temas, distances):
            tema_distancia.setdefault(tema, []).append(dist)

        # 4) Seleciona o tema com menor distância média
        tema_mais_relevante = min(
            tema_distancia,
            key=lambda t: sum(tema_distancia[t]) / len(tema_distancia[t])
        )

        # 5) Filtra trechos e distâncias pelo tema escolhido e agrupa por documento
        doc_distancia = {}
        doc_trechos = {}
        fontes_filtradas = set()

        for doc, meta, tema, dist in zip(documentos, metadados, temas, distances):
            if tema == tema_mais_relevante:
                source = meta.get("source", "Desconhecido")
                doc_distancia.setdefault(source, []).append(dist)
                doc_trechos.setdefault(source, []).append(doc)
                fontes_filtradas.add(source)

        # Se não encontrou nenhum trecho para o tema, retorna vazio
        if not doc_distancia:
            return "", [], 0.0

        # 6) Escolhe o documento (source) com menor distância média
        doc_mais_relevante = min(
            doc_distancia,
            key=lambda d: sum(doc_distancia[d]) / len(doc_distancia[d])
        )
        distancia_media = sum(doc_distancia[doc_mais_relevante]) / len(doc_distancia[doc_mais_relevante])

        # 7) Concatena apenas os trechos do documento selecionado e aplica limite de tamanho
        trechos = doc_trechos[doc_mais_relevante]
        contexto = "\n\n".join(trechos)[:MAX_CONTEXT_LENGTH]

        # Retorna contexto, lista de fontes (única) e distância média
        return contexto, [doc_mais_relevante], distancia_media

    except Exception as error:
        # Em caso de erro na consulta, exibe mensagem na UI e retorna valores padrão
        st.error(f"Erro na busca de contexto: {error}")
        return "", [], 0.0
