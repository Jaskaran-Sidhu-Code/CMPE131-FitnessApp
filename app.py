from flask import Flask, g, render_template, request, make_response, session, redirect, flash
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Google API Keys
PLACES_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'
GEOCODING_API_KEY = 'AIzaSyBPMpgZnvRwyiD47P-togXkkGLLAbJ64Jo'

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
            return redirect('/home')
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
        connection = sqlite3.connect('fitnessDatabase.db')
        cursor = connection.cursor()
        cursor.execute('SELECT username FROM Login WHERE username=?;',[username])
        user = cursor.fetchone()
        if not user:
            db.execute('INSERT INTO Login (username, email, password) VALUES (?,?,?);',[username,email,password])
            db.execute('INSERT INTO Calories (username, calCon, calBurn, calRec) VALUES (?,?,?,?)',[username,0,0,0])
            db.execute("INSERT INTO Goals (username,goalOne,goalTwo,goalThree,goalFour,goalFive) VALUES (?,?,?,?,?,?);",
                    [username,0,0,0,0,0])
            db.commit()
            return redirect('/')
        else:
            errormsg = "Username in use."
            return render_template("accountCreation.html", errormsg = errormsg)
    return render_template("accountCreation.html")

@app.route('/home')
def homePage():
    if not 'username' in session:
        return redirect("/")
    else:
        userGoals = getGoals()
        calorie = calorieInfo()
        return render_template("homePage.html", usr = session['username'],
                               usrGoals = userGoals, userInfo = calorie[3], calories=calorie[0],
                               recommendations=calorie[1], macronutrients=calorie[2], status=calorie[4])

@app.route('/goal_select', methods = ["GET","POST"])
def goalSelect():
    if not 'username' in session:
        return redirect("/")
    else:
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
    if not 'username' in session:
        return redirect("/")
    else:
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

