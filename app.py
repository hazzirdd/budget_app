from server_folder import app, db
from server_folder.model import Expense, User, Category, ExpenseCategory, Bill

import requests
import datetime
from flask import Flask, redirect, render_template, request, url_for, session, flash
from werkzeug.utils import secure_filename

@app.route('/')
def homepage():
    if "user" in session:
        user = User.query.get(session["user"])
        all_categories = Category.query.order_by(Category.limit.desc()).all()
        bills = Bill.query.filter(Bill.user_id == session["user"]).all()
        categories = []
        limits = []

        categories_dict = {}

        for category in all_categories:
            if category not in categories and category.user_id == session["user"]:
                categories.append(category)
                limits.append(category.limit)

                categories_dict[category.category_id] = category.limit

        expenses = Expense.query.filter(Expense.user_id == session["user"]).all()
        print(categories_dict)

        for key, value in categories_dict.items():
            for expense in expenses:
                if expense.category_id == key:
                    categories_dict[key] -= expense.amount

        print(categories_dict)

        return render_template('homepage.html', user=user, categories=categories, categories_dict=categories_dict, bills=bills, bill_color=user.bill_color)
    else:
        return redirect(url_for("logout"))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        users = User.query.all()

        for user in users:
            if user.email == email and user.password == password:
                session["user"] = user.user_id
                return render_template('homepage.html', user=user)

    flash("Incorrect login", "danger")
    return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"Successfully logged out", 'success')
        session.pop("user", None)

    return redirect(url_for('login'))


@app.route('/add_expense', methods=['POST', 'GET'])
def add_expense():
    if "user" in session:
        categories = Category.query.filter(Category.user_id == session["user"]).all()
        if request.method == 'GET':
            return render_template('add_expense.html', categories=categories)
        else:

            location = request.form['location']
            amount = request.form['amount']
            category = request.form['category']
            date = request.form['date']

            print(f'{location} / {amount} / {category} / {date}')

            return render_template('add_expense.html', categories=categories)
    else:
        return redirect(url_for("logout"))

@app.route('/spending', methods=['POST', 'GET'])
def spending():
    if "user" in session:
        if request.method == 'GET':

            expenses = Expense.query.filter(Expense.user_id == session["user"]).all()

            return render_template('spending.html', expenses=expenses)
    else:
        return redirect(url_for("logout"))


@app.route('/my_budget', methods=['POST', 'GET'])
def my_budget():
    if "user" in session:
        user = User.query.get(session["user"])
        all_categories = Category.query.order_by(Category.limit.desc()).all()
        categories = []
        for category in all_categories:
            if category not in categories and category.user_id == session["user"]:
                categories.append(category)

        remainder = user.budget
        for category in categories:
            remainder -= category.limit

        if remainder >= 1:
            budget_color = 'green'
        else:
            budget_color = 'red'

        if request.method == 'GET':
            return render_template('my_budget.html', categories=categories, user=user, remainder=remainder, budget_color=budget_color)
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

            return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))


@app.route('/update_budget', methods=['POST', 'GET'])
def update_budget():
    if "user" in session:
        if request.method == 'POST':
            new_budget = request.form['new_budget']

            user = User.query.get(session["user"])
            user.budget = new_budget
            db.session.commit()

            return redirect(url_for('my_budget'))
        else:
            return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))

@app.route('/new_category', methods=['POST', 'GET'])
def new_category():
    if "user" in session:
        if request.method == 'POST':
            new_title = request.form['new_title']
            new_limit = request.form['new_limit']
            new_color = request.form['new_color']

            new_category = Category(color=new_color, title=new_title, limit=new_limit, user_id=session["user"])
            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('my_budget'))
        else:
            return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))


@app.route('/delete_category/<id>')
def delete_category(id):
    if "user" in session:
        category = Category.query.get(id)
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))


if __name__ == '__main__':
    app.run(debug=True)