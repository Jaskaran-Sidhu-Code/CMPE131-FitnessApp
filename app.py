from flask import Flask, g, render_template, request, make_response
import sqlite3

userID = "Erich"

app = Flask(__name__)

def connectDB():
    sql = sqlite3.connect('./database.db')
    sql.row_factory = sqlite3.Row
    return sql

def getDB():
    if not hasattr(g,'sqlite3'):
        g.sqlite3_db = connectDB()
    return g.sqlite3_db

@app.teardown_appcontext
def closeDB(error):
    if hasattr(g,'sqlite3_db'):
        g.sqlite3_db.close()

@app.route('/', methods = ["GET","POST"])
def goalSelect():
    if request.method == "POST":
        print(request.form)
        db = getDB()
        user = request.form.get("user",False)
        goalOne = request.form.get("goalOne",False)
        goalTwo = request.form.get("goalTwo",False)
        goalThree = request.form.get("goalThree",False)
        goalFour = request.form.get("goalFour",False)
        goalFive = request.form.get("goalFive",False)
        db.execute("INSERT OR REPLACE INTO goalselect (user,goalOne,goalTwo,goalThree,goalFour,goalFive) VALUES (?,?,?,?,?,?);", [userID,goalOne,goalTwo,goalThree,goalFour,goalFive])
        db.commit()
    return render_template("goalSelect.html")

def showGoals(user):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM goalselect WHERE user=?",[user])
    results = cursor.fetchone()
    connection.close()
    return results

@app.route("/goals")
def index():
    user = showGoals(userID)
    return render_template("goalDisplay.html", usr = user)

@app.route("/temp")
def temp():
    return render_template("temp.html")
    
if __name__ == '__main__':
    app.run(debug=True)




