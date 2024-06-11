from flask import Flask, render_template
from models import db, Mario_Speedruns, Celeste_Speedruns, Hollow_Knight_Speedruns, User, Role
from flask_security import SQLAlchemyUserDatastore, Security, hash_password, roles_required, verify_password
from wtforms import StringField, PasswordField, validators
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite"
app.config['SECRET_KEY'] = 'hello mario'
app.config['SECURITY_PASSWORD_SALT'] = '882777363'
db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore, register_blueprint=False)

with app.app_context():
    db.drop_all()
    db.create_all()
    if not user_datastore.find_user(email="test@agh.edu.pl"):
        moderator = user_datastore.create_role(name='moderator', description='Moderator')
        db.session.add(moderator)
        db.session.commit()
        user = user_datastore.create_user(
            email="test@agh.edu.pl",
            username="test",
            password=hash_password("test567"),
        )
        user_datastore.add_role_to_user(user, 'moderator')
        db.session.commit()


@app.route('/', methods=['GET'])
def base():
    mario_speedruns = Mario_Speedruns.query.order_by(Mario_Speedruns.time)
    celeste_speedruns = Celeste_Speedruns.query.order_by(Celeste_Speedruns.time)
    hollow_knight_speedruns = Hollow_Knight_Speedruns.query.order_by(Hollow_Knight_Speedruns.time)
    return render_template('speedruns.html', mario_speedruns=mario_speedruns, celeste_speedruns=celeste_speedruns,
                           hollow_knight_speedruns=hollow_knight_speedruns)

@app.route('/waistlist', methods=['GET'])
@roles_required('moderator')
def waistlist():
    mario_speedruns = Mario_Speedruns.query.order_by(Mario_Speedruns.time)
    celeste_speedruns = Celeste_Speedruns.query.order_by(Celeste_Speedruns.time)
    hollow_knight_speedruns = Hollow_Knight_Speedruns.query.order_by(Hollow_Knight_Speedruns.time)
    return render_template('speedruns.html', mario_speedruns=mario_speedruns, celeste_speedruns=celeste_speedruns,
                           hollow_knight_speedruns=hollow_knight_speedruns)

class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired("Please enter your email"), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired("Please enter password")])

# @app.route('/login', methods=['GET'])
# def login():

#     return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user and verify_password(form.password.data, user.password):
            print('Success')
        else:
            print('Failure')
    return render_template('login.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)
