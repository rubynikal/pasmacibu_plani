from flask import Blueprint, request, session, redirect, render_template, url_for
import sqlite3
import google.generativeai as genai
import os
import regex
import datetime

#gemini api iestatījumi
os.environ["API_KEY"] = 'AIzaSyBgn8YiRnasLmPpQoDhc7TEcJpqO7LACuM'
genai.configure(api_key=os.environ["API_KEY"])

model_config = {
  "temperature": 0.7,
  "top_p": 1,
  "top_k": 5,
  "max_output_tokens": 10000,
}

instruction = """You are a highly qualified and very precise teacher from Latvia. You create detailed, interesting, diverse and useful study plans for your students, according to the Skola2030 standards. You do it in Latvian. And you always name the steps of your plans (like "Nr. ", "Solis", "Uzdevums", "Resursi")"""

model = genai.GenerativeModel('gemini-1.5-flash-latest', generation_config=model_config, system_instruction=instruction)

def gen_resp(temats, limenis, laiks, detalas):
  """Atgriež atbildi, izmantojot Gemini AI API un sarakstīto uzvedni."""
  response = model.generate_content(f"""
Hello! 
I am a student from Latvia and enjoy learning new things, but I struggle with planning and understanding what to study at each point.

Here is some information about me:
- I would like to learn (in Latvian): {temats}
- Some details about my current knoledge and objectives: {detalas}
- My level is: {limenis}
- I have this amount of time to study: {laiks}

Please create a detailed, diverse, and helpful study plan for me, following the Skola2030 standard in Latvia.

Response Formatting Rules:
1. Language: Write the entire study plan in Latvian.
2. Plan Structure:
   - First, provide a brief, short, condensed title for the study plan (e.g., “Programming Basics Plan”). Do not write any introduction for the plan. Just the name.
   - Then, provide a short introduction about the topic: where and why this topic would be used and which topics it is connected to. Label the introduction by writing "Ievads:".
   - List each study step in sequence, using "Nr. ..." as the label for each new step.
3. For Each Step:
   - Name each component within the step as follows:
      - Laiks: Specify the exact time required and the exact day for the task (considering the time frame given, without skipping days).
      - Solis: Describe the learning step (e.g., “Study data types”). Start with the easiest, progress to the harder ones. Be precise.
      - Uzdevums: Describe 3 exercises to practice this step. Make the exercises interesting and diverse. If the topic allows, give practical exercises and formulas. Between the exercises, write <br>.
      - Resursi: List recommended resources e.g., YouTube videos, exact websites with links, real books, or documents. Ensure the resources are functional, accurate, and suitable for the topic, give links to the sources if possible. Provide no less than 2-3 resources per step, one must be a link to a website. Between the sources, write <br>. 

4. Additional Requirements:
   - Ensure all steps are covered in the given timeframe.
   - You don't have to make one step the amount of hours I have, divide the time according to the step. But the entire plan must be the timeframe given.
   - Avoid skipping any days or shortening the given timeframe. 
   - Use the specific format and names for each component in each step (Ievads,Laiks, Solis, Uzdevums, Resursi).
   - Make every single step detailed and full.
   - The plan must have as many steps as there are days, each step full, with the components. Do not group the steps.
""")

  plans = response.text.replace("*", " ").replace("#", "").replace("|", "").replace("\n","").replace("[", " ").replace("]", " ")
  nosaukums = plans
  nosaukums = regex.sub(r'\d+\. diena', '', nosaukums.split("Ievads:")[0].strip()).strip()
  nosaukums = nosaukums + "; " + session["username"]
  ievads_start = plans.find("Ievads:")
  ievads_end = plans.find("Nr. 1") if "Nr. 1" in plans else len(plans)
  ievads = plans[ievads_start:ievads_end].strip() if ievads_start != -1 else ""
  c_ievads = regex.sub(r'\d+\. diena', '', ievads).strip()
  d_ievads = c_ievads.replace("Ievads:", "<span>Ievads:</span>")
  return [plans,d_ievads,nosaukums]

