"""Contratos de entrada: somente identificadores fictícios no piloto acadêmico."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionInput(StrictModel):
    identificador: str = Field(pattern=r"^Cliente [A-Z][A-Z0-9 -]{0,15}$")
    modo: Literal["feminino", "masculino"] = "feminino"
    pacote: str = "pacote_1"
    objetivo: str = Field(default="", max_length=2000)


class FichaInput(StrictModel):
    revision: int = Field(ge=0)
    questionario: dict[str, str] = Field(default_factory=dict, max_length=30)
    avaliacao: dict[str, dict[str, str | int | float | None]] = Field(default_factory=dict, max_length=10)


class PageInput(StrictModel):
    revision: int = Field(ge=0)
    texto: str = Field(max_length=20000)


class ApprovalInput(StrictModel):
    revision: int = Field(ge=0)
    decisao: Literal["aprovar", "reabrir"]


class ChatInput(StrictModel):
    pergunta: str = Field(min_length=3, max_length=2000)
    sessao_id: str | None = None


class PhotoInput(StrictModel):
    revision: int = Field(ge=0)
    nome: str = Field(min_length=1, max_length=120)
    data_url: str = Field(max_length=4_000_000)


class ReferenceInput(StrictModel):
    revision: int = Field(ge=0)
    titulo: str = Field(min_length=1, max_length=200)
    tipo: str = Field(default="", max_length=100)
    orientacao: str = Field(default="", max_length=2000)
    ocasiao: str = Field(default="", max_length=200)
    cor_modelagem: str = Field(default="", max_length=500)
    link: str = Field(default="", max_length=1000)


class ImportInput(StrictModel):
    versao: Literal[2, 3]
    cliente: str
    pacote: str
    questionario: dict[str, str] = Field(default_factory=dict)
    avaliacao: dict[str, dict[str, str | int | float | None]] = Field(default_factory=dict)
    paginas: dict[str, str] = Field(default_factory=dict, max_length=16)


class EditorialInput(StrictModel):
    revision: int = Field(ge=0)
    titulo: str = Field(min_length=1, max_length=160)
    tema: Literal["perfil", "visagismo", "coloracao", "proporcoes", "metodologia"]
    texto: str = Field(min_length=30, max_length=3000)
    confirmo_padrao_sem_dados_pessoais: bool = False
