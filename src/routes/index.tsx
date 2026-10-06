import { createFileRoute } from "@tanstack/react-router";
import { Workspace } from "../features/consultoria/Workspace";
export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Heloisa Hermann | Copiloto de Consultoria" },
      {
        name: "description",
        content: "O consultor conduz. O copiloto apoia os dossiês de imagem e estilo.",
      },
    ],
  }),
  component: Workspace,
});
