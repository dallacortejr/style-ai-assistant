import type { Answer, Session, Trace } from "./types";

// Apenas URL pública. Chaves de LLM nunca entram em variáveis VITE_*.
const base = import.meta.env["VITE_API_URL"] || "http://127.0.0.1:8000";

export async function request<T>(path: string, method = "GET", body?: unknown): Promise<T> {
  const response = await fetch(`${base}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    signal: AbortSignal.timeout(150000),
  });
  if (!response.ok) {
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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pergunta, sessao_id: s.id }),
    signal: AbortSignal.timeout(180000),
  });
  if (!response.ok || !response.body) {
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
  const response = await fetch(`${base}/sessions/${s.id}/export`);
  if (!response.ok) throw new Error("Não foi possível exportar o atendimento.");
  download(await response.blob(), `pasta_${s.id}.zip`);
}

export async function importFolder(file: File): Promise<Session> {
  const response = await fetch(`${base}/import`, {
    method: "POST",
    headers: { "Content-Type": "application/zip" },
    body: file,
  });
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
