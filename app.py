import random
import re
from fractions import Fraction
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


@app.route("/math-generator")
def math_generator():
    return render_template("math-generator.html")


@app.route("/question-importer")
def question_importer():
    return render_template("question-importer.html")


@app.route("/api/generate-math", methods=["POST"])
def generate_math():
    data = request.json or {}
    grade = data.get("grade", "k")
    count = min(max(int(data.get("count", 5)), 1), 200)
    topic = data.get("topic", "mixed")
    question_type = data.get("questionType", "mixed")
    questions = []

    grade_band = {"k": "k-2", "1": "k-2", "2": "k-2", "3": "3-5", "4": "3-5", "5": "3-5", "6": "6-8", "7": "6-8", "8": "6-8", "9": "9-12", "10": "9-12", "11": "9-12", "12": "9-12"}.get(str(grade), "9-12")

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
                    a, b = random.randint(10, 40), random.randint(5, 15)
                    return make_question(f"Estimate: {a} + {b} ≈ ?", a + b, "Estimate by rounding to the nearest convenient value.")
                if variant == "fact_family":
                    a, b = random.randint(2, 9), random.randint(2, 9)
                    return make_question(f"If {a} × {b} = {a * b}, what is {a * b} ÷ {b}?", a, "Use the related multiplication and division facts.")
                if variant == "missing_addend":
                    total = random.randint(8, 20)
                    addend = random.randint(2, 8)
                    if kind == "fill-in-the-blank":
                        return make_question(f"{addend} + ____ = {total}", total - addend, "Find the missing addend by subtracting.")
                    return make_question(f"What number makes {addend} + ? = {total}?", total - addend, "Subtract the known addend from the total.")
                if variant == "comparison":
                    a, b = random.randint(5, 15), random.randint(5, 15)
                    return make_question(f"Which is larger: {a} or {b}?", max(a, b), "Compare the two values directly.")
                return make_question(f"What is {random.randint(5, 15)} more than {random.randint(1, 10)}?", random.randint(1, 10) + random.randint(5, 15), "Add the extra amount to the starting number.")
            variant = random.choice(["ops", "order", "word", "ratio", "inequality", "expression", "decimal"])
            if variant == "ops":
                a, b, c = random.randint(2, 9), random.randint(2, 9), random.randint(2, 9)
                return make_question(f"{a} + {b} × {c} = ?", a + b * c, "Use the order of operations.")
            if variant == "order":
                a, b, c = random.randint(3, 10), random.randint(2, 8), random.randint(2, 8)
                return make_question(f"({a} + {b}) × {c} = ?", (a + b) * c, "Work inside parentheses first.")
            if variant == "word":
                a, b = random.randint(12, 30), random.randint(4, 9)
                return make_question(f"A class has {a} students and each table seats {b}. How many tables are needed?", (a + b - 1) // b, "Divide and round up for the remaining students.")
            if variant == "ratio":
                a, b = random.randint(4, 12), random.randint(2, 6)
                return make_question(f"How much is {a} groups of {b}?", a * b, "Multiply the group size by the number of groups.")
            if variant == "expression":
                a, b = random.randint(3, 9), random.randint(2, 6)
                return make_question(f"Write an expression for the total of {a} and {b}.", f"{a} + {b}", "An expression shows the math relationship without solving it.")
            if variant == "decimal":
                a = random.randint(10, 90)
                return make_question(f"What is {a} divided by 10?", a / 10, "Move the decimal one place left when dividing by 10.")
            return make_question(f"Choose the sign that makes the statement true: {random.randint(2, 8)} __ {random.randint(2, 8)}", "<" if random.randint(0, 1) == 0 else ">", "Compare the two values carefully.")

        if selected_topic == "counting":
            variants = [
                (f"Count the objects: {random.randint(5, 12)} stars and {random.randint(2, 6)} moons. How many objects are there altogether?", random.randint(5, 12) + random.randint(2, 6), "Count the total number of objects or add the new items to the group."),
                (f"If there are {random.randint(4, 10)} ducks and {random.randint(1, 5)} more join them, how many ducks are there now?", random.randint(4, 10) + random.randint(1, 5), "Add the new ducks to the original total."),
                (f"A basket holds {random.randint(6, 14)} apples. You add {random.randint(1, 4)} more. How many apples are there now?", random.randint(6, 14) + random.randint(1, 4), "Add the extra apples to the original amount."),
                (f"There are {random.randint(3, 8)} birds in a tree. {random.randint(1, 4)} fly away. How many are left?", random.randint(3, 8) - random.randint(1, 4), "Subtract the ones that left from the original total."),
                (f"A box has {random.randint(2, 7)} red crayons and {random.randint(2, 7)} blue crayons. How many crayons are there altogether?", random.randint(2, 7) + random.randint(2, 7), "Combine the two groups."),
            ]
            q_text, ans, explanation = random.choice(variants)
            return make_question(q_text, ans, explanation)

        if selected_topic == "shapes":
            variants = [
                ("Which shape has 3 sides?", "Triangle", "A triangle is a 2D shape with three sides."),
                ("Which shape has 4 equal sides?", "Square", "A square has four equal sides and four right angles."),
                ("Which shape has no corners?", "Circle", "A circle is round and has no corners."),
                ("How many sides does a hexagon have?", "6", "A hexagon has six sides."),
                ("Which shape has 8 sides?", "Octagon", "An octagon has eight sides."),
            ]
            q_text, ans, explanation = random.choice(variants)
            return make_question(q_text, ans, explanation)

        if selected_topic == "fractions":
            if grade_band == "3-5":
                variant = random.choice(["add", "subtract", "compare", "word", "simplify"])
                if variant == "add":
                    a, b = random.randint(1, 4), random.randint(2, 5)
                    c, d = random.randint(1, 4), random.randint(2, 5)
                    result = Fraction(a, b) + Fraction(c, d)
                    return make_question(f"What is {a}/{b} + {c}/{d}?", result, "Find a common denominator before combining the fractions.")
                if variant == "subtract":
                    a, b = random.randint(1, 4), random.randint(2, 5)
                    c, d = random.randint(1, 4), random.randint(2, 5)
                    result = Fraction(a, b) - Fraction(c, d)
                    return make_question(f"What is {a}/{b} - {c}/{d}?", result, "Subtract the fractions carefully after finding a common denominator.")
                if variant == "compare":
                    a, b = random.randint(1, 5), random.randint(2, 6)
                    c, d = random.randint(1, 5), random.randint(2, 6)
                    return make_question(f"Which is greater: {a}/{b} or {c}/{d}?", max(Fraction(a, b), Fraction(c, d)), "Compare the fractions by converting them or finding a common denominator.")
                if variant == "word":
                    a, b = random.randint(2, 6), random.randint(2, 6)
                    return make_question(f"A pizza is cut into {b} equal slices. If you eat {a} slices, what fraction of the pizza did you eat?", Fraction(a, b), "Use the number of slices eaten over the total number of slices.")
                return make_question(f"Simplify {random.randint(2, 8)}/{random.randint(2, 8)}", Fraction(random.randint(2, 8), random.randint(2, 8)), "Reduce the fraction by dividing the numerator and denominator by a common factor.")
            if grade_band == "6-8":
                variant = random.choice(["simplify", "compare", "add", "multiply", "word"])
                if variant == "simplify":
                    a, b = random.randint(2, 8), random.randint(2, 8)
                    return make_question(f"Simplify: {a}/{b}", Fraction(a, b) if a != b else 1, "Reduce the fraction by dividing by the greatest common factor.")
                if variant == "compare":
                    a, b = random.randint(1, 6), random.randint(2, 7)
                    c, d = random.randint(1, 6), random.randint(2, 7)
                    return make_question(f"Which is greater: {a}/{b} or {c}/{d}?", max(Fraction(a, b), Fraction(c, d)), "Compare the fractions by finding a common denominator or converting to decimals.")
                if variant == "add":
                    a, b = random.randint(1, 4), random.randint(2, 5)
                    c, d = random.randint(1, 4), random.randint(2, 5)
                    return make_question(f"What is {a}/{b} + {c}/{d}?", Fraction(a, b) + Fraction(c, d), "Use a common denominator to add fractions.")
                if variant == "multiply":
                    a, b = random.randint(1, 4), random.randint(2, 5)
                    c, d = random.randint(1, 4), random.randint(2, 5)
                    return make_question(f"What is {a}/{b} × {c}/{d}?", Fraction(a, b) * Fraction(c, d), "Multiply numerators together and denominators together.")
                return make_question(f"A recipe uses {random.randint(1, 4)} cups of flour for every {random.randint(2, 6)} cups of water. What fraction of the mixture is flour?", Fraction(random.randint(1, 4), random.randint(2, 6)), "Write the flour amount over the total amount in the mixture.")
            variant = random.choice(["divide", "multiply", "convert", "word"])
            if variant == "divide":
                a, b = random.randint(1, 5), random.randint(2, 6)
                c, d = random.randint(1, 5), random.randint(2, 6)
                return make_question(f"What is {a}/{b} ÷ {c}/{d}?", Fraction(a, b) / Fraction(c, d), "Divide fractions by multiplying by the reciprocal of the second fraction.")
            if variant == "multiply":
                a, b = random.randint(1, 4), random.randint(2, 5)
                c, d = random.randint(1, 4), random.randint(2, 5)
                return make_question(f"What is {a}/{b} × {c}/{d}?", Fraction(a, b) * Fraction(c, d), "Multiply numerators together and denominators together.")
            if variant == "convert":
                a, b = random.randint(1, 6), random.randint(2, 7)
                return make_question(f"Convert {a}/{b} to a decimal.", Fraction(a, b), "Divide the numerator by the denominator.")
            return make_question(f"A class ate {random.randint(1, 5)} out of {random.randint(2, 8)} slices of pie. What fraction was eaten?", Fraction(random.randint(1, 5), random.randint(2, 8)), "Write the eaten part over the total slices.")

        if selected_topic == "percentages":
            if grade_band == "3-5":
                variant = random.choice(["percent", "discount", "increase", "part-whole", "compare"])
                if variant == "percent":
                    percent = random.choice([10, 20, 25, 50])
                    base = random.randint(20, 80)
                    return make_question(f"What is {percent}% of {base}?", int(base * percent / 100), "Convert the percent to a decimal or fraction, then multiply by the base value.")
                if variant == "discount":
                    price = random.randint(20, 60)
                    percent = random.choice([10, 25, 50])
                    return make_question(f"A book costs ${price}. It is discounted by {percent}%. What is the new price?", price - int(price * percent / 100), "Find the discount amount and subtract it from the original price.")
                if variant == "increase":
                    start, increase = random.randint(10, 40), random.randint(5, 20)
                    return make_question(f"A score increases from {start} to {start + increase}. What is the percent increase?", int(increase / start * 100), "Compare the increase to the original value.")
                if variant == "part-whole":
                    total, part = random.randint(10, 50), random.randint(2, 10)
                    return make_question(f"If {part} out of {total} students are wearing hats, what percent is that?", int(part / total * 100), "Write the part over the whole, then convert to a percent.")
                return make_question(f"Which is larger: 25% of 80 or 20% of 100?", 20, "Calculate each percent first and compare the results.")
            if grade_band == "6-8":
                start = random.randint(20, 100)
                increase = random.choice([10, 20, 25, 50])
                return make_question(f"A value increases from {start} to {start + increase}. What is the percent increase?", increase, "Percent increase is the increase divided by the original amount, then multiplied by 100.")
            original = random.randint(40, 150)
            discount = random.choice([10, 15, 20, 25])
            return make_question(f"A jacket costs ${original} and is discounted by {discount}%. What is the sale price?", original - int(original * discount / 100), "Subtract the discount amount from the original price.")

        if selected_topic == "word-problems":
            variant = random.choice(["share", "distance", "total", "time", "group"])
            if variant == "share":
                a = random.randint(4, 12)
                b = random.randint(2, 6)
                return make_question(f"Mia bought {a} apples and shared them equally among {b} friends. How many apples did each friend get?", a // b, "Divide the total number of apples equally among the friends.")
            if variant == "distance":
                speed, time = random.randint(3, 8), random.randint(2, 6)
                return make_question(f"A car travels {speed} miles per hour for {time} hours. How far does it travel?", speed * time, "Distance is speed multiplied by time.")
            if variant == "total":
                a, b = random.randint(8, 20), random.randint(2, 5)
                return make_question(f"There are {a} chairs arranged in rows of {b}. How many rows are there?", a // b, "Divide the chairs evenly into rows.")
            if variant == "time":
                rate, amount = random.randint(2, 6), random.randint(3, 8)
                return make_question(f"A machine makes {rate} parts each minute. How many parts does it make in {amount} minutes?", rate * amount, "Multiply the rate by the time.")
            return make_question(f"A garden has {random.randint(5, 12)} rows with {random.randint(3, 6)} plants in each row. How many plants are there?", random.randint(5, 12) * random.randint(3, 6), "Multiply the number of rows by the plants in each row.")

        if selected_topic == "geometry":
            if grade_band == "3-5":
                length = random.randint(4, 12)
                width = random.randint(3, 10)
                return make_question(f"A rectangle has a length of {length} units and a width of {width} units. What is its area?", length * width, "Area of a rectangle is length multiplied by width.")
            if grade_band == "6-8":
                side = random.randint(3, 8)
                return make_question(f"A cube has side length {side}. What is its volume?", side ** 3, "Volume of a cube is side cubed.")
            a, b = random.randint(3, 8), random.randint(4, 10)
            return make_question(f"A right triangle has legs {a} and {b}. What is the hypotenuse length?", round((a ** 2 + b ** 2) ** 0.5, 2), "Use the Pythagorean theorem to find the missing side length.")

        if selected_topic == "algebra":
            if grade_band == "6-8":
                variant = random.choice(["solve", "factor", "graph", "evaluate", "expression"])
                if variant == "solve":
                    x = random.randint(2, 9)
                    b = random.randint(1, 10)
                    return make_question(f"Solve for x: {x}x + {b} = {x * x + b}", x, "Isolate the variable by undoing the operations in reverse order.")
                if variant == "factor":
                    a = random.randint(2, 5)
                    b = random.randint(2, 6)
                    return make_question(f"Factor: x² + {a + b}x + {a * b}", f"(x + {a})(x + {b})", "Find two numbers that multiply to the constant term and add to the middle coefficient.")
                if variant == "graph":
                    x = random.randint(1, 4)
                    return make_question(f"If y = 2x + 1, what is y when x = {x}?", 2 * x + 1, "Substitute the value of x into the expression.")
                if variant == "evaluate":
                    a = random.randint(2, 5)
                    return make_question(f"Evaluate 3a + 4 when a = {a}", 3 * a + 4, "Replace a with the given value and simplify.")
                return make_question(f"What is the slope of the line y = {random.randint(2, 5)}x + {random.randint(1, 4)}?", random.randint(2, 5), "The coefficient of x is the slope.")
            variant = random.choice(["linear", "quadratic", "system", "expand"])
            if variant == "linear":
                x = random.randint(1, 5)
                return make_question(f"Solve: 2x + 3 = {2 * x + 3}", x, "Subtract 3 and divide by 2 to isolate x.")
            if variant == "quadratic":
                a = random.randint(1, 3)
                return make_question(f"Solve: x² - {a * 2}x + {a * a} = 0", f"x = {a}", "Factor the quadratic expression to find the roots.")
            if variant == "system":
                return make_question("Solve the system: x + y = 5 and x - y = 1", "x = 3, y = 2", "Add the equations together and solve for each variable.")
            return make_question(f"Expand: {random.randint(2, 4)}(x + {random.randint(1, 4)})", f"{random.randint(2, 4)}x + {random.randint(2, 8)}", "Distribute the number outside the parentheses.")

        if selected_topic == "probability":
            variant = random.choice(["bag", "die", "deck", "spinners", "chance"])
            if variant == "bag":
                favorable = random.randint(1, 4)
                total = favorable + random.randint(2, 5)
                return make_question(f"A bag contains {total} marbles, {favorable} of which are red. What is the probability of picking a red marble?", f"{favorable}/{total}", "Probability is favorable outcomes divided by total outcomes.")
            if variant == "die":
                return make_question("A fair die is rolled. What is the probability of rolling an even number?", "3/6", "There are three even outcomes out of six total outcomes.")
            if variant == "deck":
                return make_question("What is the probability of drawing a heart from a standard deck of cards?", "13/52", "There are 13 hearts in a 52-card deck.")
            if variant == "spinners":
                return make_question("A spinner has 4 equal sections labeled red, blue, green, and yellow. What is the probability of landing on blue?", "1/4", "There is one favorable section out of four total sections.")
            return make_question(f"If the chance of rain is {random.randint(20, 80)}%, what is the chance that it will not rain?", f"{100 - random.randint(20, 80)}%", "The probabilities of an event and its complement add to 100%.")

        if selected_topic == "statistics":
            variant = random.choice(["mean", "median", "mode", "range", "spread"])
            if variant == "mean":
                numbers = [random.randint(1, 10) for _ in range(4)]
                avg = sum(numbers) / len(numbers)
                return make_question(f"What is the mean of {numbers}?", f"{avg:.1f}", "The mean is the sum of the values divided by how many values there are.")
            if variant == "median":
                numbers = [random.randint(1, 10) for _ in range(5)]
                sorted_numbers = sorted(numbers)
                mid = len(sorted_numbers) // 2
                return make_question(f"What is the median of {numbers}?", sorted_numbers[mid] if len(sorted_numbers) % 2 else (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2, "The median is the middle value when the data is ordered.")
            if variant == "mode":
                numbers = [random.randint(1, 6) for _ in range(6)]
                return make_question(f"What is the mode of {numbers}?", max(set(numbers), key=numbers.count), "The mode is the value that appears most often.")
            if variant == "range":
                numbers = [random.randint(1, 10) for _ in range(4)]
                return make_question(f"What is the range of {numbers}?", max(numbers) - min(numbers), "Range is the largest value minus the smallest value.")
            numbers = [random.randint(1, 10) for _ in range(5)]
            return make_question(f"Which value is most likely to be an outlier in {numbers}?", max(numbers), "An outlier stands far away from the rest of the data.")

        if selected_topic == "exponents":
            variant = random.choice(["evaluate", "simplify", "power", "square", "negative"])
            if variant == "evaluate":
                base = random.randint(2, 5)
                power = random.randint(2, 3)
                return make_question(f"Evaluate {base}^{power}.", base ** power, "Multiply the base by itself as many times as the exponent indicates.")
            if variant == "simplify":
                base = random.randint(2, 4)
                power = random.randint(2, 4)
                return make_question(f"Simplify {base}^{power} × {base}^{2}.", base ** (power + 2), "When multiplying like bases, add the exponents.")
            if variant == "power":
                base = random.randint(3, 6)
                return make_question(f"What is {base}²?", base ** 2, "Square the base by multiplying it by itself.")
            if variant == "square":
                return make_question("Write 5^3 as a product of factors.", "5 × 5 × 5", "An exponent tells how many times to multiply the base by itself.")
            return make_question("What is 2^0?", "1", "Any nonzero number raised to the zero power equals 1.")

        if selected_topic == "ratios":
            variant = random.choice(["recipe", "scale", "simplify", "compare", "units"])
            if variant == "recipe":
                a, b = random.randint(2, 6), random.randint(2, 6)
                return make_question(f"A recipe uses {a} cups of flour for every {b} cups of sugar. What is the ratio of flour to sugar?", f"{a}:{b}", "A ratio compares the two quantities directly.")
            if variant == "scale":
                a, b = random.randint(2, 6), random.randint(2, 6)
                return make_question(f"If the ratio of cats to dogs is {a}:{b}, how many cats are there for every {b} dogs?", a, "Use the first number in the ratio for the first quantity.")
            if variant == "simplify":
                a, b = random.randint(2, 8), random.randint(2, 8)
                return make_question(f"Simplify the ratio {a}:{b}.", f"{a // 2}:{b // 2}" if a % 2 == 0 and b % 2 == 0 else f"{a}:{b}", "Divide both parts by the same factor.")
            if variant == "compare":
                return make_question("Which ratio is greater: 2:3 or 3:4?", "3:4", "Compare the two ratios by finding equivalent forms.")
            return make_question(f"A map uses a scale of {random.randint(1, 4)} cm to {random.randint(2, 6)} km. What does this represent?", f"{random.randint(1, 4)} cm : {random.randint(2, 6)} km", "A scale compares map distance to real distance.")

        if selected_topic == "functions":
            variant = random.choice(["linear", "input-output", "graph", "table"])
            if variant == "linear":
                x = random.randint(1, 5)
                return make_question(f"If f(x) = 2x + 3, what is f({x})?", 2 * x + 3, "Substitute the given value into the function rule.")
            if variant == "input-output":
                x = random.randint(1, 4)
                return make_question(f"If g(x) = x² + 1, what is g({x})?", x * x + 1, "Square the input and add 1.")
            if variant == "graph":
                return make_question("What is the y-intercept of y = 3x + 4?", "4", "The y-intercept is the constant term.")
            return make_question(f"Complete the table for y = x + 2 when x = {random.randint(1, 4)}.", random.randint(1, 4) + 2, "Add 2 to the input value.")

        if selected_topic == "sequences":
            variant = random.choice(["next", "term", "pattern", "difference"])
            if variant == "next":
                start = random.randint(1, 6)
                step = random.randint(2, 4)
                return make_question(f"What is the next number in the sequence: {start}, {start + step}, {start + 2 * step}, ?", start + 3 * step, "Look for the common difference between consecutive terms.")
            if variant == "term":
                start = random.randint(2, 5)
                return make_question(f"What is the 5th term of the sequence 2, 4, 6, 8, ...?", 10, "Count by 2s.")
            if variant == "pattern":
                return make_question("What comes next: 1, 3, 9, 27, ?", "81", "Multiply by 3 each time.")
            return make_question("What is the missing term: 10, 15, __, 25?", "20", "Add 5 each time.")

        if selected_topic == "inequalities":
            variant = random.choice(["solve", "graph", "compare", "bound"])
            if variant == "solve":
                x = random.randint(2, 6)
                return make_question(f"Solve the inequality: x + 3 > {x + 4}", "x > 1", "Subtract 3 from both sides to isolate x.")
            if variant == "graph":
                return make_question("Which inequality means x is greater than 4?", "x > 4", "Look for the statement that says x is larger than 4.")
            if variant == "compare":
                return make_question("Is 5 greater than or equal to 5?", "True", "Equal values satisfy the phrase greater than or equal to.")
            return make_question("If x < 3, which values could x be?", "2", "Pick a value smaller than 3.")

        if selected_topic == "trigonometry":
            variant = random.choice(["sin", "cos", "tan", "special"])
            if variant == "sin":
                angle = random.choice([30, 45, 60])
                return make_question(f"What is sin({angle}°)?", {30: "1/2", 45: "√2/2", 60: "√3/2"}[angle], "Use the common exact-value trigonometric ratios for special angles.")
            if variant == "cos":
                angle = random.choice([30, 45, 60])
                return make_question(f"What is cos({angle}°)?", {30: "√3/2", 45: "√2/2", 60: "1/2"}[angle], "Use the common exact-value trigonometric ratios for special angles.")
            if variant == "tan":
                return make_question("What is tan(45°)?", "1", "Tangent is opposite over adjacent and equals 1 for a 45-degree angle.")
            return make_question("Which trig function is opposite over hypotenuse?", "Sine", "Sine compares the opposite side to the hypotenuse.")

        coeff = random.randint(2, 5)
        power = random.randint(2, 4)
        return make_question(f"Find the derivative of f(x) = {coeff}x^{power} + 3x", f"{coeff * power}x^{power - 1} + 3", "Differentiate each term by bringing the exponent down and subtracting one.")

    for index in range(count):
        selected_topic = topic if topic != "mixed" else random.choice(topic_pool)
        if topic != "mixed" and selected_topic not in topic_pool:
            selected_topic = random.choice(topic_pool)
        if selected_topic in {"trigonometry", "calculus"} and grade_band != "9-12":
            selected_topic = random.choice([t for t in topic_pool if t not in {"trigonometry", "calculus"}])

        compatible_styles = ["multiple-choice", "short-answer", "fill-in-the-blank", "ordering", "multiple-select", "true-false"]
        if question_type == "mixed":
            kind = "true-false" if index == 0 else random.choice(compatible_styles)
        else:
            kind = question_type
        difficulty = {"k-2": "Beginner", "3-5": "Foundational", "6-8": "Intermediate", "9-12": "Advanced"}[grade_band]
        generated = build_question(selected_topic, kind, difficulty)

        question = {
            "id": f"q-{index + 1}",
            "question": generated["question"],
            "answer": str(generated["answer"]),
            "topic": selected_topic.replace("-", " ").title(),
            "type": kind,
            "difficulty": difficulty,
            "explanation": generated["explanation"],
        }

        if kind in {"multiple-choice", "true-false"}:
            distractors = []
            if selected_topic in ["arithmetic", "algebra", "geometry", "percentages", "word-problems", "ratios", "exponents", "functions", "sequences", "inequalities"]:
                try:
                    distractors = [str(int(question["answer"]) + random.randint(1, 5)), str(int(question["answer"]) - random.randint(1, 5)), str(int(question["answer"]) + random.randint(2, 8))]
                except ValueError:
                    distractors = ["2", "3", "4"]
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