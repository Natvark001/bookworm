from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail,Message
#instatiation is done below
csrf=CSRFProtect()
mail=Mail()


def create_app():
    #here all import that may cause infinite recursion is kept. none of the statement is executed
    from bookapp.models import db
    app=Flask(__name__,instance_relative_config=True) #to load config from outside the package
    app.config.from_pyfile('config.py',silent=True)
    db.init_app(app)
    migrate=Migrate(app,db)
    csrf.init_app(app)
    mail.__init__(app)
    return app
    
app=create_app()   
    
#the routes are loaded here below
from bookapp import admin_routes,user_routes
from bookapp.forms import * 
