from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import config



app = Flask(__name__)

# config
app.config.update(SECRET_KEY = 'secret_xxx' )

 # flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user = User(0)

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



@app.route('/dash')
@login_required
def dash_page():

    return render_template('admin/index.html')



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if username == config.USERNAME and password == config.PASSWORD:
            login_user(user)
            return redirect("/dash")
        else:
            return abort(401)
    else:
        return render_template('admin/login.html')

@app.route("/register")
def register():  

    return render_template('admin/register.html')     


@app.route("/forgot-pass")
def forgot_pass():  

    return render_template('admin/forgot-password.html')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/dash")


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)

if __name__ == '__main__':
    app.run('0.0.0.0' ,'5000' ,debug=True)