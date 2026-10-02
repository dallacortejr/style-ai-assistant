"""Copiloto de Consultoria de Imagem — Etapa 1 (Streamlit).

O copiloto apoia a montagem do dossiê página a página, de acordo com o pacote
contratado pela cliente: cruza o questionário da cliente com a avaliação técnica
do consultor(a) e a metodologia (RAG). A decisão final é sempre do consultor(a).

Executar: streamlit run academic/app.py
"""

import io
import json
import os
import sys
import zipfile
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

import pacotes  # noqa: E402
import rag  # noqa: E402
import text_to_sql  # noqa: E402

st.set_page_config(page_title="Copiloto de Consultoria de Imagem", page_icon="◐", layout="wide")

# ---------- Identidade visual: papel, grafite, areia, terracota, oliva ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Karla:wght@400;500;600&display=swap');
:root { --papel:#F9F8F6; --linho:#F0EDE6; --grafite:#2C2B2A; --suave:#6B6660; --areia:#C9B79C;
        --terracota:#A65F43; --oliva:#6F7051; --linha:#E2DDD3; }
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button { font-family:'Karla', sans-serif; color:var(--grafite); }
h1, h2, h3, h4, h5 { font-family:'Cormorant Garamond', Georgia, serif !important; color:var(--grafite) !important;
                     font-weight:600 !important; letter-spacing:.2px; }
.stApp { background:var(--papel); }
[data-testid="stHeader"] { background:transparent; }

/* Sidebar clara em linho: todo texto escuro, sem branco sobre branco */
section[data-testid="stSidebar"] { background:var(--linho); border-right:1px solid var(--linha); }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small, section[data-testid="stSidebar"] div { color:var(--grafite); }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] { background:var(--papel); border:1px dashed var(--areia); }
section[data-testid="stSidebar"] [data-testid="stExpander"] { background:var(--papel); border:1px solid var(--linha); border-radius:6px; }
.perfil { text-align:center; padding:8px 0 4px; }
.perfil img, .avatar { width:104px; height:104px; border-radius:50%; object-fit:cover; margin:0 auto 12px; display:block;
                       border:2px solid var(--areia); }
.avatar { background:var(--terracota); color:var(--papel) !important; display:flex; align-items:center; justify-content:center;
          font-family:'Cormorant Garamond', serif; font-size:2.6rem; }
.perfil h3 { margin:0; font-size:1.5rem; }
.perfil .marca { color:var(--suave); font-size:.85rem; letter-spacing:1.5px; text-transform:uppercase; }
.nota { font-size:.8rem; color:var(--suave); text-align:center; }

/* Botões */
.stButton button, .stDownloadButton button { border-radius:999px; border:1px solid var(--grafite); background:transparent;
                                             color:var(--grafite); font-weight:500; padding:.35rem 1.2rem; }
.stButton button:hover, .stDownloadButton button:hover { border-color:var(--terracota); color:var(--terracota); }
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"] { background:var(--grafite); color:var(--papel); }
.stButton button[kind="primary"] p, .stDownloadButton button[kind="primary"] p { color:var(--papel); }
.stButton button[kind="primary"]:hover { background:var(--terracota); border-color:var(--terracota); color:var(--papel); }

/* Abas tipográficas */
.stTabs [data-baseweb="tab-list"] { gap:28px; border-bottom:1px solid var(--linha); }
.stTabs [data-baseweb="tab"] { font-family:'Cormorant Garamond', serif; font-size:1.25rem; padding:6px 0; }
.stTabs [data-baseweb="tab"] p { font-family:'Cormorant Garamond', serif; font-size:1.25rem; }
.stTabs [aria-selected="true"] p { color:var(--terracota); }
.stTabs [data-baseweb="tab-highlight"] { background:var(--terracota); }

