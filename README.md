# 🧠 Chatbot Documental  
![Python](https://img.shields.io/badge/python-3.11-blue) ![License](https://img.shields.io/badge/license-MIT-green)

<div align="center">
  <img src="https://github.com/IgorMoriera/chatbot_project/blob/master/logo.png" width="200" height="200" />
</div>


Um projeto em **Python 3.11** que implementa um chatbot capaz de responder perguntas com base em documentos locais (PDF, CSV e TXT). Este projeto utiliza tecnologias modernas para processar, indexar e gerar respostas a partir de documentos, oferecendo uma interface web (via Streamlit) e mobile (via Telegram) interativa.

### Tecnologias Utilizadas

- **LangChain**: para dividir textos em pedaços (chunking).
- **SentenceTransformers** (`all-MiniLM-L6-v2`): modelo para gerar embeddings de texto.
- **ChromaDB**: banco vetorial leve e persistente para armazenar embeddings.
- **Gemma3**: modelo de LLM local para geração de respostas.
- **Streamlit**: interface web amigável e interativa.
- **Telegram**: interface mobile para interagir via chatbot.

---

## 🔍 Visão Geral

O Chatbot Documental permite que usuários façam perguntas sobre o conteúdo de documentos locais e recebam respostas precisas baseadas em contexto recuperado. Ele funciona em quatro etapas principais:

1. **Ingestão de Documentos**

   - Lê arquivos em formatos PDF, CSV e TXT da pasta `data/`.
   - Divide o texto em pedaços menores (chunks) usando o LangChain.
   - Indexa os chunks no ChromaDB com metadados como fonte e número da página.

2. **Recuperação de Contexto**

   - Busca os trechos mais relevantes para a pergunta do usuário no ChromaDB.
   - Extrai o texto e as fontes correspondentes para montar o contexto.

3. **Geração de Resposta**

   - Cria um prompt com a pergunta e o contexto recuperado.
   - Usa o modelo Gemma3 (via Ollama) para gerar uma resposta detalhada.

4. **Interface Web e Mobile**

   - **Streamlit**: Interface web onde usuários podem interagir via chat em cima de documentos já indexados.
   - **Telegram**: Interface mobile que permite aos usuários fazer perguntas sobre documentos já indexados diretamente pelo Telegram.

---

## 📁 Estrutura de Pastas

```
chatbot_project/
├── .env                    # Variáveis de configuração (API, paths, token do Telegram, etc.)
├── requirements.txt        # Dependências do projeto
├── README.md
├── data/                   # PDFs, CSVs e TXTs a indexar
│   ├── exemplo.pdf
│   ├── exemplo.csv
│   └── exemplo.txt
├── loaders/                # Leitores de diferentes formatos
│   ├── pdf_loader.py
│   ├── csv_loader.py
│   └── txt_loader.py
├── retriever/              # Chunking de texto
│   └── retriever.py
├── embeddings/             # Geração de embeddings
│   └── embedder.py
├── store/                  # Abstração do ChromaDB
│   └── chroma_store.py
├── llm/                    # Integração com Gemma3
│   └── llm.py
├── pipeline.py             # Script de ingestão dos dados
├── app.py                  # Interface Streamlit
└── telegram_bot.py         # Integração com Telegram
```

---

## ⚙️ Instalação

### 1. Pré-requisitos

- **Ambiente virtual** utilizando o Anaconda.


- **Python 3.11** (recomendado para compatibilidade).
- **Ollama** instalado e modelo **Gemma3** baixado localmente.
- **Git** para clonar o repositório.
- **Telegram**: Crie um bot no Telegram e obtenha o token.

### 2. Clonar e Configurar o Ambiente

```bash
git clone https://github.com/seu-usuario/chatbot_documental_inteligente.git
cd chatbot_documental_inteligente
conda create --name nome_do_ambiente python=3.11
conda activate nome_do_ambiente
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

1. **Crie** um arquivo chamado `.env` na raiz do seu projeto.  
2. **Copie** e **cole** o conteúdo abaixo dentro dele.  
3. **Substitua** cada valor placeholder pelo dado real do seu ambiente.  
4. **Salve** o arquivo.

```Variáveis de ambiente
# Diretório dos arquivos de entrada/saída
DATA_DIR=/caminho/para/seus/arquivos

# Token do Telegram Bot (obtido via @BotFather)
TELEGRAM_TOKEN=SEU_TOKEN_DO_TELEGRAM_AQUI

# Quantos “chunks” recuperar por requisição (opcional; padrão: 3)
K_RESULTS=3

# Endpoint e modelo para geração via Ollama/Gemma3
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=gemma3:1b

# Nome do modelo de embeddings e chave da Hugging Face
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
HF_API_KEY=SUA_HUGGINGFACE_API_KEY_AQUI

# Pasta onde o Chroma vai persistir o banco vetorial
CHROMA_PERSIST_DIR=chroma_db
```

**Nota**: Substitua `*` pelo token do seu bot do Telegram.


## 🚀 Como Usar

### 1. Ingestão de Documentos

Execute o script de ingestão para indexar os documentos da pasta `data/`:

```bash
python pipeline.py
```

**Saída esperada:**

```
🗑️  Limpando coleção Chroma anterior...
✅ Coleção limpa.

📂  Carregado 5 documentos de 'exemplo.pdf'
✅  'exemplo.pdf': 20 chunks indexados
…
🏁  Ingestão concluída: 50 novos chunks de data
📊 Total de chunks na coleção: 50
```

> **Nota:** Execute este passo antes de iniciar as interfaces web ou Telegram.

### 2. Iniciar a Interface Streamlit

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador e:

- Digite perguntas no chat referente aos documentos indexados.
- Veja respostas, contexto, fontes e tempo de processamento.

### 3. Interagir via Telegram

Após configurar o token do Telegram no `.env`, execute o script do bot:

```bash
python telegram_bot.py
```

- No Telegram, inicie uma conversa com o seu bot.
- Envie perguntas sobre os documentos já indexados.
- Receba respostas diretamente no chat do Telegram.

### Exemplo de Uso

**Pergunta (Telegram ou Streamlit):** "O que diz o exemplo.pdf sobre sustentabilidade?"\
**Resposta:** "O exemplo.pdf menciona que a sustentabilidade envolve equilibrar recursos naturais e desenvolvimento econômico..."\
**Contexto:** Trecho do PDF com a fonte indicada.

---

## 🧩 Principais Módulos

| Módulo | Função Principal |
| --- | --- |
| `loaders/*.py` | Lê PDF, CSV e TXT, retornando texto e metadados. |
| `retriever/retriever.py` | Divide textos em chunks com `RecursiveCharacterTextSplitter`. |
| `embeddings/embedder.py` | Gera embeddings usando `SentenceTransformer`. |
| `store/chroma_store.py` | Gerencia o ChromaDB (indexação e limpeza). |
| `llm/llm.py` | Integra com Ollama/Gemma3 para gerar respostas. |
| `pipeline.py` | Executa a ingestão completa dos documentos. |
| `app.py` | Interface Streamlit com chat e visualização de resultados. |
| `telegram_bot.py` | Integração com Telegram para interações via chat. |

---

## ⚠️ Dicas de Ajuste e Resolução de Problemas

- **Python 3.11+**: Essencial para evitar erros de sintaxe como `dict | None`.
- **Erro na coleção Chroma**: Delete a pasta `chroma_db/` e reexecute `pipeline.py`.
- **Ajuste de chunks**: Modifique `chunk_size` e `chunk_overlap` em `retriever/retriever.py`.
- **Mais/menos contexto**: Altere `K_RESULTS` no `.env` ou `app.py`.
- **Timeout do LLM**: Ajuste o parâmetro `timeout` em `llm/llm.py`.
- **Telegram**: Certifique-se de que o token está corretamente configurado no `.env`.

---

## 🤝 Contribuindo

Quer ajudar a melhorar o projeto? Siga esses passos:

1. Faça um **fork** do repositório.
2. Crie uma branch: `git checkout -b feature/sua-ideia`.
3. Faça commits claros e envie um **Pull Request** com uma descrição detalhada.

> **Dica**: Contribuições para melhorar a interface web (Streamlit) ou mobile (Telegram) são especialmente bem-vindas!

---

## 📄 Licença

MIT © Igor Moreira\
Use, modifique e distribua este projeto livremente!

---

> Desenvolvido por Igor Moreira – Data Scientist & Engenheiro de Dados\
> Contato: igor.moreira@fat.uerj.br