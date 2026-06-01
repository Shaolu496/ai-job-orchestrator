# AI 任務執行平台

這是一個用來展示 Sr SWE 後端與 AI 平台能力的 side project 規劃。專案主軸不是聊天機器人，而是可可靠執行長時間 AI workload 的任務平台。

## 面試定位

我做了一個用來執行長時間 AI 任務的 backend platform。設計重點不是 demo，而是可靠執行、可重試、可觀測、可控成本，並且支援 RAG ingestion 作為其中一種 workload。

## 核心能力證明

- 後端系統設計：API、Postgres、Redis queue、worker pool。
- 可靠性：job 狀態機、retry、dead letter queue、idempotency。
- AI 工程：文件切片、embedding、pgvector retrieval、token 成本追蹤。
- 可維運性：structured logs、trace id、metrics、錯誤分類。
- 測試與驗證：unit tests、integration tests、load test。

## MVP 功能

- 建立 AI job。
- 查詢 job 狀態與 step 結果。
- Worker 非同步執行文件 ingestion。
- 將文件切片後建立 embedding。
- 使用 pgvector 查詢相似內容。
- 追蹤 latency、錯誤率、retry 次數與 token 成本。

## 建議技術棧

- FastAPI
- Celery
- Redis
- Postgres + pgvector
- OpenTelemetry
- Docker Compose
- pytest

完整設計規格見：

`docs/superpowers/specs/2026-06-01-ai-job-orchestrator-design.md`

