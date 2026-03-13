import streamlit as st

# ---------------------------------------
# Page Config
# ---------------------------------------
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")
st.title("🤖 TalentScout Hiring Assistant")

# ---------------------------------------
# Initialize Session State
# ---------------------------------------
if "conversation_step" not in st.session_state:
    st.session_state.conversation_step = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {
        "name": "",
        "email": "",
        "phone": "",
        "experience": "",
        "position": "",
        "location": "",
        "tech_stack": ""
    }

if "technical_stage" not in st.session_state:
    st.session_state.technical_stage = False

if "technical_questions" not in st.session_state:
    st.session_state.technical_questions = []

if "technical_answers" not in st.session_state:
    st.session_state.technical_answers = []

if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0


# ---------------------------------------
# Generate Structured Question Bank
# ---------------------------------------
def generate_question_bank(tech_stack):

    bank = []
    techs = [t.strip().lower() for t in tech_stack.split(",")]

    for tech in techs:

        if tech == "python":
            bank.extend([
                {"question": "What are Python decorators?",
                 "keywords": ["function", "wrapper", "modify", "behavior"]},

                {"question": "Explain list vs tuple differences.",
                 "keywords": ["mutable", "immutable", "performance"]},

                {"question": "What is GIL in Python?",
                 "keywords": ["global interpreter lock", "thread", "concurrency"]},
            ])

        elif tech == "django":
            bank.extend([
                {"question": "Explain Django MVT architecture.",
                 "keywords": ["model", "view", "template"]},

                {"question": "What is Django ORM?",
                 "keywords": ["database", "queryset", "model"]},

                {"question": "How does middleware work in Django?",
                 "keywords": ["request", "response", "processing"]},
            ])

        elif tech == "sql":
            bank.extend([
                {"question": "What is normalization?",
                 "keywords": ["redundancy", "normal form", "database"]},

                {"question": "Explain different types of JOINs.",
                 "keywords": ["inner", "left", "right", "full"]},

                {"question": "What are indexes in SQL?",
                 "keywords": ["performance", "search", "query"]},
            ])

        else:
            bank.extend([
                {"question": f"Explain core concepts of {tech}.",
                 "keywords": [tech]},

                {"question": f"What are common challenges in {tech}?",
                 "keywords": [tech]},

                {"question": f"How do you optimize performance in {tech}?",
                 "keywords": ["performance", tech]},
            ])

    return bank


# ---------------------------------------
# Answer Scoring Logic
# ---------------------------------------
def score_answer(answer, keywords):

    score = 0
    answer_lower = answer.lower()

    # Length-based scoring
    if len(answer.split()) > 8:
        score += 2
    elif len(answer.split()) > 4:
        score += 1

    # Keyword-based scoring
    for word in keywords:
        if word in answer_lower:
            score += 2

    return score


# ---------------------------------------
# Bot Logic
# ---------------------------------------
def get_bot_response(user_input):

    step = st.session_state.conversation_step
    data = st.session_state.candidate_data

    # ---------------------------
    # Technical Round Handling
    # ---------------------------
    if st.session_state.technical_stage:

        if user_input.lower().strip() == "exit":

            total_score = sum(st.session_state.technical_answers)
            max_score = len(st.session_state.technical_answers) * 6
            percentage = (total_score / max_score) * 100

            st.session_state.technical_stage = False

            return (
                f"🎉 Technical Round Completed.\n\n"
                f"📊 Final Score: {total_score}/{max_score} ({percentage:.1f}%)\n\n"
                "Our recruitment team will review your profile and contact you regarding next steps.\n"
                "Thank you for your time! 🚀"
            )

        # Score current answer
        q_index = st.session_state.current_question_index
        current_q = st.session_state.technical_questions[q_index]

        score = score_answer(user_input, current_q["keywords"])
        st.session_state.technical_answers.append(score)

        st.session_state.current_question_index += 1

        # Ask next question
        if st.session_state.current_question_index < len(st.session_state.technical_questions):
            next_q = st.session_state.technical_questions[
                st.session_state.current_question_index
            ]["question"]

            return f"Next Question:\n{next_q}"

        else:
            # Interview completed
            total_score = sum(st.session_state.technical_answers)
            max_score = len(st.session_state.technical_answers) * 6
            percentage = (total_score / max_score) * 100

            st.session_state.technical_stage = False

            return (
                f"🎉 Technical Round Finished.\n\n"
                f"📊 Final Score: {total_score}/{max_score} ({percentage:.1f}%)\n\n"
                "Thank you for completing the interview.\n"
                "Our HR team will reach out soon."
            )

    # ---------------------------
    # Candidate Information Flow
    # ---------------------------
    if step == 0:
        st.session_state.conversation_step = 1
        return "👋 Welcome to TalentScout Hiring Assistant.\nWhat is your full name?"

    elif step == 1:
        data["name"] = user_input
        st.session_state.conversation_step = 2
        return "📧 Please provide your email address."

    elif step == 2:
        data["email"] = user_input
        st.session_state.conversation_step = 3
        return "📱 Please provide your phone number."

    elif step == 3:
        data["phone"] = user_input
        st.session_state.conversation_step = 4
        return "💼 How many years of experience do you have?"

    elif step == 4:
        data["experience"] = user_input
        st.session_state.conversation_step = 5
        return "🎯 What position(s) are you applying for?"

    elif step == 5:
        data["position"] = user_input
        st.session_state.conversation_step = 6
        return "📍 What is your current location?"

    elif step == 6:
        data["location"] = user_input
        st.session_state.conversation_step = 7
        return "🛠️ Please list your Tech Stack (comma separated)."

    elif step == 7:
        data["tech_stack"] = user_input
        st.session_state.conversation_step = 8

        # Start Technical Round
        st.session_state.technical_questions = generate_question_bank(user_input)
        st.session_state.technical_answers = []
        st.session_state.current_question_index = 0
        st.session_state.technical_stage = True

        first_question = st.session_state.technical_questions[0]["question"]

        return f"🧠 Technical Round Started:\n\nQuestion 1:\n{first_question}"

    else:
        return "Please respond appropriately to continue the interview."


# ---------------------------------------
# Display Chat History
# ---------------------------------------
for sender, message in st.session_state.messages:
    if sender == "You":
        st.markdown(f"👤 **You:**  \n{message}")
    else:
        st.markdown(f"🤖 **Bot:**  \n{message}")


# ---------------------------------------
# Chat Input Form
# ---------------------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():

    st.session_state.messages.append(("You", user_input))

    bot_response = get_bot_response(user_input)

    st.session_state.messages.append(("Bot", bot_response))

    st.rerun()