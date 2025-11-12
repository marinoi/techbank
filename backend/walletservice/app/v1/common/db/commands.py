import psycopg
from psycopg import sql


def create_postgresql_db(db_name: str,
                         admin_db: str,
                         admin_username: str,
                         admin_password: str,
                         db_host: str,
                         db_port: int) -> None:

    conn = psycopg.connect(dbname=admin_db,
                           user=admin_username,
                           password=admin_password,
                           host=db_host,
                           port=db_port)

    conn.autocommit = True  # Required before running CREATE DATABASE

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cur.fetchone()

        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

    conn.close()
