# MealBudget — Plan, Budget, Send

A meal-planning agent that plans your week's meals, builds a grouped
shopping list with estimated costs, checks the list against your
grocery budget, and prepares the list to send for shopping.

## The flow — one app, four steps

1. **Plan** — pick diet, ingredients, cuisine, spice level, servings,
   days, and grocery budget. The agent writes the meal plan.
2. **List** — the agent builds a shopping list grouped by category,
   with estimated costs.
3. **Budget check** — the agent compares the estimated total with
   your budget: within budget, over by how much, and what to cut or
   swap if over.
4. **Send** — the approved shopping list can be sent by email and
   WhatsApp for purchasing (draft → approve → send; sending activates
   after Outlook and WhatsApp Business API are connected — copy and
   download work today).

## How it is built

- **LangGraph** `StateGraph` with 4 nodes:
  `generate_menu → generate_shopping_list → generate_tips → budget_check`
- **LLM:** Groq `openai/gpt-oss-120b` (temperature 0.3), plain-text
  prompts — no markdown in outputs
- **UI:** Flask app (`app.py`, port 5002) + CLI (`main.py`)
- **Observability:** Langfuse tracing — every run records all 4
  nodes with inputs, outputs, latency, and token cost
- **Evaluation:** LLM-as-judge (`judge.py`) — a second model scores
  each plan out of 10 on diet compliance, completeness, budget-verdict
  correctness, and format. Best plan scored **10/10 PASS**.

## Project structure

```text
meal-budget-app/
├── main.py              # LangGraph agent (4 nodes) + CLI
├── app.py               # Flask web UI (port 5002)
├── judge.py             # LLM-as-judge scoring script
├── templates/
│   └── index.html       # Web UI
├── requirements.txt     # Dependencies
└── .env                 # API keys (never committed)
```

## Setup

```powershell
pip install -r requirements.txt
```

Create a `.env` file in this folder:

```text
GROQ_API_KEY=your-groq-key
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://us.cloud.langfuse.com
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

> Use your own region host. If your Langfuse dashboard address is
> `eu.cloud.langfuse.com`, use that host instead. Keys stay in `.env`
> only — never commit them.

Run the web app:

```powershell
python app.py
```

Then open http://127.0.0.1:5002

Score a saved plan with the judge:

```powershell
python main.py   # builds a plan, saves meal_budget_output.txt
python judge.py  # prints the score card
```

## Notes

- The judge reads `meal_budget_output.txt` and needs the diet, days,
  and budget in its last line to match the plan that was built.
- Email sending waits on an Outlook connection; WhatsApp sending
  waits on the official WhatsApp Business API. Both send buttons are
  shown disabled until then, honestly.
