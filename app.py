import streamlit as st
import openai
import pdfplumber
import os
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

st.sidebar.header("Options")
summarize_button = st.sidebar.button("Summarize a Paper")
literature_review_button = st.sidebar.button("Generate Literature Review")

if 'show_markdown' not in st.session_state:
    st.session_state.show_markdown = True  
if summarize_button or literature_review_button:
    st.session_state.show_markdown = False

if st.session_state.show_markdown:
    st.title("Task: GPT Tool for HAI Literature Review")
    st.markdown("""  
        🤖 **Hello, Human!** 👋  

        Welcome to the future of research assistance, where humans and AI collaborate like never before. Our AI-powered tool is here to summarize papers, generate literature reviews, and make your life easier—no caffeine required! ☕🚫  

        Remember, while I might know a lot about research, I promise not to "steal" your ideas... unless it's a really good one. 🤫  

        ### **How does this work?**  
        1. Upload your research paper in PDF format.  
        2. Enter the title and author (yes, even AI knows how to cite!).  
        3. Hit the "Summarize" button and let the magic happen!  

        Get ready for some *seriously* helpful AI, with a side of humor. 😄  
    """)

def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text
def safe_openai_request(prompt, retries=5):
    for attempt in range(retries):
        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo", 
                prompt=prompt,
                max_tokens=1500
            )
            return response.choices[0].text.strip()
        except openai.error.RateLimitError:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  
                st.warning(f"Rate limit reached. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                st.error("Rate limit exceeded. Please check your OpenAI usage or plan.")
                raise

if summarize_button:
    st.header("Summarize a Research Paper")
    
    title_and_author = st.text_input("Enter Research Title and Author (e.g., Gnewuch et al., 2023)")
    
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        st.write("Extracting text from the uploaded file...")
        text = extract_text_from_pdf(uploaded_file)
        st.success("Text extraction completed!")
        
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                prompt = f"""
                You are an academic assistant. Summarize the following research paper into these categories:
                1. Context
                2. Research Question and Findings
                3. Theme of Research (Human vs. AI, Human + AI Collaboration)
                4. Method (Conceptual, Modeling, Empirical Study)
                5. Contribution (theoretical, managerial, methodological)
                6. Future Potential and Limitations

                Title and Author: {title_and_author}
                Text: {text[:2000]}  
                """
                try:
                    summary = safe_openai_request(prompt)
                    st.text_area("Summary", summary, height=300)
                except openai.error.RateLimitError:
                    pass

if literature_review_button:
    st.header("Generate a Literature Review")
    theme = st.text_input("Enter the Theme (e.g., Human + AI Collaboration)")
    
    uploaded_files = st.file_uploader("Upload Multiple PDFs", type="pdf", accept_multiple_files=True)
    if uploaded_files and theme:
        summaries = []
        for uploaded_file in uploaded_files:
            st.write(f"Processing {uploaded_file.name}...")
            text = extract_text_from_pdf(uploaded_file)
            prompt = f"""
            You are an academic assistant. Summarize the following research paper into these categories:
            1. Context
            2. Research Question and Findings
            3. Theme of Research (Human vs. AI, Human + AI Collaboration)
            4. Method (Conceptual, Modeling, Empirical Study)
            5. Contribution (theoretical, managerial, methodological)
            6. Future Potential and Limitations

            Text: {text[:2000]}  
            """
            try:
                summary = safe_openai_request(prompt)
                summaries.append(summary)
            except openai.error.RateLimitError:
                pass
        
        st.success("Summaries generated for all uploaded papers!")
        
        if st.button("Generate Literature Review"):
            with st.spinner("Generating literature review..."):
                prompt = f"""
                Based on the following summaries, write a literature review on "{theme}":
                """
                for i, summary in enumerate(summaries):
                    prompt += f"\nPaper {i+1}: {summary}\n"
                prompt += "\nSynthesize the context, findings, and contributions into a cohesive review."

                try:
                    literature_review = safe_openai_request(prompt)
                    st.text_area("Literature Review", literature_review, height=400)
                except openai.error.RateLimitError:
                    pass
