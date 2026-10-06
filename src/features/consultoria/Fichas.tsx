import { useEffect, useState } from "react";
import { Save, Check } from "lucide-react";
import type { Fields, Session } from "./types";
import { label } from "./format";

const questions = [
  ["objetivo", "Objetivo e intenção de imagem"],
  ["duvidas", "Dúvidas e pontos de atenção"],
  ["rotina", "Rotina e ocasiões frequentes"],
  ["estilo_atual", "Estilo atual e peças favoritas"],
  ["cuidados", "Cuidados com cabelo, maquiagem ou barba"],
  ["acessorios", "Óculos e acessórios"],
];
const sections: [string, string, string[]][] = [
  [
    "temperamento",
    "Temperamento",
    [
      "primario",
      "secundario",
      "sanguineo_pct",
      "colerico_pct",
      "melancolico_pct",
      "fleumatico_pct",
    ],
  ],
  [
    "visagismo",
    "Visagismo",
    [
      "formato_rosto",
      "posicao_pele",
      "posicao_cabelo",
      "contraste_graus",
      "contraste_faixa",
      "perfil",
      "terco_superior_cm",
      "terco_medio_cm",
      "terco_inferior_cm",
      "lado_dominante",
      "sobrancelha",
      "cabelo",
      "barba",
    ],
  ],
  [
    "medidas",
    "Tipologia física",
    [
      "altura_cm",
      "peso_kg",
      "ombro_cm",
      "busto_cm",
      "torax_cm",
      "cintura_cm",
      "quadril_cm",
      "tronco_cm",
      "pernas_cm",
      "biotipo_confirmado",
      "pontos_atencao",
    ],
  ],
  [
    "teste_coloracao",
    "Teste de coloração",
    ["temperatura", "intensidade", "profundidade", "vermelhos", "contraste_observado"],
  ],
  ["coloracao", "Avaliação de coloração", ["cartela", "confirmada_pelo_consultor", "metais"]],
  ["estilo", "Estilo", ["detectado", "desejado", "toques"]],
];
export function Fichas({
  session,
  busy,
  onSave,
  onDirty,
}: {
  session: Session;
  busy: boolean;
  onDirty: (dirty: boolean) => void;
  onSave: (q: Record<string, string>, a: Record<string, Fields>) => Promise<boolean>;
}) {
  const [tab, setTab] = useState("questionario"),
    [q, setQ] = useState(session.questionario),
    [a, setA] = useState(session.avaliacao);
  const [saved, setSaved] = useState(false);
  useEffect(() => {
    onDirty(
      JSON.stringify(q) !== JSON.stringify(session.questionario) ||
        JSON.stringify(a) !== JSON.stringify(session.avaliacao),
    );
  }, [q, a, session, onDirty]);
  function update(section: string, field: string, value: string) {
    setSaved(false);
    setA((prev) => ({ ...prev, [section]: { ...prev[section], [field]: value } }));
  }
  return (
    <section className="panel ficha-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Base do atendimento</span>
          <h2>Ouvir, observar e registrar.</h2>
          <p>O relato da cliente e a avaliação profissional têm origens distintas.</p>
        </div>
      </div>
      <div className="subtabs">
        <button
          className={tab === "questionario" ? "active" : ""}
          onClick={() => setTab("questionario")}
        >
          Questionário da cliente
        </button>
        <button className={tab === "avaliacao" ? "active" : ""} onClick={() => setTab("avaliacao")}>
          Avaliação do consultor
        </button>
      </div>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setSaved(await onSave(q, a));
        }}
      >
        {tab === "questionario" ? (
          <div className="form-grid">
            {questions.map(([field, title]) => (
              <label key={field}>
                {title}
                <textarea
                  value={q[field!] || ""}
                  maxLength={2000}
                  onChange={(e) => {
                    setQ({ ...q, [field!]: e.target.value });
                    setSaved(false);
                  }}
                  rows={3}
                  placeholder="Registre o relato com suas próprias palavras…"
                />
              </label>
            ))}
          </div>
        ) : (
          <div className="evaluation-sections">
            {sections.map(([section, title, fields]) => (
              <details open={section === "visagismo"} key={section}>
                <summary>
                  {title}
                  <span>Preenchimento pelo consultor</span>
                </summary>
                <div className="form-grid compact">
                  {fields
                    .filter((f) =>
                      session.modo === "masculino"
                        ? f !== "busto_cm"
                        : !["torax_cm", "barba"].includes(f),
                    )
                    .map((field) => (
                      <label key={field}>
                        {label(field)}
                        <input
                          value={String(a[section]?.[field] ?? "")}
                          maxLength={1000}
                          onChange={(e) => update(section, field, e.target.value)}
                        />
                      </label>
                    ))}
                </div>
              </details>
            ))}
          </div>
        )}
        <div className="form-footer">
          <p>Alterar a ficha devolve as páginas aprovadas para revisão.</p>
          <button className="primary" disabled={busy} type="submit">
            {saved ? <Check size={16} /> : <Save size={16} />}
            {saved ? "Ficha salva" : "Salvar ficha"}
          </button>
        </div>
      </form>
    </section>
  );
}
