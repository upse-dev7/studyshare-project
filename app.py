from flask import Flask ,redirect , url_for , flash , render_template , request, send_from_directory , session
import sqlite3
import os
import datetime

os.makedirs("uploads", exist_ok=True)
app = Flask(__name__)
app.secret_key = "secret123"
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO users (name,email,password) VALUES (?,?,?)",
        (name,email,password)
        )

        conn.commit()
        conn.close()

        return render_template("register.html", message = "Registration Successful")

    return render_template("register.html")

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS materials (
id INTEGER PRIMARY KEY AUTOINCREMENT,
filename TEXT,
user TEXT,
date TEXT
)
""")

conn.commit()
conn.close()

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]                                             

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email,password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session["user"] = email
            return render_template("dashboard.html")
        else:
            return render_template("login.html", message = "Invalid Email or Password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("logout.html", message = "Logged out successfully!")

@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html")
    else:
        flash( "please login first!")
        return redirect(url_for("login"))        
UPLOAD_FOLDER="uploads"
@app.route("/upload",methods=["GET","POST"])
def upload():
     
      if "user" not in session:
        flash("Please login first!")
        return redirect(url_for("login"))
      
      if request.method == "POST":

        file = request.files["file"]
        filename = file.filename
        current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        file.save(os.path.join(UPLOAD_FOLDER, filename))

#  upload details save in database

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO materials (filename,user,date) VALUES (?,?,?)",
        (filename, session["user"], current_time)
        )

        conn.commit()
        conn.close()

        return render_template("upload.html", message = "File Uploaded Successfully")
      return render_template("upload.html")

@app.route("/materials")
def materials():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM materials")
    data = cursor.fetchall()

    conn.close()

    return render_template("materials.html", data=data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route("/delete/<filename>")
def delete_file(filename):

    if "user" not in session:
       flash ("please login first")
       return redirect(url_for("login"))

    # file delete from folder
    path = os.path.join("uploads", filename)
    if os.path.exists(path):
        os.remove(path)

    # delete from database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM materials WHERE filename=?", (filename,))

    conn.commit()
    conn.close()

    return render_template("materials.html", data=[], message="File Deleted Successfully")
    

if __name__ == "__main__":
    app.run(debug=True)