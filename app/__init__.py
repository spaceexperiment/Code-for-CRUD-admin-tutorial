# project/__init__.py

from flask import Flask, render_template, request, session
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask('app')
app.config.update(
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///../database.db',
    )
db = SQLAlchemy(app)

from admin import admin
app.register_blueprint(admin, url_prefix='/admin')



@app.route('/')
def home():
    return 'Blog be here'

