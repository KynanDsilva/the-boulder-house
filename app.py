<<<<<<< HEAD
from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = 'kynandsilva06@gmail.com'     # ← your e-mail
app.config['MAIL_PASSWORD']   = 'nlho npvy ukzu dmyr' # ← Gmail App Password
mail = Mail(app)
BOOKINGS_FILE = 'bookings.txt'

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_card_number(card_number):
    # Remove spaces and dashes
    card_number = card_number.replace(' ', '').replace('-', '')
    # Check if it's a valid card number (basic validation)
    return card_number.isdigit() and len(card_number) >= 13 and len(card_number) <= 19

def validate_expiry_date(expiry_date):
    pattern = r'^(0[1-9]|1[0-2])/([0-9]{2})$'
    if not re.match(pattern, expiry_date):
        return False
    
    # Check if the card is expired
    month, year = expiry_date.split('/')
    current_year = datetime.now().year % 100
    current_month = datetime.now().month
    
    if int(year) < current_year or (int(year) == current_year and int(month) < current_month):
        return False
    
    return True

@app.route('/')
def home():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', current_year=datetime.now().year)

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        # Store booking details in session
        session['check_in'] = request.form.get('check_in')
        session['check_out'] = request.form.get('check_out')
        session['adults'] = request.form.get('adults')
        session['children'] = request.form.get('children')
        
        # Validate the booking details
        if not all([session['check_in'], session['check_out'], session['adults']]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('book'))
        
        return redirect(url_for('rooms'))
    
    return render_template('book.html', current_year=datetime.now().year)

@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if request.method == 'POST':
        # Store room details in session
        room_id = request.form['room_id']
        extra = int(request.form.get('extra', 0))
        adults = int(session.get('adults', 1))
        children = int(session.get('children', 0))
        total_people = adults + children + extra

        # Pricing table
        price_map = {
            'boulder': 7500,
            'eco': 7500,
            'scenic': 8000,
            'full': 23000
        }

        base = price_map[room_id]
        if room_id != 'full':
            base += extra * 1500
        session['room_id'] = room_id
        session['room_name'] = {
            'boulder': 'Boulder Room',
            'eco': 'Eco Room',
            'scenic': 'Scenic Room',
            'full': 'Full House'
        }[room_id]
        session['total_price'] = base
        return redirect(url_for('reservation'))

    return render_template('rooms.html',
                           adults=int(session.get('adults', 1)),
                           children=int(session.get('children', 0)))

@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    # Check if booking details exist in session
    if not all(key in session for key in ['check_in', 'check_out', 'adults']):
        flash('Please complete the booking details first', 'error')
        return redirect(url_for('book'))

    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        terms = request.form.get('terms')

        # Validate form data
        errors = []

        if not full_name:
            errors.append('Full name is required')

        if not email or not validate_email(email):
            errors.append('Valid email is required')

        if not phone or not validate_phone(phone):
            errors.append('Valid phone number is required')

        if not terms:
            errors.append('You must agree to the terms and conditions')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('reservation.html',
                                   current_year=datetime.now().year,
                                   check_in_date=session['check_in'],
                                   check_out_date=session['check_out'],
                                   adults=session['adults'],
                                   children=session.get('children', '0'),
                                   room_name=session.get('room_name', ''),
                                   total_price=session.get('total_price', 0))

        # Process the booking (in a real application, you would save to database here)
        # For now, we'll just clear the session and show a success message
        session.clear()
        flash('Booking request submitted! We will contact you shortly with confirmation details.', 'success')
        return redirect(url_for('home'))

    return render_template('reservation.html',
                           current_year=datetime.now().year,
                           check_in_date=session['check_in'],
                           check_out_date=session['check_out'],
                           adults=session['adults'],
                           children=session.get('children', '0'),
                           room_name=session.get('room_name', ''),
                           total_price=session.get('total_price', 0))

@app.route('/sent-message', methods=['POST'])
def send_message():
    name    = request.form.get('name', '').strip()
    email   = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    consent = request.form.get('consent')

    if not all([name, email, message]) or not consent:
        return "All fields are required and you must consent.", 400

    msg = Message(
    subject=f"Boulder House inquiry from {name}",
    sender=app.config['MAIL_USERNAME'],        # your own Gmail (must match MAIL_USERNAME)
    recipients=[app.config['MAIL_USERNAME']],  # where YOU receive it
    reply_to=email,                 # where replies should go
    body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    )

    mail.send(msg)
    print("Mail sent to:", msg.recipients)
    print("Subject:", msg.subject)
    print("Body:", msg.body)

    return render_template_string("""
    <!doctype html>
    <title>Thank You | The Boulder House</title>
    <meta http-equiv="refresh" content="2;url={{ url_for('home') }}">
    <link rel="shortcut icon" href="{{ url_for('static', filename='images/favicon.ico') }}" type="image/x-icon">
    <style>
        body{font-family:Roboto,system-ui,sans-serif;background:#f4f6f9;color:#333;text-align:center;padding:10%}
        h1{color:#686463}
        a{color:#a68164;text-decoration:none;font-weight:600}
    </style>
    <h1>Thanks, {{ name }}!</h1>
    <p>We've received your message and will reply soon.</p>
    <p><a href="{{ url_for('home') }}">← Back to Home</a></p>
    """, name=name)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/callback', methods=['POST'])
