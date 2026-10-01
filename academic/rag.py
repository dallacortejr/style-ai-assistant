"""Perguntas fundamentadas nos resumos; LLM opcional exige chave de API própria."""

import os

from knowledge_index import retrieve


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


def answer(question: str) -> dict:
    passages = retrieve(question)
    if not passages:
        return {"resposta": "A base ainda não foi indexada ou não há trechos disponíveis.", "fontes": []}
    sources = [{"fonte": p["fonte"], "secao": p["secao"]} for p in passages]
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return {"resposta": "Trechos encontrados. Para gerar uma resposta fundamentada, configure sua chave Gemini; as fontes recuperadas estão abaixo.", "fontes": sources, "trechos": passages}
    from google import genai

    context = "\n\n".join(
        f"Fonte: {p['fonte']} | Seção: {p['secao']}\n{p['texto']}" for p in passages
    )
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Pergunta: {question}\n\nTrechos recuperados:\n{context}",
        config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.2},
    )
    return {"resposta": response.text or "Não foi possível gerar uma resposta.", "fontes": sources}