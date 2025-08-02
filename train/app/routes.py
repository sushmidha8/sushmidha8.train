from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Train, Schedule, Booking, User
from datetime import datetime
import time
import random
import string

bp = Blueprint('main', __name__)

def generate_pnr():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        date = request.form.get('date')
        
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        schedules = Schedule.query.join(Train).filter(
            Train.source == source,
            Train.destination == destination,
            db.func.date(Schedule.departure) == date_obj.date()
        ).all()
        
        results = []
        for schedule in schedules:
            confirmed_bookings = sum(b.seats for b in schedule.bookings if b.status == 'confirmed')
            available_seats = schedule.train.total_seats - confirmed_bookings
            
            results.append({
                'id': schedule.id,
                'train_name': schedule.train.name,
                'departure': schedule.departure.strftime('%H:%M'),
                'arrival': schedule.arrival.strftime('%H:%M'),
                'price': schedule.price,
                'available_seats': available_seats
            })
        
        return render_template('search.html', trains=results, 
                             source=source, destination=destination, date=date)
    
    return redirect(url_for('main.index'))

@bp.route('/book/<int:schedule_id>', methods=['GET', 'POST'])
def book(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    
    if request.method == 'POST':
        seats = int(request.form.get('seats'))
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Check seat availability
        confirmed_bookings = sum(b.seats for b in schedule.bookings if b.status == 'confirmed')
        available_seats = schedule.train.total_seats - confirmed_bookings
        
        if seats > available_seats:
            flash('Not enough seats available', 'danger')
            return redirect(url_for('main.search'))
        
        # Create or get user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=name, email=email)
            db.session.add(user)
            db.session.commit()
        
        # Create booking
        booking = Booking(
            schedule_id=schedule.id,
            user_id=user.id,
            seats=seats,
            pnr=generate_pnr()
        )
        db.session.add(booking)
        db.session.commit()
        
        flash(f'Booking successful! Your PNR is {booking.pnr}', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('booking.html', schedule=schedule)

@bp.route('/api/trains')
def get_trains():
    trains = Train.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'source': t.source,
        'destination': t.destination
    } for t in trains])

# Admin routes
@bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/admin/trains')
def admin_trains():
    trains = Train.query.all()
    return render_template('admin/trains.html', trains=trains)

@bp.route('/admin/schedules')
def admin_schedules():
    schedules = Schedule.query.join(Train).all()
    return render_template('admin/schedules.html', schedules=schedules)