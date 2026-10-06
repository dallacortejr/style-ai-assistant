import { useEffect, useState } from "react";
import { Check, CheckCheck, Download, RotateCcw, Save, Sparkles } from "lucide-react";
import type { Package, Session } from "./types";
import { download } from "./api";

export function Dossie({
  session: s,
  pack,
  busy,
  connected,
  onSave,
  onDirty,
  onDecision,
  onDraft,
  onExport,
  onPhoto,
}: {
  session: Session;
  pack: Package;
  busy: boolean;
  connected: boolean;
  onDirty: (dirty: boolean) => void;
  onSave: (page: string, text: string) => Promise<boolean>;
  onDecision: (page: string, decision: string) => Promise<unknown>;
  onDraft: (page: string) => Promise<unknown>;
  onExport: () => Promise<unknown>;
  onPhoto: (page: string, file: File) => Promise<unknown>;
}) {
  const [page, setPage] = useState(pack.paginas[0]!),
    [edits, setEdits] = useState<Record<string, string>>({});
  const saved = s.paginas[page],
    text = edits[page] ?? saved?.texto ?? "";
  const dirty = text !== (saved?.texto ?? ""),
    approved = Boolean(saved?.aprovada) && !dirty;
  const count = pack.paginas.filter((p) => s.paginas[p]?.aprovada).length;
  useEffect(() => {
    onDirty(Object.entries(edits).some(([p, t]) => t !== (s.paginas[p]?.texto ?? "")));
  }, [edits, s, onDirty]);
  async function save() {
    if (!(await onSave(page, text))) return;
    setEdits((prev) => {
      const next = { ...prev };
      delete next[page];
      return next;
    });
  }
  function exportApproved() {
    const output =
      `# Dossiê — ${s.identificador}\n${pack.nome}\n\n` +
      pack.paginas
        .filter((p) => s.paginas[p]?.aprovada)
        .map((p) => `## ${p}\n${s.paginas[p]!.texto}`)
        .join("\n\n");
    download(new Blob([output], { type: "text/markdown;charset=utf-8" }), `dossie_${s.id}.md`);
  }
  return (
    <section className="dossier-layout">
      <aside className="panel page-list">
        <div className="eyebrow">Seu dossiê</div>
        <h3>Página por página</h3>
        <div className="progress-track">
          <span style={{ width: `${(count / pack.paginas.length) * 100}%` }} />
        </div>
        <p className="muted small">
          {count} de {pack.paginas.length} aprovadas
        </p>
        <nav aria-label="Páginas do dossiê">
          {pack.paginas.map((p, i) => (
            <button className={p === page ? "selected" : ""} key={p} onClick={() => setPage(p)}>
              <span className="page-number">
                {s.paginas[p]?.aprovada ? <Check size={14} /> : String(i + 1).padStart(2, "0")}
              </span>
              <span>{p}</span>
            </button>
          ))}
        </nav>
      </aside>
      <div className="panel page-editor">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              {s.identificador} / {String(pack.paginas.indexOf(page) + 1).padStart(2, "0")}
            </span>
            <h2>{page}</h2>
          </div>
          <span className={`badge ${approved ? "approved" : "review"}`}>
            {approved ? "Aprovada pelo consultor" : "Em elaboração"}
          </span>
        </div>
        <div className="editor-tools">
          <p>Seu olhar conduz. O copiloto ajuda a redigir.</p>
          <button
            className="soft"
            disabled={busy || !connected || dirty}
            onClick={() => onDraft(page)}
            title={
              dirty
                ? "Salve suas alterações antes de solicitar um rascunho."
                : "Cruzar ficha e metodologia para sugerir um texto."
            }
          >
            <Sparkles size={16} />
            Sugerir rascunho
          </button>
        </div>
        <label className="editor-label" htmlFor="dossier-text">
          Texto da página {dirty && <span>· alterações não salvas</span>}
        </label>
        <textarea
          id="dossier-text"
          className="dossier-text"
          value={text}
          maxLength={20000}
          onChange={(e) => setEdits({ ...edits, [page]: e.target.value })}
          placeholder="Comece a escrever ou peça ao copiloto um rascunho fundamentado na ficha e na metodologia.\n\nRevise o texto antes de aprovar esta página."
        />
        {saved?.fontes.length ? (
          <details className="sources">
            <summary>Fundamentação do rascunho · {saved.fontes.length} fontes</summary>
            {saved.fontes.map((f, i) => (
              <p key={i}>
                {f.fonte} › {f.secao}
              </p>
            ))}
          </details>
        ) : null}
        <div className="editor-footer">
          <span className="muted small">
            {text.length.toLocaleString("pt-BR")} caracteres ·{" "}
            {saved?.origem === "copiloto" ? "Rascunho do copiloto" : "Redação do consultor"}
          </span>
          <div className="actions">
            <button disabled={busy || !dirty} onClick={save}>
              <Save size={16} />
              Salvar texto
            </button>
            <button
              className={approved ? "" : "primary"}
              disabled={busy || dirty || !text.trim()}
              onClick={() => onDecision(page, approved ? "reabrir" : "aprovar")}
            >
              {approved ? <RotateCcw size={16} /> : <CheckCheck size={16} />}
              {approved ? "Reabrir página" : "Aprovar página"}
            </button>
          </div>
        </div>
        <section className="visual-references">
          <span className="eyebrow">Referências visuais da página</span>
          <p>Imagens fictícias de apoio, separadas da avaliação técnica.</p>
          <div className="photo-grid">
            {(s.fotos[page] || []).map((photo, i) => (
              <figure key={i}>
                <img src={photo.data_url} alt={photo.nome} />
                <figcaption>{photo.nome}</figcaption>
              </figure>
            ))}
          </div>
          <label className={`button ${!connected || busy ? "disabled" : ""}`}>
            Adicionar imagem
            <input
              type="file"
              accept="image/png,image/jpeg"
              hidden
              disabled={!connected || busy}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void onPhoto(page, file);
                e.target.value = "";
              }}
            />
          </label>
        </section>
        <div className="delivery">
          <div>
            <span className="eyebrow">Entregar com segurança</span>
            <p>Somente as páginas aprovadas entram no dossiê final.</p>
          </div>
          <div className="actions">
            <button disabled={!count || busy} onClick={exportApproved}>
              <Download size={16} />
              Páginas aprovadas
            </button>
            <button disabled={busy || !connected} onClick={onExport}>
              Salvar pasta .zip
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
