class FakeLLMClient:
    def __init__(self, reply: str = "테스트용 AI 응답"):
        self.reply = reply

    async def generate(self, prompt: str) -> str:
        return self.reply

class FailingLLMClient:
    async def generate(self, prompt: str) -> str:
        raise TimeoutError("LLM 응답 시간 초과")
