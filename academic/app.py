"""Copiloto de Consultoria de Imagem — Etapa 1 (Streamlit).

O copiloto apoia a montagem do dossiê página a página: cruza o que a cliente
informa (questionário) com a avaliação técnica do consultor(a) e a metodologia
(RAG). Não automatiza métricas administrativas; a decisão final é do consultor(a).

Executar: streamlit run academic/app.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Chave: .env local ou Secrets do Streamlit Cloud. Nunca no código.
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT.parent / ".env")
except ImportError:
    pass
try:
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if name in st.secrets and not os.getenv(name):
            os.environ[name] = st.secrets[name]
except Exception:
    pass

import rag  # noqa: E402
import text_to_sql  # noqa: E402

st.set_page_config(page_title="Copiloto de Consultoria de Imagem", page_icon="🪞", layout="wide")

# ---------- Identidade visual (inspirada no dossiê: off-white, grafite, dourado) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Karla:wght@400;500;600&display=swap');
:root { --grafite:#2F2F33; --dourado:#B08D57; --claro:#EDEDEF; --papel:#F7F6F4; }
html, body, [class*="css"], .stMarkdown, p, li, label { font-family:'Karla', sans-serif; }
h1, h2, h3, h4 { font-family:'Cormorant Garamond', Georgia, serif !important; color:var(--grafite); letter-spacing:.3px; }
.stApp { background:var(--papel); }
section[data-testid="stSidebar"] { background:var(--grafite); }
section[data-testid="stSidebar"] * { color:#F2EFEA !important; }
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea { color:var(--grafite) !important; }
.stTabs [data-baseweb="tab"] { font-family:'Cormorant Garamond', serif; font-size:1.15rem; }
.stTabs [aria-selected="true"] { color:var(--dourado) !important; }
.stTabs [data-baseweb="tab-highlight"] { background:var(--dourado); }
.stButton button[kind="primary"] { background:var(--grafite); border:1px solid var(--dourado); }
.hero { padding:28px 32px; background:white; border-left:4px solid var(--dourado);
        border-radius:4px; margin-bottom:18px; box-shadow:0 8px 24px -16px rgba(47,47,51,.35); }
.hero small { text-transform:uppercase; letter-spacing:3px; color:var(--dourado); font-size:.72rem; }
.hero h1 { margin:4px 0 6px 0; font-size:2.3rem; }
.card { background:white; padding:16px 18px; border-radius:4px; border-top:2px solid var(--dourado);
        min-height:100%; box-shadow:0 6px 18px -14px rgba(47,47,51,.4); }
.card h4 { margin:0 0 8px 0; font-size:1.25rem; }
.card p { margin:2px 0; font-size:.9rem; }
.badge { display:inline-block; padding:2px 10px; border-radius:12px; font-size:.75rem;
         background:var(--dourado); color:white !important; }
.pg { display:inline-block; margin:2px 4px 2px 0; padding:3px 10px; border-radius:12px; font-size:.78rem;
      border:1px solid var(--dourado); }
.pg.ok { background:var(--dourado); color:white; }
.avatar { width:96px; height:96px; border-radius:50%; background:var(--dourado); display:flex;
          align-items:center; justify-content:center; font-family:'Cormorant Garamond'; font-size:2.4rem; color:white; }
</style>
""", unsafe_allow_html=True)

# ---------- Perfil do consultor(a): pré-preenchido, editável, só na sessão ----------
st.session_state.setdefault("perfil", {"nome": "Consultor(a) de Imagem", "marca": "Estúdio de Imagem & Estilo",
                                       "assinatura": "Imagem que comunica quem você é."})
perfil = st.session_state.perfil

with st.sidebar:
    foto = st.session_state.get("foto_consultor")
    if foto:
        st.image(foto, width=110)
    else:
        st.markdown(f'<div class="avatar">{perfil["nome"][:1]}</div>', unsafe_allow_html=True)
    st.markdown(f"### {perfil['nome']}")
    st.caption(perfil["marca"])
    with st.expander("✎ Editar meu perfil"):
        perfil["nome"] = st.text_input("Nome", perfil["nome"])
        perfil["marca"] = st.text_input("Marca / estúdio", perfil["marca"])
        perfil["assinatura"] = st.text_input("Assinatura do dossiê", perfil["assinatura"])
        up = st.file_uploader("Foto de perfil", type=["png", "jpg", "jpeg"])
        if up:
            st.session_state.foto_consultor = up.getvalue()
    st.divider()
    st.markdown('<span class="badge">Dados 100% fictícios</span>', unsafe_allow_html=True)
    st.caption("O copiloto sugere rascunhos. A análise e a aprovação final são sempre do consultor(a).")
    if not rag.api_key():
        st.warning("Chave Gemini não configurada: a IA mostrará só os trechos encontrados.")
    if st.button("Nova conversa no assistente"):
        st.session_state.messages = []

