from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# PLEASE ENSURE YOU HAVE SET THE 'API_KEY' ENVIRONMENT VARIABLE CORRECTLY.
# FOR SECURITY REASONS, DO NOT HARDCODE YOUR API KEY DIRECTLY IN THE SCRIPT.
# Example of setting directly for local testing (NOT RECOMMENDED FOR PRODUCTION):

genai.configure(api_key=os.environ.get("API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def summarize_notes(notes: str, max_output_tokens: int = 500) -> str:
    if not notes.strip():
        return "Error: Please provide some notes to summarize."
    prompt = f"""Please provide a concise and informative summary of the following notes:\n\n{notes}\n\nEnsure the summary captures the key points and main ideas."""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_output_tokens)
        )
        return response.text if response.text else "Error: Could not generate a summary."
    except Exception as e:
        return f"Error during summarization: {e}"

def generate_related_questions(summary: str, num_questions: int = 3, difficulty: str = 'basic', max_output_tokens: int = 200) -> list[str]:
    if not summary.strip():
        return ["Error: Please provide a summary to generate questions from."]

    if difficulty == 'basic':
        prompt = f"""Based on the following summary:\n\n{summary}\n\nGenerate {num_questions} basic practice questions focusing on fundamental concepts."""
    elif difficulty == 'intermediate':
        prompt = f"""Based on the following summary:\n\n{summary}\n\nGenerate {num_questions} intermediate-level practice questions that require some analysis and understanding of relationships."""
    elif difficulty == 'advanced':
        prompt = f"""Based on the following summary:\n\n{summary}\n\nGenerate {num_questions} advanced practice questions that challenge deep understanding, critical thinking, and application of concepts."""
    elif difficulty == 'competitive':
        prompt = f"""Based on the following summary:\n\n{summary}\n\nGenerate {num_questions} practice questions that are conceptual, competency-based, and application-based, similar to JEE/BITSAT level, and include some potential PYQ-style questions."""
    else:
        return ["Error: Invalid difficulty level selected."]

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_output_tokens)
        )
        if response.text:
            questions = [q.strip() for q in response.text.split('\n') if q.strip()]
            return questions[:num_questions]
        else:
            return ["Error: Could not generate related questions."]
    except Exception as e:
        return [f"Firtly solve previous questions. Time limit:[30sec]"]

@app.route("/", methods=["GET"])
def index():
    return render_template("templates\vinai.html")

@app.route("/process", methods=["POST"])
def process():
    notes = request.form.get("notes")
    num_questions = int(request.form.get("num_questions", 3))
    question_mode = request.form.get("question_mode", "basic")
    difficulty = question_mode # Now the mode directly corresponds to the difficulty for basic/intermediate/advanced

    summary = summarize_notes(notes)
    questions = []
    if summary and not summary.startswith("Error"):
        questions = generate_related_questions(summary, num_questions=num_questions, difficulty=difficulty)

    return jsonify({"summary": summary, "questions": questions})

if __name__ == "__main__":
    app.run(debug=True) 
