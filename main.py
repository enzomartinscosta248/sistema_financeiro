from datetime import date

from database import inicializar_banco
from gestor_financeiro import GestorFinanceiro
from excecoes import ErroGestaoFinanceira

import relatorios


def ler_float(mensagem: str) -> float:
    while True:
        try:
            return float(
                input(mensagem).replace(",", ".")
            )
        except ValueError:
            print(
                "Valor invalido, digite um numero "
                "(ex: 150.50)."
            )


def ler_int(mensagem: str) -> int:
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um numero inteiro valido.")


def escolher_categoria(
    gestor: GestorFinanceiro,
    tipo: str,
) -> int:
    categorias = gestor.listar_categorias(tipo)

    print("\nCategorias disponiveis:")

    for categoria in categorias:
        print(
            f"  {categoria['id']} - "
            f"{categoria['nome']}"
        )

    return ler_int("Escolha o id da categoria: ")


def menu_adicionar(
    gestor: GestorFinanceiro,
    tipo: str,
):
    print()

    descricao = input("Descricao: ")
    valor = ler_float("Valor: R$ ")

    categoria_id = escolher_categoria(
        gestor,
        tipo,
    )

    try:
        id_criado = gestor.adicionar_transacao(
            tipo,
            descricao,
            valor,
            categoria_id,
            date.today(),
        )

        print(
            f"{tipo.capitalize()} registrada "
            f"com sucesso (id {id_criado})!"
        )

    except ErroGestaoFinanceira as erro:
        print(f"Nao foi possivel registrar: {erro}")


def menu_listar(gestor: GestorFinanceiro):
    transacoes = gestor.listar_transacoes()

    if not transacoes:
        print("\nNenhuma transacao cadastrada ainda.")
        return

    print("\n===== TRANSACOES =====")

    for transacao in transacoes:
        print(
            f"  #{transacao.id} "
            f"{transacao.resumo()}"
        )


def menu_remover(gestor: GestorFinanceiro):
    transacao_id = ler_int(
        "Id da transacao a remover: "
    )

    try:
        gestor.remover_transacao(transacao_id)
        print("Transacao removida.")

    except ErroGestaoFinanceira as erro:
        print(f"Erro: {erro}")


def menu_relatorio(gestor: GestorFinanceiro):
    relatorio = relatorios.gerar_relatorio_geral(
        gestor
    )

    print()
    print(relatorio)

    resposta = input(
        "\nSalvar esse relatorio em relatorio.txt? (s/n) "
    )

    if resposta.lower() == "s":
        relatorios.salvar_relatorio_em_arquivo(
            relatorio
        )

        print(
            "Relatorio salvo em relatorio.txt"
        )


def exibir_menu():
    print()
    print("======================================")
    print(" SISTEMA DE GESTAO FINANCEIRA")
    print("======================================")
    print("1 - Adicionar receita")
    print("2 - Adicionar despesa")
    print("3 - Listar transacoes")
    print("4 - Remover transacao")
    print("5 - Ver relatorio geral")
    print("6 - Ver saldo atual")
    print("0 - Sair")
    print("======================================")


def main():
    inicializar_banco()

    gestor = GestorFinanceiro()

    while True:
        exibir_menu()

        opcao = input(
            "Escolha uma opcao: "
        ).strip()

        if opcao == "1":
            menu_adicionar(
                gestor,
                "receita",
            )

        elif opcao == "2":
            menu_adicionar(
                gestor,
                "despesa",
            )

        elif opcao == "3":
            menu_listar(gestor)

        elif opcao == "4":
            menu_remover(gestor)

        elif opcao == "5":
            menu_relatorio(gestor)

        elif opcao == "6":
            saldo = gestor.calcular_saldo()

            print(
                f"\nSaldo atual: R$ {saldo:.2f}"
            )

        elif opcao == "0":
            print("Ate mais!")
            break

        else:
            print(
                "Opcao invalida, tente novamente."
            )


if __name__ == "__main__":
    main()
