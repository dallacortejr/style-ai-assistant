import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Copiloto de Consultoria de Imagem" },
      { name: "description", content: "Apoio à montagem de dossiês de consultoria de imagem e estilo, página por página." },
      { property: "og:title", content: "Copiloto de Consultoria de Imagem" },
      { property: "og:description", content: "Apoio à montagem de dossiês de consultoria de imagem e estilo, página por página." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Index,
});

// IMPORTANT: Replace this placeholder. See ./README.md for routing conventions.
function Index() {
  return (
    <div
      className="flex min-h-screen items-center justify-center"
      style={{ backgroundColor: "#fcfbf8" }}
    >
      <img
        data-lovable-blank-page-placeholder="REMOVE_THIS"
        src="https://cdn.gpteng.co/blank-app-v1.svg"
        alt="Your app will live here!"
      />
    </div>
  );
}
