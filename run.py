#!flask/bin/python3
from app import app
from flask import Flask
app.run(host='0.0.0.0',debug=True)