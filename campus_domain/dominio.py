"""Modelo de domínio puro (RNF-01): sem XML, JSON, banco ou HTTP.
Agregados protegem as invariantes não espaciais; as espaciais ficam na camada
de validação semântica, que conhece o modelo do campus inteiro."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

class RegraDeDominioViolada(ValueError):
    def __init__(self, regra: str, mensagem: str):
        super().__init__(f"[{regra}] {mensagem}"); self.regra = regra

# ---------- Value Objects (imutáveis, igualdade por valor) ----------
@dataclass(frozen=True)
class Identificador:
    valor: str
    def __post_init__(self):
        if not self.valor.startswith("urn:upm:campus-hig:"):
            raise RegraDeDominioViolada("INV-01", f"identificador fora do padrão: {self.valor}")

@dataclass(frozen=True)
class NumeroMapa:
    valor: int
    def __post_init__(self):
        if not 1 <= self.valor <= 999:
            raise RegraDeDominioViolada("INV-11", "número do mapa deve estar entre 1 e 999")

@dataclass(frozen=True)
class Endereco:
    logradouro: str
    numero: str
    municipio: str = "São Paulo"
    uf: str = "SP"

@dataclass(frozen=True)
class Geometria:
    """Geometria em EPSG:31983. tipo: Point | LineString | Polygon."""
    tipo: str
    coordenadas: tuple
    crs: str = "EPSG:31983"
    def __post_init__(self):
        if self.crs != "EPSG:31983":
            raise RegraDeDominioViolada("INV-10", f"CRS {self.crs} diferente do adotado (EPSG:31983)")

# ---------- Entidade interna e agregados ----------
@dataclass
class Pavimento:
    id: Identificador
    numero: int
    nome: str
    geometria: Geometria
    unidades_ocupantes: tuple = ()

@dataclass
class Edificacao:
    """Raiz de agregado. Fronteira: a edificação e seus pavimentos (INV-04, INV-05)."""
    id: Identificador
    numero_mapa: NumeroMapa
    nome: str
    localizacao: str
    categoria_uso: str
    situacao: str
    geometria: Geometria
    homenageado: Optional[str] = None
    endereco: Optional[Endereco] = None
    unidades_ocupantes: tuple = ()
    _pavimentos: list = field(default_factory=list)

    @classmethod
    def criar(cls, **dados) -> "Edificacao":
        if dados.get("localizacao") not in ("interna", "externa"):
            raise RegraDeDominioViolada("INV-12", "localização deve ser interna ou externa")
        if dados["localizacao"] == "externa" and dados.get("endereco") is None:
            raise RegraDeDominioViolada("INV-14", "edificação externa exige endereço")
        end = dados.get("endereco")
        if dados["localizacao"] == "externa" and str(dados["numero_mapa"].valor) != end.numero:
            raise RegraDeDominioViolada("INV-15", "edificação externa: número do mapa deve ser o número do endereço")
        if dados["geometria"].tipo != "Polygon":
            raise RegraDeDominioViolada("INV-03", "edificação exige geometria poligonal")
        return cls(**dados)

    @property
    def pavimentos(self) -> tuple:
        return tuple(sorted(self._pavimentos, key=lambda p: p.numero))

    def adicionar_pavimento(self, pavimento: Pavimento) -> "PavimentoAdicionado":
        if any(p.numero == pavimento.numero for p in self._pavimentos):
            raise RegraDeDominioViolada("INV-05", f"pavimento {pavimento.numero} já existe na edificação {self.numero_mapa.valor}")
        self._pavimentos.append(pavimento)
        return PavimentoAdicionado(self.id, pavimento.id, pavimento.numero)

@dataclass
class Via:
    id: Identificador
    nome: str
    classe: str
    geometria: Geometria
    revestimento: str = "nao-informado"

@dataclass
class PontoDeInteresse:
    id: Identificador
    nome: str
    categoria: str
    geometria: Geometria
    numero_portaria: Optional[int] = None
    endereco: Optional[Endereco] = None
    edificacao_ref: Optional[Identificador] = None

    @classmethod
    def criar(cls, **dados) -> "PontoDeInteresse":
        if dados["categoria"] == "portaria" and (dados.get("numero_portaria") is None or dados.get("endereco") is None):
            raise RegraDeDominioViolada("INV-07", "portaria exige número e endereço")
        return cls(**dados)

@dataclass
class AreaVerde:
    id: Identificador
    nome: str
    cobertura: str
    geometria: Geometria

# ---------- Eventos de domínio (vocabulário publicado para o G3 emitir) ----------
@dataclass(frozen=True)
class ObjetoUrbanoCadastrado:
    objeto_id: Identificador
    tipo: str
    versao: int = 1

@dataclass(frozen=True)
class GeometriaAtualizada:
    objeto_id: Identificador
    versao_anterior: int
    versao_nova: int

@dataclass(frozen=True)
class PavimentoAdicionado:
    edificacao_id: Identificador
    pavimento_id: Identificador
    numero: int

@dataclass(frozen=True)
class ObjetoUrbanoDesativado:
    objeto_id: Identificador
    motivo: str
