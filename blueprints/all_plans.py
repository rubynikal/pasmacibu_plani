from flask import Blueprint, request, session, redirect, render_template, url_for
import sqlite3

def get_names_done(username):
  """Atgriež visus lietotāja plānus nosaukumus un statusus."""
  with sqlite3.connect("users.db") as conn:
      cur = conn.cursor()
      sql = " SELECT name, done FROM Plans WHERE username=?"
      cur.execute(sql, (username,))

      result = cur.fetchall()
  conn.close()
  return result

#visu plānu lapa
visi_bp = Blueprint("visi", __name__)

@visi_bp.route("/visi_plani", methods=["POST", "GET"])
def visi():
  """Veido visu plānu lapu, izmantojot template visi.html. Lapā var apskatīt un piekļūt visiem plāniem, kas ir sadalīti kategorijās."""
  if "username" not in session:
    return redirect(url_for("login.login"))
  
  in_progress = []
  in_progress_st = []
  completed_plans = [] 
  completed_plans_st = []
  not_started = []
  not_started_st = []

  #tabulu veidošana - plāni, kas ir progresā, neuzsākti un uzsākti un progress tājos
  names_dones = get_names_done(session["username"])
  for name in names_dones:
    done_st = list(map(int, name[1].split(','))) 

    if sum(done_st) == len(done_st):
      completed_plans.append(name)
      completed_plans_st.append((sum(done_st), len(done_st)))
    elif sum(done_st) == 0:
      not_started.append(name)
      not_started_st.append((sum(done_st), len(done_st)))
    else:
      in_progress.append(name)
      in_progress_st.append((sum(done_st), len(done_st)))

  return render_template("visi.html", logged_in=True, in_progress=in_progress, not_started=not_started, completed_plans=completed_plans, in_progress_st=in_progress_st, not_started_st=not_started_st, completed_plans_st=completed_plans_st)