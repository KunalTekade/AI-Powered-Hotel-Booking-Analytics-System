
from src.result_explainer import explain_results

question = "Which market segment has the highest number of bookings?"

results = [
    {
        "market_segment": "Online TA",
        "total_bookings": 51618
    }
]

answer = explain_results(question, results)

print("\n========== AI GENERATED ANSWER ==========")
print(answer)
