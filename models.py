from flask_login import UserMixin

# Define User data-model
# class User(DB.Model, UserMixin):
#     __tablename__ = 'users'
#     id = DB.Column(DB.Integer, primary_key=True)

#     # User Authentication fields
#     email = DB.Column(DB.String(255), nullable=False, unique=True)
#     email_confirmed_at = DB.Column(DB.DateTime())
#     username = DB.Column(DB.String(50), nullable=False, unique=True)
#     password = DB.Column(DB.String(255), nullable=False)

#     # User fields
#     active = DB.Column(DB.Boolean()),
#     first_name = DB.Column(DB.String(50), nullable=False)
#     last_name = DB.Column(DB.String(50), nullable=False)

# # Setup Flask-User
# user_manager = UserManager(app, DB, User)

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        # self.name = "user" + str(id)
        # self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d" % (self.id)



