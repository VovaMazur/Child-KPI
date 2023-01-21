from childkpi import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    pin_hash = db.Column(db.String(60), nullable=False)
    is_parent = db.Column(db.Integer, nullable=False, default=0)

    @property
    def status(self):
        return 'Parent' if self.is_parent else 'Child'

    @property
    def pin(self):
        return self.pin_hash

    @pin.setter
    def pin(self, plain_text_pin):
        self.pin_hash = bcrypt.generate_password_hash(plain_text_pin).decode('utf-8')

    def check_pin(self, attempted_pin):
        return bcrypt.check_password_hash(self.pin_hash, attempted_pin)

    def can_approve(self):
        return self.is_parent


class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    clean = db.Column(db.Integer, default=0)
    clean_comm = db.Column(db.String(30))
    sch = db.Column(db.Integer, default=0)
    sch_comm = db.Column(db.String(30))
    sport = db.Column(db.Integer, default=0)
    sport_type = db.Column(db.String(10))
    sport_comm = db.Column(db.String(30))
    other = db.Column(db.Integer, default=0)
    other_comm = db.Column(db.String(30))
    is_done = db.Column(db.Integer, nullable=False, default=0)
    is_approved = db.Column(db.Integer, nullable=False, default=0)
    amount = db.Column(db.Numeric(), default=0)
    comments = db.Column(db.String(140))