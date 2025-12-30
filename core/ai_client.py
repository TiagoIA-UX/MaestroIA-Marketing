# core/ai_client.py

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIClient:
    """
    Cliente central de IA.
    Isola OpenAI do resto do sistema.
    Facilita troca de modelo, logging, cache e controle de custo.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não encontrada no .env")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def ask(self, prompt: str, system: str | None = None) -> str:
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
