import { useState } from "react";
import { ArrowUpRight, Plus, Search } from "lucide-react";
import type { Reference, Session } from "./types";

export function References({
  session,
  busy,
  onSave,
  onDirty,
}: {
  session: Session;
  busy: boolean;
  onDirty: (dirty: boolean) => void;
  onSave: (body: Omit<Reference, "id" | "quando">) => Promise<boolean>;
}) {
  const [search, setSearch] = useState("");
  const [title, setTitle] = useState("");
  const references = (session.referencias || []).filter((r) =>
    `${r.titulo} ${r.tipo} ${r.orientacao} ${r.ocasiao} ${r.cor_modelagem}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );
  return (
    <section className="panel">
      <span className="eyebrow">SELEÇÃO EXCLUSIVA DO ATENDIMENTO</span>
      <h2>Referências de {session.identificador}.</h2>
      <p>
        Você escolhe cada peça, composição ou exemplo e registra como ela se conecta ao objetivo
        desta cliente.
      </p>
      <form
        onChange={() => onDirty(true)}
        className="reference-form"
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const f = new FormData(form);
          const success = await onSave({
            titulo: String(f.get("titulo")),
            tipo: String(f.get("tipo")),
            orientacao: String(f.get("orientacao")),
            ocasiao: String(f.get("ocasiao")),
            cor_modelagem: String(f.get("cor_modelagem")),
            link: String(f.get("link")),
          });
          if (success) {
            setTitle("");
            form.reset();
            onDirty(false);
          }
        }}
      >
        <div className="form-grid">
          <label>
            Peça, composição ou referência
            <input
              name="titulo"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Descreva a referência escolhida por você…"
              maxLength={200}
              required
            />
          </label>
          <label>
            Tipo — preenchido pelo consultor
            <input
              name="tipo"
              placeholder="Organização livre, conforme este atendimento"
              maxLength={100}
            />
          </label>
          <label>
            Ocasião ou contexto
            <input name="ocasiao" maxLength={200} />
          </label>
          <label>
            Cor, modelagem e detalhes
            <input name="cor_modelagem" maxLength={500} />
          </label>
          <label>
            Orientação profissional
            <textarea
              name="orientacao"
              placeholder="Por que esta referência faz sentido para esta cliente?"
              rows={3}
              maxLength={2000}
            />
          </label>
          <label>
            Link da referência
            <input name="link" type="url" placeholder="https://…" maxLength={1000} />
            <small>As imagens podem ser adicionadas na página correspondente do dossiê.</small>
          </label>
        </div>
        <div className="form-footer">
          <p>Adicionar referências devolve as páginas para revisão.</p>
          <button className="primary" disabled={busy || !title.trim()}>
            <Plus size={16} />
            Guardar neste atendimento
          </button>
        </div>
      </form>
      <label className="search-input">
        <Search size={16} />
        <input
          aria-label="Buscar referências desta cliente"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar apenas nas referências desta cliente…"
        />
      </label>
      {!references.length ? (
        <div className="empty-state">
          <h3>Um espaço para suas escolhas.</h3>
          <p>
            As referências começam vazias. O copiloto consulta apenas o material que você registrar
            para esta cliente.
          </p>
        </div>
      ) : (
        <div className="knowledge-grid">
          {references.map((r) => (
            <article className="reference-card" key={r.id}>
              <span className="eyebrow">{r.tipo || "Referência personalizada"}</span>
              <h3>{r.titulo}</h3>
              <p>{r.orientacao}</p>
              <small>{[r.ocasiao, r.cor_modelagem].filter(Boolean).join(" · ")}</small>
              {r.link && (
                <a href={r.link} target="_blank" rel="noopener noreferrer">
                  Abrir referência <ArrowUpRight size={14} />
                </a>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
