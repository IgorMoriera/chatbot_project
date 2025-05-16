"""
app.py

Módulo de interface web para o Chatbot Documental Inteligente, incluindo:
- Configuração e inicialização do Streamlit (título, ícone e layout)
- Carregamento dos módulos internos (LLM e contexto) com tratamento de erro
- Injeção de CSS customizado para estilização de mensagens e cabeçalho
- Renderização do cabeçalho centralizado (logo, título e subtítulo) em HTML puro
- Gestão de histórico de conversas via 'st.session_state'
- Campo de entrada de perguntas ('st.chat_input') e botão para limpar histórico
- Processamento das perguntas: busca de contexto, chamada ao LLM e medição de tempo
- Exibição das interações com estilos distintos (usuário, bot, erro) e detalhes em expander
"""

# ——————————————————————————————
# Biliotecas
import time
import base64
import streamlit as st

# Importação de módulos internos
try:
    from llm.llm import obter_resposta_llama
    from app_config.app_context import get_context
    from app_config.prompt_builder import build_prompt
except ImportError as e:
    st.error(f"Erro crítico: módulos não encontrados – {e}")
    st.stop()

# ——————————————————————————————
# Configura as propriedades gerais da página no Streamlit
st.set_page_config(
    page_title="🧠 Inteligent Documents",
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
# Rodapé com seu nome
footer_html = """
                <div style="
                    text-align: left;
                    margin-top: 2rem;
                    padding-top: 1rem;
                    border-top: 1px solid #444;
                    color: #ffffff;
                    font-family: Roboto, sans-serif;
                    font-size: 0.8rem;
                ">
                    By: Igor de Paula Souza Moreira
                </div>
                """
st.markdown(footer_html, unsafe_allow_html=True)

# ——————————————————————————————
# Cabeçalho centralizado em HTML (logo, título e subtítulo)
st.markdown(f"""
                <div class="header-container">
                    <img src="data:image/png;base64,{logo_b64}" alt="Logo" />
                    <h1 style="text-align: center; color: #0088CC; font-family: Roboto, sans-serif;">
                        🧠 Inteligent Documents
                    </h1>
                    <p style="text-align: center; color: #A3BFFA; font-family: Roboto, sans-serif;">
                        Faça perguntas sobre seus documentos e obtenha respostas contextualizadas
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
    # Cria três colunas: uma vazia à esquerda, outra ao centro (onde ficará o input) e mais uma vazia à direita
    col_l, col_c, col_r = st.columns([1, 4, 1])

    # No centro, renderizamos só o chat_input
    with col_c:
        user_question = st.chat_input("Digite sua pergunta...", key="input")

    # Embaixo, fora do col_c, podemos manter o botão de limpar (ou mover para col_r, se quiser)
    if st.button("🗑️ Limpar Histórico"):
        st.session_state.history = []
        st.experimental_rerun()

# ——————————————————————————————
# Processa a pergunta do usuário
if user_question:
    with st.spinner("Buscando resposta nos documentos..."):
        start_time = time.time()
        try:

            # 1) Recupera contexto, lista de fontes e distância média
            contexto, fontes, distancia_media = get_context(user_question)

            # 2) Monta prompt único reutilizável
            prompt = build_prompt(user_question, contexto)

            # 4) Gera a resposta via Gemma 3
            resposta = obter_resposta_llama(pergunta=prompt, contexto="")

            # 5) Formata a mensagem de retorno incluindo fontes e distância média
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
