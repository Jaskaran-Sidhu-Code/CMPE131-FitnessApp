from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
app.debug = True  # Ensure debug is enabled for development

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight_pounds = db.Column(db.Float, nullable=False)
    height_feet = db.Column(db.Integer, nullable=False)
    height_inches = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    exercise_frequency = db.Column(db.String(50), nullable=False)

@app.route('/')
def home():
    return redirect(url_for('combined_form'))

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
                gender=request.form['gender'],
                exercise_frequency=request.form['exercise_frequency']
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

@app.route('/combined_form', methods=['GET', 'POST'])
def combined_form():
    users = User.query.all()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            try:
                calories_needed = calculate_daily_calories(
                    weight=float(user.weight_pounds),
                    height_feet=int(user.height_feet),
                    height_inches=int(user.height_inches),
                    age=int(user.age),
                    gender=user.gender,
                    activity_level=user.exercise_frequency
                )
                recommendations = get_diet_recommendations(
                    goal=request.form['goal'],
                    focus=request.form['focus']
                )
                flash('Results calculated successfully.')
                return render_template('combined_form.html', users=users, user=user, calories=calories_needed, recommendations=recommendations)
            except Exception as e:
                flash(f'Error in calculation: {str(e)}')
        else:
            flash('User not found.')
    return render_template('combined_form.html', users=users)

def calculate_daily_calories(weight, height_feet, height_inches, age, gender, activity_level):
    height_cm = (height_feet * 12 + height_inches) * 2.54
    weight_kg = weight * 0.453592
    if gender == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return bmr * float(activity_level)

def get_diet_recommendations(goal, focus):
    recommendations = {
        'gain': {
            'muscle': ["Increase protein intake and consider supplements such as whey protein.", "Focus on strength training."],
            'fat_loss': ["It's unusual to focus on fat gain; consider consulting a dietitian."],
            'both': ["Increase caloric intake moderately with a balanced diet high in proteins and carbohydrates."]
        },
        'lose': {
            'muscle': ["Maintain protein intake while in a caloric deficit to prevent muscle loss."],
            'fat_loss': ["Reduce caloric intake and increase cardio activities.", "Focus on foods high in fiber and low in fats."],
            'both': ["Slight caloric deficit with high protein intake and regular strength and cardio training."]
        },
        'maintain': {
            'muscle': ["Maintain a balanced diet with adequate protein."],
            'fat_loss': ["Maintain a balanced caloric intake to sustain body weight."],
            'both': ["Continue balanced nutritional intake with regular exercise."]
        }
    }
    return recommendations.get(goal, {}).get(focus, ["No specific recommendations for this choice."])

@app.cli.command("init_db")
def init_db():
    """Clear existing data and create new tables."""
    db.drop_all()
    db.create_all()
    print("Initialized the database.")

if __name__ == "__main__":
    app.run(debug=True)






























