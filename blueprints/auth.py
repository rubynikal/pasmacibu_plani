from flask import Blueprint, request, session, redirect, render_template, url_for
import sqlite3
import bcrypt

#login lapa
login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["POST", "GET"])
def login():
  """Veido autorizācijas lapu, izmantojot template login.html"""
  if "username" in session:
    return redirect(url_for("landing"))

  if request.method == "POST":
    #dabūt username un password
    name = request.form["name"]
    password = request.form["password"]

    #atrast username ar password datubāzē
    with sqlite3.connect("users.db") as conn:
      cur = conn.cursor()
      sql = " SELECT username, password FROM Users WHERE username=?"
      cur.execute(sql, (name,))

      result = cur.fetchone()

    if result is None:
      #tāda lietotāja nav
      return render_template("login.html", error="Lietotājvārds vai parole nav pareizi :(")
    
    st_username, st_password = result

    if isinstance(st_password, str):
      st_password = st_password.encode('utf-8')

    if bcrypt.checkpw(password.encode('utf-8'), st_password):
      #parole ir pareiza
      session["username"] = st_username
      return redirect("/")
    else:
      #parole nav pareiza
      return render_template("login.html", error="Lietotājvārds vai parole nav pareizi :(")

  #ja forma netika iesniegta, radīt logina lapu
  return render_template("login.html")

#registrācijas lapa
register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["POST", "GET"])
def register():
  """Veido reģistrācija lapu, izmantojot template register.html"""

  if "username" in session:
    return redirect(url_for("landing"))
  #ja forma tika iesniegta
  if request.method == "POST":
    #dabūt username un password
    name = request.form["name"]
    password = request.form["password"]
    
    #pārbaudīt, vai datubāzē nav lietotāja ar tādu pašu username
    with sqlite3.connect("users.db") as conn:
      cur = conn.cursor()
      cur.execute(" SELECT username FROM Users WHERE username=? ",(name,))

      result = cur.fetchall()
      
      #ja tāds lietotājs ir, tad atgriezt reģistrācijas lapu ar lūgumu izmainīt lietotājvārdu vai ielogoties
      if len(result) != 0:
        return render_template("register.html", error="Atvainojiet, šīs lietotājvārds jau ir aizņemts! Lūdzu, pamēģiniet citu, vai ielogojieties! :)")
      else: #ja tāda lietotāja nav, tad reģistrēt jauno lietotāju datubāzē
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sql = " INSERT INTO Users VALUES (?, ?) "
        cur.execute(sql, (name, hashed))
        conn.commit()
        return render_template("register.html", error="Jūsu konts tika izveidots! Lūdzu, ielogojieties! :)")
  #ja forma netika iesniegta, radīt logina lapu
  return render_template("register.html")

#izlogošanās
logout_bp = Blueprint("logout", __name__)

@logout_bp.route("/logout")
def logout():
  """Izlogo lietotāju no konta"""

  session.pop("username", None)
  return redirect(url_for('landing')) 