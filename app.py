from flask import Flask, g, render_template, request, make_response
import sqlite3

app = Flask(__name__)

def connectDB():
    sql=sqlite3.connect('./loginDatabase.db')
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

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/create_account', methods=["GET","POST"])
def create_account():
    if request.method == "POST":
        db = getDB()
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Create table if it does not exist
        db.execute('INSERT INTO Login (username, email, password) VALUES (?,?,?);',[username,email,password])
        db.commit()
    return render_template("accountCreation.html")

if __name__ == '__main__':
    app.run(debug=True)