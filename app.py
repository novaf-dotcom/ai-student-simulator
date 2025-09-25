import streamlit as st
import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

def get_student_response(prompt):
    """
    Generates a text response from the Gemini API, acting as a student.

    Args:
        prompt (str): The topic or question for the AI student.

    Returns:
        str: The AI's text response or an error message.
    """
    try:
        # Configure the Gemini client with the API key from Streamlit secrets
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        model = genai.GenerativeModel('gemini-pro')

        # This is the crucial part: the system prompt that defines the AI's persona.
        student_persona = (
            "You are an AI simulating a high school student. "
            "When given a topic or question, you must respond as a student would. "
            "You can explain concepts in your own simple words, ask clarifying questions if you're unsure, "
            "or admit if a topic is too difficult or you haven't learned it yet. "
            "Do not act like an expert AI. Your tone should be curious, sometimes uncertain, but always eager to learn. "
            "Keep your answers concise and conversational."
        )

        # Combine the persona and the user's prompt
        full_prompt = f"{student_persona}\n\nTOPIC/QUESTION: \"{prompt}\""


        # Generate content
        response = model.generate_content(full_prompt)

        # Process the response to get the text
        if response and response.text:
            return response.text
        
        st.error("The AI student is quiet... The response was empty.")
        return None

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# --- Streamlit App UI ---
st.set_page_config(layout="wide", page_title="AI Student Simulator", page_icon="🧑‍🎓")

st.title("🧑‍🎓 AI Student Simulator")
st.markdown("Interact with an AI that's learning, just like a real student. Ask it a question and see how it responds!")

with st.sidebar:
    st.header("How it works")
    st.write("This app uses Google's Gemini Pro model to simulate a student's response to a question.")
    st.write("The AI has been given a 'persona' to act like a student, so it might not always know the answer, or it might ask you for help!")
    st.write("You need to provide your own Gemini API key in the Streamlit Community Cloud settings.")
    st.write("For more details, check out the instructions in the `README.md` on the GitHub repository.")

st.divider()

prompt = st.text_input("Enter a topic or question for the AI student:", placeholder="e.g., Can you explain photosynthesis in simple terms?")

if st.button("Ask the AI Student", type="primary", use_container_width=True):
    if prompt:
        with st.spinner("The AI student is thinking..."):
            response_text = get_student_response(prompt)
            if response_text:
                st.info(f"**AI Student's Response:**\n\n{response_text}")
    else:
        st.warning("Please enter a topic or question for the student.")

