import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  BookOpen,
  CheckCheck,
  ChevronRight,
  ClipboardList,
  FileText,
  History,
  LayoutDashboard,
  Plus,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Activity,
} from "lucide-react";
import { api, request, downloadFolder, importFolder } from "./api";
import { Fichas } from "./Fichas";
import { Library } from "./Library";
import { References } from "./References";
import { Dossie } from "./Dossie";
import { Copiloto, HistoryPanel, Methodology, Monitor } from "./Panels";
import { sampleSessions, packages } from "./fixtures";
import type { Fields, Session } from "./types";

const navigation = [
  ["atendimento", "Atendimento", LayoutDashboard],
  ["fichas", "Fichas", ClipboardList],
  ["referencias", "Referências", BookOpen],
  ["dossie", "Dossiê", FileText],
  ["copiloto", "Copiloto", Sparkles],
  ["metodologia", "Metodologia", BookOpen],
  ["historico", "Histórico de casos", History],
  ["monitoramento", "Monitoramento", Activity],
  ["biblioteca", "Biblioteca editorial", BookOpen],
] as const;

export function Workspace() {
  const [sessions, setSessions] = useState<Session[]>(sampleSessions),
    [sid, setSid] = useState(sampleSessions[0]!.id);
  const [view, setView] = useState("atendimento"),
    [connected, setConnected] = useState(false),
    [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [newOpen, setNewOpen] = useState(false);
  const [unsaved, setUnsaved] = useState(false);
  const session = sessions.find((s) => s.id === sid) || sessions[0]!,
    pack = packages.find((p) => p.id === session.pacote)!;
  const count = pack.paginas.filter((p) => session.paginas[p]?.aprovada).length;
  async function reconnect() {
    setLoading(true);
    try {
      const items = await api.sessions();
      setSessions(items);
      setSid(items[0]!.id);
      setConnected(true);
      setError("");
    } catch {
      setConnected(false);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void reconnect();
  }, []);
  function navigate(next: string) {
    if (busy) return;
    if (unsaved) {
      setNotice("Salve as alterações antes de mudar de área ou de atendimento.");
      return;
    }
    setView(next);
    setNotice("");
  }
  useEffect(() => {
    function protect(event: BeforeUnloadEvent) {
      if (unsaved) event.preventDefault();
    }
    window.addEventListener("beforeunload", protect);
    return () => window.removeEventListener("beforeunload", protect);
  }, [unsaved]);
  function replace(s: Session) {
    setSessions((prev) => prev.map((p) => (p.id === s.id ? s : p)));
  }
  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      return true;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível concluir a ação.");
      return false;
    } finally {
      setBusy(false);
    }
  }
  function preview(change: (s: Session) => Session) {
    const next = change(structuredClone(session));
    next.revision++;
    replace(next);
    setNotice("Alteração na prévia. Conecte o serviço para guardar atendimentos.");
  }
  async function saveFicha(q: Record<string, string>, a: Record<string, Fields>) {
    return run(async () => {
      if (connected) replace(await api.ficha(session, q, a));
      else
        preview((s) => ({
          ...s,
          questionario: q,
          avaliacao: a,
          paginas: Object.fromEntries(
            Object.entries(s.paginas).map(([k, p]) => [
              k,
              { ...p, aprovada: false, aprovada_em: null },
            ]),
          ),
        }));
    });
  }
  async function savePage(page: string, text: string) {
    return run(async () => {
      if (connected) replace(await api.save(session, page, text));
      else
        preview((s) => ({
          ...s,
          paginas: {
            ...s.paginas,
            [page]: {
              texto: text,
              aprovada: false,
              aprovada_em: null,
              origem: "consultor",
              fontes: [],
            },
          },
        }));
    });
  }
  async function decision(page: string, action: string) {
    return run(async () => {
      if (connected) replace(await api.decision(session, page, action));
      else
        preview((s) => ({
          ...s,
          paginas: {
            ...s.paginas,
            [page]: {
              ...s.paginas[page]!,
              aprovada: action === "aprovar",
              aprovada_em: action === "aprovar" ? new Date().toISOString() : null,
            },
          },
        }));
    });
  }
  return (
    <div className="atelier-app">
      <aside className="sidebar">
        <a className="brand" href="/">
          <span className="brand-symbol">
            h<span>h</span>
          </span>
          <span>
            HELOISA HERMANN<small>CONSULTORIA DE IMAGEM</small>
          </span>
        </a>
        <div className="workspace-label">ESTÚDIO DO CONSULTOR</div>
        <nav aria-label="Navegação principal">
          {navigation.map(([id, title, Icon]) => (
            <button
              aria-label={title}
              className={view === id ? "active" : ""}
              onClick={() => navigate(id)}
              key={id}
            >
              <Icon size={18} />
              <span>{title}</span>
              {view === id && <ChevronRight className="nav-arrow" size={15} />}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="authority">
            <ShieldCheck size={21} />
            <div>
              <strong>Seu olhar, sua decisão.</strong>
              <p>A IA apoia. Você conduz e aprova cada entrega.</p>
            </div>
          </div>
          <div className="consultant">
            <span className="avatar">C</span>
            <div>
              <strong>Consultor</strong>
              <small>Ambiente acadêmico</small>
            </div>
            <span className="online-dot" />
          </div>
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div className="breadcrumb">
            Estúdio <ChevronRight size={14} />
            <span>{navigation.find((n) => n[0] === view)?.[1]}</span>
          </div>
          <div className="topbar-right">
            <span className="demo-tag">DADOS FICTÍCIOS</span>
            <span className="avatar small-avatar">C</span>
          </div>
        </header>
        <div className="workspace-content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">CONSULTORIA DE IMAGEM & ESTILO</span>
              <h1>
                {view === "atendimento"
                  ? "Cada imagem começa com uma história."
                  : navigation.find((n) => n[0] === view)?.[1]}
              </h1>
              <p>
                {view === "atendimento"
                  ? "Organize o atendimento. Transforme sua análise em um dossiê com propósito."
                  : `${session.identificador} · ${pack.nome}`}
              </p>
            </div>
            <button className="primary" onClick={() => setNewOpen(true)} disabled={busy || unsaved}>
              <Plus size={17} />
              Novo atendimento
            </button>
          </div>
          {!connected && (
            <div className="connection-note" role="status">
              <span>
                {loading
                  ? "Conectando ao serviço…"
                  : "Prévia com exemplos fictícios. IA e gravação de atendimentos precisam do serviço Python conectado."}
              </span>
              <button onClick={reconnect} disabled={loading}>
                Conectar serviço <ArrowUpRight size={14} />
              </button>
            </div>
          )}
          {error && (
            <div className="message error" role="alert">
              {error}
              <button aria-label="Fechar aviso" onClick={() => setError("")}>
                <X size={16} />
              </button>
            </div>
          )}
          {notice && (
            <div className="message notice" role="status">
              {notice}
            </div>
          )}
          {!["monitoramento", "metodologia"].includes(view) && (
            <div className="session-strip">
              <div>
                <span className="eyebrow">EM ATENDIMENTO</span>
                <select
                  aria-label="Cliente em atendimento"
                  value={session.id}
                  onChange={(e) => {
                    if (unsaved) {
                      setNotice("Salve as alterações antes de mudar de atendimento.");
                      return;
                    }
                    setSid(e.target.value);
                    setError("");
                    setNotice("");
                  }}
                  disabled={busy}
                >
                  {sessions.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.identificador} · {s.data}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <span className="eyebrow">PACOTE CONTRATADO</span>
                <strong>{pack.nome.replace(/^Pacote \d+ · /, "")}</strong>
                <small>
                  {pack.formato} · {pack.paginas.length} páginas
                </small>
              </div>
              <span className={`badge ${count === pack.paginas.length ? "approved" : "review"}`}>
                {count === pack.paginas.length ? "Aprovado pelo consultor" : "Em elaboração"}
              </span>
            </div>
          )}
          {view === "atendimento" && (
            <>
              <div className="metric-grid">
                <div>
                  <span>Atendimentos</span>
                  <strong>{sessions.length.toString().padStart(2, "0")}</strong>
                  <small>Organizados em um só lugar</small>
                </div>
                <div>
                  <span>Páginas deste dossiê</span>
                  <strong>{pack.paginas.length.toString().padStart(2, "0")}</strong>
                  <small>Conforme o pacote contratado</small>
                </div>
                <div>
                  <span>Aprovações do consultor</span>
                  <strong>
                    {count.toString().padStart(2, "0")}
                    <em> / {pack.paginas.length}</em>
                  </strong>
                  <small>Prontas para a entrega</small>
                </div>
              </div>
              <div className="overview-grid">
                <section className="panel journey">
                  <span className="eyebrow">O ATENDIMENTO EM TRÊS MOMENTOS</span>
                  <h2>Da escuta à entrega.</h2>
                  {[
                    [
                      "01",
                      "Conhecer a cliente",
                      "Objetivos, rotina e avaliação profissional.",
                      "fichas",
                    ],
                    [
                      "02",
                      "Construir o dossiê",
                      "Redação página por página, com apoio do copiloto.",
                      "dossie",
                    ],
                    [
                      "03",
                      "Revisar e aprovar",
                      "Seu critério profissional orienta a versão final.",
                      "dossie",
                    ],
                  ].map(([num, title, description, id]) => (
                    <button key={num} onClick={() => navigate(id!)}>
                      <span className="step-icon">{num}</span>
                      <span>
                        <small>PASSO {num}</small>
                        <strong>{title}</strong>
                        <p>{description}</p>
                      </span>
                      <ArrowUpRight size={20} />
                    </button>
                  ))}
                </section>
                <section className="panel client-card">
                  <span className="eyebrow">INTENÇÃO DE IMAGEM</span>
                  <span className="client-monogram">
                    {session.identificador.replace("Cliente ", "")}
                  </span>
                  <h2>{session.identificador}</h2>
                  <p className="client-objective">
                    “{session.questionario["objetivo"] || "Registre o objetivo de imagem na ficha."}
                    ”
                  </p>
                  <div className="client-details">
                    <span>
                      Modalidade <strong>{session.modo}</strong>
                    </span>
                    <span>
                      Sessão <strong>{session.data.split("-").reverse().join("/")}</strong>
                    </span>
                  </div>
                  <button onClick={() => navigate("fichas")}>
                    Abrir ficha da cliente <ArrowUpRight size={16} />
                  </button>
                </section>
              </div>
              <section className="panel archive-banner">
                <div>
                  <span className="eyebrow">CONTINUIDADE DO ATENDIMENTO</span>
                  <h3>Reabra uma pasta salva.</h3>
                  <p>Importe a ficha e os textos. As páginas importadas passam por nova revisão.</p>
                </div>
                <label className={`button ${!connected ? "disabled" : ""}`}>
                  <Upload size={16} />
                  Importar pasta .zip
                  <input
                    type="file"
                    accept=".zip"
                    hidden
                    disabled={!connected || busy}
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file)
                        void run(async () => {
                          const s = await importFolder(file);
                          setSessions((prev) => [...prev, s]);
                          setSid(s.id);
                          setNotice("Pasta importada. Revise as páginas antes de aprovar.");
                        });
                      e.target.value = "";
                    }}
                  />
                </label>
              </section>
            </>
          )}
          {view === "biblioteca" && (
            <Library
              key={session.id}
              session={session}
              connected={connected}
              busy={busy}
              run={run}
              onDirty={setUnsaved}
            />
          )}
          {view === "referencias" && (
            <References
              key={session.id}
              session={session}
              busy={busy}
              onDirty={setUnsaved}
              onSave={(body) =>
                run(async () => {
                  if (connected)
                    replace(
                      await request<Session>(`/sessions/${session.id}/references`, "POST", {
                        revision: session.revision,
                        ...body,
                      }),
                    );
                  else
                    preview((s) => ({
                      ...s,
                      referencias: [
                        ...(s.referencias || []),
                        { ...body, id: `REF-${Date.now()}`, quando: new Date().toISOString() },
                      ],
                    }));
                })
              }
            />
          )}
          {view === "fichas" && (
            <Fichas
              key={`${session.id}-${session.revision}`}
              session={session}
              busy={busy}
              onDirty={setUnsaved}
              onSave={saveFicha}
            />
          )}
          {view === "dossie" && (
            <Dossie
              key={session.id}
              session={session}
              pack={pack}
              busy={busy}
              connected={connected}
              onDirty={setUnsaved}
              onSave={savePage}
              onDecision={decision}
              onDraft={(page) => run(async () => replace(await api.draft(session, page)))}
              onExport={() => run(() => downloadFolder(session))}
              onPhoto={(page, file) =>
                run(async () => {
                  if (file.size > 3_000_000) throw new Error("Envie uma imagem com até 3 MB.");
                  const data = await new Promise<string>((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(String(reader.result));
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                  });
                  replace(await api.photo(session, page, file.name, data));
                })
              }
            />
          )}
          {view === "copiloto" && (
            <Copiloto
              key={session.id}
              session={session}
              busy={busy}
              connected={connected}
              onSend={(action) => run(async () => replace(await action()))}
            />
          )}
          {view === "metodologia" && <Methodology />}
          {view === "historico" && <HistoryPanel busy={busy} connected={connected} onRun={run} />}
          {view === "monitoramento" && <Monitor connected={connected} />}
          <footer className="workspace-footer">
            <span>Heloisa Hermann · Copiloto de Consultoria de Imagem</span>
            <span>O consultor dá a palavra final.</span>
          </footer>
        </div>
      </main>
      {newOpen && (
        <div className="modal-backdrop">
          <section
            className="panel modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="new-title"
          >
            <button
              className="modal-close"
              aria-label="Fechar cadastro"
              onClick={() => setNewOpen(false)}
            >
              <X size={20} />
            </button>
            <span className="eyebrow">UM NOVO COMEÇO</span>
            <h2 id="new-title">Novo atendimento</h2>
            <p>Use um identificador fictício neste ambiente acadêmico.</p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const f = new FormData(e.currentTarget);
                void run(async () => {
                  const input = {
                    identificador: String(f.get("identificador")),
                    modo: String(f.get("modo")),
                    pacote: String(f.get("pacote")),
                    objetivo: String(f.get("objetivo")),
                  };
                  const s = connected
                    ? await api.create(input)
                    : {
                        ...structuredClone(sampleSessions[0]!),
                        ...input,
                        id: `PREVIA-${Date.now()}`,
                        data: new Date().toISOString().slice(0, 10),
                        revision: 0,
                        questionario: { objetivo: input.objetivo },
                        avaliacao: {},
                        paginas: {},
                        chat: [],
                        audit: [],
                      };
                  setSessions((prev) => [...prev, s]);
                  setSid(s.id);
                  setNewOpen(false);
                  setView("fichas");
                  if (!connected)
                    setNotice("Atendimento criado na prévia; ele não é guardado após recarregar.");
                });
              }}
            >
              <label>
                Identificador
                <input
                  name="identificador"
                  defaultValue="Cliente I"
                  pattern="Cliente [A-Z][A-Z0-9 -]{0,15}"
                  maxLength={30}
                  required
                />
              </label>
              <label>
                Modalidade
                <select name="modo">
                  <option value="feminino">Feminino</option>
                  <option value="masculino">Masculino</option>
                </select>
              </label>
              <label>
                Pacote
                <select name="pacote">
                  {packages.map((p) => (
                    <option value={p.id} key={p.id}>
                      {p.nome}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Objetivo de imagem
                <textarea name="objetivo" rows={3} maxLength={2000} required />
              </label>
              <button type="submit" className="primary" disabled={busy}>
                Criar atendimento <ArrowUpRight size={16} />
              </button>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}
