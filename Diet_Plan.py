from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
app.debug = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize migrate

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight_pounds = db.Column(db.Float, nullable=False)
    height_feet = db.Column(db.Integer, nullable=False)
    height_inches = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    exercise_frequency = db.Column(db.String(50), nullable=False)

class FoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fats = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, default=date.today)

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
            user.exercise_frequency = request.form['exercise_frequency']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('view_profiles'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
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
        flash(f'Error deleting profile: {str(e)}', 'error')
    return redirect(url_for('view_profiles'))

def calculate_daily_calories(weight, height_feet, height_inches, age, gender, activity_level, goal, focus):
    # Basic metabolic rate calculation
    height_cm = (height_feet * 12 + height_inches) * 2.54
    weight_kg = weight * 0.453592
    if gender == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Apply activity level multiplier
    activity_factors = {
        "1.2": 1.2,  # Sedentary
        "1.375": 1.375,  # Light activity
        "1.55": 1.55,  # Moderate activity
        "1.725": 1.725,  # Very active
        "1.9": 1.9  # Super active
    }
    activity_multiplier = activity_factors.get(activity_level, 1.2)  # Default to sedentary if not found
    calories = bmr * activity_multiplier

    # Adjust calories based on goal and focus
    goal_factors = {
        ('gain', 'muscle'): 1.15,
        ('gain', 'fat_loss'): 1.05,
        ('gain', 'both'): 1.10,
        ('lose', 'muscle'): 0.85,
        ('lose', 'fat_loss'): 0.75,
        ('lose', 'both'): 0.80,
        ('maintain', 'muscle'): 1.05,
        ('maintain', 'fat_loss'): 0.95,
        ('maintain', 'both'): 1.00
    }
    goal_multiplier = goal_factors.get((goal, focus), 1.0)  # Default if no specific match
    calories *= goal_multiplier

    return round(calories)

@app.route('/combined_form', methods=['GET', 'POST'])
def combined_form():
    users = User.query.all()  # Fetch all users to display in the dropdown
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            # Fetch and print the activity level to ensure it's received correctly
            activity_level = request.form.get('activity_level', '1.2')  # Default to '1.2' if not found
            print("Received Activity Level:", activity_level)

            # Calculate daily calories needed based on input parameters
            calories_needed = calculate_daily_calories(
                weight=float(user.weight_pounds),
                height_feet=int(user.height_feet),
                height_inches=int(user.height_inches),
                age=int(user.age),
                gender=user.gender,
                activity_level=activity_level,
                goal=request.form['goal'],
                focus=request.form['focus']
            )

            # Calculate macronutrients based on the calories needed and other factors
            macros = calculate_macros(
                calories=calories_needed,
                goal=request.form['goal'],
                focus=request.form['focus'],
                activity_level=activity_level
            )

            # Fetch dietary recommendations based on the user's goal and focus
            recommendations = get_diet_recommendations(
                goal=request.form['goal'],
                focus=request.form['focus']
            )

            # Display results and debug information
            flash('Results calculated successfully.')
            print("Calories Needed:", calories_needed)
            print("Macros:", macros)

            # Render the page with the results to the user
            return render_template('combined_form.html', users=users, user=user, calories=calories_needed, macros=macros, recommendations=recommendations)
        else:
            flash('User not found.')
            print("User not found")

    # Render the form page without results if no POST request or an error occurred
    print("Rendering Page without results")
    return render_template('combined_form.html', users=users)



def calculate_macros(calories, goal, focus, activity_level):
    # Default macronutrient distribution
    protein_pct = 0.30
    fat_pct = 0.30
    carbs_pct = 0.40

    # Adjust macronutrient distribution based on goal, focus, and activity level
    if activity_level == "1.725" or activity_level == "1.9":  # Very active or super active
        carbs_pct += 0.05  # Increase carbs for high activity
        protein_pct -= 0.02  # Slightly less protein
        fat_pct -= 0.03  # Slightly less fat

    # Further adjustments based on goal and focus
    if goal == 'lose' and focus == 'muscle':
        protein_pct = 0.40
        fat_pct = 0.30
        carbs_pct = 0.30
    elif goal == 'gain' and focus == 'muscle':
        protein_pct = 0.30
        fat_pct = 0.25
        carbs_pct = 0.45

    protein = calories * protein_pct / 4  # 1 gram of protein = 4 calories
    fat = calories * fat_pct / 9          # 1 gram of fat = 9 calories
    carbs = calories * carbs_pct / 4      # 1 gram of carbs = 4 calories

    return {
        'protein_grams': round(protein),
        'fat_grams': round(fat),
        'carbs_grams': round(carbs)
    }



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
    """This command will be deprecated, use Flask-Migrate instead for handling migrations."""
    pass

if __name__ == "__main__":
    app.run(debug=True)






























