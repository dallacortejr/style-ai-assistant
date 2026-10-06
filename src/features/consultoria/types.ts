export type Fields = Record<string, string | number | null>;
export type Reference = {
  id: string;
  titulo: string;
  tipo: string;
  orientacao: string;
  ocasiao: string;
  cor_modelagem: string;
  link: string;
  quando: string;
};
export type Source = { fonte: string; secao: string };
export type Page = {
  texto: string;
  aprovada: boolean;
  aprovada_em: string | null;
  origem: string;
  fontes: Source[];
  atualizada_em?: string;
};
export type Message = {
  role: "user" | "assistant";
  content: string;
  fontes?: Source[];
  agentes?: string[];
  trace_id?: string;
};
export type Session = {
  referencias?: Reference[];
  id: string;
  identificador: string;
  modo: string;
  pacote: string;
  data: string;
  revision: number;
  questionario: Record<string, string>;
  avaliacao: Record<string, Fields>;
  paginas: Record<string, Page>;
  chat: Message[];
  audit: { evento: string; ator: string; quando: string; revision: number }[];
  fotos: Record<string, { nome: string; data_url: string }[]>;
};
export type Package = { id: string; nome: string; formato: string; paginas: string[] };
export type Answer = {
  texto: string;
  fontes: Source[];
  agentes: string[];
  trace_id: string;
  dados?: { sql: string; linhas: Record<string, unknown>[] };
};
export type Trace = {
  id: string;
  quando: string;
  latencia_ms: number;
  agentes: string[];
  erro: string | null;
  tokens: { input: number | null; output: number | null } | null;
  custo: number | null;
  spans: { nome: string; ms: number }[];
};
