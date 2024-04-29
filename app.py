from flask import Flask, g, render_template, request, make_response
import sqlite3

app = Flask(__name__)

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
    db = getDB('./loginDatabase.db')
    current_user = request.form.get('username')
    password = request.form.get('password')
    connection = sqlite3.connect('loginDatabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM Login WHERE username=? and password=?",[current_user, password])
    pw = cursor.fetchone()
    connection.close()
    global currentUser
    currentUser = current_user
    try: 
        if pw[0] == password:
            return render_template("homePage.html",usr=currentUser)
    except:
        return render_template("login.html")

@app.route('/create_account', methods=["GET","POST"])
def create_account():
    if request.method == "POST":
        db = getDB('./loginDatabase.db')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        db.execute('INSERT INTO Login (username, email, password) VALUES (?,?,?);',[username,email,password])
        db.commit()
    return render_template("accountCreation.html")

@app.route('/home')
def homePage():
    user = showGoals()
    return render_template("homePage.html", usr = user)

@app.route('/goalselect', methods = ["GET","POST"])
def goalSelect():
    if request.method == "POST":
        print(request.form)
        db = getDB('./database.db')
        goalOne = request.form.get("goalOne",False)
        goalTwo = request.form.get("goalTwo",False)
        goalThree = request.form.get("goalThree",False)
        goalFour = request.form.get("goalFour",False)
        goalFive = request.form.get("goalFive",False)
        db.execute("INSERT OR REPLACE INTO goalselect (user,goalOne,goalTwo,goalThree,goalFour,goalFive) VALUES (?,?,?,?,?,?);", [currentUser,goalOne,goalTwo,goalThree,goalFour,goalFive])
        db.commit()
    return render_template("goalSelect.html",usr=currentUser)

def showGoals():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM goalselect WHERE user=?",[currentUser])
    results = cursor.fetchone()
    connection.close()
    return results

@app.route('/calorietracker')
def calorieTracker():
    return render_template("calorieTracker.html",usr=currentUser)

@app.route("/temp")
def temp():
    return render_template("temp.html")
    
if __name__ == '__main__':
    app.run(debug=True)