def callback():
    name = request.form['name']
    phone = request.form['phone']
    message = f"Callback requested by {name}, phone {phone}"
    msg = Message(subject="Callback Request", sender=app.config['MAIL_USERNAME'], recipients=[app.config['MAIL_USERNAME']], body=message)
    mail.send(msg)

#---------- Booking logic ----------
def date_range(start, end):
    start = datetime.strptime(start, '%d/%m/%Y')
    end = datetime.strptime(end, '%d/%m/%Y')
    return [(start + timedelta(days=i)).strftime('%d/%m/%Y') for i in range((end - start).days + 1)]

def is_available(check_in, check_out):
    if not os.path.exists(BOOKINGS_FILE):
        return True
    with open(BOOKINGS_FILE) as f:
        for line in f:
            parts = line.strip().split(' | ')
            booked_dates = date_range(parts[0], parts[1])
            if set(date_range(check_in, check_out)).intersection(booked_dates):
                return False
            
    return True

def save_booking(check_in, check_out, adults, children, name, email):
    with open(BOOKINGS_FILE, 'a') as f:
        f.write(f"{check_in} | {check_out} | {adults} | {children} | {name} | {email}\n")

@app.route('/confirm', methods=['POST'])
def confirm():
    # --- pull data ---
    check_in  = session.get('check_in')
    check_out = session.get('check_out')
    adults    = session.get('adults')
    children  = session.get('children', '0')
    name      = request.form.get('full_name')
    email     = request.form.get('email')
    room      = session.get('room_id')
    phone     = request.form.get('phone')

    # --- explicit missing-field check ---
    missing = []
    for k in ('check_in', 'check_out', 'adults'):
        if not session.get(k):
            missing.append(k)
    if not name:
        missing.append('full_name')
    if not email:
        missing.append('email')

    if missing:
        flash(f'Missing: {", ".join(missing)}', 'error')
        return redirect(url_for('book'))

    # --- availability check ---
    if not is_available(check_in, check_out):
        flash('Sorry, we are booked for those days', 'error')
        return redirect(url_for('book'))

    # --- save booking ---
    with open(BOOKINGS_FILE, 'a') as f:
        f.write(f"{check_in} | {check_out} | {adults} | {children} | {name} | {email} | {phone} | {room}\n")

    # --- popup details ---
    # inside confirm()
    session['booking_details'] = {
    'name': name,
    'check_in': check_in,
    'check_out': check_out,
    'room': session.get('room_name'),
    'price': session.get('total_price'),
    }
    flash('booking_ok', 'success')   # keeps the old message

    # --- confirmation email (optional) ---
    msg = Message(
        subject=f"New booking {check_in} to {check_out}",
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['MAIL_USERNAME']],
        body=f"Name: {name}\nEmail: {email}\nPhone Number: {phone}\nAdults: {adults}\nChildren: {children}\nRoom: {room}\nCheck-in: {check_in}\nCheck-out: {check_out}\nTotal Price: {session['total_price']}"
    )
    mail.send(msg)

    return redirect(url_for('booking_details'))

@app.route('/api/check')
def api_check():
    check_in = request.args.get('in')
    check_out = request.args.get('out')
    if not (check_in and check_out):
        return {'available': False, 'reason': 'Missing dates'}, 400
    try:
        available = is_available(check_in, check_out)
        return {'available': available}
    except Exception as e:
        return {'available': False, 'reason': str(e)}, 400

@app.route('/booking-details')
def booking_details():
    booking_details = session.pop('booking_details', {})
    if not booking_details:
        flash('No booking details found.', 'error')
        return redirect(url_for('home'))
    
    return render_template('booking-details.html', 
                           booking_details=booking_details, 
                           current_year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html', current_year=datetime.now().year)

@app.route('/book', methods=['GET', 'POST'])
def book():
    return render_template('book.html', current_year=datetime.now().year)

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> d84eb2004362abffdf306682fba8be5d0d842fef
