from typing import Optional
from maestroia.config import settings

try:
    import openai
    _provider = getattr(settings, "LLM_PROVIDER", "openai")
    if _provider == "groq":
        client = openai.OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
        ) if settings.GROQ_API_KEY else None
    else:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
except Exception:
    openai = None
    client = None


def chat(prompt: str, model: Optional[str] = None, temperature: Optional[float] = None) -> str:
    """Enviar prompt para OpenAI (ChatCompletion). Retorna texto da resposta.

    Em caso de ausência do pacote `openai` ou erro, retorna mensagem de fallback.
    """
    model = model or settings.DEFAULT_LLM_MODEL
    temperature = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
    provider = getattr(settings, "LLM_PROVIDER", "openai")
    try:
        if not client:
            raise RuntimeError(f"Cliente {provider.upper()} não inicializado")

        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except Exception as e:
        # Fallback: retornar prompt ecoado com aviso para ambiente de dev
        label = "GROQ" if provider == "groq" else "OPENAI"
        return f"[FALLBACK {label}] Não foi possível contatar {label}: {e}. Prompt: {prompt[:500]}"


def generate_image(prompt: str, n: int = 1, size: str = "1024x1024") -> Optional[list]:
    try:
        if not client:
            raise RuntimeError("Cliente OpenAI não inicializado")
        img_resp = client.images.generate(
            prompt=prompt,
            n=n,
            size=size
        )
        urls = [d.url for d in img_resp.data]
        return urls
    except Exception:
        return None


def get_embedding(text: str) -> list:
    """Retorna embedding para `text`. Usa OpenAI Embeddings quando disponível; senão retorna vetor aleatório."""
    try:
        _ensure_api_key()
        if not openai:
            raise RuntimeError("Biblioteca openai não encontrada")
        model = getattr(settings, 'DEFAULT_EMBEDDING_MODEL', 'text-embedding-3-small')
        resp = openai.Embedding.create(model=model, input=text)
        # A resposta pode variar de formato; compatibilizar com list de floats
        emb = resp.data[0].embedding
        return emb
    except Exception:
        # fallback: vetor aleatório determinístico (hash) para estabilidade
        import hashlib
        import struct
        h = hashlib.sha256(text.encode('utf-8')).digest()
        # gerar vetor de floats a partir do hash repetido
        dims = getattr(settings, 'DEFAULT_EMBEDDING_DIM', 1536)
        vals = []
        while len(vals) < dims:
            for i in range(0, len(h), 4):
                if len(vals) >= dims:
                    break
                chunk = h[i:i+4]
                if len(chunk) < 4:
                    chunk = chunk.ljust(4, b"\0")
                vals.append(struct.unpack("!f", chunk)[0])
            h = hashlib.sha256(h).digest()
        return vals[:dims]
