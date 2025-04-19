"""
telegram_bot.py

Bridge entre o Telegram e o Chatbot Documental:
  - Recebe mensagens via polling
  - Recupera contexto no ChromaDB
  - Gera resposta via Gemma3 (Ollama)
  - Envia a resposta de volta ao usuário no Telegram
"""

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# Carrega .env
load_dotenv()

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
K_RESULTS = int(os.getenv("K_RESULTS", 5))

# Logging básico
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Importa módulos do seu projeto
from store.chroma_store import collection
from llm.llm import obter_resposta_llama


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /start"""
    await update.message.reply_text(
        "Olá! Eu sou seu Chatbot Documental. Envie qualquer pergunta e vou responder com base nos seus documentos."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para qualquer texto enviado pelo usuário"""
    user_text = update.message.text
    # 1) Recupera contexto do ChromaDB
    try:
        result = collection.query(
            query_texts=[user_text],
            n_results=K_RESULTS,
            include=["documents"]
        )
        docs = result["documents"][0]
        contexto = "\n\n".join(docs) if docs else ""
    except Exception as e:
        logging.error(f"Erro ao buscar contexto: {e}")
        contexto = ""

    if not contexto:
        await update.message.reply_text("Não encontrei contexto relevante nos documentos.")
        return

    # 2) Gera resposta via Gemma3
    resposta = obter_resposta_llama(
        pergunta=user_text,
        contexto=contexto
    )

    # 3) Envia resposta de volta ao Telegram
    await update.message.reply_text(resposta)


def main():
    """Configura e inicia o bot"""
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN não definido no .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    # Mensagens de texto comuns
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # Inicia o polling
    logging.info("Bot iniciado — aguardando mensagens...")
    app.run_polling()


if __name__ == "__main__":
    main()
