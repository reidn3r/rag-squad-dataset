# RAG SQuAD

Pipeline completo de RAG que envolve: ingestão, chunking, embedding, busca vetorial, reranking e geração, exposto via API REST.


## Visão Geral

Este projeto implementa um sistema de **RAG (Retrieval-Augmented Generation)** sobre o dataset [SQuAD (Stanford Question Answering Dataset)](https://huggingface.co/datasets/nunorc/squad_v1_pt) do Hugging Face.

O objetivo é responder perguntas em linguagem natural buscando contextos relevantes numa base vetorial e gerando respostas fundamentadas via LLM, com reranking para maximizar a qualidade do contexto entregue ao modelo.


## Fluxo

```
HuggingFace SQuAD Dataset
        │
        ▼
  Ingestion Job
  ├── Deduplicação de contextos
  ├── Chunking (RecursiveCharacterTextSplitter)
  ├── Embedding (sentence-transformers)
  └── Upsert → Qdrant
        │
        ▼
  FastAPI — /query
  ├── Embed query
  ├── Vector Search (Qdrant)
  ├── Reranking (LLM)
  └── Generation (LLM + context)
```
## Decisões

**Por que reranking?** A busca vetorial por similaridade recupera chunks semanticamente próximos, mas não necessariamente os mais úteis para a pergunta. O reranking usa o próprio LLM para reordenar os resultados antes da geração, melhorando a qualidade da resposta sem aumentar o número de documentos recuperados.

**Por que `paraphrase-multilingual-mpnet-base-v2`?** Modelo denso de 768 dimensões com bom equilíbrio entre qualidade de embedding e custo computacional, com suporte multilíngue nativo.

**Chunking com overlap:** `chunk_size=300` com `chunk_overlap=50` preserva contexto nas bordas dos chunks, evitando perda de informação em quebras de texto.


## Indexação dos Dados
 
**1. Tokenização**
Divide o texto em unidades menores (palavras, subpalavras). O modelo usa WordPiece com aproximadamente 250k tokens e suporte a 50+ idiomas.

**2. Embedding**
O Transformer processa os tokens via self-attention e gera um vetor de 768 dimensões que representa o significado semântico do texto. Textos similares ficam próximos no espaço vetorial.

**3. Indexação no Qdrant (HNSW)**
Usa HNSW, um índice baseado em grafo multi-camadas, para busca aproximada (ANN). Camadas superiores permitem navegação rápida por "atalhos" entre regiões distantes do espaço vetorial, enquanto as camadas inferiores refinam a busca com maior precisão local. O resultado é uma busca aproximada de vizinhos mais próximos que encontra os vetores mais similares de forma eficiente.

**4. Similaridade de Cosseno**
Compara o ângulo entre vetores da query e dos indexados. Score `1.0` = idênticos, `0.0` = sem relação. Mais robusta que distância euclidiana para embeddings de texto.