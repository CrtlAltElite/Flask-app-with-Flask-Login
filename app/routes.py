from flask import render_template, request, redirect, url_for
import requests
from app import app
from .forms import LoginForm, RegisterForm
from .models import User
from flask_login import login_user, logout_user, current_user, login_required

#Routes
@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html.j2')

@app.route('/students', methods=['GET'])
@login_required
def students():
    my_students=["Thu", "Leo", "Sydney", "Josh", "Chris", "Fernado", "Benny", "Vicky", "Bradley"]
    return render_template("students.html.j2",students=my_students)

@app.route('/ergast', methods=['GET','POST'])
@login_required
def ergast():
    if request.method == 'POST':
        year = request.form.get('year')
        round = request.form.get('round')
        url = f'http://ergast.com/api/f1/{year}/{round}/driverStandings.json'
        response = requests.get(url)
        if response.ok:
            #do stuff with the data
            ## This part I changed from class.. 
            # instead of the try else I check to make sure the Driver standing list
            #  is not empty before we grab the data
            data = response.json()["MRData"]["StandingsTable"]["StandingsLists"]
            if not data:
                error_string=f'There is no info for {year} round {round}'
                return render_template("ergast.html.j2",error=error_string)

            data = data[0].get("DriverStandings")
            all_racers = []
            for racer in data:
                racer_dict={
                    'first_name':racer['Driver']['givenName'],
                    'last_name':racer['Driver']['familyName'],
                    'position':racer['position'],
                    'wins':racer['wins'],
                    'DOB':racer['Driver']['dateOfBirth'],
                    'nationality':racer['Driver']['nationality'],
                    'constructor':racer['Constructors'][0]['name']
                }
                all_racers.append(racer_dict)
            return render_template("ergast.html.j2",racers=all_racers)
        else:
            error_string="Houston We Have a Problem"
            render_template("ergast.html.j2",error=error_string)
    return render_template("ergast.html.j2")

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_user_data={
                "first_name": form.first_name.data.title(),
                "last_name": form.last_name.data.title(),
                "email": form.email.data.lower(),
                "password": form.password.data
            }
            new_user_object = User()
            new_user_object.from_dict(new_user_data)
        except:
            error_string="There was a problem creating your account. Please try again"
            return render_template('register.html.j2',form=form, error=error_string)
        # Give the user some feedback that says registered successfully 
        return redirect(url_for('login'))

    return render_template('register.html.j2',form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Do login Stuff
        email = form.email.data.lower()
        password = form.password.data
        u = User.query.filter_by(email=email).first()
        print(u)
        if u is not None and u.check_hashed_password(password):
            login_user(u)
            # Give User feeedback of success
            return redirect(url_for('index'))
        else:
            # Give user Invalid Password Combo error
            return redirect(url_for('login'))
    return render_template("login.html.j2", form=form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    if current_user is not None:
        logout_user()
        return redirect(url_for('login'))

#export/set FLASK_APP=app.py
#export/set FLASK_ENV=development
