import os
from flask import Flask
from .routes import main

secret_key = "b43d0cace4b5e86243cbd55be4aa90988b49893a413e632c" # Replace with a secure random key in production

def create_app():
    app = Flask(__name__)
    app.secret_key = secret_key
    from app import routes  
    app.register_blueprint(main)

    return app
