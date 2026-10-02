"""Catálogo de pacotes de consultoria e as páginas de dossiê que cada um entrega.

Cada página tem um foco (o que o copiloto deve redigir) e o bloco de dados da ficha
que ela usa. O app mostra apenas as páginas do pacote contratado pela cliente.
"""

# Páginas reutilizáveis: chave -> (título, foco do rascunho, blocos de dados relevantes)
PAGINAS = {
    "perfil": ("Perfil e objetivo de imagem",
               "objetivo de imagem, estilo de vida e como a cliente quer ser percebida", ["cliente"]),
    "temperamento": ("Temperamento",
                     "como o temperamento primário e secundário aparece na imagem e nas escolhas de roupa",
                     ["temperamento"]),
    "visagismo": ("Visagismo — rosto, cabelo e franja",
                  "corte de cabelo, franja, óculos e acessórios pelo formato de rosto e contraste", ["visagismo"]),
    "tipologia": ("Tipologia física e silhueta",
                  "pontos de atenção da tipologia física, proporções e como valorizá-los", ["medidas"]),
    "coloracao": ("Coloração pessoal",
                  "como usar a cartela de cores no dia a dia, metais, contraste e combinações",
                  ["teste_coloracao", "coloracao"]),
    "mini_cartela": ("Mini cartela de cores",
                     "cores-base, cores de destaque e cores a evitar da cartela, com sugestões de uso",
                     ["coloracao"]),
    "estilo": ("Mapeamento de estilo",
               "estilo pessoal predominante e secundário, referências e peças-chave coerentes", ["cliente", "temperamento"]),
    "composicoes": ("Composições de looks",
                    "roteiro de composições combinando cartela, silhueta e estilo para as ocasiões da cliente",
                    ["coloracao", "medidas"]),
    "lista_compras": ("Lista de compras sugerida",
                      "peças prioritárias para completar o guarda-roupa, com cor, modelagem e motivo",
                      ["coloracao", "medidas"]),
    "closet": ("Revitalização do closet",
               "critérios para manter, ajustar ou desapegar peças e organizar o guarda-roupa", ["coloracao", "medidas"]),
    "shopping": ("Roteiro de personal shopping",
                 "objetivo das compras, lojas/tipos de peça a buscar e orçamento por prioridade", ["coloracao", "medidas"]),
    "olfativo": ("Estilo olfativo",
                 "famílias olfativas coerentes com o temperamento e o estilo da cliente", ["temperamento"]),
    "styling": ("Styling e comportamento",
                "acessórios, beleza, postura e comunicação não verbal alinhados à imagem desejada",
                ["temperamento", "visagismo"]),
    "corporativo": ("Posicionamento profissional",
                    "intenção profissional, dress code, etiqueta e presença digital", ["cliente", "temperamento"]),
    "mala": ("Mala planejada",
             "roteiro da viagem, clima, ocasiões e peças multiuso combinadas por dia", ["coloracao", "medidas"]),
    "evento": ("Styling para fotos e eventos",
               "briefing do evento, look escolhido, beleza e direcionamento no dia", ["coloracao", "visagismo"]),
}

PACOTES = {
    "pacote_1": ("Visagismo, Biotipo e Coloração", "Presencial",
                 ["perfil", "temperamento", "visagismo", "tipologia", "coloracao", "mini_cartela"]),
    "pacote_2": ("Guia de Estilo Estratégico", "Híbrido",
                 ["perfil", "estilo", "composicoes", "lista_compras", "styling"]),
    "pacote_3": ("Lookbook de Estilo", "Presencial", ["perfil", "composicoes", "styling"]),
    "pacote_4": ("Personal Shopping", "Presencial ou online", ["perfil", "shopping", "lista_compras"]),
    "pacote_5": ("Consultoria Completa — Híbrida", "8 encontros",
                 ["perfil", "temperamento", "visagismo", "tipologia", "coloracao", "mini_cartela", "estilo",
                  "olfativo", "closet", "shopping", "composicoes", "styling"]),
    "pacote_6": ("Consultoria Completa — Online", "8 encontros online",
                 ["perfil", "temperamento", "visagismo", "tipologia", "coloracao", "mini_cartela", "estilo",
                  "olfativo", "closet", "shopping", "composicoes", "styling"]),
    "pacote_7": ("Estilo Corporativo", "Presencial ou online",
                 ["perfil", "corporativo", "composicoes", "lista_compras", "styling"]),
    "pacote_8": ("Mala Planejada", "Presencial", ["perfil", "mala"]),
    "pacote_9": ("Styling para Fotos e Eventos", "Híbrido", ["perfil", "evento", "styling"]),
}


def nome(pacote: str) -> str:
    n, formato, _ = PACOTES.get(pacote, (pacote, "", []))
    return f"{pacote.replace('pacote_', 'Pacote ')} · {n}"


def paginas(pacote: str) -> dict:
    """Título -> (foco, blocos) das páginas do pacote, na ordem do dossiê."""
    chaves = PACOTES.get(pacote, PACOTES["pacote_1"])[2]
    return {PAGINAS[k][0]: (PAGINAS[k][1], PAGINAS[k][2]) for k in chaves}
