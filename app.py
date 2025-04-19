"""
store/chroma_store.py

Este módulo abstrai toda a lógica de comunicação com o ChromaDB, oferecendo:

1. Configuração e inicialização do cliente Chroma
   - Lê variáveis de ambiente (URL, caminho de persistência, etc.)
   - Instancia um único cliente global para reutilização

2. Função de embedding de texto
   - Utiliza o modelo 'all-MiniLM-L6-v2' do SentenceTransformers
   - Recebe uma lista de strings e retorna uma lista de vetores de embedding

3. Criação e recuperação de coleção (collection)
   - get_or_create_collection(name: str) → Collection
   - Verifica se já existe uma coleção com o nome fornecido; se não, cria uma nova

4. Operações sobre a coleção
   - add_documents(docs: List[Document], collection_name: str)
     • Converte cada documento em embedding
     • Insere vetores + metadados na coleção especificada
   - clear_collection(collection_name: str)
     • Remove todos os vetores e metadados daquela coleção

Cada função retorna objetos ou dados prontos para uso na camada de aplicação,
isola o código de baixo nível do ChromaDB e garante que seu pipeline de
documentos mantenha sempre consistência e persistência de dados.
"""

import base64
# ——————————————————————————————
# Biliotecas
import time

import streamlit as st

# Importação de módulos internos
try:
    from llm.llm import obter_resposta_llama
    from app_config.app_cotext import get_context
except ImportError as e:
    st.error(f"Erro crítico: módulos não encontrados – {e}")
    st.stop()

# ——————————————————————————————
# Configura as propriedades gerais da página no Streamlit
st.set_page_config(
    page_title="🧠 Chatbot Documental Inteligente",
    page_icon="🤖",
    layout="wide"
)

