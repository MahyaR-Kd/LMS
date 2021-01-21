from flask import Flask, request, redirect, url_for, flash, Response
import psycopg2
from random import randint
from email_sender import register_email
import config




def verify_code_generator(email):
    # email = request.args.get('email')
    db = psycopg2.connect(
         database = config.PSQL_DB_NAME,
         user = config.PSQL_USERNAME, 
         password = config.PSQL_PASSWORD, 
         host = config.PSQL_HOST, 
         port = config.PSQL_PORT)
    cur = db.cursor() 
    cur.execute("select * from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
    email_exist = bool(cur.rowcount)


    if email_exist:

        verify_code = randint(100000, 999999)

        cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_id = cur.fetchall()
        usr_id = usr_id[0][0]
        print(verify_code,usr_id)
        cur.execute("UPDATE lms_users SET token=%s WHERE ID=%s;" % (verify_code,usr_id,))
        print("UPDATE lms_users SET token=%s WHERE ID=%s;" % (verify_code,usr_id,))
        cur.execute("select firstname from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_firstname = cur.fetchall()
        usr_firstname = usr_firstname[0][0]
        usr_firstname = usr_firstname.replace(' ','')
        cur.execute("select lastname from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_lastname = cur.fetchall()
        usr_lastname = usr_lastname[0][0]
        usr_lastname = usr_lastname.replace(' ','')
        # register_email(usr_firstname, usr_lastname, email, verify_code)
        flash('Email Sended Please Check Your Email Inbox','success')

        db.commit()
        db.close()


