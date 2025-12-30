# main.py

from core.ai_client import AIClient


def main():
    ai = AIClient()

    resposta = ai.ask(
        prompt="Responda apenas: MaestroIA operacional",
        system="Você é um assistente técnico conciso."
    )

    print(resposta)


if __name__ == "__main__":
    main()
