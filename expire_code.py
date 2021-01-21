from flask import flash 
import psycopg2
import config




def expire_verifi_code(email):
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
        cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_id = cur.fetchall()
        usr_id = usr_id[0][0]
        cur.execute("UPDATE lms_users SET token='' WHERE ID=%s;" % (usr_id,))
        flash('Your Code Expired! ','danger')
        flash('Please Click on "Send New Verify Code" For Give New Code','info')
    else:
        flash('Your Email Not Exist Please Sign Up Frist','warning')
    db.commit()
    db.close()