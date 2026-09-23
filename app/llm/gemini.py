from langchain_litellm import ChatLiteLLM


class GeminiLLMClient:
    def __init__(self, model_name: str):
        self.model = ChatLiteLLM(
            model=model_name,
            temperature=0.2,
        )

    async def generate(self, prompt: str) -> str:
        response = await self.model.ainvoke(prompt)
        if not isinstance(response.content, str):
            raise TypeError("텍스트가 아닌 LLM 응답")
        return response.content