def getCalories():
    connection = sqlite3.connect('fitnessDatabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Calories WHERE username=?",[session['username']])
    userCal = cursor.fetchone()
    connection.close()
    print(userCal)
    calCon = userCal[1]
    calBurn = userCal[2]
    calRec = userCal[3]
    return calCon,calBurn,calRec

@app.route('/calorie_tracker', methods=['GET','POST'])
def calorie_tracker():
    if not 'username' in session:
        return redirect("/")
    else:
        if request.method == "POST":
            calCon,calBurn,calRec = getCalories()
            db = getDB('./fitnessDatabase.db')
            if 'caloriesConsumed' in request.form:
                calConsumed = int(request.form.get('caloriesConsumed'))
                tCalCon = calConsumed + calCon
                tCalBurn = calBurn
                db.execute("REPLACE INTO Calories (username, calCon, calBurn, calRec) VALUES (?, ?, ?, ?)",
                        [session['username'], tCalCon, tCalBurn, calRec])
                db.commit()
                return render_template('calorieTracker.html',tCalCon=tCalCon, tCalBurn=tCalBurn, calRec=calRec)
            elif 'caloriesBurned' in request.form:
                calBurned = int(request.form.get('caloriesBurned'))
                tCalCon = calCon
                tCalBurn = calBurned + calBurn
                db.execute("REPLACE INTO Calories (username, calCon, calBurn, calRec) VALUES (?, ?, ?, ?)",
                        [session['username'], tCalCon, tCalBurn, calRec])
                db.commit()
                return render_template('calorieTracker.html',tCalCon=tCalCon, tCalBurn=tCalBurn, calRec=calRec)
            elif 'resetCon' in request.form:
                db.execute("REPLACE INTO Calories (username, calCon, calBurn, calRec) VALUES (?, ?, ?, ?)",
                        [session['username'], 0, calBurn, calRec])
                db.commit()
                return render_template('calorieTracker.html',tCalCon=0, tCalBurn=calBurn, calRec=calRec)
            elif 'resetBurn' in request.form:
                db.execute("REPLACE INTO Calories (username, calCon, calBurn, calRec) VALUES (?, ?, ?, ?)",
                        [session['username'], calCon, 0, calRec])
                db.commit()
                return render_template('calorieTracker.html',tCalCon=calCon, tCalBurn=0, calRec=calRec)
        else:
            calCon, calBurn, calRec = getCalories()
            return render_template('calorieTracker.html',tCalCon=calCon, tCalBurn=calBurn, calRec=calRec)

@app.route('/find_gyms', methods=['GET','POST'])
def find_gyms():
    if not 'username' in session:
        return redirect("/")
    else:
        if request.method == 'POST':
            city = request.form['city']
            nearby_gyms = get_nearby_gyms(city)
            return render_template('gyms.html', city=city, gyms=nearby_gyms)
        return render_template('gyms.html')

def calorieInfo():
    userInfo = getInfo()
    userGoals = getGoals()
    calCon,calBurn,calRec = getCalories()

    if userInfo != "noEntry":
        gender = userInfo[1]
        age = userInfo[2]
        weight = userInfo[3]
        heightFeet = userInfo[4]
        heightInch = userInfo[5]
        activityLevel = userInfo[6]
        status = "set"
        goal = "gain"
        focus = "muscle"

        if(userGoals[2]=="on" and userGoals[4]=="on" and userGoals[5]=="0"):
            goal = "gain"
            focus = "muscle"
        elif((userGoals[2]=="on" and userGoals[5]=="on") or userGoals[5]=="on"):
            goal = "gain"
            focus = "both"
        elif(userGoals[1]=="on" and userGoals[4]=="on" and userGoals[5]=="0"):
            goal = "lose"
            focus = "muscle"
        elif(userGoals[1]=="on" and userGoals[5]=="on" and userGoals[4]=="0"):
            goal = "lose"
            focus = "fat"
        elif(userGoals[1]=="on" and userGoals[4]=="on" and userGoals[5]=="on"):
            goal = "lose"
            focus = "both"
        elif(userGoals[3]=="on" and userGoals[4]=="on" and userGoals[5]=="0"):
            goal = "maintain"
            focus = "muscle"
        elif(userGoals[3]=="on" and userGoals[5]=="on" and userGoals[4]=="0"):
            goal = "maintain"
            focus = "muscle"
        elif(userGoals[3]=="on" and userGoals[4]=="on" and userGoals[5]=="on"):
            goal = "maintain"
            focus = "both"
        elif(userGoals[2]=="on" and userGoals[4]=="0" and userGoals[5]=="0"):
            goal = "gain"
            focus = "fat"
        elif(userGoals[1]=="0" and userGoals[2]=="0" and userGoals[3]=="0" and userGoals[4]=="0" and userGoals[5]=="0"):
            status = "not_set"

        caloriesNeeded = calculate_daily_calories(weight,heightFeet,heightInch,age,gender,activityLevel,goal,focus)
        macronutrients = calculate_macronutrients(caloriesNeeded,goal,focus,activityLevel)
        if status == "set":
            recommendations = get_diet_recommendations(goal, focus)
        else:
            recommendations = 0

        print(caloriesNeeded)
        db = getDB('./fitnessDatabase.db')
        db.execute("REPLACE INTO Calories (username,calCon,calBurn,calRec) VALUES (?,?,?,?)",
                   [session['username'],calCon,calBurn,caloriesNeeded])
        db.commit()

        return caloriesNeeded, recommendations, macronutrients, userInfo, status
    return None,None,None,None,None

def getGoals():
    connection = sqlite3.connect('fitnessDatabase.db')
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

def calculate_daily_calories(weight, height_feet, height_inches, age, gender, activity_level, goal, focus):
    height_cm = (height_feet * 12 + height_inches) * 2.54
    weight_kg = weight * 0.453592
    if gender == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_factors = {
        "1.2": 1.2,  # Sedentary
        "1.375": 1.375,  # Light activity
        "1.55": 1.55,  # Moderate activity
        "1.725": 1.725,  # Very active
        "1.9": 1.9  # Super active
    }
    activity_multiplier = activity_factors.get(activity_level, 1.2)
    calories = bmr * activity_multiplier

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
    goal_multiplier = goal_factors.get((goal, focus), 1.0)
    calories *= goal_multiplier

    return round(calories)

def calculate_macronutrients(calories, goal, focus, activity_level):
    protein_pct = 0.30
    fat_pct = 0.30
    carbs_pct = 0.40

    if activity_level == "1.725" or activity_level == "1.9":  # Very active or super active
        carbs_pct += 0.05  # Increase carbs for high activity
        protein_pct -= 0.02  # Slightly less protein
        fat_pct -= 0.03  # Slightly less fat

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

def geocode_address(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': GEOCODING_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        return None

def get_nearby_gyms(city):
    coordinates = geocode_address(city)
    if coordinates:
        lat, lng = coordinates
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f"{lat},{lng}",
            'radius': 5000,  # Search radius in meters
            'type': 'gym',
            'key': PLACES_API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        nearby_gyms = [place['name'] for place in data.get('results', [])]

        # Insert gyms into the database
        db = getDB('./gyms.db')
        cursor = db.cursor()
        for gym in nearby_gyms:
            cursor.execute("INSERT INTO gyms (name, city, latitude, longitude) VALUES (?, ?, ?, ?)",
                           (gym, city, lat, lng))
        db.commit()

        return nearby_gyms
    else:
        return []

if __name__ == '__main__':
    app.run(debug=True)
