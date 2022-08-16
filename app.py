from server_folder import app, db
from server_folder.model import Expense, User, Category, ExpenseCategory, Bill
from functions import certain_month_expenses, find_remainder, find_month_remainder, current_month_expenses, new_month_check

import requests
import datetime
from flask import Flask, redirect, render_template, request, url_for, session, flash
from werkzeug.utils import secure_filename

month_count = 0

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

        all_expenses = Expense.query.order_by(Expense.date.desc()).all()
        expenses = current_month_expenses(all_expenses, user)

        for key, value in categories_dict.items():
            for expense in expenses:
                if expense.category_id == key:
                    categories_dict[key] -= expense.amount

        remainder, budget_color = find_month_remainder(user.user_id)
        new_month_check(user)

        return render_template('homepage.html', user=user, categories=categories, categories_dict=categories_dict, bills=bills, bill_color=user.bill_color, budget_color=budget_color, remainder=remainder)
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
                return redirect(url_for("homepage"))

    flash("Incorrect login", "danger")
    return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"Successfully logged out", 'success')
        session.pop("user", None)

    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        user = User(email=email, password=password, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()

        return render_template('signup.html')


@app.route('/add_expense', methods=['POST', 'GET'])
def add_expense():
    if "user" in session:
        remainder, budget_color = find_month_remainder(session["user"])
        categories = Category.query.filter(Category.user_id == session["user"]).all()
        if request.method == 'GET':
            return render_template('add_expense.html', categories=categories, budget_color=budget_color, remainder=remainder)
        else:
            name = request.form["name"].strip()
            location = request.form["location"].strip()
            amount = request.form['amount']
            date = request.form['date']
            category = request.form['category']

            # HANDLING ERRORS
            name_error = False
            location_error = False
            amount_error = False
            date_error = False
            if name == '':
                name_error = True
            if not location:
                location_error = True
            if not amount:
                amount_error = True
            if not date:
                date_error = True
            if name_error == True or location_error == True or amount_error == True or date_error == True:
                flash("Please enter all fields", "danger")
                return render_template('add_expense.html', categories=categories, budget_color=budget_color, remainder=remainder, name_error=name_error, location_error=location_error, amount_error=amount_error, date_error=date_error)

            expense = Expense(name=name, location=location, amount=amount, date=date, category_id=category, user_id=session['user'])
            db.session.add(expense)
            db.session.commit()

            return redirect(url_for('add_expense'))
    else:
        return redirect(url_for("logout"))

@app.route('/spending', methods=['POST', 'GET'])
def spending():
    if "user" in session:
        if request.method == 'GET':
            user = User.query.get(session["user"])
            expense_dict = {}
            all_expenses = Expense.query.order_by(Expense.date.desc()).all()
            all_bills = Bill.query.order_by(Bill.amount.desc()).all()
            bill_color = user.bill_color
            bills = []
            expenses = current_month_expenses(all_expenses, user)

            # SELECT MONTH EXPENSE VIEW
            # today = date.today().strftime('%m/%d/%Y')
            # month, day, year = today.split('/')
            # expenses_test = certain_month_expenses(all_expenses, user, month, year)

            for bill in all_bills:
                if bill.user_id == session['user']:
                    bills.append(bill)

            for expense in expenses:
                date = expense.date
                date_strip = date.strftime('%m/%d/%Y')
                category = Category.query.get(expense.category_id)
                expense_dict[expense.expense_id] = {
                    "color": category.color,
                    "category": category.title,
                    "name": expense.name,
                    "location": expense.location,
                    "amount": expense.amount,
                    "date": date_strip
                }

            remainder, budget_color = find_month_remainder(user.user_id)

            return render_template('spending.html', expense_dict=expense_dict, bills=bills, bill_color=bill_color, remainder=remainder, budget_color=budget_color)
        else:
            bill_id = request.form['bill_id']
            payed = request.form.getlist('payed')
            if payed:
                payed = True
            else:
                payed = False
            updated_bill = Bill.query.get(bill_id)
            updated_bill.payed = payed
            db.session.commit()

            return redirect(url_for('spending'))
    else:
        return redirect(url_for("logout"))


@app.route('/select_month', methods=['GET', 'POST'])
def select_month():
    if "user" in session:

        date = request.form["date"]
        year, month, day = date.split('-')
        print(year, month)

        return redirect(url_for("spending"))


@app.route('/delete_expense/<id>', methods=['POST', 'GET'])
def delete_expense(id):
    if "user" in session:
        expense = Expense.query.get(id)
        db.session.delete(expense)
        db.session.commit()
        return redirect(url_for("spending"))

@app.route('/my_budget', methods=['POST', 'GET'])
def my_budget():
    if "user" in session:
        user = User.query.get(session["user"])
        all_bills = Bill.query.order_by(Bill.amount.desc()).all()
        all_categories = Category.query.order_by(Category.limit.desc()).all()
        categories = []
        for category in all_categories:
            if category not in categories and category.user_id == session["user"]:
                categories.append(category)
        bills = []
        for bill in all_bills:
            if bill not in bills and bill.user_id == session["user"]:
                bills.append(bill)

        remainder, budget_color = find_remainder(user.user_id)

        if request.method == 'GET':
            return render_template('my_budget.html', categories=categories, user=user, remainder=remainder, budget_color=budget_color, bills=bills, bill_color=user.bill_color)
        else:

            title = request.form['title']
            limit = request.form['limit']
            color = request.form['color']
            id = request.form['id']

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
            new_title = request.form['new_title'].strip()
            new_color = request.form['new_color']
            raw_limit = request.form['new_limit']

            print(raw_limit)
            try:
                new_limit = float(raw_limit)
                print(new_limit)
            except:
                flash("Category limit must be a number (1)", "danger")
                return redirect(url_for('my_budget'))
            
            print(type(new_limit))
            if not isinstance(new_limit, float):
                flash("Category limit must be a number (2)", "danger")
                return redirect(url_for('my_budget'))

            float_limit = "{:.2f}".format(new_limit)
            print(float_limit)

            categories = Category.query.filter(Category.user_id == session["user"]).all()
            if new_title == '':
                flash("Please enter a category title", "danger")
                return redirect(url_for('my_budget'))
            for category in categories:
                if category.title == new_title:
                    flash("Category title already exists", "danger")
                    return redirect(url_for('my_budget'))

            new_category = Category(color=new_color, title=new_title, limit=float_limit, user_id=session["user"])
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
        try:
            db.session.delete(category)
            db.session.commit()
        except:
            flash("Cannot delete category with dependant expenses", "danger")
            return redirect(url_for('my_budget'))
        return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))


@app.route('/update_bill', methods=['POST', 'GET'])
def update_bill():
    if "user" in session:
        if request.method == 'POST':
            bill_name = request.form['bill_name']
            bill_amount = request.form['bill_amount']
            bill_id = request.form['bill_id']
            bill = Bill.query.get(bill_id)
            bill.name = bill_name
            bill.amount = bill_amount

            db.session.commit()

            return redirect(url_for('my_budget'))

@app.route('/new_bill', methods=['POST', 'GET'])
def new_bill():
    if "user" in session:
        if request.method == 'POST':
            new_bill_name = request.form['new_bill_name']
            new_bill_amount = request.form['new_bill_amount']

            new_bill = Bill(name=new_bill_name, amount=new_bill_amount, payed=False, user_id=session["user"])

            db.session.add(new_bill)
            db.session.commit()

            return redirect(url_for('my_budget'))
        else:
            return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))


@app.route('/delete_bill/<id>')
def delete_bill(id):
    if "user" in session:
        bill = Bill.query.get(id)
        db.session.delete(bill)
        db.session.commit()
        return redirect(url_for('my_budget'))
    else:
        return redirect(url_for("logout"))

if __name__ == '__main__':
    app.run(debug=True)