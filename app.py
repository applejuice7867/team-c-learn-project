import random
import re
from fractions import Fraction
from typing import Union, List, Dict, Any
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn
import os
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, auth as firebase_auth
except Exception:
    firebase_admin = None
    firebase_auth = None

app = FastAPI(title="EduPulse API")

# Setup Jinja2 templates pointing to the root directory
templates = Jinja2Templates(directory=".")

# Initialize Firebase Admin if service account key is available
if firebase_admin is not None:
    try:
        sa_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "firebase-service-account.json"
        if os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred)
            logging.info("Initialized Firebase Admin SDK using %s", sa_path)
        else:
            logging.info("Firebase service account not found at %s; skipping admin init", sa_path)
    except Exception as e:
        logging.exception("Failed to initialize Firebase Admin: %s", e)
else:
    logging.info("firebase_admin module not available; install firebase-admin for token verification")


# ==========================================
# PYDANTIC MODELS FOR REQUEST VALIDATION
# ==========================================

class MathGenRequest(BaseModel):
    grade: Union[str, int] = "k"
    count: int = Field(default=5, ge=1, le=200)
    topic: str = "mixed"
    questionType: str = "mixed"


class ImportQuestionsRequest(BaseModel):
    text: str = ""


# ==========================================
# HTML TEMPLATE ROUTES
# ==========================================


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")


@app.get("/math-generator", response_class=HTMLResponse)
async def math_generator(request: Request):
    return templates.TemplateResponse(
        request=request, name="math-generator.html"
    )


@app.get("/question-importer", response_class=HTMLResponse)
async def question_importer(request: Request):
    return templates.TemplateResponse(
        request=request, name="question-importer.html"
    )
# ==========================================
# API ENDPOINTS
# ==========================================

