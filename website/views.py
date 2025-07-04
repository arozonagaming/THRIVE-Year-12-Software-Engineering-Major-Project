from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import Plant, User
from . import db
import os
import json

views = Blueprint('views', __name__)

def load_plant_data():
    plants_json = os.path.join(current_app.root_path, 'static', 'plants.json')
    with open(plants_json, 'r') as file:
        return json.load(file)

@views.route('/landing')
def landing():
    return render_template("landing.html")

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    plant_data = load_plant_data()
    plant_user = current_user.plant_name.lower()
    for plant in plant_data:
        if plant["common_name"].lower() == plant_user:
            return render_template("home.html", user=current_user, plant_data=plant)

@views.route('/about_plant')
def about_plants():
    plant_data = load_plant_data()
    plant_user = current_user.plant_name.lower()
    for plant in plant_data:
        if plant["common_name"].lower() == plant_user:
            return render_template("about_plant.html", user=current_user, plant_data=plant)

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        plant_searching = request.form.get('search')

        # Basic email validation
        if "@" not in email or "." not in email or len(email) < 7:
            flash("Email must be valid.", category='error')
            return render_template("settings.html", user=current_user)

        # Check if email is taken by someone else
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash("Email already exists.", category='error')
            return render_template("settings.html", user=current_user)

        # Password validation if changing password
        if password:
            special_chars = ['!', '@', '#', '$', '%']
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in special_chars for c in password)

            if len(password) < 8:
                flash("Password must be at least 8 characters long.", category='error')
            elif not (has_upper and has_lower and has_digit and has_special):
                flash("Password must include upper, lower, digit, and special character (!, @, #, $, %).", category='error')
            else:
                current_user.password = generate_password_hash(password, method='pbkdf2:sha256')

        # Update other user details
        if email != "":
            current_user.email = email
        if first_name != "":
            current_user.first_name = first_name
        if last_name != "":
            current_user.last_name = last_name
        current_user.plant_name = plant_searching
        db.session.commit()
        flash("Settings updated successfully.", category='success')

    return render_template("settings.html", user=current_user)

@views.route('/search_plant', methods=['POST'])
def search_plant():
    if request.method == 'POST':
        plant_searching = request.form.get('search').lower()
        json_path = os.path.join(current_app.root_path, 'static', 'plants.json')

        with open(json_path, 'r') as file:
            plant_data = json.load(file)

        display_plants = [
            plant for plant in plant_data
            if plant['common_name'].lower().startswith(plant_searching)
        ]

        print(plant_searching)

        return jsonify(display_plants)

@views.route('/system', methods=['GET', 'POST'])
@login_required
def system():
    plant_data = load_plant_data()
    user_plants = Plant.query.filter_by(user_id=current_user.id).first_or_404()
    plant_user = current_user.plant_name.lower()
    for plant in plant_data:
        if plant["common_name"].lower() == plant_user:
            temperature_min = plant['min_temp_celsius']
            temperature_max = plant['max_temp_celsius']
            soil_moisture_min = 50  # Example threshold, adjust as needed
            water_interval_days = plant["water_interval_days"]  # Example interval, adjust as needed

    if user_plants.system_status == "Not Connected":
        return jsonify({ "redirect": url_for('views.not_connected') })
    elif user_plants.last_watered is None or (datetime.now() - user_plants.last_watered).days >= water_interval_days:
        user_plants.plant_status = "Plant Need Watering"
    elif user_plants.temperature > temperature_max or user_plants.temperature < temperature_min:
        user_plants.plant_status = "Temperature Out Of Range"
    elif user_plants.soil_moisture < soil_moisture_min:
        user_plants.plant_status = "Soil Moisture Low"
    else:
        user_plants.plant_status = "Good"

    return jsonify({
        "last_watered": user_plants.last_watered.strftime("%H:%M, %m/%d/%Y") if user_plants.last_watered else None,
        "soil_moisture": user_plants.soil_moisture,
        "temperature": user_plants.temperature,
        "system_status": user_plants.system_status,
        "plant_status": user_plants.plant_status
    })

@views.route('/not_connected', methods=['GET', 'POST'])
def not_connected():
    if request.method == 'POST':
        user_plants = Plant.query.filter_by(user_id=current_user.id).first_or_404()
        if user_plants.system_status == "Not Connected":
            flash('System not connected', category='error')
        else:
            return redirect(url_for('views.home'))
    return render_template("not_connected.html", user=current_user)

@views.route('/water_plant', methods=['POST'])
@login_required
def water_plant():
    plant = Plant.query.filter_by(user_id=current_user.id).first_or_404()
    plant.last_watered = datetime.now()
    db.session.commit()
    return redirect(url_for('views.home'))