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

## 🔍 Arquitetura do Chatbot Documental

<p align="center">
  <img src="https://github.com/IgorMoriera/chatbot_project/blob/master/Arquitetura%20Chatbot.png" width="600" alt="Arquitetura do Chatbot Documental"/>
</p>

O Chatbot Documental foi desenhado em quatro camadas distintas, que juntas garantem a ingestão, indexação, recuperação de contexto e geração de respostas de forma eficiente e coerente.

A primeira camada é responsável pela **Ingestão e Chunking**. Aqui, o sistema varre a pasta `data/` identificando todos os arquivos nos formatos PDF, CSV e TXT. Cada documento é então fragmentado em pedaços menores — chamados *chunks* — usando a biblioteca LangChain, de modo a manter cada fatia em um tamanho aproximado de 500 tokens. Essa etapa de divisão é fundamental para que o modelo de embeddings consiga capturar detalhes semânticos de cada trecho sem ultrapassar os limites de contexto. Em seguida, cada chunk é transformado em um vetor numérico de alta dimensão (por exemplo, `[-0.0101, -0.0101, 0.0101, …]`), que será a representação semântica daquele pedaço de texto.

Na segunda camada, conhecida como **Armazenamento Vetorial**, utilizamos o ChromaDB como repositório dos embeddings gerados. Além de armazenar cada vetor, também registramos metadados essenciais — como o nome do arquivo de origem, o número da página e a posição exata do chunk dentro do documento. Esses metadados permitem que, depois, possamos apresentar ao usuário não apenas a informação correta, mas também sua referência de onde ela foi extraída. O ChromaDB, por sua vez, mantém índices otimizados para buscas de similaridade, garantindo alta velocidade e escalabilidade mesmo quando lidamos com grandes volumes de dados.

A terceira camada diz respeito à **Recuperação de Contexto** por meio de buscas semânticas. Quando um usuário envia uma pergunta, nós primeiro convertemos esse texto em um embedding, usando o mesmo modelo e dimensão dos vetores de documento. Esse vetor de consulta é então usado para interrogar o ChromaDB em busca dos N chunks mais próximos semanticamente. Ao obter esses trechos, montamos um prompt que combina a pergunta original com os extratos de texto selecionados — cada um acompanhado de sua referência de arquivo e página — a fim de fornecer ao modelo de linguagem toda a informação contextual necessária para gerar uma resposta precisa.

Por fim, na camada de **Geração de Resposta e Interfaces**, o prompt enriquecido vai para o modelo Gemma3, rodando localmente via Ollama. Esse LLM processa o contexto e devolve uma resposta detalhada e relevante. Para entregar essa resposta ao usuário, oferecemos duas interfaces: uma aplicação web em Streamlit, que exibe o chat em um navegador de forma interativa e visualmente agradável, e um bot no Telegram, que permite ao usuário conversar diretamente pelo app de mensagens. Assim, unimos a robustez e precisão do back-end semântico com a praticidade de interfaces conhecidas e acessíveis.

> **Fluxo resumido:**  
> 1. Ingestão e fragmentação dos documentos  
> 2. Geração e indexação de embeddings no ChromaDB  
> 3. Busca semântica e montagem de contexto  
> 4. Geração de resposta pelo LLM e entrega via Streamlit ou Telegram  


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