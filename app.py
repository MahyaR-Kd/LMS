from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from passlib.hash import sha256_crypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import psycopg2
import urllib
from random import randint
from email_sender import register_email, welcome_email
from new_code import verify_code_generator
from models import User
import config
app = Flask(__name__)

# config
app.config.update(SECRET_KEY = config.SECRET_KEY)


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def expire_verifi_code(email):
    db = psycopg2.connect(
         database = config.PSQL_DB_NAME,
         user = config.PSQL_USERNAME, 
         password = config.PSQL_PASSWORD, 
         host = config.PSQL_HOST, 
         port = config.PSQL_PORT)
    cur = db.cursor() 
    cur.execute("select * from users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
    email_exist = bool(cur.rowcount)
    if email_exist:
        cur.execute("select id from users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_id = cur.fetchall()
        usr_id = usr_id[0][0]
        cur.execute("UPDATE users SET token='' WHERE ID=%s;" % (usr_id,))
    else:
        flash('Your Email Not Exist Please Sign Up Frist')
    db.commit()
    db.close()



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
        db = psycopg2.connect(
         database = config.PSQL_DB_NAME,
         user = config.PSQL_USERNAME, 
         password = config.PSQL_PASSWORD, 
         host = config.PSQL_HOST, 
         port = config.PSQL_PORT)
        cur = db.cursor() 
        
        emailaddress = request.form['emailaddress']
        password = request.form['password'] 

        cur.execute("select * from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
        email_exist = bool(cur.rowcount)
        
        if email_exist:
            cur.execute("SELECT * FROM users WHERE email='%s' AND password is NOT NULL AND password = crypt('%s',password);" % (emailaddress,password))
            usr_pass = bool(cur.rowcount)

            cur.execute("select register from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
            usr_register = cur.fetchall()
            usr_register = usr_register[0][0]
            
            cur.execute("select id from users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
            usr_id = cur.fetchall()
            usr_id = usr_id[0][0]

            user = User(usr_id)

        if email_exist and usr_pass and usr_register:# TODO add massege for wrong password or not register account
            login_user(user)
            return redirect('/dash')
        else:
            return abort(401)

        db.commit()
        db.close()
        
    else:
        return render_template('admin/login.html')
    

@app.route("/signup", methods=["GET", "POST"])
def signup(): 
    db = psycopg2.connect(
     database = config.PSQL_DB_NAME,
     user = config.PSQL_USERNAME, 
     password = config.PSQL_PASSWORD, 
     host = config.PSQL_HOST, 
     port = config.PSQL_PORT)
    cur = db.cursor() 
    
    if request.method == 'POST':

        verify_code = randint(100000, 999999)
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        emailadd = request.form['emailaddress']
        password = request.form['password']
               
        cur.execute("select * from users where to_tsvector(email) @@ to_tsquery(%s);", (emailadd,))
        email_exist = bool(cur.rowcount)
        if email_exist:
            flash(u'Your Email have exist!','info')
        else:
            
            cur.execute("INSERT INTO users(FIRSTNAME, LASTNAME, EMAIL, PASSWORD, REGISTER, TOKEN) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), 'f', %s)", (firstname, lastname, emailadd, password, verify_code) )
            # register_email(firstname, lastname, emailadd, verify_code)
            flash(u'Your Acconte Sucssesfuly Created','info')
            flash(u'Please Check Your Email Inbox','info')
            db.commit()
            db.close()
            email = request.form.get('emailaddress')
            return redirect(url_for('register', email=email))
            
    db.close()
    return render_template('admin/signup.html')   

@app.route('/register', methods=["GET", "POST"])

def register(): 
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
    db = psycopg2.connect(
     database = config.PSQL_DB_NAME,
     user = config.PSQL_USERNAME, 
     password = config.PSQL_PASSWORD, 
     host = config.PSQL_HOST, 
     port = config.PSQL_PORT)
    cur = db.cursor() 
    email = request.args.get('email')
    new_code = request.args.get('code')

    if new_code == 'new':
        verify_code_generator(email)
        return redirect(url_for('register', email=email))

    if email != None:
        cur.execute("select register from users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_register = cur.fetchall()
        usr_register = usr_register[0][0]
        r.incr(email)
        counter = int(r.get(email))
        
        if not usr_register:

            
            if counter <= 5:

                cur.execute("select * from users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
                email_exist = bool(cur.rowcount)
                
                if request.method == 'POST':
                    verify_code = request.form['verifycode']

                    if email_exist:
                        cur.execute("select token from users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
                        usr_token = cur.fetchall()
                        usr_token = usr_token[0][0]
                        usr_token = usr_token.replace(' ','')#TODO: add checker exist token
                        if usr_token == verify_code:
                            cur.execute("select id from users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
                            usr_id = cur.fetchall()
                            usr_id = usr_id[0][0]
                            cur.execute("UPDATE users SET register='t' WHERE ID=%s;" % (usr_id,))
                            flash('Your Account Registered')
                            db.commit()
                            db.close()
                            r.delete(email)
                            return redirect(url_for('login'))
                        else:
                            flash('Your Verify Code Not Valid!')


                    else:
                        flash('Your Email Not Valid!')
                    # else:
                    #     cur.execute("UPDATE users SET token='' WHERE ID=%s;" % (usr_id,))
                    #     flash('Your Verify Code Is Expire!')
                

            else:
                flash(u'expire code')
                expire_verifi_code(email)
                r.delete(email)


            db.commit()
            db.close()
        else:

            flash('Your Account Registered Please Login')

            return redirect(url_for('login'))
        
        email = urllib.parse.quote(email)


    return render_template('admin/register.html',email=email)


    


@app.route("/forgot-pass")
def forgot_pass():

    return render_template('admin/forgot-password.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/dash')

# @app.route('/new-code', methods=["GET", "POST"])

    
@app.errorhandler(429)
def ratelimit_handler(e):
    # db = psycopg2.connect(
    #  database = config.PSQL_DB_NAME,
    #  user = config.PSQL_USERNAME, 
    #  password = config.PSQL_PASSWORD, 
    #  host = config.PSQL_HOST, 
    #  port = config.PSQL_PORT)
    # cur = db.cursor()
    # cur.execute("UPDATE users SET register='t' WHERE ID=%s;" % (usr_id,)) 

    flash('your verify code is expirre!')
    return render_template('admin/register.html')
    # make_response(
    #         jsonify(error="ratelimit exceeded %s" % e.description)
    #         , 429
    # )

# handle page not found
@app.errorhandler(404)
def page_not_found(e):
    
    return render_template('admin/404.html')


# handle login failed
@app.errorhandler(401)
def login_failed(e):
    
    flash('your username or password is faild!', 'info')
    return redirect('/login')

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == '__main__':
    app.run('0.0.0.0' ,'5000' ,debug=True)