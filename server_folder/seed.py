from unicodedata import category
from model import connect_to_db, db, Expense, User, Category, ExpenseCategory, Bill

from datetime import datetime


def create_user():
    print('Users')
    User.query.delete()

    user1 = User(email='user@example.com', password='123', first_name='John', last_name='Smith', budget=0.00, bill_color='#955525')

    db.session.add(user1)

def create_category():
    print('Categories')
    Category.query.delete()

    category1 = Category(color='#FF0000', title='Groceries', limit=200.00, user_id=1)
    category2 = Category(color='#004CFF', title='Entertainment', limit=75.00, user_id=1)
    category3 = Category(color='#3BB113', title='Gas', limit=100.00, user_id=1)

    db.session.add(category1)
    db.session.add(category2)
    db.session.add(category3)

def create_expense():
    print('Expenses')
    Expense.query.delete()

    expense1 = Expense(name='Groceries', location='Target', amount=68.09, date=datetime.now(), category_id=1, user_id=1)
    expense2 = Expense(name="Harmon's Fuel", location='Harmons', amount=88.50, date=datetime.now(), category_id=3, user_id=1)

    db.session.add(expense1)
    db.session.add(expense2)

def create_expense_category():
    print('Expense Category')
    ExpenseCategory.query.delete()

    ec1 = ExpenseCategory(expense_id=1, category_id=1)

    db.session.add(ec1)

def create_bill():
    print('Bill')
    Bill.query.delete()

    bill1 = Bill(name="Rent", amount=1350.00, payed=False, user_id=1)
    bill2 = Bill(name="Sonata Insurance", amount=160.00, payed=False, user_id=1)
    bill3 = Bill(name="Sonata Payment", amount=250.00, payed=False, user_id=1)
    bill4 = Bill(name="IPhone", amount=68.00, payed=False, user_id=1)

    db.session.add(bill1)
    db.session.add(bill2)
    db.session.add(bill3)
    db.session.add(bill4)


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    connect_to_db(app)

    db.create_all()

    create_user()
    create_category()
    create_expense()
    create_expense_category()
    create_bill()

    db.session.commit()