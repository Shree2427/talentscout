EXIT_KEYWORDS = ["exit", "quit", "bye", "end"]

def is_exit_command(user_input):
    return user_input.lower().strip() in EXIT_KEYWORDS

def fallback_response():
    return "I'm sorry, I didn't understand that clearly. Could you please rephrase?"