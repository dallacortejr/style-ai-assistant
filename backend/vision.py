from pathlib import Path
import math

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODELO_PADRAO = Path(__file__).resolve().parents[1] / "runtime" / "models" / "face_landmarker.task"


def distancia(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2
        +
        (p1.y - p2.y) ** 2
    )


def extrair_medidas(landmarks):
    """
    Extrai medidas geométricas normalizadas
    a partir de landmarks faciais.

    As medidas são experimentais e destinadas
    ao apoio preliminar do MVP.
    """

    indices = {
        "topo_rosto": 10,
        "queixo": 152,
        "lateral_esquerda_rosto": 234,
        "lateral_direita_rosto": 454,
        "testa_esquerda": 70,
        "testa_direita": 300,
        "mandibula_esquerda": 172,
        "mandibula_direita": 397
    }

    pontos = {
        nome: landmarks[indice]
        for nome, indice in indices.items()
    }

    largura_rosto = distancia(
        pontos["lateral_esquerda_rosto"],
        pontos["lateral_direita_rosto"]
    )

    altura_rosto = distancia(
        pontos["topo_rosto"],
        pontos["queixo"]
    )

    largura_testa = distancia(
        pontos["testa_esquerda"],
        pontos["testa_direita"]
    )

    largura_mandibula = distancia(
        pontos["mandibula_esquerda"],
        pontos["mandibula_direita"]
    )

    altura_largura = (
        altura_rosto / largura_rosto
        if largura_rosto != 0
        else None
    )

    testa_mandibula = (
        largura_testa / largura_mandibula
        if largura_mandibula != 0
        else None
    )

    return {
        "largura_rosto": largura_rosto,
        "altura_rosto": altura_rosto,
        "largura_testa": largura_testa,
        "largura_mandibula": largura_mandibula,
        "altura_largura": altura_largura,
        "testa_mandibula": testa_mandibula
    }


def classificar_formato(medidas):
    """
    Classificação heurística experimental.

    Não representa metodologia profissional validada.
    A saída deve ser tratada somente como hipótese
    inicial para revisão da consultora.
    """

    altura_largura = medidas[
        "altura_largura"
    ]

    testa_mandibula = medidas[
        "testa_mandibula"
    ]

    evidencias = []
    candidatos = []

    if altura_largura is None:
        return {
            "hipotese_formato": "Indeterminado",
            "nivel_confianca": "Baixa",
            "evidencias": [
                "Não foi possível calcular "
                "a proporção altura/largura."
            ]
        }

    if altura_largura >= 1.30:
        evidencias.append(
            "O rosto apresenta proporção "
            "consideravelmente mais alta do que larga."
        )

        candidatos.extend([
            "Retangular",
            "Oval"
        ])

    elif altura_largura >= 1.12:
        evidencias.append(
            "O rosto apresenta proporção "
            "moderadamente mais alta do que larga."
        )

        candidatos.extend([
            "Oval",
            "Retangular"
        ])

    elif altura_largura >= 0.95:
        evidencias.append(
            "A altura e a largura do rosto apresentam "
            "proporções relativamente próximas."
        )

        candidatos.extend([
            "Quadrado",
            "Oval"
        ])

    else:
        evidencias.append(
            "A largura apresenta proporção elevada "
            "em relação à altura."
        )

        candidatos.extend([
            "Redondo",
            "Quadrado"
        ])

    if testa_mandibula is not None:

        if testa_mandibula >= 1.12:
            evidencias.append(
                "A testa apresenta largura maior "
                "que a mandíbula."
            )

            candidatos.insert(
                0,
                "Coração"
            )

        elif testa_mandibula <= 0.88:
            evidencias.append(
                "A mandíbula apresenta largura maior "
                "que a testa."
            )

            candidatos.insert(
                0,
                "Triangular"
            )

        else:
            evidencias.append(
                "Testa e mandíbula apresentam "
                "larguras relativamente semelhantes."
            )

    pontuacao = {}

    for candidato in candidatos:
        pontuacao[candidato] = (
            pontuacao.get(
                candidato,
                0
            )
            + 1
        )

    if not pontuacao:
        hipotese = "Indeterminado"
        confianca = "Baixa"

    else:
        ordenados = sorted(
            pontuacao.items(),
            key=lambda item: item[1],
            reverse=True
        )

        hipotese = ordenados[0][0]

        maior_score = ordenados[0][1]

        segundo_score = (
            ordenados[1][1]
            if len(ordenados) > 1
            else 0
        )

        diferenca = (
            maior_score
            - segundo_score
        )

        if (
            maior_score >= 2
            and diferenca >= 1
        ):
            confianca = "Média"

        else:
            confianca = "Baixa"

    if (
        1.05 <= altura_largura <= 1.25
        and testa_mandibula is not None
        and 0.93 <= testa_mandibula <= 1.07
    ):
        hipotese = "Oval"

        confianca = "Média"

        evidencias.append(
            "A combinação de altura ligeiramente "
            "superior à largura e equilíbrio entre "
            "testa e mandíbula favorece a hipótese oval."
        )

    return {
        "hipotese_formato": hipotese,
        "nivel_confianca": confianca,
        "evidencias": evidencias
    }


def analisar_foto(
    caminho_imagem,
    caminho_modelo=MODELO_PADRAO
):
    """
    Executa a análise facial preliminar completa.

    Retorno:
    {
        rosto_detectado,
        landmarks_detectados,
        medidas,
        classificacao_preliminar,
        status
    }
    """

    caminho_imagem = Path(
        caminho_imagem
    )

    caminho_modelo = Path(
        caminho_modelo
    )

    if not caminho_imagem.exists():
        raise FileNotFoundError(
            f"Imagem não encontrada: {caminho_imagem}"
        )

    if not caminho_modelo.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado: {caminho_modelo}"
        )

    imagem_bgr = cv2.imread(
        str(
            caminho_imagem
        )
    )

    if imagem_bgr is None:
        raise RuntimeError(
            "Não foi possível abrir a imagem."
        )

    imagem_rgb = cv2.cvtColor(
        imagem_bgr,
        cv2.COLOR_BGR2RGB
    )

    imagem_mp = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=imagem_rgb
    )

    base_options = python.BaseOptions(
        model_asset_path=str(
            caminho_modelo
        )
    )

    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    with vision.FaceLandmarker.create_from_options(
        options
    ) as detector:

        resultado = detector.detect(
            imagem_mp
        )

    if not resultado.face_landmarks:
        return {
            "rosto_detectado": False,
            "landmarks_detectados": 0,
            "medidas": None,
            "classificacao_preliminar": None,
            "status": "ROSTO_NAO_DETECTADO"
        }

    landmarks = resultado.face_landmarks[0]

    medidas = extrair_medidas(
        landmarks
    )

    classificacao = classificar_formato(
        medidas
    )

    return {
        "rosto_detectado": True,
        "landmarks_detectados": len(
            landmarks
        ),
        "medidas": medidas,
        "classificacao_preliminar": classificacao,
        "status": (
            "HIPOTESE_AUTOMATICA_NAO_VALIDADA"
        )
    }
