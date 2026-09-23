class FakeLLMClient:
    def __init__(self, reply: str = "테스트용 AI 응답"):
        self.reply = reply

    async def generate(self, prompt: str) -> str:
        return self.reply
