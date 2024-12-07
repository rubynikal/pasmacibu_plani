from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from blueprints.auth import login_bp, register_bp, logout_bp
from blueprints.jauns_plans import jauns_bp, save_bp, regenerate_bp
from blueprints.all_plans import visi_bp
from blueprints.single_plan import single_bp, delete_bp
from blueprints.acc import acc_bp

#datubāzes izveide
with sqlite3.connect("users.db") as conn:
    cur = conn.cursor()
    
    sql = """CREATE TABLE IF NOT EXISTS Users (
      username TEXT PRIMARY KEY,
      password TEXT
    )"""
    cur.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS Plans (
      username TEXT,
      plan TEXT,
      name TEXT,
      done TEXT,
      PRIMARY KEY(name),
      FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE
    )"""
    cur.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS Requests (
    temats TEXT,
    laiks TEXT,
    limenis TEXT,
    username TEXT,
    time TEXT
    )"""
    cur.execute(sql)


app = Flask(__name__, instance_relative_config=True, static_folder='static')
app.config.from_mapping(
  SECRET_KEY='dev',
)

#sākumlapa
@app.route('/')
def landing():
  if "username" in session:
    return render_template("landing.html", logged_in=True)
  else:
    return render_template("landing.html", logged_in=False)

#visu pārējo lapu ielādēšana
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(jauns_bp)
app.register_blueprint(visi_bp)
app.register_blueprint(save_bp)
app.register_blueprint(single_bp)
app.register_blueprint(delete_bp)
app.register_blueprint(regenerate_bp)
app.register_blueprint(acc_bp)

if __name__ == '__main__':
  app.run(debug=True)
