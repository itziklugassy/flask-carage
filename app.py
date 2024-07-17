from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
import os
from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from models.car import Car
    from models.user import User

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists')
            else:
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful. Please log in.')
                return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/')
    @login_required
    def home():
        cars = Car.query.all()
        return render_template('home.html', cars=cars)

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_car():
        if request.method == 'POST':
            car_number = request.form.get('car_number')
            description = request.form.get('description')
            image = request.files.get('image')
            
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = None

            new_car = Car(car_number=car_number, description=description, image=filename)
            db.session.add(new_car)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('add_car.html')

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_car(id):
        car = Car.query.get_or_404(id)
        if request.method == 'POST':
            car.car_number = request.form.get('car_number')
            car.description = request.form.get('description')
            
            image = request.files.get('image')
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                car.image = filename

            db.session.commit()
            return redirect(url_for('home'))
        return render_template('edit_car.html', car=car)

    @app.route('/delete/<int:id>')
    @login_required
    def delete_car(id):
        car = Car.query.get_or_404(id)
        db.session.delete(car)
        db.session.commit()
        return redirect(url_for('home'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)