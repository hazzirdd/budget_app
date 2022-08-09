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


@app.route('/add_expense', methods=['POST', 'GET'])
def add_expense():
    categories = Category.query.all()
    if request.method == 'GET':
        return render_template('add_expense.html', categories=categories)
    else:

        location = request.form['location']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        print(f'{location} / {amount} / {category} / {date}')

        return render_template('add_expense.html', categories=categories)
    

@app.route('/my_budget', methods=['POST', 'GET'])
def my_budget():
    categories = Category.query.all()
    if request.method == 'GET':
        return render_template('my_budget.html', categories=categories)
    else:

        category = request.form['category']
        amount = request.form['amount']
        color = request.form['color']
        id = request.form['id']

        print(f"category: {category} amount: {amount} color: {color} id: {id}")

        return render_template('my_budget.html', categories=categories)
    
@app.route('/spending', methods=['POST', 'GET'])
def spending():
    if request.method == 'GET':

        expenses = Expense.query.all()

        return render_template('spending.html', expenses=expenses)



if __name__ == '__main__':
    app.run(debug=True)