hora = datetime.now().hour
saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
st.markdown(f"""<div class="hero"><small>{perfil['marca']}</small>
<h1>{saudacao}, {perfil['nome'].split()[0]}.</h1>
<span>Vamos montar o dossiê da sua cliente, página por página. <em>{perfil['assinatura']}</em></span></div>""",
            unsafe_allow_html=True)

aba_dossie, aba_chat, aba_banco = st.tabs(["📖 Montagem do dossiê", "🧵 Assistente metodológico", "🔎 Padrões dos casos"])

# Páginas do dossiê (ordem do Guia) e o que cada uma pede ao copiloto.
PAGINAS = {
    "Perfil e objetivo de imagem": "objetivo de imagem, estilo de vida e como a cliente quer ser percebida",
    "Temperamento": "como o temperamento primário e secundário aparece na imagem e nas escolhas de roupa",
    "Visagismo — rosto, cabelo e franja": "corte de cabelo, franja, óculos e acessórios pelo formato de rosto e contraste",
    "Tipologia física e silhueta": "pontos de atenção da tipologia física, proporções e como valorizá-los",
    "Coloração pessoal": "como usar a cartela de cores no dia a dia, metais, contraste e combinações",
    "Estilo e montagem final": "estilo pessoal, peças-chave e combinações coerentes com objetivo, cartela e silhueta",
}

# ---------- 1. Montagem do dossiê ----------
with aba_dossie:
    text_to_sql.ensure_db()
    sessoes = text_to_sql.run(
        "SELECT s.sessao_id, c.identificador, c.modo, c.objetivo_imagem, s.data_sessao, s.status "
        "FROM sessoes s JOIN clientes c USING (cliente_id) ORDER BY s.sessao_id"
    )
    rotulo = {r.sessao_id: f"{r.identificador} · {r.data_sessao} · {r.status}" for r in sessoes.itertuples()}
    sid = st.selectbox("Cliente em atendimento", list(rotulo), format_func=rotulo.get)
    s = sessoes[sessoes.sessao_id == sid].iloc[0]

    def linha(tabela: str):
        df = text_to_sql.run(f"SELECT * EXCLUDE (sessao_id) FROM {tabela} WHERE sessao_id = '{sid}'")
        return df.iloc[0].dropna().to_dict() if len(df) else {}

    dados = {t: linha(t) for t in ("temperamento", "visagismo", "medidas", "teste_coloracao", "coloracao")}
    car = dados["coloracao"]

    st.markdown("#### 1 · O que a cliente trouxe e o que você avaliou")
    st.caption("Questionário da cliente + avaliação técnica do consultor(a). O copiloto cruza tudo na redação.")
    cols = st.columns(5)
    blocos = [("Cliente", {"modo": s.modo, "objetivo": s.objetivo_imagem}),
              ("Temperamento", dados["temperamento"]), ("Visagismo", dados["visagismo"]),
              ("Tipologia", dados["medidas"]), ("Coloração", {**dados["teste_coloracao"],
               **({"cartela": f"{car['cartela'].replace('_', ' ').title()} "
                   f"({'confirmada' if car.get('confirmada_pelo_consultor') == 'sim' else 'a confirmar'})"} if car else {})})]
    for col, (titulo, d) in zip(cols, blocos):
        itens = "".join(f"<p><b>{k.replace('_', ' ')}:</b> {v}</p>" for k, v in d.items())
        col.markdown(f'<div class="card"><h4>{titulo}</h4>{itens or "<p><i>pendente</i></p>"}</div>',
                     unsafe_allow_html=True)

    st.markdown("#### 2 · Páginas do dossiê")
    aprov = st.session_state.setdefault(f"aprovadas_{sid}", set())
    st.markdown("".join(f'<span class="pg {"ok" if p in aprov else ""}">{"✓ " if p in aprov else ""}{p}</span>'
                        for p in PAGINAS), unsafe_allow_html=True)
    st.progress(len(aprov) / len(PAGINAS), text=f"{len(aprov)} de {len(PAGINAS)} páginas aprovadas")

    pagina = st.radio("Página em edição", list(PAGINAS), horizontal=True, label_visibility="collapsed")
    chave = f"texto_{sid}_{pagina}"
    st.session_state.setdefault(chave, "")

    esq, dir_ = st.columns([3, 2])
    with esq:
        st.markdown(f"### {pagina}")
        if st.button("✨ Sugerir texto desta página", type="primary"):
            if not rag.api_key():
                st.error("Configure a chave Gemini para gerar rascunhos.")
            else:
                with st.spinner("Escrevendo rascunho fundamentado na metodologia…"):
                    trechos = rag.retrieve(f"{PAGINAS[pagina]} {dados['visagismo'].get('formato_rosto', '')} "
                                           f"{car.get('cartela', '')} {dados['temperamento'].get('primario', '')}")
                    ficha = "\n".join(f"{t}: {d}" for t, d in dados.items())
                    prompt = (f"Cliente fictícia: {s.identificador} ({s.modo}); objetivo: {s.objetivo_imagem}\n"
                              f"Ficha:\n{ficha}\n\nEscreva a página '{pagina}' do dossiê ({PAGINAS[pagina]}) "
                              f"em 1–3 parágrafos, falando diretamente com a cliente ('você'), tom acolhedor e técnico. "
                              f"Use apenas o que é relevante para esta página.\n\nFundamentação:\n{rag._context(trechos)}")
                    st.session_state[chave] = rag.generate(
                        prompt, rag.SYSTEM_PROMPT + "\nNão cite fontes no texto final da cliente.", 0.5)
        st.text_area("Rascunho (edite livremente antes de aprovar)", key=chave, height=260)
        b1, b2 = st.columns(2)
        if st.session_state[chave]:
            if pagina in aprov:
                if b1.button("↺ Reabrir página"):
                    aprov.discard(pagina); st.rerun()
            elif b1.button("✓ Aprovar página"):
                aprov.add(pagina); st.rerun()
            st.caption("⚠️ Rascunho gerado por IA — revise antes de aprovar.")
    with dir_:
        st.markdown("##### Referências visuais da página")
        st.caption("Bases e fotos preparadas por você. Ficam só nesta sessão — nunca são salvas no app.")
        imgs = st.file_uploader("Adicionar imagens", type=["png", "jpg", "jpeg"], accept_multiple_files=True,
                                key=f"img_{sid}_{pagina}")
        if imgs:
            st.image([i.getvalue() for i in imgs], width=140)

    if aprov:
        texto = f"{perfil['marca']} — Dossiê {s.identificador}\n{perfil['assinatura']}\n\n" + "\n\n".join(
            f"## {p}\n{st.session_state.get(f'texto_{sid}_{p}', '')}" for p in PAGINAS if p in aprov)
        st.download_button("⬇ Baixar páginas aprovadas", texto, file_name=f"dossie_{sid}.md")

