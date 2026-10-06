import { useEffect, useState } from "react";
import { ArrowRight, ShieldCheck, UserRound, LogOut } from "lucide-react";
import { request, setCsrf } from "./api";
import { Workspace } from "./Workspace";
import { IdentityUploads } from "./IdentityUploads";

export type Consultant = {
  id: string;
  name: string;
  email: string;
  created: string;
  photo: string | null;
  logo: string | null;
  subscription: {
    status: string;
    cycle: string;
    provider: string | null;
    checkout_available: boolean;
    price: number | null;
  };
};
type AccessResponse = { consultant: Consultant; csrf: string };

export function Access() {
  const [consultant, setConsultant] = useState<Consultant | null>(null);
  const [checking, setChecking] = useState(true),
    [register, setRegister] = useState(false);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const [photo, setPhoto] = useState<string | null>(null),
    [logo, setLogo] = useState<string | null>(null),
    [uploading, setUploading] = useState(false);
  function accept(data: AccessResponse) {
    setPhoto(null);
    setLogo(null);
    setCsrf(data.csrf);
    setConsultant(data.consultant);
    setError("");
  }
  useEffect(() => {
    request<AccessResponse>("/auth/me")
      .then(accept)
      .catch(() => {})
      .finally(() => setChecking(false));
    function expired() {
      setConsultant(null);
      setCsrf("");
    }
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, []);
  async function logout() {
    await request("/auth/logout", "POST");
    setConsultant(null);
    setCsrf("");
    setPhoto(null);
    setLogo(null);
  }
  if (consultant)
    return (
      <Workspace
        key={consultant.id}
        consultant={consultant}
        onProfile={setConsultant}
        onLogout={logout}
      />
    );
  return (
    <div className="atelier-app access-page">
      <section className="access-story">
        <a className="access-logo" href="/">
          ESTÚDIO<span>CONSULTORIA DE IMAGEM</span>
        </a>
        <div>
          <span className="eyebrow">SEU ESPAÇO PROFISSIONAL</span>
          <h1>
            Seu método.
            <br />
            Seu olhar.
            <br />
            <em>Seu estúdio.</em>
          </h1>
          <p>
            Uma conta para organizar suas consultorias, construir dossiês e contar com um copiloto
            que respeita sua decisão.
          </p>
        </div>
        <p className="access-promise">
          <ShieldCheck size={22} /> Cada consultor tem seu próprio espaço de trabalho.
        </p>
      </section>
      <section className="access-form-area">
        <div className="access-card">
          <span className="eyebrow">BEM-VINDO AO SEU ESTÚDIO</span>
          <h2>{register ? "Comece pela sua conta." : "Vamos continuar?"}</h2>
          <p>
            {register
              ? "Cadastre seu nome profissional e suas credenciais de acesso."
              : "Entre para acessar seus atendimentos e sua biblioteca."}
          </p>
          <div className="access-tabs">
            <button
              type="button"
              disabled={busy || uploading}
              className={!register ? "selected" : ""}
              onClick={() => {
                setRegister(false);
                setError("");
              }}
            >
              Entrar
            </button>
            <button
              type="button"
              disabled={busy || uploading}
              className={register ? "selected" : ""}
              onClick={() => {
                setRegister(true);
                setError("");
              }}
            >
              Criar conta
            </button>
          </div>
          {checking ? (
            <p role="status">Verificando seu acesso…</p>
          ) : (
            <form
              key={String(register)}
              onSubmit={async (e) => {
                e.preventDefault();
                const fields = new FormData(e.currentTarget);
                setBusy(true);
                setError("");
                try {
                  accept(
                    await request<AccessResponse>(
                      register ? "/auth/register" : "/auth/login",
                      "POST",
                      {
                        ...(register ? { name: fields.get("name"), photo, logo } : {}),
                        email: fields.get("email"),
                        password: fields.get("password"),
                      },
                    ),
                  );
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Não foi possível acessar.");
                } finally {
                  setBusy(false);
                }
              }}
            >
              {register && (
                <label>
                  Nome profissional
                  <input
                    name="name"
                    autoComplete="name"
                    minLength={2}
                    maxLength={100}
                    required
                    placeholder="Como você quer aparecer no estúdio"
                  />
                </label>
              )}
              <label>
                E-mail
                <input
                  name="email"
                  type="email"
                  autoComplete="email"
                  maxLength={254}
                  required
                  placeholder="seu@email.com"
                />
              </label>
              <label>
                Senha
                <input
                  name="password"
                  type="password"
                  autoComplete={register ? "new-password" : "current-password"}
                  minLength={12}
                  maxLength={128}
                  required
                  placeholder={register ? "Pelo menos 12 caracteres" : "Sua senha"}
                />
              </label>
              {register && <small>Use uma senha exclusiva com pelo menos 12 caracteres.</small>}
              {register && (
                <IdentityUploads
                  photo={photo}
                  logo={logo}
                  onPhoto={setPhoto}
                  onLogo={setLogo}
                  onPending={setUploading}
                  disabled={busy || uploading}
                />
              )}
              {error && (
                <p className="message error" role="alert">
                  {error}
                </p>
              )}
              <button className="primary" disabled={busy || uploading} type="submit">
                {busy ? "Aguarde…" : register ? "Criar meu estúdio" : "Entrar no estúdio"}
                <ArrowRight size={17} />
              </button>
            </form>
          )}
          <div className="access-plan">
            <span className="eyebrow">ASSINATURA MENSAL</span>
            <strong>Piloto sem cobrança</strong>
            <p>
              O valor e o provedor de pagamento serão definidos antes da ativação comercial. Criar
              uma conta nesta versão não gera cobrança.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export function Account({
  consultant,
  onProfile,
  onLogout,
  onDirty,
}: {
  consultant: Consultant;
  onProfile: (c: Consultant) => void;
  onLogout: () => Promise<void>;
  onDirty: (dirty: boolean) => void;
}) {
  const [name, setName] = useState(consultant.name),
    [busy, setBusy] = useState(false),
    [message, setMessage] = useState("");
  const [photo, setPhoto] = useState(consultant.photo),
    [logo, setLogo] = useState(consultant.logo),
    [uploading, setUploading] = useState(false);
  const dirty = name !== consultant.name || photo !== consultant.photo || logo !== consultant.logo;
  useEffect(() => {
    onDirty(dirty || uploading);
    return () => onDirty(false);
  }, [dirty, uploading, onDirty]);
  return (
    <section className="panel account-panel">
      <span className="eyebrow">IDENTIDADE DO CONSULTOR</span>
      <h2>Seu perfil profissional.</h2>
      <p>
        Seu nome acompanha seu espaço de trabalho. Seus atendimentos e sua biblioteca editorial
        pertencem à sua conta.
      </p>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setBusy(true);
          setMessage("");
          try {
            const c = await request<Consultant>("/auth/profile", "PUT", { name, photo, logo });
            setName(c.name);
            setPhoto(c.photo);
            setLogo(c.logo);
            onProfile(c);
            setMessage("Perfil atualizado.");
          } catch (err) {
            setMessage(err instanceof Error ? err.message : "Não foi possível salvar.");
          } finally {
            setBusy(false);
          }
        }}
      >
        <label>
          Nome profissional
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            minLength={2}
            maxLength={100}
            required
            autoComplete="name"
          />
        </label>
        <label>
          E-mail de acesso
          <input value={consultant.email} readOnly />
        </label>
        <IdentityUploads
          photo={photo}
          logo={logo}
          onPhoto={setPhoto}
          onLogo={setLogo}
          onPending={setUploading}
          disabled={busy || uploading}
        />
        <button className="primary" disabled={busy || uploading || !dirty}>
          <UserRound size={17} />
          Salvar perfil
        </button>
      </form>
      {message && <p role="status">{message}</p>}
      <div className="access-plan">
        <span className="eyebrow">PLANO MENSAL</span>
        <h3>Piloto sem cobrança</h3>
        <p>
          A contratação mensal está em preparação. Valor, checkout e cobrança recorrente serão
          integrados após a escolha do provedor.
        </p>
        <span className="badge review">Pagamento ainda não configurado</span>
      </div>
      <button
        className="button"
        disabled={busy || dirty || uploading}
        onClick={async () => {
          setBusy(true);
          try {
            await onLogout();
          } catch (err) {
            setMessage(err instanceof Error ? err.message : "Não foi possível sair.");
            setBusy(false);
          }
        }}
      >
        <LogOut size={16} />
        Sair da conta
      </button>
    </section>
  );
}
