from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    loans = db.relationship('Loan', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.name}>'

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term = db.Column(db.Integer, nullable=False)  # in months
    start_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active, Paid, Defaulted
    purpose = db.Column(db.String(200))
    payments = db.relationship('Payment', backref='loan', lazy=True)

    def monthly_payment(self):
        # Calculate monthly payment using simple interest formula
        monthly_rate = self.interest_rate / 100 / 12
        return (self.amount * monthly_rate) / (1 - (1 + monthly_rate) ** -self.term)

    def remaining_balance(self):
        total_paid = sum(payment.amount for payment in self.payments)
        return self.amount - total_paid

    def __repr__(self):
        return f'<Loan {self.id} - {self.customer.name}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50))
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<Payment {self.id} for Loan {self.loan_id}>'