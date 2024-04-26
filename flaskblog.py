from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Change the URI as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)# Replace with a secure secret key

#app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'tarzanmutuku@gmail.com'
app.config['MAIL_PASSWORD'] = 'TarzanJobs@2023!'  # Replace with your actual Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'mutukutarzan2@gmail.com'

mail = Mail(app)
# SQLAlchemy configuration


# Sample user data (in practice, this should come from a database)
users = {}

# User model for SQLAlchemy
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# Menu items and prices (in Kenyan Shillings)
menu_items = {
    'Pilau': 120,
    'chips': 100,
    'Chips masala': 150,
    'chapati': 30,
    'Beans': 50,
    'Beaf stew': 100,
    'Beef dry fry': 100,
    'Matumbo': 100,
    '1/4 Spicy chicken': 200,
    'ugali': 50,
    'rice': 60,
    'Coffee': 70,
    'Tea': 30,
    'Mahamri': 20,
    # Add more items as needed
}

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match a user in the sample data
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Set a session variable to track the user's login status
            session['logged_in'] = True
            session['selected_items'] = {}  # Initialize session variable for selected items
            return redirect(url_for('menu'))  # Redirect to the menu page after a successful login
        else:
            return render_template('login.html', error_message='Invalid credentials')  # Render the login page with an error message

    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return 'Welcome to the dashboard!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error_message='Username already exists')

        # Create a new user instance
        new_user = User(username=username, password=password)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        session['selected_items'] = {}  # Initialize session variable for selected items
        return redirect(url_for('menu'))  # Redirect to the menu page after a successful registration

    return render_template('register.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if request.method == 'POST':
        for item, price in menu_items.items():
            quantity = int(request.form.get(f'{item}_quantity', 0))
            if quantity > 0:
                session['selected_items'][item] = {'quantity': quantity, 'price': price}

        # Extract M-Pesa number from the form
        mpesa_number = request.form.get('mpesa_number')

        # Save the M-Pesa number to the session for later use
        session['mpesa_number'] = mpesa_number

        total_price = calculate_total_price()
        return render_template('menu.html', menu_items=menu_items, selected_items=session['selected_items'], total_price=total_price)

    return render_template('menu.html', menu_items=menu_items, selected_items=session['selected_items'], total_price=calculate_total_price())

def calculate_total_price():
    total_price = 0
    for item, data in session['selected_items'].items():
        total_price += data['price'] * data['quantity']
    return total_price

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle the form submission here
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Your logic for handling the form data
        print("Name:", name)
        print("Email:", email)
        print("Message:", message)

        # Send email
        msg = Message('New Contact Form Submission', recipients=['mutukutarzan2@gmail.com'])
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)

        # Your existing logic...

    return render_template('contact.html')

@app.route('/place_order', methods=['POST'])
def place_order():
    # Handle the order placement logic here
    selected_items = session['selected_items']
    total_price = calculate_total_price()

    # Extract M-Pesa number from the session
    mpesa_number = session.get('mpesa_number')

    # Implement your order placement logic here
    # For example, you can save the order details to a database

    # Clear the selected items and session variables after placing the order
    session['selected_items'] = {}
    session.pop('mpesa_number', None)

    # Send


    # Redirect to a confirmation or thank you page
    return redirect(url_for('order_confirmation',total_price=total_price))

# Add a route for the order confirmation page
@app.route('/order_confirmation')
def order_confirmation():
    total_price = request.args.get('total_price')
    return render_template('order_confirmation.html',total_price=total_price)
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables

    app.run(debug=True)
