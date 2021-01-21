import config
import psycopg2


def users_table():    
    with psycopg2.connect(
        database = config.PSQL_DB_NAME,
        user = config.PSQL_USERNAME,
        password = config.PSQL_PASSWORD,
        host = config.PSQL_HOST,
        port = config.PSQL_PORT) as conn:
                
        print ("Opened database successfully")

        cur = conn.cursor()

            # table_name = 'users'
            # cur.execute("select * from information_schema.tables where table_name=%s", (table_name,))
            # tabel_exist = bool(cur.rowcount)
            # if tabel_exist:
        # cur.execute("CREATE EXTENSION pgcrypto;")
        cur.execute("DROP TABLE IF EXISTS lms_users;")
        cur.execute("""CREATE TABLE lms_users(
                ID SERIAL PRIMARY KEY,
                FIRSTNAME CHAR(15), 
                LASTNAME CHAR(15), 
                EMAIL  TEXT NOT NULL, 
                PASSWORD TEXT NOT NULL,
                REGISTER BOOL DEFAULT 'F',
                CREATE_AT TIMESTAMPTZ DEFAULT Now(),
                TOKEN CHAR(6),
                USER_ROLES CHAR(1) NOT NULL DEFAULT 'S');""")


        print ("Table created successfully")

        conn.commit()


def course_table():
        with psycopg2.connect(
            database = config.PSQL_DB_NAME,
            user = config.PSQL_USERNAME,
            password = config.PSQL_PASSWORD,
            host = config.PSQL_HOST,
            port = config.PSQL_PORT) as conn:
                    
            print ("Opened database successfully")

            cur = conn.cursor()
        #     DEFAULT uuid_generate_v4 ()
            cur.execute("DROP TABLE IF EXISTS lms_posts;")
            cur.execute("""CREATE TABLE lms_posts(
                    ID SERIAL PRIMARY KEY,
                    post_author integer,
                    post_date TIMESTAMPTZ DEFAULT Now(),
                    post_content TEXT,
                    post_title TEXT,
                    post_excerpt TEXT,
                    post_image TEXT,
                    post_status varchar DEFAULT 'publish',
                    post_name varchar(200),
                    menu_order integer
                    );""" )
                
            print ("Table created successfully")

            conn.commit()




def site_setting_table():
        with psycopg2.connect(
            database = config.PSQL_DB_NAME,
            user = config.PSQL_USERNAME,
            password = config.PSQL_PASSWORD,
            host = config.PSQL_HOST,
            port = config.PSQL_PORT) as conn:
                    
            print ("Opened database successfully")

            cur = conn.cursor()
            
            cur.execute("DROP TABLE IF EXISTS site_setting;")
            cur.execute("""CREATE TABLE site_setting(
                    ID SERIAL PRIMARY KEY,
                    SLIDER CHAR(15),
                    IMG_PATH TEXT);""" )
                
            print ("Table created successfully")

            conn.commit()

# users_table()
course_table()
# site_setting_table()
