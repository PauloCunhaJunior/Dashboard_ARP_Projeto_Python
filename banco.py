"""Histórico local em SQLite (já incluído na instalação do Python)."""

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

ARQUIVO_BANCO = Path(__file__).resolve().parent / "historico_arp.sqlite3"


def inicializar_banco():
    with closing(sqlite3.connect(ARQUIVO_BANCO)) as conexao:
        with conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS coletas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    momento TEXT NOT NULL,
                    fonte TEXT NOT NULL,
                    total INTEGER NOT NULL
                )
            """)
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS observacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coleta_id INTEGER NOT NULL,
                    interface TEXT NOT NULL,
                    ip TEXT NOT NULL,
                    mac TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    FOREIGN KEY(coleta_id) REFERENCES coletas(id)
                )
            """)
            conexao.execute("""
                CREATE INDEX IF NOT EXISTS ix_historico
                ON observacoes(ip, mac, coleta_id)
            """)


def salvar_coleta(registros, fonte):
    momento = datetime.now().astimezone().isoformat(timespec="seconds")
    with closing(sqlite3.connect(ARQUIVO_BANCO)) as conexao:
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO coletas(momento, fonte, total) VALUES (?, ?, ?)",
                (momento, fonte, len(registros)),
            )
            coleta_id = cursor.lastrowid
            conexao.executemany(
                """INSERT INTO observacoes(coleta_id, interface, ip, mac, tipo)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (coleta_id, r["interface"], r["ip"], r["mac"], r["tipo"])
                    for r in registros
                ],
            )
    return coleta_id


def ultima_coleta(fonte):
    with closing(sqlite3.connect(ARQUIVO_BANCO)) as conexao:
        conexao.row_factory = sqlite3.Row
        coleta = conexao.execute(
            "SELECT * FROM coletas WHERE fonte = ? ORDER BY id DESC LIMIT 1",
            (fonte,),
        ).fetchone()
        if coleta is None:
            return None, []
        linhas = conexao.execute(
            """SELECT interface, ip, mac, tipo FROM observacoes
               WHERE coleta_id = ? ORDER BY ip, mac""",
            (coleta["id"],),
        ).fetchall()
        return dict(coleta), [dict(registro) for registro in linhas]


def obter_historico(ip, mac, fonte):
    with closing(sqlite3.connect(ARQUIVO_BANCO)) as conexao:
        conexao.row_factory = sqlite3.Row
        linha = conexao.execute(
            """SELECT MIN(c.momento) AS primeira_vez,
                      MAX(c.momento) AS ultima_vez,
                      COUNT(DISTINCT c.id) AS quantidade_coletas
               FROM observacoes AS o
               JOIN coletas AS c ON c.id = o.coleta_id
               WHERE o.ip = ? AND o.mac = ? AND c.fonte = ?""",
            (ip, mac, fonte),
        ).fetchone()
        return dict(linha)
