from dataclasses import dataclass
from datetime import date


@dataclass
class Transacao:
    descricao: str
    valor: float
    data: date
    categoria: str
    id: int = None

    def __str__(self) -> str:
        return self.resumo()

    def resumo(self) -> str:
        return (
            f"[{self.data}] {self.descricao}: "
            f"R$ {self.valor:.2f} ({self.categoria})"
        )


@dataclass
class Receita(Transacao):
    def __str__(self) -> str:
        return self.resumo()

    def resumo(self) -> str:
        return f"(+) {super().resumo()}"


@dataclass
class Despesa(Transacao):
    def __str__(self) -> str:
        return self.resumo()

    def resumo(self) -> str:
        return f"(-) {super().resumo()}"