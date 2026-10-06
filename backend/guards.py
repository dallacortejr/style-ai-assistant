"""Guardrails básicos e auditáveis. Não são um detector universal de ataques."""
import re
import unicodedata


def plain(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def anonymize(text: str) -> str:
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b", "[EMAIL]", text)
    text = re.sub(r"\b\d{3}[. ]?\d{3}[. ]?\d{3}[- ]?\d{2}\b", "[CPF]", text)
    return re.sub(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?[ -]*)?9\d{4}[ -]?\d{4}(?!\d)", "[TELEFONE]", text)


def check_input(text: str) -> str:
    normalized = plain(text)
    attacks = (
        r"ignore.{0,40}(instruc|regra|prompt)",
        r"(revele|mostre|exiba).{0,40}(system prompt|chave|segredo|senha)",
        r"(aprove|aprovar|publique|publicar).{0,30}(automatic|sem revis|sem consult)",
        r"(diagnostique|diagnostico medico|doenca pela foto)",
        r"(ameace|humilhe|ofenda).{0,30}(cliente|pessoa)",
    )
    if any(re.search(pattern, normalized) for pattern in attacks):
        raise ValueError("Pedido bloqueado: o copiloto não revela segredos, faz diagnóstico ou substitui a aprovação do consultor.")
    return anonymize(text)


def check_output(text: str) -> str:
    if re.search(r"(?:AIza[\w-]{25,}|sk-[\w-]{20,})", text):
        raise ValueError("A saída foi bloqueada por conter um possível segredo.")
    if re.search(r"(automaticamente aprovado|dispensa.{0,20}consultor)", plain(text)):
        raise ValueError("A saída tentou substituir a revisão profissional.")
    return anonymize(text)
