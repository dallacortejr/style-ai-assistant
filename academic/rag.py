"""Perguntas fundamentadas nos resumos; LLM opcional exige chave de API própria."""

import os
from collections.abc import Iterator

from knowledge_index import retrieve


MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """Você é um copiloto de consultoria de imagem e estilo para consultores(as).
Responda em português brasileiro, de modo cuidadoso e objetivo. Use SOMENTE os
trechos de resumos próprios recuperados como fundamentação técnica. Cite a fonte
e a seção de cada afirmação relevante. Se não houver fundamento suficiente,
diga que não encontrou respaldo na base; não invente uma resposta nem uma fonte.
Não diagnostique uma pessoa só por texto ou fotografia. Coloração exige teste
comparativo; a forma segue a função, portanto considere o objetivo de imagem.
As sugestões são rascunhos e nunca substituem a decisão do consultor(a).
Não inclua dados pessoais reais nem reproduza longos trechos de publicações.
"""


def api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


_CLIENT = None


def client():
    """Cliente único reaproveitado (um cliente temporário é fechado antes do uso)."""
    global _CLIENT
    if _CLIENT is None:
        from google import genai
        _CLIENT = genai.Client(api_key=api_key())
    return _CLIENT


def _context(passages: list[dict]) -> str:
    return "\n\n".join(
        f"Fonte: {p['fonte']} | Seção: {p['secao']}\n{p['texto']}" for p in passages
    )


def _contents(question: str, passages: list[dict], history: list[dict] | None) -> str:
    previous = "\n".join(
        f"{'Consultor(a)' if m['role'] == 'user' else 'Copiloto'}: {m['content']}"
        for m in (history or [])[-6:]
    )
    return (
        (f"Conversa anterior:\n{previous}\n\n" if previous else "")
        + f"Pergunta: {question}\n\nTrechos recuperados:\n{_context(passages)}"
    )


def stream_answer(question: str, history: list[dict] | None = None) -> tuple[Iterator[str], list[dict]]:
    """Retorna (gerador de texto em partes, trechos usados)."""
    passages = retrieve(question)
    if not passages:
        return iter(["A base ainda não foi indexada ou não há trechos disponíveis."]), []
    if not api_key():
        return iter(["Trechos encontrados. Configure a chave Gemini para gerar a resposta; as fontes estão abaixo."]), passages

    def gen() -> Iterator[str]:
        for chunk in client().models.generate_content_stream(
            model=MODEL,
            contents=_contents(question, passages, history),
            config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.2},
        ):
            if chunk.text:
                yield chunk.text

    return gen(), passages


def answer(question: str) -> dict:
    parts, passages = stream_answer(question)
    return {"resposta": "".join(parts),
            "fontes": [{"fonte": p["fonte"], "secao": p["secao"]} for p in passages]}


def generate(prompt: str, system: str, temperature: float = 0.2) -> str:
    """Até 3 tentativas com espera crescente só para sobrecarga (429/503)."""
    import time
    from google.genai import errors

    for attempt in range(3):
        try:
            response = client().models.generate_content(
                model=MODEL, contents=prompt,
                config={"system_instruction": system, "temperature": temperature},
            )
            return response.text or ""
        except errors.APIError as exc:
            if getattr(exc, "code", None) not in (429, 503) or attempt == 2:
                raise
            time.sleep(4 * 2 ** attempt)
    return ""
