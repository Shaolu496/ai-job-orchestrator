# AI 任務執行平台

這是一個用來展示 Sr SWE 後端與 AI 平台能力的 side project 規劃。專案主軸不是聊天機器人，而是可可靠執行長時間 AI workload 的任務平台。

## 面試定位

我做了一個用來執行長時間 AI 任務的 backend platform。設計重點不是 demo，而是可靠執行、可重試、可觀測、可控成本，並且支援 RAG ingestion 作為其中一種 workload。

## FAANG 面試官視角

這個專案的重點不是「我用了 FastAPI、Redis、pgvector」，而是能不能證明我具備 senior engineer 的判斷：

- 我能定義清楚的系統邊界與責任分工。
- 我能說明為什麼長時間 AI 任務需要 queue 與 worker。
- 我能處理 retry、idempotency、worker crash、provider timeout、rate limit。
- 我能用 metrics、logs、trace id 追查 production issue。
- 我能用壓測與測試證明設計不是只停留在 demo。
- 我能說清楚 MVP 的取捨，以及流量變大後如何演進。

## 核心能力證明

- 後端系統設計：API、Postgres、Redis queue、worker pool。
- 可靠性：job 狀態機、retry、dead letter queue、idempotency。
- AI 工程：文件切片、embedding、pgvector retrieval、token 成本追蹤。
- 可維運性：structured logs、trace id、metrics、錯誤分類。
- 測試與驗證：unit tests、integration tests、load test。

## 面試時要準備回答的問題

1. 如果 worker 做完 embedding 但 DB 寫入前 crash，重跑如何避免重複資料？
2. 如果 client 重送同一個 idempotency key 但 payload 不同，API 應該如何回應？
3. 如果 LLM provider rate limit，retry policy 怎麼設計才不會造成更多流量？
4. 如果 retrieval latency 變慢，會先看哪些 metrics？
5. 如何量化 RAG retrieval quality？
6. Redis queue 未來什麼情況下需要換成 Kafka 或其他 event streaming 系統？

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
