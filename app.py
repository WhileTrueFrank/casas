import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)

# @app.route("/")
# def home():
#     return "Hello, Railway!"

class StudentPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.String(200), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    team = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)

allowed_reasons = [
    "Vencer um jogo de perguntas e respostas em sala de aula.",
    "Avançar de fase em olimpíada do conhecimento.",
    "Melhor desempenho em um projeto de classe."
]

allowed_teams = ["Brasil", "Espanha", "Egito", "China"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        student_name = request.form['student_name']
        teacher_name = request.form['teacher_name']
        date = request.form['date']
        reason = request.form['reason']
        class_name = request.form['class_name']
        team = request.form['team']
        points = request.form['points']

        if reason not in allowed_reasons:
            return "Motivo inválido", 400

        if team not in allowed_teams:
            return "Equipe inválida", 400

        new_entry = StudentPoints(
            student_name=student_name,
            teacher_name=teacher_name,
            date=datetime.strptime(date, '%Y-%m-%d'),
            reason=reason,
            class_name=class_name,
            team=team,
            points=int(points)
        )
        
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))
    
    entries = StudentPoints.query.all()
    return render_template('index.html', entries=entries, allowed_reasons=allowed_reasons, allowed_teams=allowed_teams)

@app.route('/leaderboard')
def leaderboard():
    results = db.session.query(StudentPoints.team, func.sum(StudentPoints.points)).group_by(StudentPoints.team).all()
    team_scores = {team: score if score else 0 for team, score in results}
    
    for team in allowed_teams:
        if team not in team_scores:
            team_scores[team] = 0
    
    return render_template('leaderboard.html', team_scores=team_scores)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
