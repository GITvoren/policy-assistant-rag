from rag import build_user_message, generate, retrieve

QUESTIONS: list[str] = [
    "How many vacation days do I get?",
    "How much can I spend on a hotel?",
    "Tell me about the 401(k) plan.",
    "What is the mileage reimbursement rate?",
    "How many sick days do I get?",
    "What is the learning budget?",
    "How much can I spend on a hotel in Tokyo?",
    "Does the company pay for gym memberships?",
    "Can I bring my dog to the office?",
    "What is the capital of France?",
]

for q in QUESTIONS:
    result = generate(build_user_message(q, retrieve(q)))
    print(f"\nQ: {q}")
    print(f"found: {result.found}")
    print(f"answer: {result.answer}")
    for c in result.citations:
        print(f"  [{c.excerpt_id}] {c.quote!r}")