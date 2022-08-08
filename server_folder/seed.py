from model import connect_to_db, db, Expense, User, Category, ExpenseCategory

from datetime import datetime


def create_user():
    print('Users')
    User.query.delete()

    user1 = User(email='user@example.com', password='123', first_name='John', last_name='Smith')

    db.session.add(user1)

def create_category():
    print('Categories')
    Category.query.delete()

    category1 = Category(color='#FF0000', title='Groceries', user_id=1)

    db.session.add(category1)

def create_expense():
    print('Expenses')
    Expense.query.delete()

    expense1 = Expense(name='Groceries', location='Target', amount=68.09, date=datetime.now(), category_id=1, user_id=1)

    db.session.add(expense1)

def create_expense_category():
    print('Expense Category')
    ExpenseCategory.query.delete()

    ec1 = ExpenseCategory(expense_id=1, category_id=1)

    db.session.add(ec1)


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    connect_to_db(app)

    db.create_all()

    create_user()
    create_category()
    create_expense()
    create_expense_category()

    db.session.commit()