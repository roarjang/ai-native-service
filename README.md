# AI Native Service

질문을 받아 AI 답변을 돌려주고, 대화와 AI 실행 이력을 저장하는 대화형 AI 서비스입니다.

## 아키텍처 초안

React · FastAPI(Router · Schema · Service · LLM Client · Repository) · Gemini · PostgreSQL

```mermaid
flowchart TB
   React[React 화면]
   Router[Router]
   Schema[Schema]
   Service[Service]
   LLM[LLM Client]
   Repo[Repository]
   Gemini[(Gemini)]
   PG[(PostgreSQL)]

	 %% 1. 요청 및 검증
   React --> | 1. 질문 요청 JSON | Router
   Router --> | 2. 요청 본문 검증 | Schema
   Schema --> | 3. 검증된 DTO | Service
   
   %% 2. 초기 상태 저장 (RUNNING)
   Service --> | 4. 사용자 질문 저장 & 실행 상태 RUNNING | Repo
   Repo --> | 5. SQL Insert/Update | PG
   
   %% 3. LLM 호출
   Service --> | 6. 대화 기록 + 요청 | LLM
   LLM --> | 7. API Call | Gemini
   Gemini --> | 8. 답변 또는 Exception | LLM
   LLM --> | 9. 결과 또는 예외 전달 | Service
   
   %% 4. 결과 저장 (COMPLETED /FAILED) 및 실패 이력 조회
   Service --> | 10. AI 답변 저장, 상태 COMPLETED 또는 FAILED | Repo
   Service --> | 실패 이력 조회 요청 | Repo
   Repo --> | 11. SQL Query | PG
   PG --> | 12. DB 결과 데이터 | Repo
   Repo --> | 13. 엔티티/조회 결과 | Service
   
   %% 5. 응답 변환 및 반환
   Service --> | 14. 비즈니스 결과 객체 | Schema
   Schema --> | 15. Chat Response DTO 반환 | Router
   Router --> | 16. 최종 응답 JSON | React
```

- React 는 FastAPI 만 호출하고 Gemini 와 PostgreSQL 에 직접 닿지 않습니다.
- AI 호출과 저장 순서는 Service 한 곳에서 정합니다.
- Gemini 연결은 LLM Client, SQL 은 Repository 에 둡니다. 모델을 바꾸면 LLM Client 만 고칩니다.
- AI 실행은 호출 전에 `running` 으로 저장하고, 끝나면 `completed` 또는 `failed` 로 바꿉니다.

## API 명세

모든 엔드포인트는 요청자 식별용 `X-Client-Id` 헤더(`student-`로 시작)가 필요합니다. 헤더가 없으면 `422`, 형식이 맞지 않으면 `400`을 반환합니다.

| 사용자 행동 | Method·URL | 구현 상태 | Success | Error |
|---|---|---|---|---|
| 새 대화 시작 | `POST /api/conversations` | 예정 | `201` | `422` 제목 누락·빈 제목·100자 초과 |
| 대화 목록 확인 | `GET /api/conversations` | 예정 | `200` | `500` 서버 조회 실패 |
| 질문 전송 | `POST /api/conversations/{id}/messages` | 구현됨 | `200` | `400` 잘못된 `X-Client-Id` · `422` 헤더 누락·입력 오류 · `502` Gemini 실패(예정) |

```json
{ "content": "FastAPI의 장점을 설명해 줘" }
```

```json
{
  "conversation_id": 42,
  "user_message": { "id": 1, "role": "user", "content": "FastAPI의 장점을 설명해 줘" },
  "assistant_message": { "id": 2, "role": "assistant", "content": "..." }
}
```

## 실행 방법

```bash
# 서버 실행
uv run fastapi dev app/main.py

# 테스트 실행
uv run pytest
```

