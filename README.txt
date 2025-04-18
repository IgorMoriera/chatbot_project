# 🧠 Chatbot Documental Inteligente

Um projeto em **Python 3.11** que implementa um chatbot capaz de responder perguntas com base em documentos locais (PDF, CSV e TXT). Utiliza:

- **LangChain** para chunking de texto
- **SentenceTransformers** (`all‑MiniLM‑L6‑v2`) para gerar embeddings
- **ChromaDB** como vector store leve e persistente
- **Ollama** + **Gemma3** local para geração de respostas
- **Streamlit** para interface web interativa

---

## 🔍 Visão Geral

1. **Ingestão de documentos**
   - Leitura de arquivos em `data/` via loaders especializados
   - Chunking de texto para criar pedaços de tamanho controlado
   - Indexação de chunks com metadados (fonte, número de página, ID) no ChromaDB

2. **Recuperação de contexto**
   - Busca dos _k_ chunks mais relevantes para a pergunta do usuário
   - Extração de trechos e lista de fontes para montar o contexto

3. **Geração de resposta**
   - Montagem de prompt com instruções e contexto
   - Envio ao modelo Gemma3 local via Ollama HTTP API
   - Recebimento e exibição da resposta

4. **Interface Web**
   - Upload ou uso de documentos já indexados
   - Caixa de chat com histórico de perguntas e respostas
   - Visualização de trechos de contexto, tempo de resposta e fontes
   - Tema escuro customizado em CSS

---

## 📁 Estrutura de Pastas

```
chatbot_project/
├── .env                    # Variáveis de configuração (API, paths, etc.)
├── requirements.txt        # Dependências do projeto
├── README.md               # Este arquivo (agora como .txt)
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
├── llm/                    # Integração com Ollama/Gemma3
│   └── llm.py
├── pipeline.py             # Script de ingestão completo
└── app.py                  # Interface Streamlit
```

---

## ⚙️ Instalação

### 1. Pré‑requisitos

- **Python 3.11** (recomendado)
- **Ollama** instalado e modelo **Gemma3** baixado localmente
- Git

### 2. Clonar e criar ambiente

```bash
git clone https://github.com/seu-usuario/chatbot_documental_inteligente.git
cd chatbot_documental_inteligente
python3.11 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz com:

```dotenv
# URL e modelo do Ollama/Gemma3
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=gemma3:1b

# Quantos chunks recuperar por pergunta (opcional)
K_RESULTS=3

# Pasta de persistência do Chroma (opcional)
CHROMA_PERSIST_DIR=chroma_db
```

---

## 🚀 Como usar

### 1. Ingestão de documentos

Rode o pipeline de ingestão para indexar todo o conteúdo de `data/`:

```bash
python pipeline.py
```

Você verá:

```
🗑️  Limpando coleção Chroma anterior...
✅ Coleção limpa.

📂  Carregado 5 documentos de 'exemplo.pdf'
✅  'exemplo.pdf': 20 chunks indexados
…
🏁  Ingestão concluída: 50 novos chunks de data
📊 Total de chunks na coleção: 50
```

> Sempre faça isso **antes** de iniciar a interface.

### 2. Iniciar a interface Streamlit

```bash
streamlit run app.py
```

Abra no navegador: `http://localhost:8501`

- **Digite sua pergunta** na caixa de chat.
- Veja o **contexto recuperado**, o **tempo de resposta** e as **fontes** utilizadas.
- Expanda o **contexto completo** se quiser inspecionar o trecho exato enviado ao LLM.

---

## 🧩 Principais Módulos

| Módulo                      | Responsabilidade                                               |
|-----------------------------|----------------------------------------------------------------|
| `loaders/*.py`              | Carregam PDF, CSV e TXT, retornando `[{"text", "metadata"}]`   |
| `retriever/retriever.py`    | Divide textos em chunks com `RecursiveCharacterTextSplitter`   |
| `embeddings/embedder.py`    | Gera embeddings com `SentenceTransformer("all‑MiniLM‑L6‑v2")`   |
| `store/chroma_store.py`     | Configura ChromaDB, adiciona documentos e limpa coleção        |
| `llm/llm.py`                | Monta prompt e chama Ollama/Gemma3 via HTTP API                |
| `pipeline.py`               | Pipeline completo: limpeza, ingestão incremental e relatório   |
| `app.py`                    | Interface Streamlit de chat com estilo dark-mode e balões      |

---

## ⚠️ Dicas de Ajuste e Resolução de Problemas

- **Versão do Python:** use 3.11 ou superior para evitar erros de sintaxe `dict | None`.
- **Limpeza da coleção:** `pipeline.py` usa `limpar_colecao()` para garantir índice limpo. Se der erro, delete a pasta `chroma_db/`.
- **Ajustes de chunking:** modifique `chunk_size`/`chunk_overlap` em `retriever/retriever.py`.
- **Número de resultados:** ajuste `K_RESULTS` no `.env` ou em `app.py`.
- **Timeout LLM:** no `llm/llm.py`, altere o `timeout` conforme necessidade.

---

## 🤝 Contribuindo

1. Fork este repositório.
2. Crie uma branch para sua feature: `git checkout -b feature/nova-coisa`.
3. Faça commits claros e pequenos.
4. Abra um Pull Request descrevendo seu objetivo.

---

## 📄 Licença

MIT © [Seu Nome]
Sinta‑se à vontade para usar, modificar e distribuir este projeto livremente!

---

> Desenvolvido por **[Seu Nome]** — Data Scientist & Engenheiro de Dados
> Entre em contato: seu.email@exemplo.com
