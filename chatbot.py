import streamlit as st
import re
import time
import google.generativeai as genai
import joblib
import pandas as pd
import os

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

# ==============================
# LOAD MODELS
# ==============================

# ML Hiring Model
ml_model = joblib.load("hiring_model.pkl")

# Gemini AI Model
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini_model = genai.GenerativeModel("gemini-flash-latest")

# ==============================
# SAFE AI CALL
# ==============================

def safe_generate(prompt, retries=2):

    for attempt in range(retries + 1):

        try:
            response = gemini_model.generate_content(prompt)
            return response.text

        except Exception as e:

            if "429" in str(e):
                wait = 20
                st.warning(f"Rate limit reached. Waiting {wait}s...")
                time.sleep(wait)

            else:
                st.error(str(e))
                return None

    return None

# ==============================
# SESSION STATE
# ==============================

if "stage" not in st.session_state:
    st.session_state.stage = "welcome"

if "candidate" not in st.session_state:
    st.session_state.candidate = {}

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "scores" not in st.session_state:
    st.session_state.scores = []

# ==============================
# VALIDATION FUNCTIONS
# ==============================

def valid_name(name):
    return len(name.strip()) >= 3 and name.replace(" ", "").isalpha()

def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def valid_phone(phone):
    return re.match(r'^\d{10}$', phone)

def valid_experience(exp):

    try:
        exp = float(exp)
        return 0 <= exp <= 50
    except:
        return False

def valid_tech_stack(tech_input):

    techs = [t.strip().lower() for t in tech_input.split(",")]
    techs = [t for t in techs if len(t) >= 2]

    return list(set(techs))

# ==============================
# AI FUNCTIONS
# ==============================

def generate_questions(tech_stack, experience):

    prompt = f"""
You are a professional technical interviewer.

Generate exactly 5 interview questions for a candidate
with {experience} years experience in:

{', '.join(tech_stack)}

Return only numbered questions.
"""

    text = safe_generate(prompt)

    if not text:
        return []

    questions = [q.strip() for q in text.split("\n") if q.strip()]

    return questions[:5]

def evaluate_answer(question, answer):

    prompt = f"""
You are a strict technical interviewer.

Question:
{question}

Candidate Answer:
{answer}

Evaluate and return:

Score: X/10
Feedback: <short explanation>
"""

    return safe_generate(prompt)

# ==============================
# UI
# ==============================

st.title("🤖 TalentScout Hiring Assistant")

# ==============================
# WELCOME PAGE
# ==============================

if st.session_state.stage == "welcome":

    st.write("👋 Enter your details to begin interview")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone (10 digits)")
    experience = st.text_input("Years of Experience")
    tech_stack = st.text_input("Tech Stack (comma separated)")

    if st.button("Start Interview"):

        techs = valid_tech_stack(tech_stack)

        if not valid_name(name):
            st.error("Invalid name")

        elif not valid_email(email):
            st.error("Invalid email")

        elif not valid_phone(phone):
            st.error("Invalid phone")

        elif not valid_experience(experience):
            st.error("Invalid experience")

        elif not techs:
            st.error("Enter valid tech stack")

        else:

            st.session_state.candidate = {
                "name": name,
                "experience": experience,
                "tech_stack": techs
            }

            with st.spinner("Generating interview questions..."):

                st.session_state.questions = generate_questions(
                    techs,
                    experience
                )

            if st.session_state.questions:

                st.session_state.stage = "interview"
                st.rerun()

# ==============================
# INTERVIEW STAGE
# ==============================

elif st.session_state.stage == "interview":

    q_index = st.session_state.current_q
    questions = st.session_state.questions

    if q_index < len(questions):

        question = questions[q_index]

        st.subheader(f"Question {q_index + 1}")
        st.write(question)

        answer = st.text_area("Your Answer")

        if st.button("Submit Answer"):

            if len(answer.strip()) < 10:
                st.warning("Answer too short")

            else:

                with st.spinner("Evaluating answer..."):

                    feedback = evaluate_answer(question, answer)

                if feedback:

                    st.session_state.scores.append(feedback)
                    st.session_state.current_q += 1
                    st.rerun()

    else:

        st.session_state.stage = "result"
        st.rerun()

# ==============================
# RESULT STAGE
# ==============================

elif st.session_state.stage == "result":

    st.success("🎉 Interview Completed")

    total_score = 0

    for idx, feedback in enumerate(st.session_state.scores):

        st.write(f"### Question {idx+1} Evaluation")
        st.write(feedback)

        match = re.search(r'(\d+)/10', feedback)

        if match:
            total_score += int(match.group(1))

    if st.session_state.scores:
        average = total_score / len(st.session_state.scores)
    else:
        average = 0

    st.write("## Final Score")
    st.write(f"⭐ Average Score: {average:.2f}/10")

    # ==============================
    # ML DECISION
    # ==============================

    experience = float(st.session_state.candidate["experience"])
    tech_count = len(st.session_state.candidate["tech_stack"])

    input_data = [[experience, tech_count, average]]

    prediction = ml_model.predict(input_data)[0]
    probability = ml_model.predict_proba(input_data)[0][1]

    decision = int(prediction)

    if decision == 1:
        st.success(f"Selected 🎉 (Confidence {probability:.2f})")
    else:
        st.error(f"Not Selected ❌ (Confidence {1-probability:.2f})")

    # ==============================
    # AI SUMMARY
    # ==============================

    summary_prompt = f"""
Candidate experience: {experience}
Tech stack: {', '.join(st.session_state.candidate["tech_stack"])}
Average score: {average}

Write a short professional interview summary.
"""

    summary = safe_generate(summary_prompt)

    if summary:
        st.subheader("🧠 AI Interview Summary")
        st.write(summary)

    # ==============================
    # SAVE DATASET
    # ==============================

    data = {
        "Experience": experience,
        "Tech_Count": tech_count,
        "Avg_Score": round(average,2),
        "Final_Decision": decision
    }

    df = pd.DataFrame([data])

    file = "interview_dataset.csv"

    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)

    st.write("📁 Interview data saved for ML training")

    # ==============================
    # RESTART
    # ==============================

    if st.button("Restart Interview"):

        st.session_state.clear()
        st.rerun()