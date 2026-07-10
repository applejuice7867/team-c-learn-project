import random
from typing import Any

from fastapi import FastAPI
from workers import WorkerEntrypoint
import asgi

app = FastAPI()

DEFAULT_CONFIG = {
    "grade_bands": {
        "k-2": ["arithmetic", "counting", "shapes"],
        "3-5": ["arithmetic", "fractions", "percentages", "word-problems", "geometry"],
        "6-8": ["arithmetic", "fractions", "percentages", "algebra", "geometry", "probability", "statistics", "exponents", "ratios"],
        "9-12": ["algebra", "geometry", "probability", "statistics", "functions", "sequences", "inequalities", "trigonometry", "calculus", "exponents"],
    },
    "variants": {
        "arithmetic": ["add", "subtract", "compare", "missing", "pattern", "before_after", "count_objects", "number_sentence", "multiply", "divide", "mixed", "estimate", "fact_family", "number_line", "missing_addend", "comparison"],
        "fractions": ["add", "subtract", "compare", "multiply", "convert", "share"],
        "algebra": ["linear", "two_step", "combine", "evaluate", "distribute", "factor"],
        "geometry": ["rectangle_area", "triangle_area", "perimeter", "circle_circumference", "missing_angle", "volume"],
        "word-problems": ["shopping", "distance", "reading", "sharing"],
        "probability": ["dice", "coins", "marbles", "spinners"],
        "statistics": ["mean", "median", "range", "mode"],
        "exponents": ["power", "product_rule", "zero_exponent", "expanded"],
    },
}


def get_config() -> dict[str, Any]:
    return DEFAULT_CONFIG


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate-math")
async def generate_math(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    config = get_config()
    payload = payload or {}

    grade_band = payload.get("gradeBand") or payload.get("grade_band") or "9-12"
    selected_topic = payload.get("topic") or payload.get("selectedTopic") or payload.get("selected_topic")

    topic_pool = config["grade_bands"].get(grade_band, config["grade_bands"]["9-12"])
    if selected_topic not in topic_pool:
        selected_topic = random.choice(topic_pool)

    variants = config["variants"].get(selected_topic, ["default"])
    variant = random.choice(variants)

    return {
        "status": "success",
        "gradeBand": grade_band,
        "topic": selected_topic,
        "variant": variant,
        "questions": [
            {
                "prompt": f"Solve the {variant} {selected_topic} question.",
                "answer": "Example answer",
            }
        ],
    }


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)