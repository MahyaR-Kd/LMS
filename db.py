from config import *
import psycopg2

with psycopg2.connect(database = PSQL_DB_NAME, user = PSQL_USERNAME, password = PSQL_PASSWORD, host = PSQL_HOST, port = PSQL_PORT) as conn:
            
    print ("Opened database successfully")

    cur = conn.cursor()

        # table_name = 'users'
        # cur.execute("select * from information_schema.tables where table_name=%s", (table_name,))
        # tabel_exist = bool(cur.rowcount)
        # if tabel_exist:

    cur.execute("DROP TABLE IF EXISTS users;")
    cur.execute("""CREATE TABLE users(
            ID int NOT NULL PRIMARY KEY,
            FIRSTNAME CHAR(30), 
            LASTNAME CHAR(30), 
            EMAIL  CHAR(30), 
            PASSWORD CHAR(30),
            REGISTER BOOL);""")


    print ("Table created successfully")

    conn.commit()


