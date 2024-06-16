from flask import Flask, render_template, redirect, url_for, flash
from models import db, Speedruns, User, Role
from flask_security import SQLAlchemyUserDatastore, Security, hash_password, roles_required, verify_password, \
    login_user, logout_user, anonymous_user_required, login_required, current_user
from wtforms import StringField, PasswordField, validators, SelectField
from flask_wtf import FlaskForm
from wtforms_components import DateField, TimeField, DateRange
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.sqlite"
app.config['SECRET_KEY'] = 'hello mario'
app.config['SECURITY_PASSWORD_SALT'] = '882777363'
app.config['PAGINATION_PER_PAGE'] = 5
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
def index():
    return redirect(url_for('mario_speedruns'))

@app.route('/mario_speedruns', methods=['GET'])
@app.route('/mario_speedruns/page/<int:page>', methods=['GET'])
def mario_speedruns(page=1):
    mario_speedruns = Speedruns.query.order_by(Speedruns.time).filter(
        Speedruns.category == 'mario', Speedruns.verified == True).paginate(page=page, per_page=5, error_out=False)
    return render_template('mario_speedruns.html', mario_speedruns=mario_speedruns)

@app.route('/celeste_speedruns', methods=['GET'])
@app.route('/celeste_speedruns/page/<int:page>', methods=['GET'])
def celeste_speedruns(page=1):
    celeste_speedruns = Speedruns.query.order_by(Speedruns.time).filter(
        Speedruns.category == 'celeste', Speedruns.verified == True).paginate(page=page, per_page=5, error_out=False)
    return render_template('celeste_speedruns.html', celeste_speedruns=celeste_speedruns)

@app.route('/hollow_knight_speedruns', methods=['GET'])
@app.route('/hollow_knight_speedruns/page/<int:page>', methods=['GET'])
def hollow_knight_speedruns(page=1):
    hollow_knight_speedruns = Speedruns.query.order_by(Speedruns.time).filter(
        Speedruns.category == 'hollow_knight', Speedruns.verified == True).paginate(page=page, per_page=5,
                                                                                    error_out=False)
    return render_template('hollow_knight_speedruns.html', hollow_knight_speedruns=hollow_knight_speedruns)


class LoginForm(FlaskForm):
    email = StringField('Email', [validators.DataRequired("Please enter your email"),
                                  validators.Email(message="Please enter a valid email")])
    password = PasswordField('Password', [validators.DataRequired("Please enter password"),
                                          validators.Length(min=7, max=25,
                                                            message="Password must be between 7 and 25 characters")])


@app.route('/login', methods=['GET', 'POST'])
@anonymous_user_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and verify_password(form.password.data, user.password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired("Please enter your username"),
                                        validators.Length(min=4, max=25,
                                                          message="Username must be between 4 and 25 characters")])
    email = StringField('Email', [validators.DataRequired("Please enter your email"),
                                  validators.Email(message="Please enter a valid email")])
    password = PasswordField('Password', [validators.DataRequired("Please enter password"),
                                          validators.Length(min=7, max=25,
                                                            message="Password must be between 7 and 25 characters")])


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
            return redirect(url_for('index'))
    return render_template('register.html', form=form)


class AddForm(FlaskForm):
    time = TimeField('Enter the approximate time of the speedrun:',
                     [validators.DataRequired("Please enter time"), DateRange(min=datetime.time(0, 0, 0, 1))],
                     format='%H:%M:%S', render_kw={"step": "1"})
    date = DateField('Enter when the speedrun was achieved',
                     [validators.DataRequired("Please enter date"), DateRange(min=datetime.date(1996, 1, 1))])
    link_id = StringField('Enter the link to a youtube video of the speedrun',
                          [validators.DataRequired("Please enter link"),
                           validators.Regexp('^(https:\/\/www.youtube.com\/watch\?v=)([a-zA-Z0-9_-]{11})$',
                                             message="Not a valid youtube link")])
    category = SelectField('Select the category of the speedrun:',
                           choices=[('mario', 'Mario'), ('celeste', 'Celeste'), ('hollow_knight', 'Hollow Knight')])


@app.route('/add_speedrun', methods=['GET', 'POST'])
@login_required
def add_speedrun():
    form = AddForm()
    if form.validate_on_submit():
        category = form.category.data
        link_id = form.link_id.data
        link_id = link_id[link_id.rfind('=') + 1:]
        speedrun_time = form.time.data
        speedrun_time = datetime.datetime.combine(datetime.date.min, speedrun_time) - datetime.datetime.min
        if category == 'mario':
            speedrun = Speedruns(
                user_id=current_user.id,
                time=speedrun_time,
                date=form.date.data,
                link_id=link_id,
                category=category
            )
        elif category == 'celeste':
            speedrun = Speedruns(
                user_id=current_user.id,
                time=speedrun_time,
                date=form.date.data,
                link_id=link_id,
                category=category
            )
        else:
            speedrun = Speedruns(
                user_id=current_user.id,
                time=speedrun_time,
                date=form.date.data,
                link_id=link_id,
                category=category
            )
        db.session.add(speedrun)
        db.session.commit()
        return redirect(url_for('show_speedrun', speedrun_id=speedrun.id))
    return render_template('add_speedrun.html', form=form)


@app.route('/show_speedrun/<int:speedrun_id>', methods=['GET'])
def show_speedrun(speedrun_id=0):
    if speedrun_id <= 0:
        return redirect(url_for('index'))
    speedrun = Speedruns.query.get_or_404(speedrun_id)
    if speedrun.verified is False and current_user is not speedrun.user and not current_user.has_role('moderator'):
        return redirect(url_for('index'))
    speedrun.date = speedrun.date.strftime('%d.%m.%Y')
    return render_template('show_speedrun.html', speedrun=speedrun)


@app.route('/delete_speedrun/<int:speedrun_id>', methods=['GET'])
@login_required
def delete_speedrun(speedrun_id=0):
    if speedrun_id <= 0:
        return redirect(url_for('index'))
    speedrun = Speedruns.query.get_or_404(speedrun_id)
    if current_user is speedrun.user or current_user.has_role('moderator'):
        db.session.delete(speedrun)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/waitlist', methods=['GET'])
@roles_required('moderator')
def waitlist():
    waitlists = Speedruns.query.order_by(Speedruns.date).where(Speedruns.verified == False)
    mod_requests = User.query.filter_by(moderator_request=True)
    return render_template('waitlist.html', waitlist=waitlists, mod_requests=mod_requests)

@app.route('/verify_speedrun/<int:speedrun_id>', methods=['GET'])
@roles_required('moderator')
def verify_speedrun(speedrun_id=0):
    if speedrun_id <= 0:
        return redirect(url_for('index'))
    speedrun = Speedruns.query.get_or_404(speedrun_id)
    if speedrun.verified is True:
        return redirect(url_for('waitlist'))
    if speedrun.user_id == current_user.id:
        return redirect(url_for('waitlist'))
    speedrun.verified = True
    db.session.commit()
    return redirect(url_for('waitlist'))

@app.route('/moderator_requests', methods=['GET'])
@login_required
def moderator_requests():
    current_user.moderator_request = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/moderator_approve/<int:user_id>', methods=['GET'])
@roles_required('moderator')
def moderator_approve(user_id=0):
    if user_id <= 0:
        return redirect(url_for('waitlist'))
    user = User.query.get_or_404(user_id)
    user_datastore.add_role_to_user(user, 'moderator')
    user.moderator_request = False
    db.session.commit()
    return redirect(url_for('waitlist'))


if __name__ == '__main__':
    app.run(debug=True)
