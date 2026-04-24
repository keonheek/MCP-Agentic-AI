# FinAgent — Architecture Diagram

Multi-agent financial analysis system. Use this diagram in pitch decks, SDIC teaching, and GitHub README.

---

## Business-facing version (for clients, pitches, non-technical audiences)

```mermaid
flowchart LR
    A[User Question<br/>e.g. Samsung Q3 outlook?] --> B{FinAgent<br/>Orchestrator}
    B --> C[Financial Data<br/>Agent]
    B --> D[Market Research<br/>Agent]
    B --> E[Reasoning<br/>Agent]
    C --> F[(DART Filings<br/>SQLite)]
    D --> G[(News + Reports<br/>VectorDB)]
    E --> H[Synthesized<br/>Answer]
    F --> H
    G --> H
    H --> I[Investment Thesis<br/>+ Citations]

    style A fill:#e1f5ff,stroke:#0366d6
    style I fill:#d4edda,stroke:#28a745
    style B fill:#fff3cd,stroke:#856404
```

**Talking points:**
- One question in, structured thesis out
- Three specialized agents beat one generalist LLM
- Every claim cited back to source filings or news

---

## Technical version (for SDIC teaching, GitHub README, engineering audiences)

```mermaid
flowchart TB
    subgraph UI[Frontend Layer]
        ST[Streamlit UI]
    end

    subgraph API[API Layer]
        FA[FastAPI Backend]
    end

    subgraph ORCH[Orchestration - LangGraph]
        SUP[Supervisor Node]
        RT{Router}
    end

    subgraph AGENTS[Agent Layer]
        A1[Financial Agent<br/>Text2SQL]
        A2[Research Agent<br/>RAG Retrieval]
        A3[Reasoning Agent<br/>GPT-4o]
    end

    subgraph DATA[Data Layer]
        DB[(SQLite<br/>DART Filings)]
        VDB[(Custom VectorDB<br/>Cosine Similarity)]
        EMB[OpenAI<br/>Embeddings API]
    end

    ST --> FA
    FA --> SUP
    SUP --> RT
    RT -->|financial query| A1
    RT -->|context query| A2
    RT -->|synthesis| A3
    A1 --> DB
    A2 --> VDB
    VDB <--> EMB
    A1 --> SUP
    A2 --> SUP
    A3 --> SUP
    SUP -->|final answer| FA
    FA --> ST

    style SUP fill:#fff3cd,stroke:#856404
    style A1 fill:#cce5ff,stroke:#004085
    style A2 fill:#cce5ff,stroke:#004085
    style A3 fill:#cce5ff,stroke:#004085
    style DB fill:#f8d7da,stroke:#721c24
    style VDB fill:#f8d7da,stroke:#721c24
```

**Teaching points for SDIC:**
- **Supervisor pattern:** one node decides which agent runs. This is the core LangGraph pattern.
- **Why custom VectorDB?** Built from scratch with numpy cosine similarity to understand what Pinecone/Chroma do under the hood.
- **Text2SQL vs RAG:** structured data (filings) goes to SQL, unstructured (news) goes to vectors. Pick the right retrieval for the data shape.
- **Why LangGraph not LangChain?** State machine model handles multi-step reasoning and retries cleanly; LangChain chains break when agents need to loop back.

---

## Sequence version (for explaining the flow step-by-step)

```mermaid
sequenceDiagram
    actor U as User
    participant UI as Streamlit
    participant S as Supervisor
    participant F as Financial Agent
    participant R as Research Agent
    participant Y as Reasoning Agent
    participant DB as SQLite
    participant V as VectorDB

    U->>UI: Samsung Q3 outlook?
    UI->>S: route query
    S->>F: get latest filings
    F->>DB: SELECT FROM samsung_q3
    DB-->>F: revenue, margins
    S->>R: get market context
    R->>V: similarity_search(samsung memory)
    V-->>R: top 5 news chunks
    S->>Y: synthesize thesis
    Y-->>S: draft + citations
    S-->>UI: final answer
    UI-->>U: Investment thesis
```

---

## Where to use each version

| Version | Use for |
|---|---|
| Business flowchart | Client pitches, Soomgo listings, YouTube demo thumbnails, LinkedIn posts |
| Technical flowchart | GitHub README, SDIC curriculum slides, consulting interview whiteboard |
| Sequence diagram | Step-by-step teaching, debugging sessions, technical blog posts |

---

## How to render

- **Notion:** paste inside a `/code` block with language set to `mermaid`
- **GitHub:** paste inside a ` ```mermaid ` fence in any .md file (renders natively)
- **PDF/Deck:** render at [mermaid.live](https://mermaid.live), export as SVG, drop into Figma/Keynote
- **Claude artifacts:** paste as mermaid code block
