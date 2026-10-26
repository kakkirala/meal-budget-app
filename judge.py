"""LLM-as-Judge for MealBudget - scores a saved plan + budget check."""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

judge_llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    temperature=0,  # judge must be strict, not creative
)

JUDGE_PROMPT = """You are a strict meal-plan and budget evaluator. Score
the plan below against this rubric. Be honest - a wrong budget
verdict is a fail.

Rubric (score each, then total out of 10):
1. Diet compliance (0-3): Does EVERY dish match the stated diet?
   Vegan = no animal products at all. Eggetarian = eggs OK, no meat/fish.
   Non-vegetarian = any dishes allowed.
2. Completeness (0-2): All requested days present? Every day has its
   meals? Shopping list grouped? Chef tips present?
3. Budget verdict (0-3): Read the shopping list's estimated total
   cost and the grocery budget. Is the WITHIN/OVER verdict CORRECT?
   Is the over/under amount right? If over budget, are cuts or swaps
   suggested? A wrong verdict scores 0 here.
4. Format (0-2): PLAIN TEXT only? No markdown stars (**), no tables,
   no HTML tags? Deduct for every markdown leak.

Return exactly this format:
Diet: X/3 - one-line reason
Completeness: X/2 - one-line reason
Budget: X/3 - one-line reason
Format: X/2 - one-line reason
TOTAL: X/10
VERDICT: PASS (8+) or NEEDS WORK
ONE FIX: the single most important improvement, in one line

DIET: {diet}
DAYS: {days}
GROCERY BUDGET: {budget} {currency}
PLAN AND BUDGET CHECK:
{plan}
"""

def judge(plan_text, diet, days, budget, currency):
    prompt = JUDGE_PROMPT.format(
        diet=diet, days=days, budget=budget,
        currency=currency, plan=plan_text,
    )
    return judge_llm.invoke(prompt).content

if __name__ == "__main__":
    with open("meal_budget_output.txt", encoding="utf-8") as f:
        plan = f.read()
    # Change these to match the plan you just built:
    print(judge(plan, diet="Eggetarian", days=3, budget=150, currency="$"))
    print(judge(plan, diet="Vegan", days=3, budget=100, currency="$"))
    print(judge(plan, diet="Non-Vegetarian", days=3, budget=350, currency="$"))


