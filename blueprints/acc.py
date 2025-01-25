{% extends  "base.html" %}
{% block title %} {{ name }} {% endblock %}

{% block content %}
  <div class="account">
    <h1>{{ name }}</h1>
    <button id="theme-toggle">Izmainīt tēmu</button>
    <h3>Plāni, kas ir progresā</h3>
    <table>
      <tr>
        <th>Plāna nosaukums</th>
        <th>Progress</th>
      </tr>
      {% for i in range(in_progress|length) %}
      <tr>
        <td><a href="{{ url_for('single.single', nosaukums=in_progress[i][0]) }}">{{in_progress[i][0]}}</a></td>
        <td><progress value="{{ in_progress_st[i][0] }}" max="{{ in_progress_st[i][1] }}"></progress></td>
      </tr>
      {% endfor %}
    </table> 
    <h3> Jūs pabeidzāt {{completed_count}} plānus, un Jums ir {{not_started_count}} neuzsākti plani! </h3>
    <hr> <br>
    <form method="POST">
      <button type="submit">Nodzēst kontu</button>
    </form>
    <p>*Šī darbība ir neatgriezeniskā. Visi uzģenerēti plāni arī tiks nodzēsti.</p>
  </div>

  <script>
    document.addEventListener('DOMContentLoaded', function () {
      const themeToggle = document.getElementById('theme-toggle');
      const currentTheme = localStorage.getItem('theme');

      if (currentTheme === 'light') {
        document.documentElement.classList.add('light-mode');
      }

      themeToggle.addEventListener('click', function () {
        const isLightMode = document.documentElement.classList.contains('light-mode');

        if (isLightMode) {
          document.documentElement.classList.remove('light-mode');
          localStorage.setItem('theme', 'dark');
        } else {
          document.documentElement.classList.add('light-mode');
          localStorage.setItem('theme', 'light');
        }
      });
    });

  </script>
  
{% endblock %}
