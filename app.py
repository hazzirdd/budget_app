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
    

@app.route('/spending', methods=['POST', 'GET'])
def spending():
    if request.method == 'GET':

        expenses = Expense.query.all()

        return render_template('spending.html', expenses=expenses)


@app.route('/my_budget', methods=['POST', 'GET'])
def my_budget():
    categories = Category.query.all()
    if request.method == 'GET':
        return render_template('my_budget.html', categories=categories)
    else:

        title = request.form['title']
        limit = request.form['limit']
        color = request.form['color']
        id = request.form['id']

        print(f"category: {title} limit: {limit} color: {color} id: {id}")

        selected_category = Category.query.get(id)
        selected_category.title = title
        selected_category.limit = limit
        selected_category.color = color
        
        db.session.commit()

        return render_template('my_budget.html', categories=categories)


@app.route('/new_category', methods=['POST', 'GET'])
def new_category():
    if request.method == 'POST':
        new_title = request.form['new_title']
        new_limit = request.form['new_limit']
        new_color = request.form['new_color']

        # CHANGE USER ID TO SESSION[ID]
        # THIS IS A TEMPORARY PLACEHOLDER (8/9)
        new_category = Category(color=new_color, title=new_title, limit=new_limit, user_id=1)
        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for('my_budget'))
    else:
        return redirect(url_for('my_budget'))


@app.route('/delete_category/<id>')
def delete_category(id):
    category = Category.query.get(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('my_budget'))


if __name__ == '__main__':
    app.run(debug=True)