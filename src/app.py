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


# HOME PAGE (dashboard)
@app.route("/home")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)