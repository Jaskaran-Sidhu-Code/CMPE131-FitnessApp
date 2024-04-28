from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Needed for session management and flashing messages

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight_pounds = db.Column(db.Float, nullable=False)
    height_feet = db.Column(db.Integer, nullable=False)
    height_inches = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('create_profile'))

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        try:
            new_user = User(
                name=request.form['name'],
                weight_pounds=float(request.form['weight']),
                height_feet=int(request.form['heightFeet']),
                height_inches=int(request.form['heightInches']),
                age=int(request.form['age']),
                gender=request.form['gender']
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Profile created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error creating profile: ' + str(e), 'error')
        return redirect(url_for('view_profiles'))
    return render_template('create_profile.html')

@app.route('/view_profiles')
def view_profiles():
    users = User.query.all()
    return render_template('view_profiles.html', users=users)

if __name__ == "__main__":
    app.run(debug=True)