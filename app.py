"""MealBudget - Flask web UI (plan, budget, send)."""
from flask import Flask, render_template, request, send_file
from main import app as mealbudget_agent

flask_app = Flask(__name__)


@flask_app.route("/", methods=["GET", "POST"])
def index():
    result = None
    form = None
    if request.method == "POST":
        state = {
            "diet_type": request.form["diet_type"],
            "ingredients": request.form.get("ingredients", ""),
            "cuisine": request.form.get("cuisine", "Indian"),
            "spice_level": request.form.get("spice_level", "medium"),
            "avoid": request.form.get("avoid", ""),
            "servings": int(request.form.get("servings") or 2),
            "days": int(request.form.get("days") or 3),
            "grocery_budget": float(request.form.get("grocery_budget") or 0),
            "currency": request.form.get("currency", "$"),
            "menu": "",
            "shopping_list": "",
            "tips": "",
            "budget_check": "",
        }
        result = mealbudget_agent.invoke(state)
        form = state
        full = (
            result["menu"]
            + "\n\n" + result["shopping_list"]
            + "\n\n" + result["tips"]
            + "\n\n" + result["budget_check"]
        )
        with open("meal_budget_output.txt", "w", encoding="utf-8") as f:
            f.write(full)
    return render_template("index.html", result=result, form=form)


@flask_app.route("/download")
def download():
    return send_file("meal_budget_output.txt", as_attachment=True)


if __name__ == "__main__":
    flask_app.run(debug=True, port=5002)
