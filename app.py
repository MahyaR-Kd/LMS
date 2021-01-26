import redis
import psycopg2
import urllib

from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, abort, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from passlib.hash import sha256_crypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from random import randint
from datetime import timedelta

from email_sender import register_email, welcome_email
from new_code import verify_code_generator
from expire_code import expire_verifi_code
from dashboard import users_edit, user_profile, course_creator, course_remover
from view import users_view, course_excerpt_view, img_slider
from models import User
from werkzeug.utils import secure_filename

import config
import os


app = Flask(__name__)

UPLOAD_FOLDER = '/home/mahyar/W/LMS/LMS/static/courses/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


# config
app.config.update(SECRET_KEY = config.SECRET_KEY)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = 'warning'
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "500 per hour"]
)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

# main site route
@app.route('/')
def main_page():
    result_list = course_excerpt_view()
    course_list = result_list[0]
    return render_template('site/index.html',data = {'course_list':course_list,})

@app.route('/courses')
def course_view():
    result_list = course_excerpt_view()
    course_list = result_list[0]
    ids = result_list[1]
    post_id = request.args.get('id')
    return render_template('site/course_view.html',data = {'course_list':course_list, 'ids':ids, 'id':post_id})


@app.route('/about')
def about_page():

    return render_template('site/about.html')

@app.route('/services')
def services_page():

    return render_template('site/services.html')

@app.route('/contact')
def contact_page():

    return render_template('site/contact.html')

@app.route('/dash')
@login_required
def dash_page():
    user = session.get('User')
    user_roles = session.get('Roles')
    result_list = course_excerpt_view()
    total_course = len(result_list[1])
    # user roles: A = admin , T = teacher , S = student
    if user_roles == 'A':
        user_roles = 'Admin'
        return render_template('admin/admin_dash.html', data = {'user':user,'total_course':total_course})
    if user_roles == 'T':
        user_roles = 'Teacher'
        return render_template('admin/teacher_dash.html', data = {'user':user,'total_course':total_course})
    if user_roles == 'S':
        user_roles = 'Student'
        return render_template('admin/student_dash.html', data = {'user':user,})


@app.route('/dash/create_course', methods=["GET", "POST"])
@login_required
def create_course():
    user_roles = session.get('Roles')
    if user_roles == 'A' or user_roles == 'T':
        user = session.get('User')
        
        path = app.config['UPLOAD_FOLDER']+user

        if not os.path.exists(path):
            path = app.config['UPLOAD_FOLDER']+user

            os.mkdir(path)


        if request.method == 'POST':
            # check if the post request has the file part
            coursetitle = request.form['coursetitle']
            caption = request.form['caption']
            summary = request.form['summary']
            file = request.files['filename']

            # if 'file' not in request.files:
            #     flash('No file part','warning')
            #     return redirect(request.url)
            # # if user does not select file, browser also
            # # submit an empty part without filename
            # if file.filename == '':
            #     flash('No selected file','warning')
            #     return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = path+'/'+filename
                file_exist = os.path.exists(file_path)

                if file_exist:
                    round_name = str(randint(1,34678))+'_'
                    filename =round_name+filename
                    file.save(os.path.join(path, filename))
                else:
                    file.save(os.path.join(path, filename))
 
                file_path = user + '/' + filename
                
                course_creator(user, coursetitle, caption, summary, file_path)
                return redirect(url_for('create_course'))

        return render_template('admin/create_course.html', data = {'user':user})
    else:
        return abort(403)  



@app.route('/dash/all_course', methods=["GET", "POST"])
@login_required
def all_course():
    user_roles = session.get('Roles')
    if user_roles == 'A' or user_roles == 'T':
        user = session.get('User')
        course_id = request.args.get('course-id')
        if course_id != None:
            course_id = int(course_id)
            course_remover(user, course_id)
        print(course_id)
        result_list = course_excerpt_view()
        course_list = result_list[0]
        return render_template('admin/all_course.html', data = {'user':user, 'course_list':course_list})
    else:
        return abort(403)    

@app.route('/dash/users', methods=["GET", "POST"])
@login_required
def users_table():
    user_roles = session.get('Roles')
    if user_roles == 'A':
        user = session.get('User')
        edit_user = request.args.get('edit_user')
        if edit_user:
            changing_user = request.args.get('email')
            if request.method == 'POST':
                user_roles = request.form['user_roles']
                users_edit(changing_user, user_roles)
                flash('Setting Chenged','success')
            return render_template('admin/users_edit.html', data = {'user':user,'changing_user':changing_user})
        user_table = users_view()
        
        return render_template('admin/users_tables.html', data = {'user':user,'user_table':user_table})
    else:
        return abort(403)

