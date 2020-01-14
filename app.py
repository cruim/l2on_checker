from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, Column, Boolean, DateTime, CheckConstraint
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
import bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5433/flask'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True

app.debug = True
db = SQLAlchemy(app)


class Staff(db.Model):
    id = Column(Integer, primary_key=True)
    l2on_id = Column(Integer, unique=True)
    name = Column(String(100), nullable=False)
    grade_id = Column(Integer, ForeignKey('grade.id'))
    type_id = Column(Integer, ForeignKey('type.id'))

class Grade(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    created_on = Column(DateTime, default=db.func.now())
    updated_on = Column(DateTime, default=db.func.now(), onupdate=db.func.now())

class Type(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    created_on = Column(DateTime, default=db.func.now())
    updated_on = Column(DateTime, default=db.func.now(), onupdate=db.func.now())

class Scheduller(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_on = Column(DateTime, default=db.func.now())
    updated_on = Column(DateTime, default=db.func.now(), onupdate=db.func.now())

class GameServer(db.Model):
    id = Column(Integer, primary_key=True)
    l2on_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(20), unique=True, nullable=False)
    created_on = Column(DateTime, default=db.func.now())
    updated_on = Column(DateTime, default=db.func.now(), onupdate=db.func.now())

class User(db.Model):
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    created_on = Column(DateTime, server_default=db.func.now())
    updated_on = Column(DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

class UserLog(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    state = Column(String(25))
    user_message = Column(String(255))
    created_on = Column(DateTime, default=db.func.now())
    updated_on = Column(DateTime, default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        CheckConstraint("state in ('item_list', 'search_item', 'pick_item', 'set_price', 'delete_item',"
                        "'telegram_id', 'pick_price', 'main_menu')",
                        name='state_valid_values'),
        {})


if __name__ == "__main__":
    app.run()