"""
app.py

Aplicação Streamlit para o Chatbot Documental Inteligente.
Permite ao usuário:
  - Fazer perguntas sobre o conteúdo indexado de documentos.
  - Visualizar trechos de contexto recuperados.
  - Conferir tempo de resposta e fontes utilizadas.
"""

# ——————————————————————————————
import os
import time
from typing import Tuple, List

import streamlit as st
from dotenv import load_dotenv

# ——————————————————————————————
# Carregamento de variáveis de ambiente
load_dotenv()

# ——————————————————————————————
# Configurações globais
# Número padrão de resultados contextuais a recuperar
K_RESULTS = int(os.getenv("K_RESULTS", 3))

# ——————————————————————————————
# Importação de módulos internos
# Busca o cliente ChromaDB e a função de geração via Ollama/Gemma3
try:
    from store.chroma_store import collection
    from llm.llm import obter_resposta_llama
except ImportError as e:
    st.error(f"Erro crítico: módulos não encontrados – {e}")
    st.stop()


# ——————————————————————————————
# Função auxiliar para recuperação de contexto
def get_context(query: str, k: int = K_RESULTS) -> Tuple[str, List[str]]:
    """
    Busca os k trechos mais relevantes no ChromaDB e extrai as fontes.

    Args:
        query (str): Pergunta inserida pelo usuário.
        k (int): Quantidade de chunks a retornar para formar o contexto.

    Returns:
        Tuple[str, List[str]]:
            - String com os trechos concatenados.
            - Lista de nomes de arquivos que serviram de fonte.
    """
    try:
        # Executa a query no ChromaDB incluindo documentos e metadados
        result = collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas"]
        )
        documentos = result["documents"][0]
        metadados  = result["metadatas"][0]

        # Extrai nomes de fonte únicos para apresentar ao usuário
        fontes = list({m["source"] for m in metadados if "source" in m})
        contexto = "\n\n".join(documentos)
        return contexto, fontes

    except Exception as e:
        st.error(f"Erro na busca de contexto: {e}")
        return "", []

# ——————————————————————————————
# Configuração da página Streamlit
st.set_page_config(
    page_title="🧠 Chatbot Documental Inteligente",
    page_icon="🤖",
    layout="wide"
)

# ——————————————————————————————
# CSS customizado para balões de conversa
st.markdown("""
<style>
    .user-message {
        padding: 1rem;
        border-radius: 15px;
        background: #3C3D37;
        margin: 1rem 0;
        max-width: 80%;
        float: right;
        color: #FFFFFF;
        border: 1px solid #bdc3c7;
        font-weight: bold;
    }
    .bot-message {
        padding: 1rem;
        border-radius: 15px;
        background: #697565;
        margin: 1rem 0;
        max-width: 80%;
        float: left;
        color: #FFFFFF;
        border: 1px solid #aed6f1;
        line-height: 1.6;
    }
    .css-1q1n0ol {
        color: #34495e !important;
    }
</style>
""", unsafe_allow_html=True)

# ——————————————————————————————
# Estado de sessão para histórico de conversas
if "history" not in st.session_state:
    st.session_state.history = []  # Cada item: dict com pergunta, resposta, tempo, fontes, contexto

# ——————————————————————————————
# Título e subtítulo da aplicação
st.title("🧠 Chatbot Documental Inteligente")
st.caption("Faça perguntas sobre seus documentos e obtenha respostas contextualizadas")

# ——————————————————————————————
# Área de entrada de perguntas
with st.container():
    user_question = st.chat_input("Digite sua pergunta...", key="input")

# ——————————————————————————————
# Processamento da pergunta ao clicar em "Enviar"
if user_question:
    with st.spinner("🔍 Analisando documentos e gerando resposta..."):
        start_time = time.time()
        try:
            # 1) Recupera contexto e fontes
            contexto, fontes = get_context(user_question)

            # 2) Gera resposta via LLM local (Gemma3)
            resposta = obter_resposta_llama(
                pergunta=user_question,
                contexto=contexto
            )

            # 3) Calcula tempo de processamento
            processing_time = time.time() - start_time

            # 4) Armazena interação no histórico
            st.session_state.history.append({
                "pergunta": user_question,
                "resposta": resposta,
                "tempo": f"{processing_time:.2f}s",
                "fontes": fontes,
                "contexto": contexto
            })

        except Exception as e:
            # Em caso de erro, notifica e registra apenas a pergunta
            st.error(f"Erro ao processar pergunta: {e}")
            st.session_state.history.append({
                "pergunta": user_question,
                "resposta": "Desculpe, ocorreu um erro ao processar sua solicitação.",
                "erro": True
            })

# ——————————————————————————————
# Renderização do histórico de conversas
for entry in st.session_state.history:
    # Mensagem do usuário (direita)
    st.markdown(
        f"<div class='user-message'>🙋 **VOCÊ:** {entry['pergunta']}</div>",
        unsafe_allow_html=True
    )

    # Mensagem do assistente (esquerda)
    if entry.get("erro"):
        st.markdown(
            f"<div class='bot-message'>❌ **ERRO:** {entry['resposta']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-message'>🤖 **ASSISTENTE:** {entry['resposta']}</div>",
            unsafe_allow_html=True
        )

        # Exibe tempo e fontes
        cols = st.columns([1, 4])
        with cols[0]:
            st.caption(f"⏱️ {entry['tempo']}")
        with cols[1]:
            if entry['fontes']:
                st.caption(f"📚 Fontes: {', '.join(entry['fontes'])}")

        # Expande para mostrar contexto completo
        with st.expander("🔍 Ver contexto utilizado"):
            st.write(entry['contexto'])

    st.divider()
