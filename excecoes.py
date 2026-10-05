class ErroGestaoFinanceira(Exception):
    """Classe base para todas as excecoes do sistema."""


class ValorInvalidoError(ErroGestaoFinanceira):
    """Levantada quando o valor de uma transacao e zero ou negativo."""


class CategoriaNaoEncontradaError(ErroGestaoFinanceira):
    """Levantada quando a categoria informada nao existe no banco."""


class TransacaoNaoEncontradaError(ErroGestaoFinanceira):
    """Levantada quando uma transacao nao existe."""


class TipoInvalidoError(ErroGestaoFinanceira):
    """Levantada quando o tipo nao e receita nem despesa."""