# ---------- 2. Assistente metodológico (RAG + streaming) ----------
with aba_chat:
    st.caption("Dúvida técnica durante o atendimento? Pergunte sobre coloração, visagismo, temperamento, "
               "tipologia ou estilo. As respostas citam o resumo e a seção usados.")
    st.session_state.setdefault("messages", [])
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🧵" if m["role"] == "assistant" else None):
            st.markdown(m["content"])
            if m.get("fontes"):
                st.caption("Fontes: " + " · ".join(m["fontes"]))

    pergunta = st.chat_input("Ex.: Que corte valoriza rosto quadrado com contraste alto?")
    if pergunta:
        history = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)
        with st.chat_message("assistant", avatar="🧵"):
            try:
                with st.spinner("Buscando na metodologia…"):
                    partes, trechos = rag.stream_answer(pergunta, history)
                texto = st.write_stream(partes)
            except Exception as exc:
                texto, trechos = f"Não foi possível gerar a resposta agora ({type(exc).__name__}). Tente novamente em instantes.", []
                st.error(texto)
            fontes = list(dict.fromkeys(f"{t['fonte']} › {t['secao']}" for t in trechos))
            if fontes:
                st.caption("Fontes: " + " · ".join(fontes))
                with st.expander("Ver trechos recuperados"):
                    for t in trechos:
                        st.markdown(f"**{t['fonte']} › {t['secao']}**\n\n{t['texto']}")
        st.session_state.messages.append({"role": "assistant", "content": texto, "fontes": fontes})

# ---------- 3. Padrões técnicos dos casos (Text-to-SQL no DuckDB) ----------
with aba_banco:
    st.caption("Compare casos fictícios por critérios técnicos (cartela, contraste, rosto, temperamento). "
               "O copiloto gera uma consulta somente leitura e mostra o SQL usado.")
    exemplos = ["Quais clientes têm contraste alto e qual o formato de rosto delas?",
                "Que cartelas aparecem junto com temperamento melancólico?",
                "Quais cartelas ainda estão aguardando confirmação do consultor?"]
    escolha = st.selectbox("Exemplos", ["—"] + exemplos)
    q = st.text_input("Sua pergunta", value="" if escolha == "—" else escolha)
    if st.button("Consultar", type="primary") and q:
        if not rag.api_key():
            st.error("Configure a chave Gemini para consultar em linguagem natural.")
        else:
            try:
                with st.spinner("Gerando a consulta…"):
                    sql = text_to_sql.to_sql(q)
                st.code(sql, language="sql")
                df = text_to_sql.run(sql)
                st.dataframe(df, use_container_width=True)
                st.info(text_to_sql.summarize(q, sql, df.head(20).to_markdown(index=False)))
            except Exception as exc:
                st.error(f"Não consegui responder: {exc}")
