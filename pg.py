import psycopg2


class PostgresDB(object):
    def __init__(self, host, db, user, password):
        self._db = psycopg2.connect(f'host={host} dbname={db} user={user} password={password}')

    def query(self, sql):
        try:
            cur = self._db.cursor()
            cur.execute(sql)
            cur.close()
            self._db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def close(self):
        self._db.close()
