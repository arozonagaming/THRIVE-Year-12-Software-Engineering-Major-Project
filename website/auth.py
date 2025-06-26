from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, session
from .models import User, Plant
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import os
import json

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup',  methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email1 = request.form.get('email')
        password1 = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        special_chars = ['!', '@', '#', '$', '%']
        has_upper = False
        has_lower = False
        has_digit = False
        has_special = False

        for char in password1:
            if char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif char.isdigit():
                has_digit = True
            elif char in special_chars:
                has_special = True
    
        user = User.query.filter_by(email=email1).first()
        if user:
            flash('Email already exists.', category='error')
        elif "@" not in email1 or "." not in email1 or len(email1) < 7:
            flash("Email must be valid.", category='error')
        elif not has_upper:
            flash("Password must include at least one uppercase letter.", category='error')
        elif not has_lower:
            flash("Password must include at least one lowercase letter.", category='error')
        elif not has_digit:
            flash("Password must include at least one number.", category='error')
        elif not has_special:
            flash("Password must include at least one special character from: ['!', '@', '#', '$', '%']", category='error')
        elif len(password1) < 8:
            flash("Password must be at least 8 characters long.", category='error')
        elif password1 != confirm_password:
            flash("Passwords do not match.", category='error')
        else:
            session['email'] = email1
            session['password'] = password1
            return redirect(url_for('auth.user_details'))
        
    return render_template("sign_up.html", user=current_user)

@auth.route('/user_details', methods=['GET', 'POST'])
def user_details():
    email1 = session.get('email')
    password1 = session.get('password')
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        plant_searching = request.form.get('search')
        json_path = os.path.join(current_app.root_path, 'static', 'plants.json')

        with open(json_path, 'r') as file:
            plant_data = json.load(file)
        
        matching_plants = [
            plant for plant in plant_data
            if plant['common_name'].lower() == plant_searching.lower()
        ]

        if matching_plants:
            new_user = User(
                email=email1,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                first_name=firstname,
                last_name=lastname,
                plant_name=plant_searching
            )

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # Log the user in BEFORE accessing current_user

            existing_plant = Plant.query.filter_by(user_id=new_user.id).first()
            if not existing_plant:
                new_plant = Plant(
                    last_watered=None,
                    soil_moisture=0,
                    temperature=0,
                    system_status='Not Connected',
                    plant_status=None,
                    user_id=new_user.id
                )
                db.session.add(new_plant)
                db.session.commit()
            session.pop('email', None)
            session.pop('password', None)
            return redirect(url_for('views.home'))
        else:
            flash("No matching plants found. Try again", category='error')

    return render_template('user_details.html', email=email1, password=password1)


@auth.route('/search_plant', methods=['POST'])
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