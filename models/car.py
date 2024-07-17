from extensions import db

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_number = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(100), nullable=True)

    def __init__(self, car_number, description=None, image=None):
        self.car_number = car_number
        self.description = description
        self.image = image