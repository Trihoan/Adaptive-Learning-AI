from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # sau này sẽ kiểm tra database ở đây

        return redirect(url_for("home"))

    return render_template("login.html")


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # sau này sẽ lưu user vào database

        return redirect(url_for("login"))

    return render_template("register.html")


# HOME PAGE
@app.route("/home")
def home():
    return render_template("home.html")


# COURSE PAGE
@app.route("/course/<course_name>")
def course(course_name):

    if course_name == "triethoc":

        chapters = [
            "Chương 1: Vật chất và ý thức",
            "Chương 2: Phép biện chứng",
            "Chương 3: Chủ nghĩa duy vật lịch sử"
        ]

        course_title = "Triết học Mác - Lênin"

    else:
        chapters = []
        course_title = "Unknown"

    return render_template(
        "course.html",
        course_title=course_title,
        chapters=chapters
    )


# QUIZ PAGE
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


# RESULT PAGE (xử lý khi bấm Nộp bài)
@app.route("/result", methods=["POST"])
def result():

    score = 0
    total = 3

    # đáp án đúng
    answers = {
        "q1": "A",
        "q2": "B",
        "q3": "C"
    }

    # kiểm tra đáp án
    for key in answers:
        user_answer = request.form.get(key)

        if user_answer == answers[key]:
            score += 1

    return render_template(
        "result.html",
        score=score,
        total=total
    )


if __name__ == "__main__":
    app.run(debug=True)