/* Blocos editoriais */
.hero { padding:36px 40px; background:var(--linho); border-radius:6px; margin-bottom:22px; }
.eyebrow { text-transform:uppercase; letter-spacing:3px; color:var(--terracota); font-size:.72rem; font-weight:600; }
.hero h1 { margin:6px 0 8px; font-size:2.7rem; }
.hero p { color:var(--suave); margin:0; max-width:720px; }
.hero em { font-family:'Cormorant Garamond', serif; font-size:1.15rem; color:var(--grafite); }
.secao { margin:26px 0 6px; }
.secao .eyebrow { display:block; }
.secao h3 { margin:2px 0 0; font-size:1.7rem; }
.card { background:#FFFFFF; padding:18px 20px; border-radius:6px; border:1px solid var(--linha); height:100%; }
.card h4 { margin:0 0 10px; font-size:1.3rem; border-bottom:1px solid var(--linha); padding-bottom:6px; }
.card p { margin:3px 0; font-size:.88rem; }
.card b { color:var(--suave); font-weight:500; }
.pill { display:inline-block; margin:3px 6px 3px 0; padding:4px 14px; border-radius:999px; font-size:.8rem;
        border:1px solid var(--linha); color:var(--suave); background:#FFFFFF; }
.pill.on { background:var(--grafite); border-color:var(--grafite); color:var(--papel); }
.pill.ok { background:var(--oliva); border-color:var(--oliva); color:var(--papel); }
.pacote { background:#FFFFFF; border:1px solid var(--linha); border-left:3px solid var(--terracota); border-radius:6px;
          padding:14px 18px; margin:8px 0 4px; }
.pacote small { color:var(--suave); }
.stProgress > div > div > div > div { background:var(--oliva); }
</style>
""", unsafe_allow_html=True)

# ---------- Perfil do consultor(a): pré-preenchido, editável, só na sessão ----------
st.session_state.setdefault("perfil", {"nome": "Consultor de Imagem", "marca": "Estúdio de Imagem & Estilo",
                                       "assinatura": "Imagem que comunica quem você é."})
perfil = st.session_state.perfil

with st.sidebar:
    with st.expander("Editar meu perfil"):
        perfil["nome"] = st.text_input("Nome", perfil["nome"])
        perfil["marca"] = st.text_input("Marca / estúdio", perfil["marca"])
        perfil["assinatura"] = st.text_input("Assinatura do dossiê", perfil["assinatura"])
        up = st.file_uploader("Foto de perfil", type=["png", "jpg", "jpeg"])
        if up is not None and st.session_state.get("foto_id") != up.file_id:
            st.session_state.foto_consultor = up.getvalue()
            st.session_state.foto_id = up.file_id
        if st.session_state.get("foto_consultor") and st.button("Remover foto"):
            st.session_state.pop("foto_consultor")

    foto = st.session_state.get("foto_consultor")
    if foto:
        import base64
        tag = f'<img src="data:image/png;base64,{base64.b64encode(foto).decode()}">'
    else:
        tag = f'<div class="avatar">{(perfil["nome"] or "C")[:1].upper()}</div>'
    # Perfil exibido depois do expander para refletir a foto/nome na mesma execução.
    st.markdown(f'<div class="perfil">{tag}<h3>{perfil["nome"]}</h3>'
                f'<div class="marca">{perfil["marca"]}</div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<p class="nota">Demonstração acadêmica com dados fictícios.<br>'
                'O copiloto sugere; a análise e a aprovação são do consultor.</p>', unsafe_allow_html=True)
    if not rag.api_key():
        st.warning("Chave Gemini não configurada: a IA mostrará só os trechos encontrados.")
    if st.button("Nova conversa no assistente", use_container_width=True):
        st.session_state.messages = []

hora = datetime.now().hour
saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
st.markdown(f"""<div class="hero"><span class="eyebrow">{perfil['marca']}</span>
<h1>{saudacao}, {(perfil['nome'].split() or ['consultor'])[0]}.</h1>
<p>Escolha a cliente, confira o pacote contratado e monte o dossiê página por página.
<em>{perfil['assinatura']}</em></p></div>""", unsafe_allow_html=True)


def secao(rotulo: str, titulo: str):
    st.markdown(f'<div class="secao"><span class="eyebrow">{rotulo}</span><h3>{titulo}</h3></div>',
                unsafe_allow_html=True)


aba_dossie, aba_chat, aba_banco = st.tabs(["Dossiê da cliente", "Metodologia", "Padrões dos casos"])


def exportar_pasta(sid: str, identificador: str, pacote: str, paginas: dict) -> bytes:
    """Pasta da cliente (.zip) para o consultor(a) guardar no próprio computador."""
    fotos = st.session_state.get(f"fotos_{sid}", {})
    nomes = list(paginas)
    ficha = {"versao": 2, "sessao_id": sid, "cliente": identificador, "pacote": pacote,
             "pacote_nome": pacotes.nome(pacote), "salvo_em": datetime.now().isoformat(timespec="minutes"),
             "paginas": {p: st.session_state.get(f"texto_{sid}_{p}", "") for p in nomes},
             "aprovadas": sorted(st.session_state.get(f"aprovadas_{sid}", set())),
             "fotos": {p: [n for n, _ in fotos.get(p, [])] for p in nomes if fotos.get(p)}}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("ficha.json", json.dumps(ficha, ensure_ascii=False, indent=2))
        for i, p in enumerate(nomes):
            for n, b in fotos.get(p, []):
                z.writestr(f"fotos/{i + 1:02d}/{n}", b)
    return buf.getvalue()


def importar_pasta(arquivo) -> str:
    """Reabre uma pasta salva: restaura pacote, textos, aprovações e fotos na sessão."""
    with zipfile.ZipFile(arquivo) as z:
        ficha = json.loads(z.read("ficha.json"))
        sid = ficha["sessao_id"]
        pacote = ficha.get("pacote", "pacote_1")
        nomes = list(ficha.get("paginas") or pacotes.paginas(pacote))
        fotos = {}
        for info in z.infolist():
            partes = info.filename.split("/")
            if len(partes) == 3 and partes[0] == "fotos" and partes[2] and int(partes[1]) <= len(nomes):
                fotos.setdefault(nomes[int(partes[1]) - 1], []).append((partes[2], z.read(info)))
    st.session_state[f"pacote_{sid}"] = pacote
    for p, t in ficha.get("paginas", {}).items():
        st.session_state[f"texto_{sid}_{p}"] = t
    st.session_state[f"aprovadas_{sid}"] = set(ficha.get("aprovadas", []))
    st.session_state[f"fotos_{sid}"] = fotos
    return sid


# ---------- 1. Dossiê da cliente ----------
with aba_dossie:
    text_to_sql.ensure_db()
    sessoes = text_to_sql.run(
        "SELECT s.sessao_id, c.identificador, c.modo, c.objetivo_imagem, s.data_sessao, s.pacote, s.status "
        "FROM sessoes s JOIN clientes c USING (cliente_id) ORDER BY s.sessao_id"
    )

    with st.expander("Reabrir pasta de uma cliente salva no computador"):
        pasta = st.file_uploader("Arquivo da pasta (.zip)", type=["zip"], key="pasta_import")
        if pasta and st.session_state.get("pasta_lida") != pasta.file_id:
            try:
                sid_lido = importar_pasta(pasta)
                if sid_lido in set(sessoes.sessao_id):
                    st.session_state.cliente_sel = sid_lido
                st.session_state.pasta_lida = pasta.file_id
                st.success("Pasta reaberta: pacote, textos, aprovações e fotos restaurados.")
            except Exception as exc:
                st.error(f"Não consegui ler essa pasta ({type(exc).__name__}).")

    secao("Atendimento", "Cliente e pacote contratado")
    rotulo = {r.sessao_id: f"{r.identificador} · {r.data_sessao}" for r in sessoes.itertuples()}
    c1, c2 = st.columns([1, 1])
    sid = c1.selectbox("Cliente em atendimento", list(rotulo), format_func=rotulo.get, key="cliente_sel")
    s = sessoes[sessoes.sessao_id == sid].iloc[0]
    chave_pac = f"pacote_{sid}"
    st.session_state.setdefault(chave_pac, s.pacote if s.pacote in pacotes.PACOTES else "pacote_1")
    pacote = c2.selectbox("Pacote contratado", list(pacotes.PACOTES), format_func=pacotes.nome, key=chave_pac)
    nome_pac, formato, _ = pacotes.PACOTES[pacote]
    PAGINAS = pacotes.paginas(pacote)
    st.markdown(f'<div class="pacote"><b>{pacotes.nome(pacote)}</b><br><small>{formato} · '
                f'{len(PAGINAS)} páginas no dossiê · status: {s.status.replace("_", " ")}<br>'
                f'O dossiê abre somente as páginas do pacote contratado.</small></div>',
                unsafe_allow_html=True)

    def linha(tabela: str):
        df = text_to_sql.run(f"SELECT * EXCLUDE (sessao_id) FROM {tabela} WHERE sessao_id = '{sid}'")
        return df.iloc[0].dropna().to_dict() if len(df) else {}

    dados = {t: linha(t) for t in ("temperamento", "visagismo", "medidas", "teste_coloracao", "coloracao")}
    dados["cliente"] = {"modo": s.modo, "objetivo": s.objetivo_imagem}
    car = dados["coloracao"]

    secao("Ficha", "O que a cliente trouxe e o que você avaliou")
    st.caption("Questionário da cliente + avaliação técnica do consultor. O copiloto cruza tudo na redação.")
    cartela = {}
    if car:
        cartela = {"cartela": f"{car['cartela'].replace('_', ' ').title()} "
                              f"({'confirmada' if car.get('confirmada_pelo_consultor') == 'sim' else 'a confirmar'})"}
    blocos = [("Cliente", dados["cliente"]), ("Temperamento", dados["temperamento"]),
              ("Visagismo", dados["visagismo"]), ("Tipologia", dados["medidas"]),
              ("Coloração", {**dados["teste_coloracao"], **cartela})]
    for col, (titulo, d) in zip(st.columns(5), blocos):
        itens = "".join(f"<p><b>{k.replace('_', ' ')}</b> · {v}</p>" for k, v in d.items())
        col.markdown(f'<div class="card"><h4>{titulo}</h4>{itens or "<p><i>pendente</i></p>"}</div>',
                     unsafe_allow_html=True)

    secao("Dossiê", "Páginas do pacote")
    aprov = st.session_state.setdefault(f"aprovadas_{sid}", set())
    aprov_pac = aprov & set(PAGINAS)
    st.markdown("".join(f'<span class="pill {"ok" if p in aprov else ""}">{"✓ " if p in aprov else ""}{p}</span>'
                        for p in PAGINAS), unsafe_allow_html=True)
    st.progress(len(aprov_pac) / len(PAGINAS), text=f"{len(aprov_pac)} de {len(PAGINAS)} páginas aprovadas")

    pagina = st.radio("Página em edição", list(PAGINAS), horizontal=True, label_visibility="collapsed",
                      key=f"pag_{sid}_{pacote}")
    foco, blocos_pag = PAGINAS[pagina]
    chave = f"texto_{sid}_{pagina}"
    st.session_state.setdefault(chave, "")

    esq, dir_ = st.columns([3, 2], gap="large")
    with esq:
        st.markdown(f"### {pagina}")
        st.caption(f"Foco da página: {foco}.")
        if st.button("Sugerir texto desta página", type="primary"):
            if not rag.api_key():
                st.error("Configure a chave Gemini para gerar rascunhos.")
            else:
                with st.spinner("Escrevendo rascunho fundamentado na metodologia…"):
                    trechos = rag.retrieve(f"{foco} {dados['visagismo'].get('formato_rosto', '')} "
                                           f"{car.get('cartela', '')} {dados['temperamento'].get('primario', '')}")
                    ficha = "\n".join(f"{t}: {dados[t]}" for t in blocos_pag + ["cliente"] if dados.get(t))
                    prompt = (f"Cliente fictícia: {s.identificador} ({s.modo}); objetivo: {s.objetivo_imagem}\n"
                              f"Pacote contratado: {pacotes.nome(pacote)}\n"
                              f"Ficha relevante:\n{ficha}\n\nEscreva a página '{pagina}' do dossiê ({foco}) "
                              f"em 1–3 parágrafos, falando diretamente com a cliente ('você'), tom acolhedor e técnico. "
                              f"Use apenas o que é relevante para esta página; não misture temas de outras páginas."
                              f"\n\nFundamentação:\n{rag._context(trechos)}")
                    st.session_state[chave] = rag.generate(
                        prompt, rag.SYSTEM_PROMPT + "\nNão cite fontes no texto final da cliente.", 0.5)
        st.text_area("Rascunho (edite livremente antes de aprovar)", key=chave, height=280)
        if st.session_state[chave]:
            if pagina in aprov:
                if st.button("Reabrir página"):
                    aprov.discard(pagina); st.rerun()
            elif st.button("Aprovar página"):
                aprov.add(pagina); st.rerun()
            st.caption("Rascunho gerado por IA — revise antes de aprovar.")
    with dir_:
        st.markdown("##### Referências visuais da página")
        st.caption("Bases e fotos preparadas por você. Entram na pasta da cliente quando você salva.")
        fotos = st.session_state.setdefault(f"fotos_{sid}", {})
        imgs = st.file_uploader("Adicionar imagens", type=["png", "jpg", "jpeg"], accept_multiple_files=True,
                                key=f"img_{sid}_{pagina}")
        lista = fotos.setdefault(pagina, [])
        for i in imgs or []:
            if i.name not in [n for n, _ in lista]:
                lista.append((i.name, i.getvalue()))
        if lista:
            st.image([b for _, b in lista], width=140, caption=[n for n, _ in lista])
            if st.button("Remover fotos desta página"):
                fotos[pagina] = []; st.rerun()

    secao("Arquivo", "Guardar o atendimento")
    st.caption("A pasta da cliente fica no seu computador — nada é guardado no app. "
               "Reabra-a depois para revisões ou para o próximo pacote.")
    g1, g2, _ = st.columns([1, 1, 1])
    g1.download_button("Salvar pasta da cliente (.zip)", exportar_pasta(sid, s.identificador, pacote, PAGINAS),
                       file_name=f"pasta_{s.identificador.replace(' ', '_')}_{sid}.zip", type="primary",
                       use_container_width=True)
    if aprov_pac:
        texto = (f"# {perfil['marca']} — Dossiê {s.identificador}\n{pacotes.nome(pacote)}\n\n_{perfil['assinatura']}_\n\n"
                 + "\n\n".join(f"## {p}\n{st.session_state.get(f'texto_{sid}_{p}', '')}"
                               for p in PAGINAS if p in aprov_pac))
        g2.download_button("Baixar páginas aprovadas", texto, file_name=f"dossie_{sid}.md", use_container_width=True)

# ---------- 2. Metodologia (RAG + streaming) ----------
with aba_chat:
    secao("Assistente", "Dúvidas de metodologia durante o atendimento")
    st.caption("Pergunte sobre coloração, visagismo, temperamento, tipologia ou estilo. "
               "As respostas citam o resumo e a seção usados.")
    st.session_state.setdefault("messages", [])
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("fontes"):
                st.caption("Fontes: " + " · ".join(m["fontes"]))

    pergunta = st.chat_input("Ex.: Que corte valoriza rosto quadrado com contraste alto?")
    if pergunta:
        history = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Buscando na metodologia…"):
                    partes, trechos = rag.stream_answer(pergunta, history)
                texto = st.write_stream(partes)
            except Exception as exc:
                texto, trechos = f"Não foi possível gerar a resposta agora ({type(exc).__name__}). Tente novamente.", []
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
    secao("Casos", "Padrões técnicos entre atendimentos")
    st.caption("Compare casos fictícios por critérios técnicos (cartela, contraste, rosto, temperamento, pacote). "
               "O copiloto gera uma consulta somente leitura e mostra o SQL usado.")
    exemplos = ["Quais clientes têm contraste alto e qual o formato de rosto delas?",
                "Que cartelas aparecem junto com temperamento melancólico?",
                "Quais cartelas ainda estão aguardando confirmação do consultor?",
                "Quais clientes contrataram pacotes com coloração e qual a cartela de cada uma?"]
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
