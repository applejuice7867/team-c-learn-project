import random
import re
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__, static_folder=".", static_url_path="", template_folder=".")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/generate-math", methods=["POST"])
def generate_math():
    data = request.json
    grade = data.get("grade", "k-2")
    count = int(data.get("count", 5))
    questions = []

    for _ in range(count):
        if grade == "k-2":
            a, b = random.randint(1, 15), random.randint(1, 15)
            op = random.choice(["+", "-"])
            if op == "-" and a < b:
                a, b = b, a
            ans = a + b if op == "+" else a - b
            q_text = f"{a} {op} {b} = ?"
        elif grade == "3-5":
            op = random.choice(["+", "-", "*", "/"])
            if op in ["+", "-"]:
                a, b = random.randint(20, 100), random.randint(10, 50)
                ans = a + b if op == "+" else a - b
            elif op == "*":
                a, b = random.randint(3, 12), random.randint(3, 12)
                ans = a * b
            else:
                b = random.randint(2, 10)
                ans = random.randint(2, 12)
                a = b * ans
            q_text = f"{a} {op} {b} = ?"
        elif grade == "6-8":
            x = random.randint(-10, 10)
            a = random.randint(2, 9)
            b = random.randint(-15, 15)
            c = a * x + b
            op_str = f"+ {b}" if b >= 0 else f"- {abs(b)}"
            q_text = f"Solve for x: {a}x {op_str} = {c}"
            ans = f"x = {x}"
        else:  # 9-12 (Algebra & Quadratics)
            r1, r2 = random.randint(-7, 7), random.randint(-7, 7)
            b = -(r1 + r2)
            c = r1 * r2
            b_str = f"+ {b}x" if b > 0 else (f"- {abs(b)}x" if b < 0 else "")
            c_str = f"+ {c}" if c > 0 else (f"- {abs(c)}" if c < 0 else "")
            q_text = f"Find the roots of: x² {b_str} {c_str} = 0"
            ans = f"x = {r1}, x = {r2}" if r1 != r2 else f"x = {r1}"

        questions.append({"question": q_text, "answer": str(ans)})

    return jsonify({"status": "success", "questions": questions})


@app.route("/api/import-questions", methods=["POST"])
def import_questions():
    data = request.json
    raw_text = data.get("text", "")
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    parsed = []

    for line in lines:
        clean_line = re.sub(r"^(Q?\d+[\.\)\:]?|\-|\*)\s*", "", line, flags=re.I)
        if clean_line:
            parsed.append({"question": clean_line, "status": "Ready to assign"})

    return jsonify({"status": "success", "imported": parsed})


if __name__ == "__main__":
    app.run(debug=True, port=5000)