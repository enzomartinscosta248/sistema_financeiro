import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).parent / "financeiro.db"


def conectar():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa'))
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa')),
            descricao TEXT NOT NULL,
            valor REAL NOT NULL CHECK (valor > 0),
            data TEXT NOT NULL,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
        """
    )

    conexao.commit()

    categorias_padrao = [
        ("Salario", "receita"),
        ("Freelance", "receita"),
        ("Alimentacao", "despesa"),
        ("Transporte", "despesa"),
        ("Moradia", "despesa"),
        ("Lazer", "despesa"),
    ]

    for nome, tipo in categorias_padrao:
        try:
            cursor.execute(
                "INSERT INTO categorias (nome, tipo) VALUES (?, ?)",
                (nome, tipo),
            )
        except sqlite3.IntegrityError:
            pass

    conexao.commit()
    conexao.close()