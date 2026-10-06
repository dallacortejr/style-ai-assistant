import { useRef, useState } from "react";
import { ImagePlus, UserRound, X } from "lucide-react";

export function IdentityUploads({
  photo,
  logo,
  onPhoto,
  onLogo,
  onPending,
  disabled,
}: {
  photo: string | null;
  logo: string | null;
  onPhoto: (value: string | null) => void;
  onLogo: (value: string | null) => void;
  onPending: (pending: boolean) => void;
  disabled: boolean;
}) {
  const [error, setError] = useState("");
  const pending = useRef(0);
  return (
    <fieldset className="identity-uploads" disabled={disabled}>
      <legend>
        Sua identidade visual <span>(opcional)</span>
      </legend>
      <p>Adicione sua foto e, se tiver, a logo do seu estúdio. Você pode alterá-las depois.</p>
      <div className="identity-upload-grid">
        {(
          [
            ["photo", "Foto do consultor", photo, onPhoto],
            ["logo", "Logo do estúdio", logo, onLogo],
          ] as const
        ).map(([kind, label, value, onChange]) => (
          <div className="identity-upload" key={kind}>
            <div className={`identity-preview ${kind}`}>
              {value ? (
                <img
                  src={value}
                  alt={
                    kind === "photo" ? "Prévia da foto do consultor" : "Prévia da logo do estúdio"
                  }
                />
              ) : kind === "photo" ? (
                <UserRound size={28} />
              ) : (
                <ImagePlus size={28} />
              )}
            </div>
            <label className="identity-file-label">
              {label}
              <span className="identity-file-action" aria-hidden="true">
                {value ? "Trocar imagem" : "Escolher imagem"}
              </span>
              <input
                type="file"
                className="identity-file-input"
                aria-label={label}
                accept="image/png,image/jpeg"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  e.target.value = "";
                  if (!file) return;
                  setError("");
                  pending.current++;
                  onPending(true);
                  try {
                    if (!["image/png", "image/jpeg"].includes(file.type))
                      throw new Error("Envie uma imagem PNG ou JPEG.");
                    if (file.size > 3_000_000) throw new Error("Cada imagem pode ter até 3 MB.");
                    const result = await new Promise<string>((resolve, reject) => {
                      const reader = new FileReader();
                      reader.onload = () => resolve(String(reader.result));
                      reader.onerror = () => reject(new Error("Não foi possível ler a imagem."));
                      reader.readAsDataURL(file);
                    });
                    onChange(result);
                  } catch (err) {
                    setError(
                      err instanceof Error ? err.message : "Não foi possível carregar a imagem.",
                    );
                  } finally {
                    pending.current--;
                    onPending(pending.current > 0);
                  }
                }}
              />
            </label>
            {value && (
              <button type="button" className="identity-remove" onClick={() => onChange(null)}>
                <X size={13} />
                Remover {kind === "photo" ? "foto" : "logo"}
              </button>
            )}
          </div>
        ))}
      </div>
      <small>PNG ou JPEG · até 3 MB por imagem. A logo mantém a transparência.</small>
      {error && (
        <p className="message error" role="alert">
          {error}
        </p>
      )}
    </fieldset>
  );
}
