from flask import flash
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

def course_remover(user, post_id):
    db = psycopg2.connect(
    database = config.PSQL_DB_NAME,
    user = config.PSQL_USERNAME, 
    password = config.PSQL_PASSWORD, 
    host = config.PSQL_HOST, 
    port = config.PSQL_PORT)
    cur = db.cursor()

    cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (user,))
    usr_id = cur.fetchall()
    usr_id = usr_id[0][0]
    cur.execute("select id from lms_posts where post_author=%s;" % (usr_id))
    course_list = cur.fetchall()
    course_id_list = []
    for i in course_list:
        course_id_list.append(i[0])
    if post_id in course_id_list:
        # print(post_id,course_id_list,'yes')
        cur.execute("DELETE FROM lms_posts WHERE id = %s;" % (post_id))
        flash('Course Remove Succsessfuly','success')
    else:
        flash('Course dosn`t Remove','warning')

    db.commit()
    db.close()
