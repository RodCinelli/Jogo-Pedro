import sqlite3
import os


def connect_db(path: str):
    conn = sqlite3.connect(path)
    return conn


def print_players(conn):
    cur = conn.cursor()
    # Ordem de criação: id ASC (ids autoincrement refletem inserção)
    cur.execute("SELECT id, name FROM players ORDER BY id ASC")
    rows = cur.fetchall()
    print("Players ({}):".format(len(rows)))
    for idx, (_pid, name) in enumerate(rows, start=1):
        print(f" {idx}. {name}")


def print_top_scores(conn, limit=10):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT player_name, MAX(score) AS best, COUNT(*) AS plays
        FROM scores
        GROUP BY player_name
        ORDER BY best DESC, player_name ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    print("Top scores (limit {}):".format(limit))
    for i, (name, best, plays) in enumerate(rows, start=1):
        print(f" {i}. {name} / best = {best} / plays = {plays}")


# (Removed sequences section per request)


def main():
    db_path = os.path.join(os.getcwd(), "warrior_platform.db")
    if not os.path.exists(db_path):
        print("Database not found:", db_path)
        return
    conn = connect_db(db_path)
    try:
        print_players(conn)
        print()
        print_top_scores(conn, limit=10)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
