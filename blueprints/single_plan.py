from flask import Blueprint, request, session, redirect, render_template, url_for
import sqlite3
from blueprints.jauns_plans import formating

#viena plāna lapa
single_bp = Blueprint("single", __name__)

@single_bp.route("/plan/<nosaukums>", methods=["POST", "GET"])
def single(nosaukums):
  """Veido viena plāna lapu, izmantojot template plan.html. Lapā var apskatīt visus plāna soļus, atzīmēt un pārskatīt progresu."""
  if "username" not in session:
    return redirect(url_for("login.login"))
  
  #dabūt plāna detāļas no datubāzes
  with sqlite3.connect("users.db") as conn:
    cur = conn.cursor()
    sql = f" SELECT * FROM Plans WHERE name=? AND username=? "
    cur.execute(sql, (nosaukums,session["username"]))
    plans = cur.fetchone()
  
  if plans:
    #ja plāns tika atrasts
    nosaukums = plans[2]
    correct_plans = formating(plans[1])

    #pārveidot statusus listā
    done_st = list(map(int, plans[3].split(','))) 

    #ja kāds solis tika atzīmēts
    if request.method == "POST": 
      for i in range(len(correct_plans)):
        step_status = request.form.get(f"step_{i}")
        if step_status is not None: #ja solis tika atzīmēts
          #izmainīt izpildījuma statusu
          done_st[i] = 1 if done_st[i] == 0 else 0

          #atjaunot statusus datubāzē
          done_st_str = ",".join(map(str, done_st))

          with sqlite3.connect("users.db") as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Plans SET done=? WHERE name=? AND username=?", (done_st_str, nosaukums, session["username"]))
            conn.commit()

    completed = sum(done_st)
    total = len(done_st)
    perc = int((completed/total)*100)

    return render_template("plan.html", logged_in=True, nosaukums=nosaukums, plans=correct_plans, statuses=done_st, completed=completed, total=total, perc=perc)
    
  else:
    return "Plan not found", 404
  
#plāna dzēšana
delete_bp = Blueprint("delete",__name__)

@delete_bp.route("/plan/delete/<nosaukums>", methods=["POST"])
def delete(nosaukums):
  """Nodzēs mācību plānu"""
  if "username" not in session:
    return redirect(url_for("landing"))

  with sqlite3.connect("users.db") as conn:
    cur = conn.cursor()
    cur.execute("DELETE FROM Plans WHERE name=? AND username=?", (nosaukums,session["username"]))
    conn.commit()
    
  return redirect(url_for("visi.visi"))

