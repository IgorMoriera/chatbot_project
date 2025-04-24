# prompt_to_model/prompt_builder.py

def build_prompt(question: str, context: str) -> str:
    """
    Constrói o prompt completo para o modelo utilizado (Ex: Gemma 3),
    combinando instruções fixas, a pergunta do usuário
    e o contexto extraído dos documentos.
    """
    return (
        "Você é um assistente especializado em responder perguntas "
        "com base exclusivamente no tema relacionado à pergunta.\n\n"
        "Instruções:\n"
        "1. Ignore informações de outros temas ou documentos,\n"
        "2. Detalhe cada etapa ou ponto mencionado no contexto,\n"
        "   explicando o que significa e como aplicá-lo,\n"
        "3. Não resuma demais; forneça explicações completas,\n"
        "4. Responda de forma clara, concisa e detalhada,\n"
        "   abordando apenas o tema principal.\n\n"
        f"Pergunta: {question}\n\n"
        f"Contexto:\n{context}\n\n"
        "Resposta:"
    )
