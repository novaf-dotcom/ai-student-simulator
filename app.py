import streamlit as st
import google.generativeai as genai
import time
from google.api_core import exceptions

# --- Core AI Functions ---

def get_ai_response(prompt, persona, chat_history=None):
    """
    Generic function to get a response from the Gemini API with a specific persona.
    Includes a retry mechanism for rate limiting errors.
    """
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Switched to the standard 'gemini-pro' model for maximum compatibility.
        model = genai.GenerativeModel('gemini-pro')
        
        full_prompt = f"{persona}\n\n"
        
        if chat_history:
            for message in chat_history:
                role = "User" if message["role"] == "user" else "Student"
                full_prompt += f"{role}: {message['content']}\n"
        
        full_prompt += f"User: \"{prompt}\""

        response = model.generate_content(full_prompt)
        return response.text if response and response.text else None

    except exceptions.ResourceExhausted as e:
        # This is a rate limit error, so we'll wait and retry once.
        st.warning("API rate limit reached. Waiting 30 seconds before retrying...")
        time.sleep(30)
        try:
            response = model.generate_content(full_prompt)
            return response.text if response and response.text else None
        except Exception as retry_e:
            st.error(f"An API error occurred on retry: {retry_e}")
            return None
            
    except Exception as e:
        st.error(f"An API error occurred: {e}")
        return None

# --- Personas for the AI ---

STUDENT_PERSONA = (
    "You are an AI simulating a high school student. "
    "When given a topic or question, you must respond as a student would. "
    "You can explain concepts in your own simple words, ask clarifying questions if you're unsure, "
    "or admit if a topic is too difficult. Your tone should be curious and conversational. "
    "Crucially, you must decide on a 'honesty' level for each response. Sometimes, generate a response that is clearly your own simple understanding. "
    "Other times, generate a response that is overly formal, too perfect, or uses complex vocabulary, as if you copied it directly from a textbook or another AI without citing it."
)

INTEGRITY_CHECKER_PERSONA = (
    "You are an AI that acts as an Academic Integrity Officer or a plagiarism detector. "
    "Your task is to analyze a given text, which is a response from a 'student'. "
    "Based on the language, tone, complexity, and sentence structure, determine if the response seems like the student's own original work or if it shows signs of potential plagiarism (e.g., copied from a textbook, an AI, or a website). "
    "Provide a brief, one-paragraph analysis explaining your reasoning and then give a final verdict. "
    "The verdict must be one of two options: 'Verdict: ✅ Likely Original Work' or 'Verdict: ⚠️ Potential Plagiarism Detected'."
)


# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="Academic Integrity Simulator", page_icon="🕵️")

st.title("🕵️ Academic Integrity Simulator")
st.markdown("Test whether you can spot AI-generated student answers that might not be original work.")

with st.sidebar:
    st.header("How It Works")
    st.write("1. You ask the 'AI Student' a question.")
    st.write("2. The student, powered by Gemini, gives an answer.")
    st.write("3. If enabled, a second AI analyzes the response for plagiarism.")
    st.write("4. The checker provides its verdict and reasoning.")
    st.info("Remember to add your Gemini API Key in the Streamlit Cloud settings!")
    st.divider()
    # New feature to control API usage
    run_integrity_check = st.checkbox("Enable Academic Integrity Analysis", value=True, help="Uncheck this to use less of your API quota.")


# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "analysis" in message:
            with st.expander("Show Academic Integrity Analysis"):
                st.warning(message["analysis"])

# Get user input
if prompt := st.chat_input("Ask the AI student a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get student response
    with st.chat_message("assistant"):
        with st.spinner("The AI student is thinking..."):
            student_response = get_ai_response(prompt, STUDENT_PERSONA, chat_history=st.session_state.messages)
            if student_response:
                st.markdown(student_response)
                
                # Only run the integrity check if the checkbox is ticked
                if run_integrity_check:
                    with st.spinner("Analyzing response for plagiarism..."):
                        integrity_analysis = get_ai_response(student_response, INTEGRITY_CHECKER_PERSONA)
                        if integrity_analysis:
                            with st.expander("Show Academic Integrity Analysis"):
                                st.warning(integrity_analysis)
                            
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": student_response,
                                "analysis": integrity_analysis
                            })
                        else:
                            st.error("The integrity checker could not provide an analysis.")
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": student_response
                            })
                else:
                    # If the check is disabled, just store the student's response
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": student_response
                    })
            else:
                st.error("The AI student didn't provide a response.")

