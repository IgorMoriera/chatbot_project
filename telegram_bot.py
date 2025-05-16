"""
telegram_bot.py

Bridge entre o Telegram e o Chatbot Documental Inteligente:
  - Recebe mensagens via polling
  - Recupera contexto no ChromaDB
  - Monta prompt único via prompt_builder
  - Gera resposta via Gemma 3 (Ollama)
  - Envia resposta de volta ao usuário no Telegram, incluindo fontes e distância média
"""

# Importação de bibliotecas e módulos internos
import logging
import os

from llm.llm import obter_resposta_llama
from app_config.app_context import get_context
from app_config.prompt_builder import build_prompt

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# Carrega variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
K_RESULTS = int(os.getenv("K_RESULTS", 3))

# Configuração básica de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    await update.message.reply_text(
        "Olá! Eu sou seu Chatbot Documental. Envie qualquer pergunta "
        "e eu responderei com base nos documentos indexados."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para qualquer texto recebido — recupera contexto, gera prompt e responde."""
    user_text = update.message.text

    try:
        # 1) Recupera contexto, lista de fontes e distância média
        contexto, fontes, distancia_media = get_context(user_text)

        # 2) Se não encontrou contexto, envia fallback
        if not contexto.strip():
            await update.message.reply_text(
                "Não encontrei contexto relevante nos documentos."
            )
            return

        # 3) Monta prompt único reutilizável
        prompt = build_prompt(user_text, contexto)

        # 4) Gera a resposta via Gemma 3
        resposta = obter_resposta_llama(pergunta=prompt, contexto="")

        # 5) Formata a mensagem de retorno incluindo fontes e distância média
        fontes_txt = ", ".join(fontes) if fontes else "nenhuma"
        reply = (
            f"{resposta}\n\n"
            f"📚 Fontes: {fontes_txt}\n"
            f"🔎 Distância média: {distancia_media:.3f}"
        )

    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {e}")
        reply = "Desculpe, ocorreu um erro ao processar sua solicitação."

    # 6) Envia a resposta de volta ao usuário
    await update.message.reply_text(reply)


def main():
    """Configura e inicia o bot de polling do Telegram."""
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN não definido no .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registra handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Inicia o polling
    logging.info("Bot iniciado — aguardando mensagens...")
    app.run_polling()


if __name__ == "__main__":
    main()
