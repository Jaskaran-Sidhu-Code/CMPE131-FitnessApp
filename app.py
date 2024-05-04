from flask import Flask, g, render_template, request, make_response, session, redirect, flash
from datetime import timedelta
import sqlite3 

app = Flask(__name__) 
app.secret_key = "mysecretkey"

def connectDB(dbName):
    sql = sqlite3.connect(dbName)
    sql.row_factory = sqlite3.Row
    return sql

def getDB(dbName):
    if not hasattr(g,'sqlite3'):
        g.sqlite3_db = connectDB(dbName)
    return g.sqlite3_db

@app.teardown_appcontext
def closeDB(error):
    if hasattr(g,'sqlite3_db'):
        g.sqlite3_db.close()

@app.route('/', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        connection = sqlite3.connect('fitnessDatabase.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Login WHERE username=? and password=?",[username, password])
        user = cursor.fetchone()
        connection.close()
        if user:
            session['username'] = request.form['username']
            return redirect('\home')
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/')

@app.route('/create_account', methods=["GET","POST"])
def create_account():
    if request.method == "POST":
        db = getDB('./fitnessDatabase.db')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        db.execute('INSERT INTO Login (username, email, password) VALUES (?,?,?);',[username,email,password])
        db.commit()
        return redirect('/')
    return render_template("accountCreation.html")

@app.route('/home')
def homePage():
    if not 'username' in session:
        return redirect("/login")
    else:
        userGoals = getGoals()
        calorie = calorieInfo()
        return render_template("homePage.html", usr = session['username'], usrGoals = userGoals, userInfo = calorie[3], calories=calorie[0], recommendations=calorie[1], macronutrients=calorie[2])

@app.route('/goalselect', methods = ["GET","POST"])
def goalSelect():
    if request.method == "POST":
        db = getDB('./fitnessDatabase.db')
        goalWeight = request.form['goalWeight']
        if(goalWeight == "goalOne"):
            goalOne = "on"
            goalTwo = 0
            goalThree = 0
        elif(goalWeight == "goalTwo"):
            goalOne = 0
            goalTwo = "on"
            goalThree = 0
        elif(goalWeight == "goalThree"):
            goalOne = 0
            goalTwo = 0
            goalThree = "on"
        goalFour = request.form.get("goalFour",False)
        goalFive = request.form.get("goalFive",False)
        db.execute("INSERT OR REPLACE INTO Goals (username,goalOne,goalTwo,goalThree,goalFour,goalFive) VALUES (?,?,?,?,?,?);", 
                   [session['username'],goalOne,goalTwo,goalThree,goalFour,goalFive])
        db.commit()
    return render_template("goalSelect.html", usr = session['username'])

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        db = getDB('./fitnessDatabase.db')
        weight = float(request.form.get('weight'))
        heightFeet = int(request.form.get('heightFeet'))
        heightInch = int(request.form.get('heightInches'))
        age = int(request.form.get('age'))
        gender = request.form.get('gender')
        exerciseFreq = request.form['exercise_frequency']
        db.execute("INSERT OR REPLACE INTO Diets (username,gender,age,weight,heightFeet,heightInch,exerciseFreq) VALUES (?,?,?,?,?,?,?);",
                   [session['username'],gender,age,weight,heightFeet,heightInch,exerciseFreq])
        db.commit()
        flash('Profile updated successfully!', 'success')
    return render_template('edit_profile.html', usr=session['username'])

def calorieInfo():
    userInfo = getInfo()
    userGoals = getGoals()

    if userInfo != "noEntry":
        gender = userInfo[1]
        age = userInfo[2]
        weight = userInfo[3]
        heightFeet = userInfo[4]
        heightInch = userInfo[5]
        activityLevel = userInfo[6]

        if(userGoals[2]=="on" and userGoals[4]=="on" and userGoals[5]==0):
            goal = "gain"
            focus = "muscle"
        elif((userGoals[2]=="on" and userGoals[5]=="on") or userGoals[5]=="on"):
            goal = "gain"
            focus = "both"
        elif(userGoals[1]=="on" and userGoals[4]=="on" and userGoals[5]==0):
            goal = "lose"
            focus = "muscle"
        elif(userGoals[1]=="on" and userGoals[5]=="on" and userGoals[4]==0):
            goal = "lose"
            focus = "fat"
        elif(userGoals[1]=="on" and userGoals[4]=="on" and userGoals[5]=="on"):
            goal = "lose"
            focus = "both"
        elif(userGoals[3]=="on" and userGoals[4]=="on" and userGoals[5]==0):
            goal = "maintain"
            focus = "muscle"
        elif(userGoals[3]=="on" and userGoals[5]=="on" and userGoals[4]==0):
            goal = "maintain"
            focus = "muscle"
        elif(userGoals[3]=="on" and userGoals[4]=="on" and userGoals[5]=="on"):
            goal = "maintain"
            focus = "both"
        elif(userGoals[2]=="on" and userGoals[4]==0 and userGoals[5]==0):
            goal = "gain"
            focus = "fat"
        else:
            goal = "gain"
            focus = "muscle"

        caloriesNeeded = calculate_daily_calories(weight,heightFeet,heightInch,age,gender,activityLevel)
        macronutrients = calculate_macronutrients(caloriesNeeded)
        recommendations = get_diet_recommendations(goal, focus)
               
        return caloriesNeeded, recommendations, macronutrients, userInfo
    return None,None,None

def getGoals():
    connection = sqlite3.connect("fitnessDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Goals WHERE username=?",[session['username']])
    goals = cursor.fetchone()
    connection.close()
    if goals is not None:
        return goals
    else:
        return "noEntry"

def getInfo():
    connection = sqlite3.connect('fitnessDatabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Diets WHERE username=?",[session['username']])
    userInfo = cursor.fetchone()
    connection.close()
    if userInfo is not None:
        return userInfo
    else:
        return "noEntry"

def calculate_daily_calories(weight, height_feet, height_inches, age, gender, activity_level):
    height_cm = (height_feet * 12 + height_inches) * 2.54
    weight_kg = weight * 0.453592
    if gender == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    total_calories = bmr * float(activity_level)
    return round(total_calories)

def calculate_macronutrients(calories, protein_pct=30, fat_pct=30, carb_pct=40):
    protein_calories = (calories * protein_pct) / 100
    fat_calories = (calories * fat_pct) / 100
    carb_calories = (calories * carb_pct) / 100

    protein_grams = round(protein_calories / 4)
    fat_grams = round(fat_calories / 9)
    carb_grams = round(carb_calories / 4)

    return {
        'Protein (g)': protein_grams,
        'Fat (g)': fat_grams,
        'Carbohydrates (g)': carb_grams
    }

def get_diet_recommendations(goal, focus):
    recommendations = {
        'gain': {
            'muscle': ["Increase protein intake and consider supplements such as whey protein.", "Focus on strength training."],
            'fat': ["It's unusual to focus on fat gain; consider consulting a dietitian."],
            'both': ["Increase caloric intake moderately with a balanced diet high in proteins and carbohydrates."]
        },
        'lose': {
            'muscle': ["Maintain protein intake while in a caloric deficit to prevent muscle loss."],
            'fat': ["Reduce caloric intake and increase cardio activities.", "Focus on foods high in fiber and low in fats."],
            'both': ["Slight caloric deficit with high protein intake and regular strength and cardio training."]
        },
        'maintain': {
            'muscle': ["Maintain a balanced diet with adequate protein."],
            'fat': ["Maintain a balanced caloric intake to sustain body weight."],
            'both': ["Continue balanced nutritional intake with regular exercise."]
        }
    }
    return recommendations.get(goal, {}).get(focus, ["No specific recommendations for this choice."])

if __name__ == '__main__':
    app.run(debug=True)




