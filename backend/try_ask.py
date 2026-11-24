import json

from rag import ask

QUESTIONS = [
    "How much can I spend on a hotel?",
    "What is the mileage reimbursement rate?",
    "How many vacation days do I get?",
    "Is there a gym?",
    "Can I bring my dog to the office?",
    "What is the capital of France?",
]

for q in QUESTIONS:
    result = ask(q)
    print("=" * 60)
    print("Q:", q)
    print(json.dumps(result, indent=2))