@app.post("/api/generate-math")
async def generate_math(payload: MathGenRequest, token=Depends(verify_firebase_token_from_header)):
    grade = payload.grade
    count = min(max(int(payload.count), 1), 200)
    topic = payload.topic
    question_type = payload.questionType
    questions = []

    grade_band = {
        "k": "k-2", "1": "k-2", "2": "k-2", "3": "3-5", "4": "3-5", 
        "5": "3-5", "6": "6-8", "7": "6-8", "8": "6-8", "9": "9-12", 
        "10": "9-12", "11": "9-12", "12": "9-12"
    }.get(str(grade), "9-12")

    grade_topics = {
        "k-2": ["arithmetic", "counting", "shapes"],
        "3-5": ["arithmetic", "fractions", "percentages", "word-problems", "geometry"],
        "6-8": ["arithmetic", "fractions", "percentages", "algebra", "geometry", "probability", "statistics", "exponents", "ratios"],
        "9-12": ["algebra", "geometry", "probability", "statistics", "functions", "sequences", "inequalities", "trigonometry", "calculus", "exponents"]
    }

    topic_pool = grade_topics.get(grade_band, grade_topics["9-12"])

    def build_question(selected_topic, kind, difficulty):
        def make_question(question_text, answer_value, explanation_text):
            return {"question": question_text, "answer": str(answer_value), "explanation": explanation_text}

        if kind == "true-false":
            if selected_topic == "arithmetic":
                a, b = random.randint(2, 8), random.randint(2, 8)
                return make_question(f"{a} + {b} = {a + b}.", True, "Check whether the equation is correct.")
            if selected_topic == "counting":
                return make_question("If you add 3 apples to 2 apples, you get 5 apples.", True, "Three plus two makes five.")
            if selected_topic == "shapes":
                shape_name = random.choice(["triangle", "square", "circle", "hexagon"])
                statement = "has three sides" if shape_name == "triangle" else "has four equal sides" if shape_name == "square" else "has no corners" if shape_name == "circle" else "has six sides"
                return make_question(f"A {shape_name} {statement}.", True, "Check the shape's defining properties.")
            if selected_topic == "fractions":
                return make_question("One half is equal to two quarters.", True, "Both represent the same amount of a whole.")
            if selected_topic == "percentages":
                return make_question("25% of 80 is 20.", True, "Twenty-five percent of eighty is twenty.")
            if selected_topic == "geometry":
                return make_question("A rectangle's area is length times width.", True, "Area is found by multiplying length and width.")
            if selected_topic == "probability":
                return make_question("The probability of an event is favorable outcomes divided by total outcomes.", True, "Probability compares favorable outcomes to all possible outcomes.")
            if selected_topic == "statistics":
                return make_question("The median is the middle value when data is ordered.", True, "The median is the middle of the ordered data set.")
            if selected_topic == "inequalities":
                return make_question("If x < 5, then x could be 4.", True, "4 is less than 5, so it satisfies the inequality.")
            if selected_topic == "algebra":
                return make_question("x + 3 = 7 means x = 4.", True, "Subtracting 3 from both sides gives x = 4.")
            return make_question("Word problems often require choosing the correct operation.", True, "Reading carefully helps you choose the right math step.")

        if kind == "multiple-select":
            if selected_topic == "arithmetic":
                a, b = random.randint(2, 8), random.randint(2, 8)
                correct = a + b
                choices = [str(correct), str(correct + 1), str(correct + 2), str(correct - 1)]
                random.shuffle(choices)
                return {"question": f"Select all values equal to {a} + {b}.", "answer": str(correct), "explanation": "Choose every value that matches the expression.", "choices": choices}
            if selected_topic == "fractions":
                choices = ["1/2", "2/4", "3/4", "1/3"]
                random.shuffle(choices)
                return {"question": "Select all fractions equal to one half.", "answer": "1/2,2/4", "explanation": "Equivalent fractions describe the same part of a whole.", "choices": choices}
            choices = ["2", "4", "6", "8"]
            random.shuffle(choices)
            return {"question": "Select all even numbers from the list.", "answer": "2,4,6,8", "explanation": "Even numbers can be divided by 2 with no remainder.", "choices": choices}

        if kind == "ordering":
            if selected_topic == "arithmetic":
                numbers = random.sample(range(1, 10), 4)
                return make_question(f"Put these numbers in order from least to greatest: {', '.join(map(str, numbers))}.", ", ".join(map(str, sorted(numbers))), "Arrange the values from smallest to largest.")
            if selected_topic == "fractions":
                numbers = ["1/4", "1/2", "3/4", "1"]
                return make_question(f"Put these fractions in order from least to greatest: {', '.join(numbers)}.", "1/4, 1/2, 3/4, 1", "Compare the size of each fraction.")
            return make_question("Put these values in order from least to greatest: 7, 2, 5, 3.", "2, 3, 5, 7", "Arrange the numbers from smallest to largest.")

        if selected_topic == "arithmetic":
            if grade_band == "k-2":
                variant = random.choice(["add", "subtract", "compare", "missing", "pattern", "before_after", "count_objects", "number_sentence"])
                if variant == "add":
                    a, b = random.randint(1, 15), random.randint(1, 15)
                    return make_question(f"{a} + {b} = ?", a + b, "Add the two numbers together.")
                if variant == "subtract":
                    a, b = random.randint(3, 18), random.randint(1, 12)
                    return make_question(f"{a} - {b} = ?", a - b, "Subtract the second number from the first.")
                if variant == "compare":
                    a, b = random.randint(1, 15), random.randint(1, 15)
                    return make_question(f"Which is greater: {a} or {b}?", max(a, b), "Compare the two values to see which is larger.")
                if variant == "missing":
                    total = random.randint(3, 15)
                    part = random.randint(1, total - 1)
                    return make_question(f"If you have {total} toys and {part} are red, how many are not red?", total - part, "Subtract the known part from the total.")
                if variant == "pattern":
                    start, step = random.randint(1, 6), random.randint(1, 3)
                    return make_question(f"Complete the pattern: {start}, {start + step}, {start + 2 * step}, ?", start + 3 * step, "Keep the same step size each time.")
                if variant == "count_objects":
                    a, b = random.randint(2, 6), random.randint(2, 6)
                    return make_question(f"How many objects are there in all if you have {a} blocks and {b} cubes?", a + b, "Count both groups and add them together.")
                if variant == "number_sentence":
                    a, b = random.randint(1, 9), random.randint(1, 9)
                    if kind == "fill-in-the-blank":
                        return make_question(f"{a} + {b} = ____", a + b, "Fill in the missing sum.")
                    return make_question(f"Which number sentence matches: {a} and {b} make {a + b}?", f"{a} + {b} = {a + b}", "A number sentence shows the two parts and the whole.")
                return make_question(f"Which number comes right after {random.randint(1, 10)}?", random.randint(1, 10) + 1, "Count one step forward.")
            if grade_band == "3-5":
                variant = random.choice(["multiply", "divide", "mixed", "estimate", "fact_family", "number_line", "missing_addend", "comparison"])
                if variant == "multiply":
                    a, b = random.randint(3, 12), random.randint(3, 12)
                    return make_question(f"{a} × {b} = ?", a * b, "Use multiplication facts to find the product.")
                if variant == "divide":
                    b = random.randint(2, 6)
                    ans = random.randint(2, 8)
                    a = b * ans
                    return make_question(f"{a} ÷ {b} = ?", ans, "Use division facts to split evenly.")
                if variant == "mixed":
                    a, b = random.randint(6, 20), random.randint(2, 8)
                    return make_question(f"{a} + {b} × 2 = ?", a + b * 2, "Multiply before adding.")
                if variant == "estimate":
                    a, b = random.randint(10, 80), random.randint(10, 80)
                    return make_question(f"Estimate {a} + {b} by rounding each to the nearest ten.", round(a, -1) + round(b, -1), "Round each number first, then add.")
                if variant == "fact_family":
                    a, b = random.randint(3, 9), random.randint(3, 9)
                    return make_question(f"If {a} × {b} = {a * b}, what is {a * b} ÷ {b}?", a, "Use the related multiplication and division facts.")
                if variant == "number_line":
                    start = random.randint(10, 50)
                    step = random.randint(5, 10)
                    return make_question(f"What number is {step} units to the right of {start} on a number line?", start + step, "Moving right on a number line increases the value.")
                if variant == "missing_addend":
                    total = random.randint(20, 100)
                    part = random.randint(5, total - 5)
                    return make_question(f"? + {part} = {total}", total - part, "Subtract the known addend from the sum.")
                return make_question(f"Which is smaller: {random.randint(100, 500)} or {random.randint(100, 500)}?", min(random.randint(100, 500), random.randint(100, 500)), "Compare place values starting from the hundreds digit.")
            a, b = random.randint(12, 40), random.randint(2, 12)
            return make_question(f"Evaluate: {a} - {b} × 2 + 6.", a - (b * 2) + 6, "Follow order of operations: multiply before adding and subtracting.")

        if selected_topic == "counting":
            questions_pool = [
                (f"Count the objects: {random.randint(5, 12)} stars and {random.randint(2, 6)} moons. How many objects are there altogether?", random.randint(5, 12) + random.randint(2, 6), "Count each group and add them together."),
                (f"If you start at {random.randint(1, 5)} and count forward {random.randint(3, 7)} steps, what number do you land on?", random.randint(1, 5) + random.randint(3, 7), "Count forward step by step."),
                (f"How many fingers are on {random.randint(2, 6)} hands?", random.randint(2, 6) * 5, "Count by fives for each hand."),
            ]
            q_text, q_ans, q_exp = random.choice(questions_pool)
            return make_question(q_text, q_ans, q_exp)

        if selected_topic == "fractions":
            variant = random.choice(["add", "subtract", "compare", "multiply", "convert", "share"])
            if variant in ["add", "subtract"]:
                denom = random.choice([2, 3, 4, 5, 6, 8, 10])
                num1 = random.randint(1, denom - 1)
                num2 = random.randint(1, denom - 1)
                if variant == "add":
                    ans = Fraction(num1 + num2, denom)
                    return make_question(f"{num1}/{denom} + {num2}/{denom} = ?", f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator), "Add the numerators while keeping the common denominator.")
                if num1 < num2:
                    num1, num2 = num2, num1
                ans = Fraction(num1 - num2, denom)
                return make_question(f"{num1}/{denom} - {num2}/{denom} = ?", f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator), "Subtract the numerators while keeping the common denominator.")
            if variant == "compare":
                a, b = random.randint(1, 5), random.choice([2, 3, 4, 6, 8])
                c, d = random.randint(1, 5), random.choice([2, 3, 4, 6, 8])
                f1, f2 = Fraction(a, b), Fraction(c, d)
                ans = f"{a}/{b}" if f1 > f2 else f"{c}/{d}"
                return make_question(f"Which is greater: {a}/{b} or {c}/{d}?", ans, "Find a common denominator or convert to decimals to compare.")
            if variant == "multiply":
                a, b = random.randint(1, 4), random.randint(2, 5)
                c, d = random.randint(1, 4), random.randint(2, 5)
                ans = Fraction(a, b) * Fraction(c, d)
                return make_question(f"{a}/{b} × {c}/{d} = ?", f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator), "Multiply numerators together and denominators together.")
            if variant == "convert":
                a, b = random.randint(1, 6), random.choice([2, 4, 5, 10])
                return make_question(f"Write {a}/{b} as a decimal.", str(a / b), "Divide the numerator by the denominator.")
            a = random.randint(4, 12)
            b = random.randint(2, 6)
            return make_question(f"Mia bought {a} pizzas and shared them among {b} friends. How much pizza does each friend get?", str(Fraction(a, b)), "Divide the total items by the number of people.")

        if selected_topic == "percentages":
            percent = random.choice([10, 20, 25, 50, 75])
            whole = random.choice([20, 40, 60, 80, 100, 120, 200])
            return make_question(f"What is {percent}% of {whole}?", int(whole * (percent / 100)), "Convert percent to a decimal or fraction and multiply by the whole.")

        if selected_topic == "algebra":
            variant = random.choice(["linear", "two_step", "combine", "evaluate", "distribute", "factor"])
            if variant == "linear":
                x = random.randint(-10, 10)
                a = random.choice([2, 3, 4, 5])
                b = random.randint(-15, 15)
                c = a * x + b
                return make_question(f"Solve for x: {a}x + {b} = {c}.", x, "Subtract the constant term, then divide by the coefficient.")
            if variant == "two_step":
                x = random.randint(1, 8)
                a = random.choice([2, 3, 4])
                b = random.randint(1, 10)
                return make_question(f"Solve for x: ({a}x + {b}) / 2 = {int((a * x + b) / 2)}.", x, "Multiply by 2 first, then isolate x.")
            if variant == "combine":
                a, b, c = random.randint(2, 8), random.randint(1, 6), random.randint(1, 5)
                return make_question(f"Simplify: {a}x + {b}x - {c}x.", f"{a + b - c}x", "Combine like terms by adding or subtracting coefficients.")
            if variant == "evaluate":
                x = random.randint(2, 6)
                a, b = random.randint(2, 5), random.randint(1, 10)
                return make_question(f"Evaluate {a}x² - {b} when x = {x}.", a * (x ** 2) - b, "Substitute the value of x and follow order of operations.")
            if variant == "distribute":
                a, b, c = random.randint(2, 5), random.randint(1, 6), random.randint(1, 6)
                return make_question(f"Expand: {a}({b}x + {c}).", f"{a * b}x + {a * c}", "Multiply the outer term by each term inside the parentheses.")
            a = random.randint(2, 5)
            b = random.randint(2, 6)
            return make_question(f"Factor: x² + {a + b}x + {a * b}.", f"(x + {a})(x + {b})", "Find two numbers that multiply to the constant and add to the coefficient of x.")

        if selected_topic == "geometry":
            variant = random.choice(["rectangle_area", "triangle_area", "perimeter", "circle_circumference", "missing_angle", "volume"])
            if variant == "rectangle_area":
                l, w = random.randint(3, 15), random.randint(2, 10)
                return make_question(f"Find the area of a rectangle with length {l} and width {w}.", l * w, "Multiply length by width.")
            if variant == "triangle_area":
                b, h = random.randint(4, 14), random.randint(2, 10)
                return make_question(f"Find the area of a triangle with base {b} and height {h}.", (b * h) / 2, "Multiply base by height and divide by 2.")
            if variant == "perimeter":
                s1, s2, s3 = random.randint(3, 9), random.randint(3, 9), random.randint(3, 9)
                return make_question(f"Find the perimeter of a triangle with sides {s1}, {s2}, and {s3}.", s1 + s2 + s3, "Add the lengths of all outer sides.")
            if variant == "circle_circumference":
                r = random.choice([7, 14, 21])
                return make_question(f"Find the approximate circumference of a circle with radius {r} (use π ≈ 22/7).", int(2 * (22 / 7) * r), "Use the formula C = 2πr.")
            if variant == "missing_angle":
                a, b = random.randint(30, 80), random.randint(30, 80)
                return make_question(f"In a triangle, two angles are {a}° and {b}°. What is the third angle?", 180 - (a + b), "The interior angles of a triangle add up to 180°.")
            l, w, h = random.randint(2, 6), random.randint(2, 6), random.randint(2, 6)
            return make_question(f"Find the volume of a rectangular prism with dimensions {l} × {w} × {h}.", l * w * h, "Multiply length, width, and height.")

        if selected_topic == "word-problems":
            variant = random.choice(["shopping", "distance", "reading", "sharing"])
            if variant == "shopping":
                price = random.randint(3, 12)
                qty = random.randint(2, 6)
                paid = qty * price + random.choice([5, 10])
                return make_question(f"A book costs ${price}. Leo buys {qty} books and pays with a ${paid} bill. How much change does he get?", paid - (qty * price), "Multiply price by quantity, then subtract from amount paid.")
            if variant == "distance":
                speed = random.choice([30, 40, 50, 60])
                hours = random.randint(2, 5)
                return make_question(f"A car travels at {speed} mph for {hours} hours. How far does it go?", speed * hours, "Use distance = speed × time.")
            if variant == "reading":
                total = random.choice([100, 120, 150, 200])
                per_day = random.choice([10, 15, 20, 25])
                return make_question(f"Nora is reading a {total}-page book. If she reads {per_day} pages a day, how many days will it take her to finish?", total // per_day, "Divide total pages by pages read per day.")
            total_candies = random.randint(20, 50)
            friends = random.randint(3, 7)
            return make_question(f"Liam has {total_candies} candies to share equally among {friends} friends. How many candies are left over?", total_candies % friends, "Use the remainder after division.")

        if selected_topic == "probability":
            variant = random.choice(["dice", "coins", "marbles", "spinners"])
            if variant == "dice":
                target = random.choice(["an even number", "a number greater than 4", "a 6"])
                ans = "1/2" if target == "an even number" else "1/3" if target == "a number greater than 4" else "1/6"
                return make_question(f"When rolling a fair 6-sided die, what is the probability of rolling {target}?", ans, "Count favorable outcomes and divide by 6 possible outcomes.")
            if variant == "coins":
                return make_question("If you flip two fair coins, what is the probability of getting two heads?", "1/4", "Each coin has a 1/2 chance; multiply 1/2 × 1/2.")
            if variant == "marbles":
                red, blue = random.randint(2, 5), random.randint(2, 5)
                total = red + blue
                return make_question(f"A bag contains {red} red marbles and {blue} blue marbles. What is the probability of picking a red marble?", f"{red}/{total}", "Divide red marbles by total marbles.")
            return make_question("A spinner has 4 equal sections labeled red, blue, green, and yellow. What is the probability of landing on blue?", "1/4", "There is 1 blue section out of 4 total sections.")

        if selected_topic == "statistics":
            variant = random.choice(["mean", "median", "range", "mode"])
            data = [random.randint(2, 15) for _ in range(5)]
            if variant == "mean":
                data = [x * 2 for x in random.sample(range(1, 10), 5)]
                return make_question(f"Find the mean of this data set: {', '.join(map(str, data))}.", sum(data) // len(data), "Add all values and divide by the number of values.")
            if variant == "median":
                sorted_data = sorted(data)
                return make_question(f"Find the median of this data set: {', '.join(map(str, data))}.", sorted_data[len(sorted_data) // 2], "Order the numbers from least to greatest and pick the middle value.")
            if variant == "range":
                return make_question(f"Find the range of this data set: {', '.join(map(str, data))}.", max(data) - min(data), "Subtract the smallest value from the largest value.")
            val = random.randint(3, 9)
            data = [val, val, random.randint(1, 2), random.randint(10, 12)]
            random.shuffle(data)
            return make_question(f"Find the mode of this data set: {', '.join(map(str, data))}.", val, "The mode is the number that appears most frequently.")

        if selected_topic == "exponents":
            variant = random.choice(["power", "product_rule", "zero_exponent", "expanded"])
            if variant == "power":
                base, exp = random.randint(2, 6), random.randint(2, 4)
                return make_question(f"Evaluate: {base}^{exp}.", base ** exp, "Multiply the base by itself exponent times.")
            if variant == "product_rule":
                base = random.choice(["x", "y", "a"])
                e1, e2 = random.randint(2, 5), random.randint(2, 5)
                return make_question(f"Simplify: {base}^{e1} × {base}^{e2}.", f"{base}^{e1 + e2}", "When multiplying powers with the same base, add the exponents.")
            if variant == "zero_exponent":
                val = random.randint(5, 50)
                return make_question(f"Evaluate: {val}^0.", 1, "Any non-zero number raised to the zero power equals 1.")
            return make_question("Write 5^3 as a product of factors.", "5 × 5 × 5", "An exponent tells how many times to multiply the base by itself.")

        return make_question("What is 2^3 + 4?", 12, "Evaluate exponent first, then add.")

    for _ in range(count):
        selected_topic = random.choice(topic_pool) if topic == "mixed" else topic
        if topic != "mixed" and selected_topic not in topic_pool:
            selected_topic = topic_pool[0]

        kind = random.choice(["multiple-choice", "fill-in-the-blank", "true-false", "ordering", "multiple-select"]) if question_type == "mixed" else question_type
        difficulty = random.choice(["easy", "medium", "hard"])
        question = build_question(selected_topic, kind, difficulty)

        question["topic"] = selected_topic
        question["difficulty"] = difficulty
        question["type"] = kind

        if kind in ["multiple-choice", "multiple-select", "true-false"]:
            if selected_topic == "arithmetic":
                try:
                    num_ans = int(question["answer"])
                    distractors = [str(num_ans + 1), str(num_ans - 1), str(num_ans + 2)]
                except ValueError:
                    distractors = ["10", "12", "15"]
            elif selected_topic == "fractions":
                distractors = [str(Fraction(1, 2)), str(Fraction(3, 4)), str(Fraction(1, 4))]
            elif selected_topic == "probability":
                distractors = ["1/2", "2/3", "3/4"]
            elif selected_topic == "shapes":
                distractors = ["Square", "Circle", "Hexagon"]
            elif kind == "true-false":
                distractors = ["True", "False"]
            else:
                distractors = ["2", "3", "4"]

            if kind == "true-false":
                choices = ["True", "False"]
            else:
                choices = [str(question["answer"])] + [str(choice) for choice in distractors if str(choice) != str(question["answer"])]
                random.shuffle(choices)
            question["choices"] = choices

        questions.append(question)

    return {"status": "success", "questions": questions}


@app.post("/api/import-questions")
async def import_questions(payload: ImportQuestionsRequest, token=Depends(verify_firebase_token_from_header)):
    raw_text = payload.text
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    parsed = []

    for line in lines:
        clean_line = re.sub(r"^(Q?\d+[\.\)\:]?|\-|\*)\s*", "", line, flags=re.IGNORECASE)
        if len(clean_line) > 3:
            parsed.append({
                "question": clean_line, 
                "answer": "To be determined", 
                "explanation": "Imported item. Add custom explanation or review manually.", 
                "choices": [clean_line, "True", "False", "None of the above"]
            })

    return {"status": "success", "questions": parsed[:50]}


# Verify Firebase token helper and endpoint
def verify_firebase_token_from_header(request: Request):
    """Dependency to verify Firebase ID token from Authorization header.

    Returns decoded token dict on success, raises HTTPException on failure.
    """
    if firebase_admin is None or firebase_auth is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Firebase Admin not configured on server")

    auth_header = request.headers.get("Authorization") or ""
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")

    id_token = auth_header.split(" ", 1)[1].strip()
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid ID token: {e}")


@app.post("/api/verify-token")
async def api_verify_token(request: Request):
    """Verify a Firebase ID token provided either in JSON {idToken} or Authorization: Bearer <token> header."""
    # Try header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        if firebase_admin is None or firebase_auth is None:
            return JSONResponse({"status": "error", "message": "Firebase Admin not available on server"}, status_code=501)
        id_token = auth_header.split(" ", 1)[1].strip()
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            return {"status": "success", "user": decoded}
        except Exception as e:
            return JSONResponse({"status": "error", "message": f"Invalid token: {e}"}, status_code=401)

    body = await request.json()
    id_token = body.get("idToken")
    if not id_token:
        return JSONResponse({"status": "error", "message": "No idToken provided"}, status_code=400)

    if firebase_admin is None or firebase_auth is None:
        return JSONResponse({"status": "error", "message": "Firebase Admin not available on server"}, status_code=501)

    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return {"status": "success", "user": decoded}
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Invalid token: {e}"}, status_code=401)


# ==========================================
# STATIC FILE SERVING (MOUNT LAST)
# ==========================================
# Mount the root folder to serve app.js, styles.css, etc.
app.mount("/", StaticFiles(directory=".", html=False), name="static")


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)