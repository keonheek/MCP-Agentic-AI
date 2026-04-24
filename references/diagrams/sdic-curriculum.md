# SDIC AI 컨설팅 어시스턴트 - 커리큘럼 다이어그램

_Companion to the Notion page "SDIC AI 컨설팅 어시스턴트 - 코스 안내". Three diagrams, three audiences._

---

## 1a. Student Journey - for first-time recruits

```
AUDIENCE: SDIC 신입 멤버 (AI를 처음 쓰는 학생)
QUESTION: 이 과정을 끝내면 내가 뭘 만들 수 있어?
STATUS: final
```

```mermaid
flowchart LR
    W0[Week 0<br/>도구 설치<br/>VS Code + Claude Code]:::blue
    W1[Week 1<br/>Claude Code 익히기<br/>첫 앱 실행]:::blue
    W2[Week 2<br/>DART 자동 수집<br/>재무 데이터 저장]:::yellow
    W3[Week 3<br/>AI가 보고서 읽기<br/>RAG + PDF 생성]:::yellow
    W4[Week 4<br/>차트 + 배포<br/>공개 URL 완성]:::green

    W0 --> W1 --> W2 --> W3 --> W4

    W4 --> OUT[🎓 CV 한 줄<br/>Multi-step LangGraph AI<br/>consulting assistant, deployed]:::final

    classDef blue fill:#cce5ff,stroke:#004085,color:#000
    classDef yellow fill:#fff3cd,stroke:#856404,color:#000
    classDef green fill:#d4edda,stroke:#155724,color:#000
    classDef final fill:#d1ecf1,stroke:#0c5460,color:#000,font-weight:bold
```

**Use this for:** 신입 모집 인스타 스토리, 첫 OT 핸드아웃, 학부모/친구한테 "뭐 배우는 거야?" 질문 받을 때.

---

## 1b. 4주 vs 6주 트랙 비교

```
AUDIENCE: 등록 예정 멤버 (어느 트랙 할지 고민 중)
QUESTION: 집중 vs 심화 - 뭐가 어떻게 달라?
STATUS: final
```

```mermaid
flowchart TB
    Q{집중 vs 심화<br/>어느 트랙?}:::decision

    Q -->|4주 집중| F1[W1: 온보딩 + 첫 commit]:::blue
    F1 --> F2[W2: DART ETL<br/>2노드 LangGraph]:::yellow
    F2 --> F3[W3: RAG + Text2SQL<br/>PDF 생성]:::yellow
    F3 --> F4[W4: Plotly + 배포<br/>데모]:::green

    Q -->|6주 심화| S1[W1: 온보딩 + 첫 commit]:::blue
    S1 --> S2[W2: DART ETL<br/>2노드 LangGraph]:::yellow
    S2 --> S3[W3: Supervisor<br/>멀티에이전트]:::added
    S3 --> S4[W4: RAG + Text2SQL<br/>PDF]:::yellow
    S4 --> S5[W5: Plotly +<br/>LLM 평가 프레임워크]:::added
    S5 --> S6[W6: 채팅 Q&A<br/>+ 배포 + 데모]:::green

    F4 --> OUT1[📜 Multi-step LangGraph<br/>AI consulting assistant]:::final
    S6 --> OUT2[📜 Multi-agent Supervisor<br/>+ LLM-as-judge framework]:::final

    classDef decision fill:#fef3c7,stroke:#92400e,color:#000
    classDef blue fill:#cce5ff,stroke:#004085,color:#000
    classDef yellow fill:#fff3cd,stroke:#856404,color:#000
    classDef green fill:#d4edda,stroke:#155724,color:#000
    classDef added fill:#e7d5ff,stroke:#5b2d8f,color:#000,font-weight:bold
    classDef final fill:#d1ecf1,stroke:#0c5460,color:#000
```

**보라색 박스 = 6주에만 있는 심화 내용** (Supervisor 멀티에이전트, LLM 평가, 채팅 Q&A)

**Use this for:** 등록 전 상담, Notion 비교표를 시각적으로 대체, "나 4주만 할까 6주 할까?" 상담할 때.

---

## 1c. 매주 2시간 세션 표준 흐름 (운영진용)

```
AUDIENCE: 나 (회장) + 팀 리드
QUESTION: 매주 수요일 2시간을 어떻게 운영하지?
STATUS: final
```

```mermaid
flowchart LR
    A[🔵 Warmup<br/>15분<br/>지난 주 복기<br/>+ 이번 주 목표]:::human
    B[🟣 /plan 모드<br/>30분<br/>Claude에게 계획 세우게 하기]:::ai
    C[⚙️ 실행<br/>45분<br/>Claude Code가 코드 작성<br/>팀원은 PM 역할]:::ai
    D[✅ 검증<br/>15분<br/>실행 → 동작 확인<br/>에러 고치기]:::human
    E[📤 Git push<br/>10분<br/>commit + push<br/>다음 주 예고]:::human
    F[💬 질문 타임<br/>5분]:::human

    A --> B --> C --> D --> E --> F

    classDef human fill:#cce5ff,stroke:#004085,color:#000
    classDef ai fill:#e5e5e5,stroke:#495057,color:#000
```

**파란색 = 사람이 주도. 회색 = AI가 주도.**

**Use this for:** 수요일 세션 운영 체크리스트, 팀 리드 인수인계, 대타 선생 부를 때.

---

## How these fit together

- **1a (Journey)** → 회원 모집 단계
- **1b (Branching)** → 등록 상담 단계
- **1c (Weekly flow)** → 실제 운영 단계

3개 다이어그램으로 학회 운영의 **sales funnel → operations**를 한 눈에 설명 가능.

**다음 개선:** 각 다이어그램을 Notion 커리큘럼 페이지 상단에 embed (Notion `/code mermaid` 블록 지원).
