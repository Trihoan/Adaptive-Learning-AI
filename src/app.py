from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # TODO: check database sau
        return redirect(url_for("home"))

    return render_template("login.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # TODO: lưu database
        return redirect(url_for("login"))

    return render_template("register.html")


# ================= HOME =================
@app.route("/home")
def home():
    return render_template("home.html")


# ================= COURSE =================
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


# ================= QUIZ (có topic AI) =================
@app.route("/quiz")
def quiz():

    topic = request.args.get("topic")

    # 🔥 dữ liệu giả theo topic
    if topic == "nguon_goc":
        questions = [
            {"id": "q1", "text": "Nguồn gốc triết học là gì?", "A": "Ý thức", "B": "Thực tiễn", "C": "Tự nhiên", "correct": "B"},
            {"id": "q2", "text": "Triết học xuất hiện khi nào?", "A": "Cổ đại", "B": "Hiện đại", "C": "Trung đại", "correct": "A"},
            {"id": "q3", "text": "Nguồn gốc xã hội là gì?", "A": "Lao động", "B": "Tư duy", "C": "Tự nhiên", "correct": "A"}
        ]

    elif topic == "ban_chat":
        questions = [
            {"id": "q1", "text": "Bản chất triết học là gì?", "A": "Khoa học", "B": "Thế giới quan", "C": "Tự nhiên", "correct": "B"},
            {"id": "q2", "text": "Triết học nghiên cứu gì?", "A": "Xã hội", "B": "Con người", "C": "Quy luật chung", "correct": "C"},
            {"id": "q3", "text": "Vai trò triết học?", "A": "Định hướng", "B": "Giải trí", "C": "Kỹ thuật", "correct": "A"}
        ]

    else:
        questions = [
            {"id": "q1", "text": "Câu nâng cao 1?", "A": "A", "B": "B", "C": "C", "correct": "C"},
            {"id": "q2", "text": "Câu nâng cao 2?", "A": "A", "B": "B", "C": "C", "correct": "B"},
            {"id": "q3", "text": "Câu nâng cao 3?", "A": "A", "B": "B", "C": "C", "correct": "A"}
        ]

    return render_template("quiz.html", questions=questions, topic=topic)


# ================= RESULT =================
@app.route("/result", methods=["POST"])
def result():

    score = 0
    total = 3

    # 🔥 đáp án + topic (cốt lõi AI)
    answers = {
        "q1": {"correct": "A", "topic": "nguon_goc"},
        "q2": {"correct": "B", "topic": "ban_chat"},
        "q3": {"correct": "C", "topic": "lich_su"}
    }

    resultData = []

    for key in answers:
        user_answer = request.form.get(key)

        is_correct = user_answer == answers[key]["correct"]

        if is_correct:
            score += 1

        resultData.append({
            "topic": answers[key]["topic"],
            "correct": is_correct
        })

    # 🔥 chuyển sang recommend kèm data
    return redirect(url_for("recommend", data=json.dumps(resultData)))


# ================= RECOMMEND (AI PAGE) =================
@app.route("/recommend")
def recommend():

    data = request.args.get("data")

    if data:
        resultData = json.loads(data)
    else:
        resultData = []

    return render_template("recommend.html", resultData=resultData)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)