def formating(plans):
  """Atgriež pārformatēto Gemini atbildi divdimensiālā masīvā."""

  #sadalīt katru plāna daļu, tās sakās ar "Nr."
  solu_saraksts = regex.split(r"(?=Nr\.\s*\d+)", plans, flags=regex.DOTALL)

  #šablons, pēc kurā dalīt plānu uz daļām
  pattern = r"(Nr\.\s*\d+|Laiks:|Solis:|Uzdevums:|Resursi:)(.*?)(?=Nr\.\s*\d+|Laiks:|Solis:|Uzdevums:|Resursi:|$)"

  viss_plans = []
  #apstrādāt katru soli atsevišķi
  for solis in solu_saraksts:
    if solis.strip():
      matches = regex.findall(pattern, solis, regex.DOTALL)
      elements = [f"{match[0].strip()} {match[1].strip()}" for match in matches]
      viss_plans.append(elements)

  #noņemt iespējamus kļūdaimus sadalījumus
  correct_plan = []
  for plan in viss_plans:
    if plan == []:
      continue
    plan2 = [regex.sub(r'\d+\. diena', '', item).strip() for item in plan]
    correct_plan.append(plan2)

  result = []
  current = []  
    
  for item in correct_plan:
    #ja elements ir list, kas sastāv no 1 elementa 
    if isinstance(item, list) and len(item) == 1:
      #pievienot iepriekšējam elementam
      if current:
        current[-1] += " " + item[0]
    else:
      if current:
        result.append(current) 
      current = item  

  #pievienot finālāi masīva versijai
  if current:
    result.append(current)

  keywords = ["Nr.", "Laiks", "Solis", "Uzdevums", "Resursi"]

  def format_text(item):
    """Pārveido plāna soļus, lai būtu iespējams izmainīt atslēgvārdu stilu."""
    for keyword in keywords:
      if keyword == "Laiks":
        item = item.replace(keyword, f"<span>{keyword}</span>").replace(",","")
      else:
        item = item.replace(keyword, f"<span>{keyword}</span>")
    return item
  
  last_result = []
  
  for i in result:
    last_result.append([format_text(item) for item in i])

  return last_result

def remove_ltv(string): 
  """Noņem latviešu valodas simbolus no teksta"""
  latvian_to_english = {
    'ā': 'a', 'č': 'c', 'ē': 'e', 'ģ': 'g', 'ī': 'i', 'ķ': 'k',
    'ļ': 'l', 'ņ': 'n', 'š': 's', 'ū': 'u', 'ž': 'z'
  }
  
  string = string.lower()
  
  result = ""
  for char in string:
    if char in latvian_to_english:
      result += latvian_to_english[char]
    else:
      result += char

  return result

def compare_strings(str1, str2):
    """Salīdzina 2 tekstus, neņēmot vērā punktuāciju un citus simbolus."""

    #noņemt visus simbolus izņēmot burtus un ciparus
    cleaned_str1 = regex.sub(r'[^A-Za-z0-9]', '', str1).lower()
    cleaned_str2 = regex.sub(r'[^A-Za-z0-9]', '', str2).lower()
  
    return cleaned_str1 == cleaned_str2

def resources(nosaukums):
  """Pievieno papildresursus"""
  keyword = ["matematika","anglu", "latviesu", "biologija", "dabaszinibas", "datorika", "dizains", "tehnologijas", "fizika", "francu", "geografija", "krievu", "kimija", "vesture", "literatura", "muzika", "socialas", "kultura", "maksla", "sports", "veseliba", "programmesana", "vacu"]
  linki = ['<a href="https://skolo.lv/course/index.php?categoryid=7539">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7665">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7509">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7653">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7533">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7653">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7662">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7512">pamatskolai</a>, <a href="https://skolo.lv/course/view.php?id=190806">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7515">pamatskolai</a>, <a href="https://skolo.lv/course/view.php?id=353765">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7518">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7668">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7518">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7668">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7587">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7662">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7521">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7653">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7596">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7662">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7530">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7653">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7605">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7662">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7611">pamatskolai</a>, <a href="https://skolo.lv/course/index.php?categoryid=7659">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7536">pamatskolai</a>, <a href="https://skolo.lv/course/view.php?id=159636">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7545">pamatskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7659">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7656">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7656">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7671">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7671">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7668">vidusskolai</a>', '<a href="https://skolo.lv/course/index.php?categoryid=7653">vidusskolai</a>']
  
  nos = remove_ltv(nosaukums)
  nosaukums_dalas = nos.split()
  num = 0
  for i in nosaukums_dalas:
    if i in keyword:
      num = keyword.index(i)
      return "<br>Latvijas izglītības sistēmas oficiālie resursi šīm, vai ar to saistītiem tematiem: "+linki[num]
  return ""

jauns_bp = Blueprint("jauns", __name__)

