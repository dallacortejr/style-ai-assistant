import type { Answer, Session, Trace } from "./types";

// Apenas URL pública. Chaves de LLM nunca entram em variáveis VITE_*.
const base =
  import.meta.env["VITE_API_URL"] ||
  (typeof window === "undefined"
    ? "http://127.0.0.1:8000"
    : `${window.location.protocol}//${window.location.hostname}:8000`);

let csrf: string = import.meta.hot?.data["csrf"] || "";
// Preserva somente memória durante atualizações do servidor de desenvolvimento.
if (import.meta.hot)
  import.meta.hot.dispose((data) => {
    data.csrf = csrf;
  });
export function setCsrf(value: string) {
  csrf = value;
}
function expired(response: Response) {
  if (response.status === 401) window.dispatchEvent(new Event("session-expired"));
}

export async function request<T>(path: string, method = "GET", body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      method,
      credentials: "include",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
      signal: AbortSignal.timeout(path.startsWith("/auth/") ? 15000 : 150000),
    });
  } catch {
    throw new Error(
      "Não foi possível conectar ao serviço. Confira se a API está em execução e tente novamente.",
    );
  }
  if (!response.ok) {
    if (!["/auth/login", "/auth/register"].includes(path)) expired(response);
    const error = await response.json().catch(() => ({ detail: "O servidor não respondeu." }));
    throw new Error(
      typeof error.detail === "string" ? error.detail : "Confira os campos preenchidos.",
    );
  }
  return response.json() as Promise<T>;
}

export const api = {
  sessions: () => request<Session[]>("/sessions"),
  create: (body: unknown) => request<Session>("/sessions", "POST", body),
  ficha: (s: Session, questionario: Session["questionario"], avaliacao: Session["avaliacao"]) =>
    request<Session>(`/sessions/${s.id}/ficha`, "PUT", {
      revision: s.revision,
      questionario,
      avaliacao,
    }),
  save: (s: Session, page: string, texto: string) =>
    request<Session>(`/sessions/${s.id}/pages/${encodeURIComponent(page)}`, "PUT", {
      revision: s.revision,
      texto,
    }),
  decision: (s: Session, page: string, decisao: string) =>
    request<Session>(`/sessions/${s.id}/pages/${encodeURIComponent(page)}/decision`, "POST", {
      revision: s.revision,
      decisao,
    }),
  draft: (s: Session, page: string) =>
    request<Session>(`/sessions/${s.id}/pages/${encodeURIComponent(page)}/draft`, "POST"),
  photo: (s: Session, page: string, nome: string, data_url: string) =>
    request<Session>(`/sessions/${s.id}/pages/${encodeURIComponent(page)}/photos`, "POST", {
      revision: s.revision,
      nome,
      data_url,
    }),
  history: (pergunta: string) => request<Answer>("/history", "POST", { pergunta }),
  traces: () => request<Trace[]>("/traces"),
};

export async function chat(
  s: Session,
  pergunta: string,
  onDelta: (text: string) => void,
): Promise<Session> {
  const response = await fetch(`${base}/chat`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
    body: JSON.stringify({ pergunta, sessao_id: s.id }),
    signal: AbortSignal.timeout(180000),
  });
  if (!response.ok || !response.body) {
    expired(response);
    const error = await response.json().catch(() => ({ detail: "O chat está indisponível." }));
    throw new Error(typeof error.detail === "string" ? error.detail : "Pedido inválido.");
  }
  const reader = response.body.getReader(),
    decoder = new TextDecoder();
  let buffer = "",
    result: Session | undefined;
  function consume(line: string) {
    if (!line.trim()) return;
    const event = JSON.parse(line) as {
      tipo: string;
      texto?: string;
      mensagem?: string;
      session?: Session;
    };
    if (event.tipo === "delta" && event.texto) onDelta(event.texto);
    if (event.tipo === "erro") throw new Error(event.mensagem || "Falha na resposta.");
    if (event.tipo === "final") result = event.session;
  }
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";
      lines.forEach(consume);
      if (done) {
        consume(buffer);
        break;
      }
    }
  } finally {
    await reader.cancel();
  }
  if (!result) throw new Error("A resposta não foi concluída. Tente novamente.");
  return result;
}

export async function downloadFolder(s: Session) {
  const response = await fetch(`${base}/sessions/${s.id}/export`, { credentials: "include" });
  if (!response.ok) {
    expired(response);
    throw new Error("Não foi possível exportar o atendimento.");
  }
  download(await response.blob(), `pasta_${s.id}.zip`);
}

export async function importFolder(file: File): Promise<Session> {
  const response = await fetch(`${base}/import`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/zip", "X-CSRF-Token": csrf },
    body: file,
  });
  expired(response);
  const data = await response.json();
  if (!response.ok)
    throw new Error(typeof data.detail === "string" ? data.detail : "Pasta inválida.");
  return data as Session;
}

export function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob),
    anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = name;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
