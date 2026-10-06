import { useEffect, useState } from "react";
import { BookOpen, Download, Search, Sparkles } from "lucide-react";
import { download, request } from "./api";
import type { Session } from "./types";

type Pattern = {
  id: string;
  titulo: string;
  tema: string;
  texto: string;
  ativa: boolean;
  origem: { pagina: string };
  similaridade?: number;
};
type ModelStatus = {
  trechos_autorizados: number;
  pronto: boolean;
  desatualizado: boolean;
  modelo: null | { versao: string; trechos: number; vocabulario: number; treinado_em: string };
};
type LibraryData = { trechos: Pattern[]; status: ModelStatus };

export function Library({
  session,
  connected,
  busy,
  run,
  onDirty,
}: {
  session: Session;
  connected: boolean;
  busy: boolean;
  run: (action: () => Promise<void>) => Promise<boolean>;
  onDirty: (dirty: boolean) => void;
}) {
  const [data, setData] = useState<LibraryData>();
  const [text, setText] = useState(""),
    [query, setQuery] = useState("");
  const [results, setResults] = useState<Pattern[]>([]);
  const [info, setInfo] = useState("");
  const approved = Object.keys(session.paginas).filter((p) => session.paginas[p]?.aprovada);
  const [page, setPage] = useState(approved[0] || "");
  useEffect(() => {
    onDirty(Boolean(text));
  }, [text, onDirty]);
  useEffect(() => {
    if (connected)
      void request<LibraryData>("/library")
        .then(setData)
        .catch(() => setInfo("Não foi possível carregar a biblioteca."));
  }, [connected]);
  async function refresh() {
    setData(await request<LibraryData>("/library"));
  }
  return (
    <section className="panel editorial-library">
      <span className="eyebrow">MEMÓRIA DO TRABALHO REVISADO</span>
      <h2>Seu método ganha continuidade.</h2>
      <p>
        Transforme trechos de dossiês aprovados em padrões de escrita e análise. Você decide o que
        pode ser reutilizado; cada nova conclusão continua personalizada.
      </p>
      {!connected && (
        <p className="message">
          Conecte o serviço para guardar os padrões e usar a recuperação por ML.
        </p>
      )}
      <div className="message">
        <BookOpen size={18} /> Registre apenas padrões gerais, sem nomes, medidas, fotos, peças ou
        preferências de clientes.
      </div>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget,
            fields = new FormData(form);
          const success = await run(async () => {
            await request(
              `/sessions/${session.id}/pages/${encodeURIComponent(page)}/library`,
              "POST",
              {
                revision: session.revision,
                titulo: fields.get("titulo"),
                tema: fields.get("tema"),
                texto: text,
                confirmo_padrao_sem_dados_pessoais: fields.get("confirmo") === "on",
              },
            );
            await refresh();
          });
          if (success) {
            setText("");
            form.reset();
            setInfo("Padrão autorizado. Atualize o modelo para incluí-lo nas sugestões.");
          }
        }}
      >
        <h3>Autorizar um padrão reutilizável</h3>
        {!approved.length && (
          <p className="muted">
            Este atendimento ainda não tem páginas aprovadas. Finalize e aprove uma página no dossiê
            para começar.
          </p>
        )}
        <div className="form-grid">
          <label>
            Página de origem aprovada
            <select
              value={page}
              onChange={(e) => setPage(e.target.value)}
              required
              disabled={!connected || !approved.length || busy}
            >
              <option value="">Escolha a página</option>
              {approved.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </label>
          <label>
            Assunto do padrão
            <select name="tema">
              <option value="perfil">Perfil e intenção de imagem</option>
              <option value="visagismo">Visagismo</option>
              <option value="coloracao">Coloração</option>
              <option value="proporcoes">Proporções</option>
              <option value="metodologia">Método e estrutura do dossiê</option>
            </select>
          </label>
          <label className="wide">
            Título
            <input
              name="titulo"
              required
              maxLength={160}
              placeholder="Ex.: Como explicar o equilíbrio das linhas do rosto"
            />
          </label>
          <label className="wide">
            Trecho revisado e generalizado
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
              minLength={30}
              maxLength={3000}
              rows={5}
              placeholder="Reescreva aqui somente o padrão que poderá apoiar outros atendimentos."
            />
          </label>
        </div>
        <label className="consent-line">
          <input type="checkbox" name="confirmo" required /> Revisei o conteúdo, retirei os dados
          pessoais e autorizo seu uso como referência geral pelo copiloto.
        </label>
        <button className="primary" disabled={!connected || busy || !approved.length}>
          Autorizar padrão
        </button>
      </form>
      <div className="section-heading library-training">
        <div>
          <h3>Recuperação por aprendizado de máquina</h3>
          <p className="muted">
            {data?.status.trechos_autorizados || 0} padrões autorizados ·{" "}
            {data?.status.pronto
              ? `Modelo ${data.status.modelo?.versao} pronto`
              : data?.status.desatualizado
                ? "Biblioteca alterada: atualize o modelo"
                : "Aguardando treinamento"}
          </p>
        </div>
        <button
          className="soft"
          disabled={!connected || busy || (data?.status.trechos_autorizados || 0) < 2}
          onClick={() =>
            void run(async () => {
              await request("/library/train", "POST");
              await refresh();
              setResults([]);
              setInfo(
                "Modelo atualizado com os padrões autorizados. O copiloto já pode recuperá-los.",
              );
            })
          }
        >
          <Sparkles size={16} /> Atualizar modelo
        </button>
      </div>
      <p className="small muted">
        O modelo aprende a encontrar textos semelhantes. As respostas da IA continuam sujeitas à sua
        revisão. Novos padrões entram no modelo somente quando você o atualiza.
      </p>
      <form
        className="search-line"
        onSubmit={async (e) => {
          e.preventDefault();
          await run(async () => {
            const r = await request<{ trechos: Pattern[] }>(
              `/library/search?q=${encodeURIComponent(query)}`,
            );
            setResults(r.trechos);
            setInfo(
              r.trechos.length
                ? "Referências encontradas; a similaridade indica proximidade textual."
                : "Nenhum padrão relevante encontrado. Confira o treinamento e reformule a busca.",
            );
          });
        }}
      >
        <input
          aria-label="Buscar padrões editoriais"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          minLength={3}
          required
          placeholder="Ex.: explicar linhas e equilíbrio no visagismo"
        />
        <button className="soft" disabled={!connected || busy || !data?.status.pronto}>
          <Search size={16} /> Buscar
        </button>
      </form>
      {info && (
        <p role="status" className="message">
          {info}
        </p>
      )}
      {results.map((r) => (
        <article className="reference-card" key={r.id}>
          <h3>{r.titulo}</h3>
          <p>{r.texto}</p>
          <small>Similaridade textual: {Math.round((r.similaridade || 0) * 100)}%</small>
        </article>
      ))}
      <div className="section-heading">
        <h3>Padrões autorizados</h3>
        <button
          className="soft"
          disabled={!connected || busy}
          onClick={() =>
            void run(async () => {
              const dataset = await request("/library/dataset");
              download(
                new Blob([JSON.stringify(dataset, null, 2)], { type: "application/json" }),
                "dataset-editorial.json",
              );
            })
          }
        >
          <Download size={16} /> Exportar dataset
        </button>
      </div>
      {!data?.trechos.some((r) => r.ativa) && (
        <p className="muted">
          A biblioteca começa vazia. Os padrões vêm do trabalho que você revisa e autoriza.
        </p>
      )}
      {data?.trechos
        .filter((r) => r.ativa)
        .map((r) => (
          <article className="reference-card" key={r.id}>
            <div className="section-heading">
              <h3>{r.titulo}</h3>
              <button
                className="soft"
                disabled={busy}
                onClick={() =>
                  void run(async () => {
                    await request(`/library/${r.id}/revoke`, "POST");
                    await refresh();
                    setResults([]);
                    setInfo(
                      "Padrão retirado. Atualize o modelo para usar o restante da biblioteca.",
                    );
                  })
                }
              >
                Retirar referência
              </button>
            </div>
            <small>
              {r.tema} · Origem: {r.origem.pagina}
            </small>
            <p>{r.texto}</p>
          </article>
        ))}
    </section>
  );
}
