const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:5000";

export async function askQuestion(question) {
  let response;
  try {
    response = await fetch(`${API_URL}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  } catch {
    throw new Error("Can't reach the server. Is the backend running?");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error ?? "Something went wrong. Please try again.");
  }
  return data;
}