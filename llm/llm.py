"""
llm/llm.py

Módulo responsável por interagir com o serviço Ollama para gerar respostas
do modelo local Gemma.3, montando prompts com contexto recuperado.
"""

# ——————————————————————————————
import os

import requests
from dotenv import load_dotenv

# ——————————————————————————————
# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# ——————————————————————————————
# URL e modelo padrão para o serviço Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# ——————————————————————————————
# Opções padrão de geração de texto
DEFAULT_OPTIONS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_ctx": 4096
}


# ——————————————————————————————
def obter_resposta_llama(
    pergunta: str,
    contexto: str,
    modelo: str = OLLAMA_MODEL,
    options: dict | None = None,
    timeout: int = 60
) -> str:
    """
    Obtém resposta do modelo LLaMA/Gemma3 via Ollama HTTP API.

    Constrói um prompt estruturado com o contexto e instruções claras, envia
    a requisição e trata possíveis erros de conexão ou timeout.

    Args:
        pergunta (str): Pergunta do usuário.
        contexto (str): Texto relevante previamente recuperado dos documentos.
        modelo (str): Nome do modelo a ser utilizado (ex.: "gemma3:1b").
        options (dict | None): Parâmetros de geração (temperature, top_p, num_ctx).
        timeout (int): Tempo máximo de espera pela resposta, em segundos.

    Returns:
        str: Texto retornado pelo modelo ou mensagem de erro.
    """
    # Define opções padrão se nenhuma for fornecida
    if options is None:
        options = DEFAULT_OPTIONS

    # Monta prompt com contexto e instruções específicas
    prompt = f"""Você é um assistente especializado que responde perguntas com base no contexto fornecido.


Contexto:
{contexto}

Pergunta: {pergunta}

Instruções:
1. Responda de forma clara e detalhada, procure elaborar bem as respsotas.
2. Baseie sua resposta estritamente no contexto fornecido.
3. Se a resposta estiver no contexto, diga informe de qual arquivo foi tirado.
4. Use português claro e formal.

Resposta:"""

    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "options": options
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        # A API do Ollama pode retornar 'response' ou listar em 'choices'
        return data.get("response") \
            or (data.get("choices", [{}])[0]
                   .get("message", {}).get("content")) \
            or "Erro: Resposta vazia do modelo"

    except requests.exceptions.Timeout:
        return "Erro: Tempo esgotado ao consultar o modelo"

    except Exception as error:
        return f"Erro ao conectar com o modelo: {error}"


# ——————————————————————————————
if __name__ == "__main__":
    # Teste rápido de sanidade para ver se o serviço está ativo
    test_pergunta = "Como posso agendar minhas férias?"
    test_contexto = "Nenhum contexto relevante fornecido."
    print("⏳ Testando obter_resposta_llama()...")
    resposta = obter_resposta_llama(test_pergunta, test_contexto)
    print("Resposta do modelo:\n", resposta)