@jauns_bp.route("/jauns", methods=["POST", "GET"])
def jauns():
  correct_plan = []
  nosaukums = ""
  ievads_d = ""
  tosave = {"plans": "", "nosaukums": "", "done_st": ""}
  if "username" not in session:
    return redirect(url_for("login.login"))
  if request.method == "POST":
    #dabūt ievadus
    temats = request.form["temats"]
    detalas = request.form["detalas"]
    dienas = request.form["dienas"]
    stundas = request.form["stundas"]
    limenis = request.form["zinlim"]

    laiks = f"{str(dienas)} dienas pa {str(stundas)} stundām dienā."
    
    #saglabāt request
    with sqlite3.connect("users.db") as conn:
      cur = conn.cursor()
      sql = " INSERT INTO Requests (temats, laiks, limenis, username, time) VALUES (?, ?, ?, ?, ?)"
      cur.execute(sql, (temats, laiks, limenis, session["username"], str(datetime.datetime.now())))

    #saglabāt pēdējos datus sessijā
    session["temats"] = temats
    session["laiks"] = laiks
    session["limenis"] = limenis
    session["detalas"] = detalas

    #pārbaudīt, vai lietotājam jau nav tāda plāna
    with sqlite3.connect("users.db") as conn:
      cur = conn.cursor()
      sql = " SELECT name FROM Plans WHERE username=? "
      cur.execute(sql, (session["username"],))

      result = cur.fetchall()

    planame = temats + "; " + session["username"]
    for i in result:
      if compare_strings(i[0], planame):
        return render_template("jauns.html", logged_in=True, plans=["",""], nosaukums="Jums jau ir plāns par šo tematu. Lūdzu, izvelieties citu!", tosave=tosave)

    if limenis == "uzsacejs":
      limenis = "a total beginner at this subject"
    elif limenis == "videjais":
      limenis = "intermediate at this subject"
    else:
      limenis = "a professional who wants to understand the subject deeply"
    
    #plāna ģenerēšana
    cycles = 0
    while True:
      resp = gen_resp(temats,laiks,limenis,detalas)
      plans = resp[0]
      ievads = resp[1]
      nosaukums = resp[2]
      cycles += 1
      if cycles >= 5: #ja ģenerācija nenostrādāja pareizi 5 reizes
        return render_template("jauns.html", logged_in=True, plans=["",""], nosaukums="Kļūda plāna ģenerēšanā. Lūdzu, izmainiet savas prasības vai atjaunojiet lapu un pamēģiniet vēlreiz.", tosave=tosave, ievads=ievads)
      if len(nosaukums) <= 120: #ja formātējums salūza, pārģenerēt
        break
    
    #plāna formatējums
    correct_plan = formating(plans)

    #progresa statusi
    done_st = ["0" for _ in range(len(correct_plan))]
    done_st = ",".join(done_st)

    nosaukums = temats + " - " + session["username"]
    ievads_d = ievads + resources(nosaukums)

    tosave = {"plans":plans, "nosaukums":nosaukums, "done_st": done_st}
        
  return render_template("jauns.html", logged_in=True, plans=correct_plan, nosaukums=nosaukums, tosave=tosave, ievads=ievads_d)

#plāna saglabāšana
save_bp = Blueprint("save", __name__)
@save_bp.route("/savereturn", methods=['POST'])
def save():
  """Saglabā plānu datubāzē."""
  if "username" not in session:
    return redirect(url_for("login.login"))
  
  plans = request.form.get("plans")
  nosaukums = request.form.get("nosaukums")
  done_st = request.form.get("done_st")

  with sqlite3.connect("users.db") as conn:
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO Plans (username, plan, name, done) 
      VALUES (?, ?, ?, ?)
    """, (session["username"], plans, nosaukums, done_st))
    conn.commit()

  return redirect("/visi_plani")

#reģenerēšana
regenerate_bp = Blueprint("regenerate", __name__)
@regenerate_bp.route("/regenerate", methods=['POST'])
def regenerate():
  """Reģenerē plānu ar tiem pašiem pieprasījumiem."""
  correct_plan = []
  tosave = {"plans": "", "nosaukums": "", "done_st": ""}
  ievads_d = ""
  if "username" not in session:
    return redirect(url_for("login.login"))
  
  #dabūt lietotāja pēdējo pieprasījumu
  temats = session.get("temats")
  laiks = session.get("laiks")
  limenis = session.get("limenis")
  detalas = session.get("detalas")

  if not temats or not laiks or not limenis or not detalas:
    return redirect(url_for("jauns")) 

  #ģenerēt plānu
  cycles = 0
  while True:
    resp = gen_resp(temats,laiks,limenis, detalas)
    plans = resp[0]
    ievads = resp[1]
    nosaukums = resp[2]
    cycles += 1

    if cycles >= 5: #ja ģenerācija nenostrādāja pareizi 5 reizes
      return render_template("jauns.html", logged_in=True, plans=["",""], nosaukums="Kļūda plāna ģenerēšanā. Lūdzu, izmainiet savas prasības vai atjaunojiet lapu un pamēģiniet vēlreiz.", tosave=tosave, ievads=ievads)
    if len(nosaukums) <= 120: #ja formātējums salūza, pārģenerēt
      break

  #plāna formatēšana
  correct_plan = formating(plans)
  done_st = ",".join(["0" for _ in range(len(correct_plan))])
  nosaukums = temats + " - " + session["username"]
  ievads_d = ievads + resources(nosaukums)

  tosave = {"plans": plans, "nosaukums": nosaukums, "done_st": done_st}

  return render_template("jauns.html", logged_in=True, plans=correct_plan, nosaukums=nosaukums, tosave=tosave, ievads=ievads_d)
