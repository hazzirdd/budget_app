from server_folder import app, db
from server_folder.model import Expense, User, Category, ExpenseCategory

import requests
import datetime
from flask import Flask, redirect, render_template, request, url_for, session, flash
from werkzeug.utils import secure_filename

@app.route('/')
def homepage():

    user = User.query.get(1)

    return render_template('homepage.html', user=user)




if __name__ == '__main__':
    app.run(debug=True)