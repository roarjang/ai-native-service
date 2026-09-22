import pytest


URL = "/api/conversations/1/messages"
VALID_HEADERS = {"X-Client-Id": "student-01"}


def test_send_message_success(client):
    response = client.post(
        URL,
        headers=VALID_HEADERS,
        json={"content": "테스트 질문"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"] == 1
    assert body["assistant_message"]["content"] == "테스트 응답"


def test_missing_client_id(client):
    response = client.post(
        URL,
        json={"content": "테스트 질문"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["header", "X-Client-Id"]


def test_invalid_client_id(client):
    response = client.post(
        URL,
        headers={"X-Client-Id": "guest-01"},
        json={"content": "테스트 질문"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "X-Client-Id header invalid"

@pytest.mark.parametrize(
    "content,error_type",
    [
        ("", "string_too_short"),
        ("가" * 2001, "string_too_long"),
    ],
)
def test_invalid_content(client, content, error_type):
    response = client.post(
        URL,
        headers=VALID_HEADERS,
        json={"content": content},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == error_type




def test_invalid_conversation_id(client):
    response = client.post(
        "/api/conversations/abc/messages",
        headers=VALID_HEADERS,
        json={"content": "테스트 질문"},
    )
    assert response.status_code == 422
