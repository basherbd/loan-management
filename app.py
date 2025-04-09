from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Customer, Loan, Payment
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loans.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    loans = Loan.query.all()
    return render_template('index.html', loans=loans)


@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    if request.method == 'POST':
        # Get form data
        customer_name = request.form['customer_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        amount = float(request.form['amount'])
        interest_rate = float(request.form['interest_rate'])
        term = int(request.form['term'])
        purpose = request.form['purpose']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()

        # Check if customer exists or create new
        customer = Customer.query.filter_by(email=email).first()
        if not customer:
            customer = Customer(name=customer_name, email=email, phone=phone, address=address)
            db.session.add(customer)
            db.session.commit()

        # Create loan
        loan = Loan(
            customer_id=customer.id,
            amount=amount,
            interest_rate=interest_rate,
            term=term,
            start_date=start_date,
            purpose=purpose,
            status='Active'
        )
        db.session.add(loan)
        db.session.commit()

        flash('Loan added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_loan.html')


@app.route('/loan/<int:loan_id>')
def view_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    payments = Payment.query.filter_by(loan_id=loan_id).order_by(Payment.payment_date.desc()).all()
    return render_template('view_loan.html', loan=loan, payments=payments)


@app.route('/add_payment/<int:loan_id>', methods=['POST'])
def add_payment(loan_id):
    loan = Loan.query.get_or_404(loan_id)

    amount = float(request.form['amount'])
    payment_date = datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
    payment_method = request.form['payment_method']
    notes = request.form.get('notes', '')

    payment = Payment(
        loan_id=loan_id,
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        notes=notes
    )
    db.session.add(payment)
    db.session.commit()

    flash('Payment recorded successfully!', 'success')
    return redirect(url_for('view_loan', loan_id=loan_id))


@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        # Search by customer name or loan ID
        try:
            loan_id = int(query)
            loans = Loan.query.filter(Loan.id == loan_id).all()
        except ValueError:
            loans = Loan.query.join(Customer).filter(
                Customer.name.ilike(f'%{query}%')
            ).all()
    else:
        loans = []

    return render_template('loans_list.html', loans=loans)


if __name__ == '__main__':
    app.run(debug=True)