# --- local ---
from rag import build_user_message, generate, renumber_markers, retrieve, verify_citations
import sys

QUESTION = " ".join(sys.argv[1:]) or "How many vacations leave do we have?"

results = retrieve(QUESTION)
print("RETRIEVED:")
for i, (doc, score) in enumerate(results, start=1):
    print(i, round(score, 3), doc.metadata["source"], doc.metadata["page"])

answer = generate(build_user_message(QUESTION, results))
print("found:", answer.found)
print("answer:", answer.answer)
print("citations:", answer.citations)

verified = verify_citations(answer, results)
print("verified:", verified)
print("renumbered:", renumber_markers(answer.answer, verified))