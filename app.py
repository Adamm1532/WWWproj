from flask import Flask, render_template, jsonify
import datetime
from models import db, Mario_Speedruns, Celeste_Speedruns, Hollow_Knight_Speedruns, User, Role
from flask_security import SQLAlchemyUserDatastore, Security

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite"
app.config['SECRET_KEY'] = 'hello mario'
db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

with app.app_context():
    db.create_all()
    num_rows_deleted = db.session.query(Mario_Speedruns).delete()
    num_rows_deleted2 = db.session.query(Celeste_Speedruns).delete()
    db.session.commit()
    obj = Mario_Speedruns(user='Suigi', time=datetime.timedelta(minutes=14, seconds=35, milliseconds=500),
                          date=datetime.datetime(2023, 2, 22), link='https://youtu.be/ngMFEeDoX54', verified=True)
    db.session.add(obj)
    obj2 = Mario_Speedruns(user='Slipperynip', time=datetime.timedelta(minutes=14, seconds=41, milliseconds=210),
                          date=datetime.datetime(2023, 11, 21), link='https://player.twitch.tv/?video=v1984963404&amp;parent=www.speedrun.com', verified=True)
    db.session.add(obj2)
    obj3 = Celeste_Speedruns(user='secureaccount', time=datetime.timedelta(minutes=24, seconds=58, milliseconds=23),
                          date=datetime.datetime(2024, 3, 12), link='https://youtu.be/jNE6lSSbYNM', verified=True)
    db.session.add(obj3)
    obj4 = Celeste_Speedruns(user='Kezaron', time=datetime.timedelta(minutes=25, seconds=53, milliseconds=528),
                             date=datetime.datetime(2024, 4, 6), link='https://youtu.be/NDUJPdAu6vk', verified=True)
    db.session.add(obj4)
    db.session.commit()


@app.route('/', methods=['GET'])
def base():
    mario_speedruns = Mario_Speedruns.query.order_by(Mario_Speedruns.time)
    celeste_speedruns = Celeste_Speedruns.query.order_by(Celeste_Speedruns.time)
    hollow_knight_speedruns = Hollow_Knight_Speedruns.query.order_by(Hollow_Knight_Speedruns.time)
    return render_template('base.html', mario_speedruns=mario_speedruns, celeste_speedruns=celeste_speedruns,
                           hollow_knight_speedruns=hollow_knight_speedruns)

@app.route('/table/mario')
def table1():
    data = Mario_Speedruns.query.all()
    return jsonify(data)

@app.route('/table/celeste')
def table2():
    data = Celeste_Speedruns.query.all()
    return jsonify(data)

@app.route('/table/hollowknight')
def table3():
    data = Hollow_Knight_Speedruns.query.all()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
