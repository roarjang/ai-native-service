from datetime import datetime, timedelta, timezone


import jwt
import pytest
from pwdlib import PasswordHash


from app.models.conversation import Conversation
from app.models.user import User
from app.settings import settings


HEADERS = {"X-Client-Id": "student-01"}
PASSWORD_A = "studentA-pass"
PASSWORD_B = "studentB-pass"


password_hash = PasswordHash.recommended()




# ── 준비 ──────────────────────────────────────────────────────
@pytest.fixture
def users(session):
   """A · B 두 계정. 타인 접근을 보려면 둘이 필요합니다."""
   user_a = User(email="a@example.com", password_hash=password_hash.hash(PASSWORD_A))
   user_b = User(email="b@example.com", password_hash=password_hash.hash(PASSWORD_B))
   session.add(user_a)
   session.add(user_b)
   session.commit()
   session.refresh(user_a)
   session.refresh(user_b)
   return user_a, user_b




@pytest.fixture
def conversation_a(session, users):
   """A 가 주인인 대화 하나."""
   user_a, _ = users
   row = Conversation(title="A 의 대화", user_id=user_a.id)
   session.add(row)
   session.commit()
   session.refresh(row)
   return row




def login(client, email: str, password: str):
   return client.post(
       "/api/auth/token",
       data={"username": email, "password": password},
   )




def token_of(client, email: str, password: str) -> str:
   response = login(client, email, password)
   assert response.status_code == 200, response.text
   return response.json()["access_token"]




def with_token(token: str) -> dict[str, str]:
   return {**HEADERS, "Authorization": f"Bearer {token}"}




# ── 1. 올바른 계정 로그인 → 200 ───────────────────────────────
def test_login_success(db_client, users):
   response = login(db_client, "a@example.com", PASSWORD_A)


   assert response.status_code == 200
   body = response.json()
   assert body["token_type"] == "bearer"
   assert body["access_token"]




# ── 2. 잘못된 비밀번호 → 401 ──────────────────────────────────
def test_login_wrong_password(db_client, users):
   response = login(db_client, "a@example.com", "틀린-비밀번호")


   assert response.status_code == 401




# ── 3. 토큰 없는 보호 API → 401 ───────────────────────────────
def test_list_without_token(db_client, users):
   response = db_client.get("/api/conversations", headers=HEADERS)


   assert response.status_code == 401




# ── 4. 변조 토큰 → 401 ────────────────────────────────────────
def test_list_with_tampered_token(db_client, users):
   token = token_of(db_client, "a@example.com", PASSWORD_A)
   tampered = token[:-1] + ("a" if token[-1] != "a" else "b")


   response = db_client.get("/api/conversations", headers=with_token(tampered))


   assert response.status_code == 401




# ── 5. 만료 토큰 → 401 ────────────────────────────────────────
def test_list_with_expired_token(db_client, users):
   user_a, _ = users
   expired = jwt.encode(
       {
           "sub": str(user_a.id),
           "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
       },
       settings.jwt_secret_key.get_secret_value(),
       algorithm="HS256",
   )


   response = db_client.get("/api/conversations", headers=with_token(expired))


   assert response.status_code == 401




# ── 6. A 가 A 대화 조회 → 200 ─────────────────────────────────
def test_owner_can_read_own_conversation(db_client, conversation_a):
   token = token_of(db_client, "a@example.com", PASSWORD_A)


   listed = db_client.get("/api/conversations", headers=with_token(token))
   assert listed.status_code == 200
   assert [row["id"] for row in listed.json()] == [conversation_a.id]


   detail = db_client.get(
       f"/api/conversations/{conversation_a.id}/messages",
       headers=with_token(token),
   )
   assert detail.status_code == 200




# ── 7. B 가 A 대화 조회 → 404 ─────────────────────────────────
def test_other_user_gets_404(db_client, conversation_a):
   token = token_of(db_client, "b@example.com", PASSWORD_B)


   listed = db_client.get("/api/conversations", headers=with_token(token))
   assert listed.status_code == 200
   assert listed.json() == []


   detail = db_client.get(
       f"/api/conversations/{conversation_a.id}/messages",
       headers=with_token(token),
   )
   # 403 이 아니라 404 입니다. 403 은 「그 대화가 있다」는 사실을 알려 줍니다.
   assert detail.status_code == 404




# ── 8. 로그인 입력 검증 실패 → 422 ────────────────────────────
def test_login_missing_fields(db_client, users):
   response = db_client.post("/api/auth/token", data={})


   assert response.status_code == 422
