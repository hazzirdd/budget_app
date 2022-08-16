from server_folder.model import Bill, Category, User, Expense
from server_folder import db

from flask import session
from datetime import date

def find_remainder(user_id):
    user = User.query.get(user_id)

    all_bills = Bill.query.order_by(Bill.amount.desc()).all()
    all_categories = Category.query.order_by(Category.limit.desc()).all()
    categories = []
    for category in all_categories:
        if category not in categories and category.user_id == user_id:
            categories.append(category)
    bills = []
    for bill in all_bills:
        if bill not in bills and bill.user_id == user_id:
            bills.append(bill)

    rough_remainder = user.budget
    for category in categories:
        rough_remainder -= category.limit

    for bill in bills:
        rough_remainder -= bill.amount

    if rough_remainder >= 1:
        budget_color = 'green'
    else:
        budget_color = 'red'
    remainder = "{:.2f}".format(rough_remainder)
    return remainder, budget_color


def find_month_remainder(user_id):
    user = User.query.get(user_id)

    all_bills = Bill.query.order_by(Bill.amount.desc()).all()
    all_categories = Category.query.order_by(Category.limit.desc()).all()
    categories = []
    for category in all_categories:
        if category not in categories and category.user_id == user_id:
            categories.append(category)
    bills = []
    for bill in all_bills:
        if bill not in bills and bill.user_id == user_id:
            bills.append(bill)
    
    expenses = current_month_expenses(all_expenses=Expense.query.order_by(Expense.date.desc()).all(), user=user)

    rough_remainder = user.budget
    for expense in expenses:
        rough_remainder -= expense.amount
    for bill in bills:
        if bill.payed == True:
            rough_remainder -= bill.amount

    if rough_remainder >= 1:
        budget_color = 'green'
    else:
        budget_color = 'red'

    remainder = "{:.2f}".format(rough_remainder)

    return remainder, budget_color


def current_month_expenses(all_expenses, user):
    today = date.today().strftime('%m/%d/%Y')
    month, day, year = today.split('/')
    expenses = []

    for expense in all_expenses:
        expense_date = expense.date.strftime('%m/%d/%Y')
        e_month, e_day, e_year = expense_date.split('/')
        if expense.user_id == user.user_id and e_month == month and e_year == year:
            expenses.append(expense)

    return expenses


def certain_month_expenses(all_expenses, user, month, year):
    expenses = []

    for expense in all_expenses:
        expense_date = expense.date.strftime('%m/%d/%Y')
        e_month, e_day, e_year = expense_date.split('/')
        if expense.user_id == user.user_id and e_month == month and e_year == year:
            expenses.append(expense)

    return expenses


def new_month_check(user):
    bills = Bill.query.filter(Bill.user_id == user.user_id).all()
    today = date.today().strftime('%m/%d/%Y')
    month, day, year = today.split('/')

    if day == '28':
        print('The month is ready to reset...')
        user.new_month_switch = False

    if day == '1' and user.new_month_switch == False:
        print("It's a new month!")
        for bill in bills:
            bill.payed = False
        user.new_month_switch = True
    db.session.commit()