from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight_pounds = db.Column(db.Float, nullable=False)
    height_feet = db.Column(db.Integer, nullable=False)
    height_inches = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

@app.route('/')
def home():
    return render_template('Diet_Plan.html')

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
            return redirect(url_for('view_profiles'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating profile: ' + str(e), 'error')
    return render_template('create_profile.html')

@app.route('/view_profiles')
def view_profiles():
    users = User.query.all()
    return render_template('view_profiles.html', users=users)

@app.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
def edit_profile(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        try:
            user.name = request.form['name']
            user.weight_pounds = float(request.form['weight'])
            user.height_feet = int(request.form['heightFeet'])
            user.height_inches = int(request.form['heightInches'])
            user.age = int(request.form['age'])
            user.gender = request.form['gender']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('view_profiles'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile: ' + str(e), 'error')
    return render_template('edit_profile.html', user=user)

@app.route('/delete_profile/<int:id>', methods=['POST'])
def delete_profile(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Profile deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting profile: ' + str(e), 'error')
    return redirect(url_for('view_profiles'))

@app.route('/calculate', methods=['GET', 'POST'])
def calculate_calories_route():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        height_feet = int(request.form['heightFeet'])
        height_inches = int(request.form['heightInches'])
        age = int(request.form['age'])
        gender = request.form['gender']
        activity_level = float(request.form['activityLevel'])
        calories_needed = calculate_daily_calories(weight, height_feet, height_inches, age, gender, activity_level)
        return render_template('calorie_result.html', calories=calories_needed)
    return render_template('calorie_calculator.html')

@app.route('/recommendations', methods=['GET', 'POST'])
def get_recommendations_route():
    if request.method == 'POST':
        goal = request.form['goal']
        focus = request.form['focus']
        recommendations = get_diet_recommendations(goal, focus)
        return render_template('recommendations.html', recommendations=recommendations)
    return render_template('diet_recommendation.html')

def calculate_daily_calories(weight, height_feet, height_inches, age, gender, activity_level):
    height_cm = (height_feet * 12 + height_inches) * 2.54
    weight_kg = weight * 0.453592
    if gender == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    return bmr * activity_level

def get_diet_recommendations(goal, focus):
    recommendations = {
        'gain': {
            'muscle': [
                "Increase protein intake and consider supplements such as whey protein.",
                "Focus on strength training."
            ],
            'fat_loss': [
                "It's unusual to focus on fat gain; consider consulting a dietitian."
            ],
            'both': [
                "Increase caloric intake moderately with a balanced diet high in proteins and carbohydrates."
            ]
        },
        'lose': {
            'muscle': [
                "Focus on maintaining protein intake while in a slight caloric deficit to prevent muscle loss."
            ],
            'fat_loss': [
                "Reduce caloric intake and increase cardio activities.",
                "Focus on foods high in fiber and low in fats."
            ],
            'both': [
                "Slight caloric deficit with high protein intake and regular strength training and cardio."
            ]
        },
        'maintain': {
            'muscle': [
                "Maintain a balanced diet with adequate protein to support muscle maintenance."
            ],
            'fat_loss': [
                "Maintain a balanced diet with a normal caloric intake to sustain current body weight."
            ],
            'both': [
                "Continue balanced nutritional intake with regular exercise to maintain current body composition."
            ]
        }
    }
    return recommendations.get(goal, {}).get(focus, ["No specific recommendations for this choice."])

if __name__ == "__main__":
    app.run(debug=True)





















