"""MealBudget - combined brain: meal plan + shopping + budget check."""
import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()


load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    temperature=0.3,
)


class MealBudgetState(TypedDict):
    diet_type: str
    ingredients: str
    cuisine: str
    spice_level: str
    avoid: str
    servings: int
    days: int
    grocery_budget: float
    currency: str
    menu: str
    shopping_list: str
    tips: str
    budget_check: str


MENU_PROMPT = """You are a meal planning chef.
PLAIN TEXT ONLY. No markdown, no stars (**), no #, no tables.
Use simple numbered lines.

Diet: {diet_type}
Ingredients on hand: {ingredients}
Cuisine: {cuisine}
Spice level: {spice_level}
Avoid: {avoid}
Servings: {servings}
Days: {days}

Write a day-by-day menu. For each day give breakfast, lunch, and
dinner with per-meal calories, then a day total with calories and
protein. Keep every dish within the diet and avoid list.
"""

SHOPPING_PROMPT = """Based on this menu, write a grouped shopping list
(vegetables, dairy, grains, spices, household). Give quantities
for {servings} servings and end with an estimated total cost
in {currency}. PLAIN TEXT ONLY. No markdown, no stars, no tables.

MENU:
{menu}
"""

TIPS_PROMPT = """Based on this menu, write exactly 3 short chef tips
as numbered steps, one tip per line, in this exact format:
Step 1: ...
Step 2: ...
Step 3: ...
Then on a new line:
Leftover idea: ...
PLAIN TEXT ONLY. No markdown, no stars, no tables.

MENU:
{menu}
"""

BUDGET_PROMPT = """You are a grocery budget checker.
PLAIN TEXT ONLY. No markdown, no stars, no tables.
Numbered lines only.

Grocery budget: {grocery_budget} {currency}
Shopping list with estimated cost:
{shopping_list}

Answer these, using the estimated total cost from the list:
1. Budget verdict: WITHIN BUDGET or OVER BUDGET
2. Difference: how much under, or over by how much, in {currency}
3. If over budget: what to cut or swap to fit the budget
   (name the items, keep the meals working)
4. If within budget: what to do with the money left
Keep it short and simple.
"""


def generate_menu(state: MealBudgetState) -> MealBudgetState:
    prompt = MENU_PROMPT.format(
        diet_type=state["diet_type"],
        ingredients=state["ingredients"],
        cuisine=state["cuisine"],
        spice_level=state["spice_level"],
        avoid=state["avoid"],
        servings=state["servings"],
        days=state["days"],
    )
    # state["menu"] = llm.invoke(prompt).content

    state["menu"] = llm.invoke(prompt, config={"callbacks": [langfuse_handler]}).content
    
    return state


def generate_shopping_list(state: MealBudgetState) -> MealBudgetState:
    prompt = SHOPPING_PROMPT.format(
        menu=state["menu"],
        servings=state["servings"],
        currency=state["currency"],
    )
    state["shopping_list"] = llm.invoke(prompt, config={"callbacks": [langfuse_handler]}).content
    return state


def generate_tips(state: MealBudgetState) -> MealBudgetState:
    prompt = TIPS_PROMPT.format(menu=state["menu"])
    state["tips"] = llm.invoke(prompt, config={"callbacks": [langfuse_handler]}).content
    return state


def budget_check(state: MealBudgetState) -> MealBudgetState:
    prompt = BUDGET_PROMPT.format(
        grocery_budget=state["grocery_budget"],
        currency=state["currency"],
        shopping_list=state["shopping_list"],
    )
    state["budget_check"] = llm.invoke(prompt, config={"callbacks": [langfuse_handler]}).content
    return state


graph = StateGraph(MealBudgetState)
graph.add_node("generate_menu", generate_menu)
graph.add_node("generate_shopping_list", generate_shopping_list)
graph.add_node("generate_tips", generate_tips)
graph.add_node("budget_check", budget_check)
graph.set_entry_point("generate_menu")
graph.add_edge("generate_menu", "generate_shopping_list")
graph.add_edge("generate_shopping_list", "generate_tips")
graph.add_edge("generate_tips", "budget_check")
graph.add_edge("budget_check", END)
app = graph.compile()

if __name__ == "__main__":
    # Sample numbers just for testing - the real form comes next.
    sample = {
        "diet_type": "Eggetarian",
        "ingredients": "rice, eggs, tomatoes, onions, spinach",
        "cuisine": "Indian",
        "spice_level": "medium",
        "avoid": "nuts",
        "servings": 2,
        "days": 3,
        "grocery_budget": 150,
        "currency": "$",
        "menu": "",
        "shopping_list": "",
        "tips": "",
        "budget_check": "",
    }
    result = app.invoke(sample)
    full = (
        result["menu"]
        + "\n\n" + result["shopping_list"]
        + "\n\n" + result["tips"]
        + "\n\n" + result["budget_check"]
    )
    print(full)
    with open("meal_budget_output.txt", "w", encoding="utf-8") as f:
        f.write(full)
    print("Saved to meal_budget_output.txt")
