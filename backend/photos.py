"""Validação de imagens locais; o conteúdo nunca entra no RAG nem nos traces."""
import base64
import io
import re
from pathlib import Path
from PIL import Image


def safe_name(name):
    if Path(name).name != name or ".." in name or "/" in name or "\\" in name:
        raise ValueError("Nome da imagem inválido.")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", name)


def validate(data_url):
    if not data_url.startswith(("data:image/png;base64,", "data:image/jpeg;base64,")):
        raise ValueError("Envie PNG ou JPEG.")
    try:
        data = base64.b64decode(data_url.split(",", 1)[1], validate=True)
        if len(data) > 3_000_000:
            raise ValueError("Imagem maior que 3 MB.")
        image = Image.open(io.BytesIO(data))
        if image.width * image.height > 16_000_000:
            raise ValueError("Imagem com resolução muito grande.")
        if image.format not in ("PNG", "JPEG"):
            raise ValueError("Formato inválido.")
        image.verify()
        return data
    except (ValueError, Image.DecompressionBombError):
        raise
    except Exception as exc:
        raise ValueError("Não foi possível ler a imagem.") from exc
