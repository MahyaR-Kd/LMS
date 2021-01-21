import psycopg2
import config


def users_edit(email, user_roles):
    db = psycopg2.connect(
    database = config.PSQL_DB_NAME,
    user = config.PSQL_USERNAME, 
    password = config.PSQL_PASSWORD, 
    host = config.PSQL_HOST, 
    port = config.PSQL_PORT)
    cur = db.cursor()

    cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
    usr_id = cur.fetchall()
    usr_id = usr_id[0][0]
    cur.execute("UPDATE lms_users SET user_roles='%s' WHERE ID=%s;" % (user_roles,usr_id,))
    db.commit()
    db.close()


def user_profile():
    pass


def course_creator(email, title, content, summary, image):
    db = psycopg2.connect(
    database = config.PSQL_DB_NAME,
    user = config.PSQL_USERNAME, 
    password = config.PSQL_PASSWORD, 
    host = config.PSQL_HOST, 
    port = config.PSQL_PORT)
    cur = db.cursor()

    cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
    usr_id = cur.fetchall()
    usr_id = usr_id[0][0]

    cur.execute("INSERT INTO lms_posts(post_author, post_title, post_content, post_excerpt, post_image) VALUES (%s, %s, %s, %s, %s)", (usr_id, title, content, summary, image))

    db.commit()
    db.close()