# dashboard route
@app.route('/dash/profile', methods=["GET", "POST"])
@login_required
def dash_profile():
    user = session.get('User')

    return render_template('admin/users_profile.html', data = {'user':user})

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

        cur.execute("select * from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
        email_exist = bool(cur.rowcount)
        
        if email_exist:
            cur.execute("SELECT * FROM lms_users WHERE email='%s' AND password is NOT NULL AND password = crypt('%s',password);" % (emailaddress,password))
            usr_pass = bool(cur.rowcount)

            cur.execute("select register from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
            usr_register = cur.fetchall()
            usr_register = usr_register[0][0]
            
            cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
            usr_id = cur.fetchall()
            usr_id = usr_id[0][0]

            user = User(usr_id)

            cur.execute("select user_roles from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (emailaddress,))
            usr_roles = cur.fetchall()
            usr_roles = usr_roles[0][0]

        if email_exist and usr_pass and usr_register:# TODO add massege for wrong password or not register account
            login_user(user)
            session['User'] = emailaddress
            session['Roles'] = usr_roles
            return redirect(url_for('dash_page'))
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
               
        cur.execute("select * from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (emailadd,))
        email_exist = bool(cur.rowcount)
        if email_exist:
            flash(u'Your Email have exist!','warning')
        else:
            
            cur.execute("INSERT INTO lms_users(FIRSTNAME, LASTNAME, EMAIL, PASSWORD, TOKEN) VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), %s)", (firstname, lastname, emailadd, password, verify_code) )
            # register_email(firstname, lastname, emailadd, verify_code)
            flash(u'Your Acconte Sucssesfuly Created','success')
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
        cur.execute("select * from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        email_exist = bool(cur.rowcount)
        if email_exist:
            verify_code_generator(email)
        else:
            flash('Your Email Not Exist Please Sign Up First','warning')
        return redirect(url_for('register', email=email))

    if email != None:
        cur.execute("select register from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
        usr_register = cur.fetchall()
        if usr_register != []:
            usr_register = usr_register[0][0]
        
        if not usr_register:
            counter = r.get(email)
            if counter != None:
                counter = int(counter)
            else:
                r.incr(email)
                counter = r.get(email)
                counter = int(counter)

            if counter <= 5 or counter == None:

                cur.execute("select * from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
                email_exist = bool(cur.rowcount)
                
                if request.method == 'POST':
                    verify_code = request.form['verifycode']
                    r.incr(email)

                    if email_exist:
                        cur.execute("select token from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
                        usr_token = cur.fetchall()
                        usr_token = usr_token[0][0]
                        usr_token = usr_token.replace(' ','')#TODO: add checker exist token
                        if usr_token == verify_code:
                            cur.execute("select id from lms_users where to_tsvector(email) @@ to_tsquery(%s);", (email,))
                            usr_id = cur.fetchall()
                            usr_id = usr_id[0][0]
                            cur.execute("UPDATE lms_users SET register='t' WHERE ID=%s;" % (usr_id,))
                            flash('Your Account Registered','success')
                            db.commit()
                            db.close()
                            r.delete(email)
                            return redirect(url_for('login'))
                        else:
                            flash('Your Verify Code Not Valid!','warning')


                    else:
                        flash('Your Email Not Valid!','warning')
                    # else:
                    #     cur.execute("UPDATE lms_users SET token='' WHERE ID=%s;" % (usr_id,))
                    #     flash('Your Verify Code Is Expire!')
                

            else:
                expire_verifi_code(email)
                r.delete(email)


            db.commit()
            db.close()
        else:

            flash('Your Account Registered Please Login','success')

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
    # cur.execute("UPDATE lms_users SET register='t' WHERE ID=%s;" % (usr_id,)) 

    # flash('your verify code is expirre!')
    return e
    # render_template('admin/register.html')
    # make_response(
    #         jsonify(error="ratelimit exceeded %s" % e.description)
    #         , 429
    # )

# handle page not found
@app.errorhandler(404)
def page_not_found(e):
    
    return render_template('admin/404.html')

@app.errorhandler(403)
def forbidden(e):
    
    return render_template('admin/403.html')

# handle login failed
@app.errorhandler(401)
def login_failed(e):
    
    flash('your username or password is faild!', 'danger')
    return redirect('/login')

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__ == '__main__':
    app.run('0.0.0.0' ,'5000' ,debug=True)