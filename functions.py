from server_folder.model import Bill, Category, User

from flask import session

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

    remainder = user.budget
    for category in categories:
        remainder -= category.limit

    for bill in bills:
        remainder -= bill.amount

    if remainder >= 1:
        budget_color = 'green'
    else:
        budget_color = 'red'

    return remainder, budget_color