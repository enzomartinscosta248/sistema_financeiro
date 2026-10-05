from gestor_financeiro import GestorFinanceiro


def gerar_relatorio_geral(gestor: GestorFinanceiro) -> str:
    linhas = []

    linhas.append("=" * 50)
    linhas.append("RELATORIO FINANCEIRO GERAL".center(50))
    linhas.append("=" * 50)

    saldo = gestor.calcular_saldo()

    linhas.append(f"Saldo atual: R$ {saldo:.2f}")
    linhas.append("")

    linhas.append("Totais por categoria:")

    totais = gestor.total_por_categoria()

    if not totais:
        linhas.append("  Nenhuma transacao cadastrada.")

    for linha in totais:
        sinal = "+" if linha["tipo"] == "receita" else "-"

        linhas.append(
            f"  {sinal} {linha['categoria']:<15} "
            f"R$ {linha['total']:.2f}"
        )

    linhas.append("")
    linhas.append("Ultimas transacoes:")

    transacoes = gestor.listar_transacoes()

    if not transacoes:
        linhas.append("  Nenhuma transacao cadastrada.")

    for transacao in transacoes[:10]:
        linhas.append(f"  {transacao.resumo()}")

    linhas.append("=" * 50)

    return "\n".join(linhas)


def gerar_relatorio_mensal(
    gestor: GestorFinanceiro,
    ano: int,
    mes: int,
) -> str:
    resumo = gestor.resumo_mensal(ano, mes)

    linhas = [
        f"Resumo de {mes:02d}/{ano}",
        "-" * 30,
        f"Receitas: R$ {resumo['receitas']:.2f}",
        f"Despesas: R$ {resumo['despesas']:.2f}",
        f"Saldo:    R$ {resumo['saldo']:.2f}",
    ]

    return "\n".join(linhas)


def salvar_relatorio_em_arquivo(
    conteudo: str,
    caminho: str = "relatorio.txt",
):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)
