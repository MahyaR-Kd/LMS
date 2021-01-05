from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from passlib.hash import sha256_crypt
import psycopg2
from models import User
from config import *

app = Flask(__name__)

# config
app.config.update(SECRET_KEY = SECRET_KEY)

#database


# table_name = 'users'
# cur.execute("DROP TABLE IF EXISTS users;")
# cur.execute("CREATE TABLE users(%s, %s, %s, %s, %s);" % ("ID INT PRIMARY KEY","FIRSTNAME TEXT", "LASTNAME TEXT", "EMAIL  TEXT", "PASSWORD TEXT"))

# conn.commit()


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# create some users with ids 1 to 20       


# main site route

@app.route('/')
def main_page():

    return render_template('site/index.html')

@app.route('/about')
def about_page():

    return render_template('site/about.html')

@app.route('/services')
def services_page():

    return render_template('site/services.html')

@app.route('/contact')
def contact_page():

    return render_template('site/contact.html')


# dashboard route


@app.route('/dash')
@login_required
def dash_page():

    return render_template('admin/index.html')



@app.route("/login", methods=["GET", "POST"])
def login():  # sourcery skip: remove-unnecessary-else, swap-if-else-branches
    if request.method == 'POST':
        db = psycopg2.connect(database = PSQL_DB_NAME, user = PSQL_USERNAME, password = PSQL_PASSWORD, host = PSQL_HOST, port = PSQL_PORT)
        cur = db.cursor() 
        
        emailaddress = request.form['emailaddress']
        password = request.form['password'] 

        cur.execute("select * from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
        email_exist = bool(cur.rowcount)
        
        cur.execute("select password from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
        usr_pass = cur.fetchall()
        usr_pass = usr_pass[0][0]
        usr_pass = usr_pass.replace(' ','')

        cur.execute("select register from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
        usr_register = cur.fetchall()
        usr_register = usr_register[0][0]
        
        cur.execute("select id from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
        usr_id = cur.fetchall()
        usr_id = usr_id[0][0]

        # usr_id = cur.fetchall()[0]

        user = User(usr_id)

        if email_exist and usr_pass == password and usr_register:
            login_user(user)
            return redirect('/dash')
        else:
            return abort(401)

        db.commit()
        db.close()
        
    else:
        return render_template('admin/login.html')
    

@app.route("/register", methods=["GET", "POST"])
def register(): 
    db = psycopg2.connect(database = PSQL_DB_NAME, user = PSQL_USERNAME, password = PSQL_PASSWORD, host = PSQL_HOST, port = PSQL_PORT)
    cur = db.cursor() 
    
    if request.method == 'POST':
        id = '0'
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        emailadd = request.form['emailaddress']
        password = request.form['password']
       
        cur.execute("select id from users;")
        id_exist = bool(cur.rowcount)
        if id_exist:
            ids = cur.fetchall()
            last_id = ids[-1][0]
            id = str(last_id + 1)
        # UPDATE users SET register='t' WHERE ID=0;
          
        cur.execute("select * from users where to_tsvector(email) @@ to_tsquery(%s);", (emailadd,))
        email_exist = bool(cur.rowcount)
        if email_exist:
            flash(u'You Email have exist!','info')
        else:
            cur.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)", (id, firstname, lastname, emailadd, password, 'f') )
            flash(u'You Acconte Sucssesfuly Create','info')
    db.commit()
    db.close()
    return render_template('admin/register.html')     


@app.route("/forgot-pass")
def forgot_pass():

    return render_template('admin/forgot-password.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/dash')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    
    flash('your username or password is faild!', 'info')
    return redirect('/login')

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == '__main__':
    app.run('0.0.0.0' ,'5000' ,debug=True)