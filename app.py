from flask import Flask, render_template, redirect, url_for, flash, session
from models import db, Mario_Speedruns, Celeste_Speedruns, Hollow_Knight_Speedruns, User, Role
from flask_security import SQLAlchemyUserDatastore, Security, hash_password, roles_required, verify_password, login_user, logout_user, anonymous_user_required, login_required, current_user
from wtforms import StringField, PasswordField, validators, SelectField
from flask_wtf import FlaskForm
from wtforms_components import DateField, TimeField, DateRange
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite"
app.config['SECRET_KEY'] = 'hello mario'
app.config['SECURITY_PASSWORD_SALT'] = '882777363'
db.init_app(app)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore, register_blueprint=False)

with app.app_context():
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


@app.route('/waitlist', methods=['GET'])
@roles_required('moderator')
def waitlist():
    mario_speedruns = Mario_Speedruns.query.order_by(Mario_Speedruns.time)
    celeste_speedruns = Celeste_Speedruns.query.order_by(Celeste_Speedruns.time)
    hollow_knight_speedruns = Hollow_Knight_Speedruns.query.order_by(Hollow_Knight_Speedruns.time)
    return render_template('speedruns.html', mario_speedruns=mario_speedruns, celeste_speedruns=celeste_speedruns,
                           hollow_knight_speedruns=hollow_knight_speedruns)


class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired("Please enter your email"),
                                  validators.Email(message="Please enter a valid email")])
    password = PasswordField('Password', [validators.DataRequired("Please enter password"),
                                          validators.Length(min=7, max=25, message="Password must be between 7 and 25 characters")])


@app.route('/login', methods=['GET', 'POST'])
@anonymous_user_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and verify_password(form.password.data, user.password):
            login_user(user)
            session['_flashes'].clear()
            return redirect(url_for('base'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('base'))

class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired("Please enter your username"), validators.Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    email = StringField('Email', [validators.DataRequired("Please enter your email"), validators.Email(message="Please enter a valid email")])
    password = PasswordField('Password', [validators.DataRequired("Please enter password"), validators.Length(min=7, max=25, message="Password must be between 7 and 25 characters")])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        username = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Email already taken')
        elif username:
            flash('Username already taken')
        else:
            user2 = user_datastore.create_user(
                email=form.email.data,
                username=form.username.data,
                password=hash_password(form.password.data),
            )
            db.session.add(user2)
            db.session.commit()
            login_user(user2)
            return redirect(url_for('base'))
    return render_template('register.html', form=form)


class AddForm(FlaskForm):
    time = TimeField('Enter the approximate time of the speedrun:', [validators.DataRequired("Please enter time"), DateRange(min=datetime.time(0, 1))])
    date = DateField('Enter when the speedrun was achieved', [validators.DataRequired("Please enter date"), DateRange(min=datetime.date(1996, 1, 1))])
    link_id = StringField('Enter the link to a youtube video of the speedrun', [validators.DataRequired("Please enter link"),
                                                                                validators.Regexp('^(https:\/\/www.youtube.com\/watch\?v=)([a-zA-Z0-9_-]{11})$', message="Not a valid youtube link")])
    category = SelectField('Select the category of the speedrun:', choices=[('mario', 'Mario'), ('celeste', 'Celeste'), ('hollow_knight', 'Hollow Knight')])


@app.route('/add_speedrun', methods=['GET', 'POST'])
@login_required
def add_speedrun():
    form = AddForm()
    if form.validate_on_submit():
        category = form.category.data
        link_id = form.link_id.data
        link_id = link_id[link_id.rfind('=')+1:]
        speedrun_time = form.time.data
        speedrun_time = datetime.datetime.combine(datetime.date.min, speedrun_time) - datetime.datetime.min
        if category == 'mario':
            speedrun = Mario_Speedruns(
                user_id=current_user.id,
                time=speedrun_time,
                date=form.date.data,
                link_id=link_id
            )
        elif category == 'celeste':
            speedrun = Celeste_Speedruns(
                user_id=current_user.id,
                time=speedrun_time,
                date=form.date.data,
                link_id=link_id
            )
        else:
            speedrun = Hollow_Knight_Speedruns(
                user_id=current_user.id,
                time=speedrun_time,
                date=form.date.data,
                link_id=link_id
            )
        db.session.add(speedrun)
        db.session.commit()
        return redirect(url_for('base'))
    else:
        flash('Invalid data')
    return render_template('add_speedrun.html', form=form)

@app.route('/show_speedrun/<int:speedrun_id>', methods=['GET'])
def show_speedrun(speedrun_id=0):
    if(speedrun_id<=0):
        return redirect(url_for('base'))
    speedrun = Mario_Speedruns.query.get_or_404(speedrun_id)
    if speedrun.verified is False and current_user is not speedrun.user and not current_user.has_role('moderator'):
        return redirect(url_for('base'))
    print(speedrun.link_id)
    return render_template('show_speedrun.html', speedrun=speedrun)




if __name__ == '__main__':
    app.run(debug=True)
