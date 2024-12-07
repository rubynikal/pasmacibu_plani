from flask import Blueprint, request, session, redirect, render_template, url_for
import sqlite3
from blueprints.all_plans import get_names_done

#konta lapa
acc_bp = Blueprint("acc", __name__)

@acc_bp.route("/<username>", methods=["GET","POST"])
def acc(username):
  """Veido konta lapu, izmantojot template acc.html. Lapā var apskatīt lietotāja radītāju tabulu un nodzēst kontu."""
  if "username" not in session:
    return redirect(url_for("login.login"))
  
  in_progress = []
  in_progress_st = []
  not_started_count = 0
  completed_count = 0

  #radītāju tabula
  names_dones = get_names_done(session["username"])
  for name in names_dones:
    done_st = list(map(int, name[1].split(','))) 

    if sum(done_st) == len(done_st):
      completed_count += 1
    elif sum(done_st) == 0:
      not_started_count += 1
    else:
      in_progress.append(name)
      in_progress_st.append((sum(done_st), len(done_st)))

  #konta dzēšana
  if request.method == "POST":
    with sqlite3.connect("users.db") as conn:
      cur = conn.cursor()
      cur.execute("PRAGMA foreign_keys = ON")
      cur.execute(" DELETE FROM Users WHERE username=? ", (username,))
      conn.commit()
    session.pop("username", None)
    return redirect("landing")
  
  return render_template("acc.html", logged_in=True, name=username, in_progress=in_progress, in_progress_st=in_progress_st, completed_count=completed_count, not_started_count=not_started_count)
  
