"""
app_2.py

Interface Streamlit para o Chatbot Documental Inteligente.
Fornece uma aplicação web onde o usuário pode:
  - Enviar perguntas relacionadas ao conteúdo indexado
  - Visualizar os trechos de documentos usados como contexto
  - Conferir o tempo de resposta e as fontes consultadas
"""

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
# Número padrão de trechos (chunks) a recuperar para cada pergunta
K_RESULTS = int(os.getenv("K_RESULTS", 3))

# ——————————————————————————————
# Importação de módulos internos
# Aqui buscamos o cliente Chroma e a função de geração via Ollama
try:
    from store.chroma_store import collection
    from llm.llm import obter_resposta_llama
except ImportError as e:
    # Se algum módulo não existir, exibe erro crítico e interrompe a execução
    st.error(f"Erro crítico: Módulos não encontrados – {str(e)}")
    st.stop()


# ——————————————————————————————
# Funções auxiliares

def get_context(query: str, k: int = K_RESULTS) -> Tuple[str, List[str]]:
    """
    Recupera os k trechos mais relevantes para a pergunta e extrai as fontes.

    Args:
        query (str): Texto da pergunta do usuário.
        k (int): Quantidade de resultados relevantes a retornar.

    Returns:
        Tuple[str, List[str]]:
            - Contexto concatenado (string) com os textos dos documentos.
            - Lista de nomes de arquivos que serviram de fonte.
    """
    try:
        # Consulta o ChromaDB solicitando documentos e metadados
        result = collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas"]
        )
        documentos = result["documents"][0]
        metadados  = result["metadatas"][0]

        # Extrai nomes de arquivo únicos a partir dos metadados
        fontes = list({m["source"] for m in metadados if "source" in m})

        # Concatena todos os trechos em um único texto
        contexto = "\n\n".join(documentos)
        return contexto, fontes

    except Exception as e:
        # Em caso de falha na busca, exibe erro na UI e retorna vazio
        st.error(f"Erro na busca de contexto: {str(e)}")
        return "", []


# ——————————————————————————————
# Configuração da página Streamlit
st.set_page_config(
    page_title="🧠 Chatbot Documental Inteligente",
    page_icon="🤖",
    layout="centered"
)

# CSS customizado para tema escuro e balões de chat
st.markdown("""
<style>
    :root {
        --fundo: #181C14;
        --usuario: #3C3D37;
        --assistente: #697565;
        --destaque: #ECDFCC;
    }
    .stApp { background-color: var(--fundo); color: var(--destaque); }
    .conversa-container { max-width: 800px; margin: 0 auto; padding: 1rem; }
    .user-message {
        background: var(--usuario); color: var(--destaque);
        border-radius: 15px 15px 0 15px; padding: 1.2rem;
        margin: 1rem 0 1rem 30%; position: relative;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .bot-message {
        background: var(--assistente); color: var(--destaque);
        border-radius: 15px 15px 15px 0; padding: 1.2rem;
        margin: 1rem 30% 1rem 0; position: relative;
        box-shadow: -2px 2px 5px rgba(0,0,0,0.1);
    }
    .user-message::after {
        content: ''; position: absolute; right: -10px; top: 15px;
        border-width: 10px 0 10px 10px; border-style: solid;
        border-color: transparent transparent transparent var(--usuario);
    }
    .bot-message::before {
        content: ''; position: absolute; left: -10px; top: 15px;
        border-width: 10px 10px 10px 0; border-style: solid;
        border-color: transparent var(--assistente) transparent transparent;
    }
    .detalhes-tecnicos { background: #2a2d27; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ——————————————————————————————
# Inicialização do estado de sessão para histórico de conversas
if "history" not in st.session_state:
    st.session_state.history = []  # Cada item: dict com 'pergunta', 'resposta', 'tempo', 'fontes', 'contexto'

# ——————————————————————————————
# Título e subtítulo da aplicação
st.title("🧠 Chatbot Documental Inteligente")
st.caption("Faça perguntas sobre seus documentos e obtenha respostas contextualizadas")

# ——————————————————————————————
# Área de entrada de texto (chat_input) e processamento da pergunta
with st.container():
    user_input = st.chat_input("Digite sua pergunta...", key="input")

    if user_input:
        with st.spinner("🔍 Analisando documentos..."):
            start_time = time.time()

            try:
                # 1) Recupera contexto e fontes
                contexto, fontes = get_context(user_input)

                # 2) Gera resposta chamando o LLM local via Ollama
                resposta = obter_resposta_llama(user_input, contexto)

                # 3) Calcula tempo de processamento
                processing_time = time.time() - start_time

                # 4) Adiciona interação ao histórico
                st.session_state.history.append({
                    "pergunta":  user_input,
                    "resposta":  resposta,
                    "tempo":     f"{processing_time:.2f}s",
                    "fontes":    fontes,
                    "contexto":  contexto
                })

            except Exception as e:
                # Caso ocorra erro, exibe mensagem e interrompe apenas esta interação
                st.error(f"Erro ao processar: {str(e)}")

# ——————————————————————————————
# Renderização do histórico de conversas
for interacao in st.session_state.history:
    # Bloco de mensagem do usuário (alinhado à direita)
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 VOCÊ</strong><br><br>
        {interacao['pergunta']}
    </div>
    """, unsafe_allow_html=True)

    # Bloco de resposta do assistente (alinhado à esquerda)
    st.markdown(f"""
    <div class="bot-message">
        <strong>🤖 ASSISTENTE</strong><br><br>
        {interacao['resposta']}
    </div>
    """, unsafe_allow_html=True)

    # Área expansível com detalhes técnicos (tempo e fontes)
    with st.expander("⚙️ Detalhes da Resposta"):
        cols = st.columns([1, 3])
        with cols[0]:
            st.metric("⏱ Tempo", interacao['tempo'])
        with cols[1]:
            if interacao['fontes']:
                st.write("**📚 Fontes utilizadas:**")
                for fonte in interacao['fontes']:
                    st.caption(f"• {fonte}")

    # Área expansível com o contexto completo utilizado no prompt
    with st.expander("🔍 Contexto completo utilizado"):
        st.code(interacao['contexto'], language='markdown')

    st.divider()
