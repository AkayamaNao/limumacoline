from flask_sqlalchemy import SQLAlchemy as SA


class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        SA.apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(63), nullable=False, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    option = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    __tablename__ = 'orders'
    date = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.String(63), nullable=False, primary_key=True)
    type = db.Column(db.String(63), nullable=False, primary_key=True)  # order or delivery or exemption or bonus
    menu = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    collected = db.Column(db.Integer, nullable=False, default=0)
