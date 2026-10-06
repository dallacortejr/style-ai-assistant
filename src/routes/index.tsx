import { createFileRoute } from "@tanstack/react-router";
import { Access } from "../features/consultoria/Access";
export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Estúdio | Copiloto de Consultoria" },
      {
        name: "description",
        content: "O consultor conduz. O copiloto apoia os dossiês de imagem e estilo.",
      },
    ],
  }),
  component: Access,
});