# ——————————————————————————————
# CSS personalizado para estilizar a interface
st.markdown("""
<style>
    /* Estilo para mensagens do usuário */
    .user-message {
        padding: 1rem;
        border-radius: 15px;
        background: #3C3D37;
        margin: 1rem 0;
        max-width: 80%;
        float: right;
        color: #FFFFFF;
        border: 1px solid #697565;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        animation: fadeIn 0.3s ease-in;
    }
    .user-message b { font-weight: bold; }

    /* Estilo para mensagens do bot */
    .bot-message {
        padding: 1rem;
        border-radius: 15px;
        background: #3A6073;
        margin: 1rem 0;
        max-width: 80%;
        float: left;
        color: #FFFFFF;
        border: 1px solid #A3BFFA;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        animation: fadeIn 0.3s ease-in;
    }
    .bot-message b { font-weight: bold; }

    /* Estilo para mensagens de erro */
    .error-message {
        padding: 1rem;
        border-radius: 15px;
        background: #5C2D2D;
        margin: 1rem 0;
        max-width: 80%;
        float: left;
        color: #FFFFFF;
        border: 1px solid #EF5350;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        font-family: 'Roboto', sans-serif;
        font-size: 16px;
        animation: fadeIn 0.3s ease-in;
    }

    /* Animação de entrada para mensagens */
    @keyframes fadeIn {
        from { 
               opacity: 0; transform: translateY(10px); 
        }       
        to { 
             opacity: 1; transform: translateY(0); 
        }
    }

    /* Estilo para divisores */
    .stDivider { 
                 background-color: #0088CC;
                 height: 1px; 
                 opacity: 0.3;
    }
    
    /* Estilo para legendas */
    .stCaption { 
                 color: #A3BFFA !important;
    }

    /* Estilo para o expander */
    .stExpander {
        background-color: #2A2C33;
        border: 1px solid #697565;
        border-radius: 10px;
        padding: 0.5rem;
    }
    .stExpander div { color: #FFFFFF; font-family: 'Roboto', sans-serif; font-size: 14px; }
    .stExpander p { color: #FFFFFF; }

    /* Divisor dentro do expander */
    .expander-divider { background-color: #A3BFFA; height: 1px; opacity: 0.3; margin: 0.5rem 0; }
    .fontes-container { display: inline; color: #A3BFFA; font-size: 14px; }
    .stExpander > div > div > div > div > p {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #A9A9A9 !important;
    }

    /* Cabeçalho centralizado: logo, título e subtítulo */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 1rem;
    }
    .header-container img {
        width: 200px;
        height: auto;
        margin-bottom: 0.5rem;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# ——————————————————————————————
# carregue o logo e transforme em base64
with open("logo.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()

# ——————————————————————————————
# Cabeçalho centralizado em HTML (logo, título e subtítulo)
st.markdown(f"""
                <div class="header-container">
                    <img src="data:image/png;base64,{logo_b64}" alt="Logo" />
                    <h1 style="text-align: center; color: #0088CC; font-family: Roboto, sans-serif;">
                        🧠 Iteligents Documents
                    </h1>
                    <p style="text-align: center; color: #A3BFFA; font-family: Roboto, sans-serif;">
                        Faça perguntas sobre seus documentos e obtenha respostas contextualizadas
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

# ——————————————————————————————
# Estado de sessão para armazenar o histórico de conversas
if "history" not in st.session_state:
    st.session_state.history = []

# ——————————————————————————————
# Área de entrada de perguntas com botão de limpar
with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        user_question = st.chat_input("Digite sua pergunta...", key="input")
    with col2:
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.history = []
            st.rerun()

# ——————————————————————————————
# Processa a pergunta do usuário
if user_question:
    with st.spinner("Buscando resposta nos documentos..."):
        start_time = time.time()
        try:
            contexto, fontes, distancia_media = get_context(user_question)
            prompt = (
                f"Responda à pergunta a seguir com base exclusivamente no tema relacionado à pergunta. "
                f"Ignore informações de outros temas ou documentos, mesmo que estejam presentes no contexto. "
                f"Detalhe cada etapa ou ponto mencionado no contexto, explicando o que significa e como aplicá-lo. "
                f"Não resuma demais; forneça uma explicação completa para cada item. "
                f"Pergunta: {user_question}\n\n"
                f"Contexto:\n{contexto}\n\n"
                f"Responda de forma clara, concisa e detalhada, abordando apenas o tema principal da pergunta."
            )
            resposta = obter_resposta_llama(pergunta=prompt, contexto="")
            processing_time = time.time() - start_time
            st.session_state.history.append({
                "pergunta": user_question,
                "resposta": resposta,
                "tempo": f"{processing_time:.2f}s",
                "fontes": fontes,
                "contexto": contexto,
                "distancia_media": distancia_media
            })
        except Exception as e:
            st.error(f"Erro ao processar pergunta: {e}")
            st.session_state.history.append({
                "pergunta": user_question,
                "resposta": "Desculpe, ocorreu um erro ao processar sua solicitação.",
                "erro": True
            })

# ——————————————————————————————
# Renderiza o histórico de conversas
with st.container():
    for entry in st.session_state.history:
        st.markdown(
            f"<div class='user-message'>🙃 <b>VOCÊ:</b> {entry['pergunta']}</div>",
            unsafe_allow_html=True
        )
        if entry.get("erro"):
            st.markdown(
                f"<div class='error-message'>❌ <b>ERRO:</b> {entry['resposta']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='bot-message'>🤖 <b>ASSISTENTE:</b> {entry['resposta']}</div>",
                unsafe_allow_html=True
            )
            with st.expander("📋 **Detalhes da Resposta:**"):
                st.markdown(f"**⏱️ Tempo de processamento:** {entry['tempo']}")
                st.markdown("<div class='expander-divider'></div>", unsafe_allow_html=True)
                if entry['fontes']:
                    fontes_str = ", ".join(entry['fontes'])
                    distancia_media = entry.get('distancia_media', 0.0)
                    st.markdown(
                        f"**📚 Fontes utilizadas:** <span class='fontes-container'>{fontes_str}</span> "
                        f"**- Distância média:** <span class='fontes-container'>{distancia_media:.3f}</span>",
                        unsafe_allow_html=True
                    )
                st.markdown("<div class='expander-divider'></div>", unsafe_allow_html=True)
                st.markdown("**🔍 Contexto utilizado:**")
                st.write(entry['contexto'])
        st.divider()
