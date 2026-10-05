from datetime import date

from database import conectar
from excecoes import (
    ValorInvalidoError,
    CategoriaNaoEncontradaError,
    TransacaoNaoEncontradaError,
    TipoInvalidoError,
)
from models import Receita, Despesa


class GestorFinanceiro:

    TIPOS_VALIDOS = ("receita", "despesa")

    # ==========================================================
    # CATEGORIAS
    # ==========================================================

    def listar_categorias(self, tipo: str = None):
        conexao = conectar()

        if tipo:
            linhas = conexao.execute(
                "SELECT * FROM categorias WHERE tipo = ? ORDER BY nome",
                (tipo,)
            ).fetchall()
        else:
            linhas = conexao.execute(
                "SELECT * FROM categorias ORDER BY tipo, nome"
            ).fetchall()

        conexao.close()
        return linhas

    def criar_categoria(self, nome: str, tipo: str):
        if tipo not in self.TIPOS_VALIDOS:
            raise TipoInvalidoError(
                f"Tipo '{tipo}' invalido. Use 'receita' ou 'despesa'."
            )

        conexao = conectar()

        try:
            conexao.execute(
                "INSERT INTO categorias (nome, tipo) VALUES (?, ?)",
                (nome, tipo)
            )
            conexao.commit()
        finally:
            conexao.close()

    def _categoria_existe(self, conexao, categoria_id: int) -> bool:
        linha = conexao.execute(
            "SELECT id FROM categorias WHERE id = ?",
            (categoria_id,)
        ).fetchone()

        return linha is not None

    # ==========================================================
    # TRANSACOES
    # ==========================================================

    def adicionar_transacao(
        self,
        tipo: str,
        descricao: str,
        valor: float,
        categoria_id: int,
        data_transacao: date = None
    ) -> int:

        if tipo not in self.TIPOS_VALIDOS:
            raise TipoInvalidoError(
                f"Tipo '{tipo}' invalido. Use 'receita' ou 'despesa'."
            )

        if valor <= 0:
            raise ValorInvalidoError(
                "O valor da transacao precisa ser maior que zero."
            )

        data_transacao = data_transacao or date.today()

        conexao = conectar()

        try:
            if not self._categoria_existe(conexao, categoria_id):
                raise CategoriaNaoEncontradaError(
                    f"Categoria com id {categoria_id} nao existe."
                )

            cursor = conexao.execute(
                """
                INSERT INTO transacoes
                (tipo, descricao, valor, data, categoria_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    tipo,
                    descricao,
                    valor,
                    data_transacao.isoformat(),
                    categoria_id,
                )
            )

            conexao.commit()
            return cursor.lastrowid

        finally:
            conexao.close()

    def listar_transacoes(self, tipo: str = None):
        conexao = conectar()

        consulta = """
            SELECT
                t.id,
                t.tipo,
                t.descricao,
                t.valor,
                t.data,
                c.nome AS categoria
            FROM transacoes t
            LEFT JOIN categorias c
                ON c.id = t.categoria_id
        """

        parametros = ()

        if tipo:
            consulta += " WHERE t.tipo = ?"
            parametros = (tipo,)

        consulta += " ORDER BY t.data DESC, t.id DESC"

        linhas = conexao.execute(
            consulta,
            parametros
        ).fetchall()

        conexao.close()

        transacoes = []

        for linha in linhas:
            classe = Receita if linha["tipo"] == "receita" else Despesa

            transacoes.append(
                classe(
                    id=linha["id"],
                    descricao=linha["descricao"],
                    valor=linha["valor"],
                    data=date.fromisoformat(linha["data"]),
                    categoria=linha["categoria"],
                )
            )

        return transacoes

    def buscar_transacao(self, transacao_id: int):
        conexao = conectar()

        linha = conexao.execute(
            "SELECT * FROM transacoes WHERE id = ?",
            (transacao_id,)
        ).fetchone()

        conexao.close()

        if linha is None:
            raise TransacaoNaoEncontradaError(
                f"Transacao {transacao_id} nao encontrada."
            )

        return linha

    def atualizar_transacao(self, transacao_id: int, **campos):
        self.buscar_transacao(transacao_id)

        if "valor" in campos and campos["valor"] <= 0:
            raise ValorInvalidoError(
                "O valor da transacao precisa ser maior que zero."
            )

        colunas_permitidas = {
            "descricao",
            "valor",
            "data",
            "categoria_id",
        }

        atualizacoes = {
            chave: valor
            for chave, valor in campos.items()
            if chave in colunas_permitidas
        }

        if not atualizacoes:
            return

        if "categoria_id" in atualizacoes:
            conexao = conectar()

            try:
                if not self._categoria_existe(
                    conexao,
                    atualizacoes["categoria_id"]
                ):
                    raise CategoriaNaoEncontradaError(
                        f"Categoria com id "
                        f"{atualizacoes['categoria_id']} nao existe."
                    )
            finally:
                conexao.close()

        set_clause = ", ".join(
            f"{coluna} = ?"
            for coluna in atualizacoes
        )

        valores = list(atualizacoes.values())
        valores.append(transacao_id)

        conexao = conectar()

        try:
            conexao.execute(
                f"UPDATE transacoes SET {set_clause} WHERE id = ?",
                valores
            )

            conexao.commit()

        finally:
            conexao.close()

    def remover_transacao(self, transacao_id: int):
        self.buscar_transacao(transacao_id)

        conexao = conectar()

        try:
            conexao.execute(
                "DELETE FROM transacoes WHERE id = ?",
                (transacao_id,)
            )

            conexao.commit()

        finally:
            conexao.close()

    # ==========================================================
    # RELATORIOS
    # ==========================================================

    def calcular_saldo(self) -> float:
        conexao = conectar()

        try:
            total_receitas = conexao.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM transacoes
                WHERE tipo = 'receita'
                """
            ).fetchone()[0]

            total_despesas = conexao.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM transacoes
                WHERE tipo = 'despesa'
                """
            ).fetchone()[0]

            return total_receitas - total_despesas

        finally:
            conexao.close()

    def total_por_categoria(self, tipo: str = None):
        conexao = conectar()

        consulta = """
            SELECT
                c.nome AS categoria,
                t.tipo,
                SUM(t.valor) AS total
            FROM transacoes t
            JOIN categorias c
                ON c.id = t.categoria_id
        """

        parametros = ()

        if tipo:
            consulta += " WHERE t.tipo = ?"
            parametros = (tipo,)

        consulta += """
            GROUP BY c.nome, t.tipo
            ORDER BY total DESC
        """

        linhas = conexao.execute(
            consulta,
            parametros
        ).fetchall()

        conexao.close()

        return linhas

    def resumo_mensal(self, ano: int, mes: int):
        mes_str = f"{ano:04d}-{mes:02d}"

        conexao = conectar()

        try:
            receitas = conexao.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM transacoes
                WHERE tipo = 'receita'
                AND data LIKE ?
                """,
                (f"{mes_str}%",)
            ).fetchone()[0]

            despesas = conexao.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM transacoes
                WHERE tipo = 'despesa'
                AND data LIKE ?
                """,
                (f"{mes_str}%",)
            ).fetchone()[0]

            return {
                "receitas": receitas,
                "despesas": despesas,
                "saldo": receitas - despesas,
            }

        finally:
            conexao.close()