"""Copiloto de Consultoria de Imagem — Etapa 1 (Streamlit).

Executar: streamlit run academic/app.py
"""

import os
import sys
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

st.markdown("""
<style>
:root { --grafite:#2F2F33; --dourado:#B08D57; --claro:#EDEDEF; }
h1, h2, h3 { font-family: Georgia, serif; color: var(--grafite); }
.stApp { background: #F7F6F4; }
.badge { display:inline-block; padding:2px 10px; border-radius:12px;
  background:var(--dourado); color:white; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🪞 Copiloto")
    st.caption("Apoio ao consultor(a) de imagem e estilo. As sugestões são rascunhos — a decisão final é sempre do consultor(a).")
    st.markdown('<span class="badge">Dados 100% fictícios</span>', unsafe_allow_html=True)
    if not rag.api_key():
        st.warning("Chave Gemini não configurada: o chat mostrará só os trechos encontrados.")
    if st.button("Nova conversa"):
        st.session_state.messages = []

st.title("Copiloto de Consultoria de Imagem")
aba_chat, aba_banco, aba_ficha = st.tabs(["💬 Consultar a base", "📊 Perguntar aos atendimentos", "📝 Ficha da sessão"])

# ---------- 1. Chat com RAG e streaming ----------
with aba_chat:
    st.caption("Pergunte sobre coloração, visagismo, temperamento, tipologia, estilo ou atendimento. As respostas citam o resumo e a seção usados.")
    st.session_state.setdefault("messages", [])
    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🧵" if m["role"] == "assistant" else None):
            st.markdown(m["content"])
            if m.get("fontes"):
                st.caption("Fontes: " + " · ".join(m["fontes"]))

    pergunta = st.chat_input("Ex.: Como avaliar o contraste pessoal da cliente?")
    if pergunta:
        history = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)
        with st.chat_message("assistant", avatar="🧵"):
            try:
                with st.spinner("Buscando nos resumos…"):
                    partes, trechos = rag.stream_answer(pergunta, history)
                texto = st.write_stream(partes)
            except Exception as exc:  # erro do provedor: mostra mensagem, sem repetir
                texto, trechos = f"Não foi possível gerar a resposta agora ({type(exc).__name__}). Tente novamente em instantes.", []
                st.error(texto)
            fontes = list(dict.fromkeys(f"{t['fonte']} › {t['secao']}" for t in trechos))
            if fontes:
                st.caption("Fontes: " + " · ".join(fontes))
                with st.expander("Ver trechos recuperados"):
                    for t in trechos:
                        st.markdown(f"**{t['fonte']} › {t['secao']}**\n\n{t['texto']}")
        st.session_state.messages.append({"role": "assistant", "content": texto, "fontes": fontes})

# ---------- 2. Text-to-SQL no DuckDB ----------
with aba_banco:
    st.caption("Pergunte em linguagem natural sobre os atendimentos fictícios. O copiloto gera uma consulta somente leitura e mostra o SQL usado.")
    exemplos = ["Quantos atendimentos têm cartela inverno frio confirmada?",
                "Quais clientes têm contraste alto e qual o formato de rosto?",
                "Liste as sessões em revisão com a cartela proposta."]
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

# ---------- 3. Ficha da sessão + sugerir com IA ----------
with aba_ficha:
    text_to_sql.ensure_db()
    sessoes = text_to_sql.run(
        "SELECT s.sessao_id, c.identificador, c.modo, c.objetivo_imagem, s.data_sessao, s.status "
        "FROM sessoes s JOIN clientes c USING (cliente_id) ORDER BY s.sessao_id"
    )
    rotulo = {r.sessao_id: f"{r.identificador} · {r.data_sessao} · {r.status}" for r in sessoes.itertuples()}
    sid = st.selectbox("Atendimento", list(rotulo), format_func=rotulo.get)
    s = sessoes[sessoes.sessao_id == sid].iloc[0]
    st.markdown(f"**{s.identificador}** ({s.modo}) — objetivo de imagem: *{s.objetivo_imagem}*")

    def linha(tabela: str):
        df = text_to_sql.run(f"SELECT * EXCLUDE (sessao_id) FROM {tabela} WHERE sessao_id = '{sid}'")
        return df.iloc[0].dropna().to_dict() if len(df) else {}

    dados = {t: linha(t) for t in ("temperamento", "visagismo", "medidas", "teste_coloracao", "coloracao")}
    cols = st.columns(4)
    for col, (titulo, tabela) in zip(cols, [("Temperamento", "temperamento"), ("Visagismo", "visagismo"),
                                            ("Tipologia", "medidas"), ("Coloração", "teste_coloracao")]):
        with col:
            st.subheader(titulo)
            for k, v in dados[tabela].items():
                st.markdown(f"- **{k.replace('_', ' ')}:** {v}")
    car = dados["coloracao"]
    if car:
        st.markdown(f"**Cartela:** {car['cartela'].replace('_', ' ').title()} — "
                    f"{'confirmada pelo consultor(a)' if car['confirmada_pelo_consultor'] == 'sim' else 'proposta, aguardando confirmação'}")

    st.divider()
    st.subheader("Texto personalizado (tipo C)")
    secoes = {
        "Corte de cabelo e franja": "corte de cabelo e franja indicados pelo formato de rosto e contraste",
        "Pontos de atenção da silhueta": "pontos de atenção da tipologia física e como valorizá-los",
        "Leitura do temperamento": "como o temperamento primário e secundário aparece na imagem",
        "Uso da cartela no dia a dia": "como usar a cartela de cores no dia a dia, metais e contraste",
    }
    secao = st.selectbox("Seção do dossiê", list(secoes))
    chave = f"texto_{sid}_{secao}"
    st.session_state.setdefault(chave, "")
    if st.button("✨ Sugerir com IA"):
        if not rag.api_key():
            st.error("Configure a chave Gemini para gerar rascunhos.")
        else:
            with st.spinner("Escrevendo rascunho fundamentado…"):
                trechos = rag.retrieve(f"{secoes[secao]} {dados['visagismo'].get('formato_rosto', '')} "
                                       f"{car.get('cartela', '')} {dados['temperamento'].get('primario', '')}")
                ficha = "\n".join(f"{t}: {d}" for t, d in dados.items())
                prompt = (f"Cliente fictícia: {s.identificador} ({s.modo}); objetivo: {s.objetivo_imagem}\n"
                          f"Ficha:\n{ficha}\n\nEscreva a seção '{secao}' do dossiê em 1–2 parágrafos, "
                          f"falando diretamente com a cliente ('você'), tom acolhedor e técnico.\n\n"
                          f"Fundamentação:\n{rag._context(trechos)}")
                st.session_state[chave] = rag.generate(prompt, rag.SYSTEM_PROMPT + "\nNão cite fontes no texto final da cliente.", 0.5)
    st.text_area("Rascunho (edite livremente antes de aprovar)", key=chave, height=220)
    if st.session_state[chave]:
        st.caption("⚠️ Rascunho gerado por IA. Revise e aprove antes de incluir no dossiê.")
        st.download_button("Baixar texto", st.session_state[chave], file_name=f"{sid}_{secao}.txt")
