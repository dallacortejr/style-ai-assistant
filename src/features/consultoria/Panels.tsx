import { useEffect, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { api, chat } from "./api";
import { label } from "./format";
import { knowledge } from "./fixtures";
import type { Session, Trace } from "./types";

export function Copiloto({
  session,
  busy,
  connected,
  onSend,
}: {
  session: Session;
  busy: boolean;
  connected: boolean;
  onSend: (a: () => Promise<Session>) => Promise<boolean>;
}) {
  const [question, setQuestion] = useState(""),
    [stream, setStream] = useState("");
  return (
    <section className="panel chat-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">APOIO À SUA ANÁLISE</span>
          <h2>Pense junto com o copiloto.</h2>
          <p>Ficha, metodologia e dados se encontram aqui. As decisões continuam com você.</p>
        </div>
        <span className="badge">
          <ShieldCheck size={14} />
          Revisão humana
        </span>
      </div>
      <div className="chat-messages" aria-live="polite">
        {!session.chat.length && !busy ? (
          <div className="chat-empty">
            <span>
              <Sparkles size={26} />
            </span>
            <h3>Um apoio para transformar conhecimento em texto.</h3>
            <p>
              Peça uma síntese da ficha, consulte a metodologia ou investigue padrões nos casos
              fictícios.
            </p>
            <div className="prompt-examples">
              {[
                "Como explicar o contraste pessoal no dossiê?",
                "Resuma os objetivos desta cliente.",
                "Quantas clientes há por modalidade na base fictícia?",
              ].map((q) => (
                <button key={q} disabled={!connected} onClick={() => setQuestion(q)}>
                  {q}
                  <ArrowUpRight size={14} />
                </button>
              ))}
            </div>
          </div>
        ) : (
          session.chat.map((m, i) => (
            <article className={`chat-message ${m.role}`} key={i}>
              <span className="eyebrow">
                {m.role === "user" ? "CONSULTOR" : "COPILOTO · SUGESTÃO PARA REVISÃO"}
              </span>
              <p>{m.content}</p>
              {m.fontes?.length ? (
                <details className="sources">
                  <summary>Fontes consultadas</summary>
                  {m.fontes.map((f, j) => (
                    <small key={j}>
                      {f.fonte} › {f.secao}
                      <br />
                    </small>
                  ))}
                </details>
              ) : null}
              {m.agentes && <small className="muted">{m.agentes.join(" + ")}</small>}
            </article>
          ))
        )}
        {busy && (
          <article className="chat-message assistant">
            <span className="eyebrow">COPILOTO · ELABORANDO</span>
            <p>{stream || "Consultando as informações…"}</p>
          </article>
        )}
      </div>
      <form
        className="chat-composer"
        onSubmit={async (e) => {
          e.preventDefault();
          if (!question.trim()) return;
          const q = question;
          setStream("");
          const success = await onSend(() =>
            chat(session, q, (delta) => setStream((prev) => prev + delta)),
          );
          if (success) setQuestion("");
          setStream("");
        }}
      >
        <input
          aria-label="Mensagem para o copiloto"
          value={question}
          maxLength={2000}
          disabled={!connected || busy}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={
            connected
              ? "Como posso ajudar neste atendimento?"
              : "Conecte o serviço Python para conversar com a IA."
          }
        />
        <button
          className="primary"
          aria-label="Enviar mensagem"
          disabled={!connected || busy || question.trim().length < 3}
        >
          <ArrowUpRight size={19} />
        </button>
      </form>
      <p className="small muted">
        O copiloto não aprova páginas nem altera avaliações profissionais.
      </p>
    </section>
  );
}

export function Methodology() {
  const [search, setSearch] = useState("");
  return (
    <section className="panel knowledge-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">BASE DE CONHECIMENTO</span>
          <h2>Fundamentação para o seu olhar.</h2>
          <p>Resumos próprios aprovados. As fontes acompanham os rascunhos do copiloto.</p>
        </div>
        <BookOpen size={28} />
      </div>
      <label className="search-input">
        <Search size={18} />
        <input
          aria-label="Buscar na metodologia"
          placeholder="Buscar tema, conceito ou referência…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </label>
      <div className="knowledge-grid">
        {knowledge
          .filter((doc) =>
            `${doc.titulo} ${doc.conteudo}`.toLowerCase().includes(search.toLowerCase()),
          )
          .map((doc, i) => (
            <details key={doc.arquivo}>
              <summary>
                <span className="knowledge-number">{String(i + 1).padStart(2, "0")}</span>
                <strong>{doc.titulo}</strong>
                <Plus size={16} />
              </summary>
              <div className="knowledge-text">{doc.conteudo}</div>
              <small>{doc.arquivo}</small>
            </details>
          ))}
      </div>
    </section>
  );
}

export function HistoryPanel({
  busy,
  connected,
  onRun,
}: {
  busy: boolean;
  connected: boolean;
  onRun: (a: () => Promise<void>) => Promise<boolean>;
}) {
  const [question, setQuestion] = useState(""),
    [answer, setAnswer] = useState<Awaited<ReturnType<typeof api.history>>>();
  return (
    <section className="panel">
      <span className="eyebrow">DADOS PARA APOIAR SUA LEITURA</span>
      <h2>Investigue padrões entre os casos.</h2>
      <p>Consultas somente de leitura sobre os oito exemplos fictícios da etapa 1.</p>
      <form
        className="history-form"
        onSubmit={(e) => {
          e.preventDefault();
          void onRun(async () => setAnswer(await api.history(question)));
        }}
      >
        <input
          aria-label="Pergunta sobre os casos"
          value={question}
          maxLength={2000}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ex.: Quantas sessões foram contratadas por pacote?"
        />
        <button className="primary" disabled={!connected || busy || question.length < 3}>
          Consultar
        </button>
      </form>
      {answer && (
        <div className="history-answer">
          <p>{answer.texto}</p>
          {answer.dados?.linhas.length ? (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    {Object.keys(answer.dados.linhas[0]!).map((k) => (
                      <th key={k}>{label(k)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {answer.dados.linhas.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((v, j) => (
                        <td key={j}>{String(v ?? "—")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
          <details className="sources">
            <summary>Detalhes técnicos da consulta</summary>
            <pre>{answer.dados?.sql}</pre>
          </details>
        </div>
      )}
    </section>
  );
}

export function Monitor({ connected }: { connected: boolean }) {
  const [traces, setTraces] = useState<Trace[]>([]),
    [error, setError] = useState("");
  useEffect(() => {
    if (connected)
      api
        .traces()
        .then(setTraces)
        .catch(() => setError("Não foi possível carregar os registros."));
  }, [connected]);
  return (
    <section className="panel">
      <span className="eyebrow">RASTREABILIDADE DO COPILOTO</span>
      <h2>Entenda cada execução.</h2>
      <p>
        Latência, agentes e etapas do fluxo. Os registros não contêm fichas, perguntas ou imagens.
      </p>
      {error && <p role="alert">{error}</p>}
      {!traces.length ? (
        <div className="empty-state">
          <Activity size={30} />
          <h3>Nenhuma execução registrada.</h3>
          <p>
            As consultas ao copiloto conectado aparecem aqui. Tokens e custo indisponíveis são
            exibidos como não informados.
          </p>
        </div>
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Execução</th>
                <th>Etapas</th>
                <th>Latência</th>
                <th>Tokens</th>
                <th>Resultado</th>
              </tr>
            </thead>
            <tbody>
              {traces.map((t) => (
                <tr key={t.id}>
                  <td>
                    {t.id.slice(0, 8)}
                    <small>{new Date(t.quando).toLocaleString("pt-BR")}</small>
                  </td>
                  <td>{t.spans.map((s) => s.nome.replaceAll("_", " ")).join(" → ")}</td>
                  <td>{t.latencia_ms} ms</td>
                  <td>
                    {t.tokens
                      ? `${t.tokens.input ?? "—"} / ${t.tokens.output ?? "—"}`
                      : "Não informado"}
                  </td>
                  <td>{t.erro || "Concluída"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
