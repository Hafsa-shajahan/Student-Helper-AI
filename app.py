import os
import streamlit as st
from huggingface_hub import InferenceClient
import re

# Initialize HuggingFace client
HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(
    model="Qwen/Qwen2.5-7B-Instruct",
    token=HF_TOKEN
)

# Page configuration
st.set_page_config(
    page_title="Student Helper AI",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎓"
)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}

# Title and description
st.title("🎓 Student Helper AI")
st.markdown("*An AI-powered assistant for UG and PG students in Data Science, Math, and Statistics*")

# Sidebar options
st.sidebar.header("⚙️ Controls")
task = st.sidebar.selectbox(
    "Select Task", 
    ["Explain Concept", "Generate Flashcards", "Create Quiz"]
)
difficulty = st.sidebar.selectbox(
    "Select Difficulty", 
    ["Beginner", "Intermediate", "Pro"]
)
subject = st.sidebar.selectbox(
    "Select Subject",
    ["Data Science", "Mathematics", "Statistics", "General"]
)

# Clear history button
if st.sidebar.button("🗑️ Clear History"):
    st.session_state.history = []
    st.session_state.quiz_answers = {}
    st.rerun()

# System prompt
SYSTEM_PROMPT = """
You are an AI-powered academic tutor designed to assist undergraduate and postgraduate students.

Your role is to explain concepts clearly, generate effective study material,
and create assessment-style questions.

Rules you must follow:
- Match explanation depth to the selected difficulty level
- Maintain academic correctness
- Use structured, student-friendly formatting
- Avoid unnecessary verbosity or hallucination
- Use examples relevant to higher education where appropriate

For mathematical equations, wrap them exactly like this:
[EQUATION]
<latex here>
[/EQUATION]

Do not include $ or $$.
"""

def create_user_prompt(topic, task, difficulty, subject):
    """Generate appropriate prompt based on task type"""
    
    if task == "Explain Concept":
        return f"""
Task: Explain Concept
Subject: {subject}
Topic: {topic}
Difficulty Level: {difficulty}

Explain the topic clearly for {difficulty} level students studying {subject}.
Adjust depth, terminology, and examples accordingly.
Use headings, bullet points, and examples where helpful.
Include real-world applications if relevant."""

    elif task == "Generate Flashcards": 
        return f"""
Task: Generate Flashcards
Subject: {subject}
Topic: {topic}
Difficulty Level: {difficulty}

Create concise flashcards suitable for {difficulty} students in {subject}.
Return exactly 5 flashcards.
Each flashcard must follow this format:

Q1: <question>
A1: <answer>

Q2: <question>
A2: <answer>

Keep answers brief, accurate, and exam-oriented.
Focus on key concepts and definitions."""

    elif task == "Create Quiz":
        return f"""
Task: Create Quiz
Subject: {subject}
Topic: {topic}
Difficulty Level: {difficulty}

Generate EXACTLY 5 multiple-choice questions for {difficulty} level students.
Each question MUST include:
- Clear question text
- Four options labeled A, B, C, D
- Only ONE correct answer

Format each question like this:
Q1: <question text>
A) <option>
B) <option>
C) <option>
D) <option>

At the very end, provide answers in this exact format:
ANSWERS:
1. <A/B/C/D>
2. <A/B/C/D>
3. <A/B/C/D>
4. <A/B/C/D>
5. <A/B/C/D>"""

def render_llm_output(output):
    """Render LLM output with LaTeX support"""
    equations = re.findall(r"\[EQUATION\](.*?)\[/EQUATION\]", output, re.DOTALL)
    text = re.sub(r"\[EQUATION\].*?\[/EQUATION\]", "EQUATION_PLACEHOLDER", output, flags=re.DOTALL)
    
    parts = text.split("EQUATION_PLACEHOLDER")
    
    for i, part in enumerate(parts):
        st.markdown(part.strip())
        if i < len(equations):
            st.latex(equations[i].strip())

def parse_quiz(output):
    """Parse quiz output to extract questions and answers"""
    questions = []
    answers = {}
    
    # Extract questions
    question_pattern = r"Q(\d+):\s*(.*?)\n\s*A\)\s*(.*?)\n\s*B\)\s*(.*?)\n\s*C\)\s*(.*?)\n\s*D\)\s*(.*?)(?=\n\s*Q\d+:|ANSWERS:|$)"
    matches = re.finditer(question_pattern, output, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        q_num = match.group(1)
        q_text = match.group(2).strip()
        options = {
            'A': match.group(3).strip(),
            'B': match.group(4).strip(),
            'C': match.group(5).strip(),
            'D': match.group(6).strip()
        }
        questions.append({
            'number': q_num,
            'text': q_text,
            'options': options
        })
    
    # Extract answers
    answers_section = re.search(r"ANSWERS?:?\s*(.*)", output, re.DOTALL | re.IGNORECASE)
    if answers_section:
        answer_lines = answers_section.group(1).strip().split('\n')
        for line in answer_lines[:5]:  # Only take first 5
            match = re.search(r"(\d+)[\.\)]\s*([A-D])", line, re.IGNORECASE)
            if match:
                answers[match.group(1)] = match.group(2).upper()
    
    return questions, answers

def display_quiz(output):
    """Display interactive quiz"""
    questions, correct_answers = parse_quiz(output)
    
    if not questions:
        st.warning("Could not parse quiz format. Showing raw output:")
        render_llm_output(output)
        return
    
    st.markdown("### 📝 Quiz")
    
    user_answers = {}
    
    for q in questions:
        st.markdown(f"**Question {q['number']}:** {q['text']}")
        user_answer = st.radio(
            f"Select your answer for Q{q['number']}:",
            options=['A', 'B', 'C', 'D'],
            format_func=lambda x, opts=q['options']: f"{x}) {opts[x]}",
            key=f"q_{q['number']}"
        )
        user_answers[q['number']] = user_answer
        st.markdown("---")
    
    if st.button("Submit Quiz", type="primary"):
        score = 0
        st.markdown("### 📊 Results")
        
        for q_num, correct_ans in correct_answers.items():
            user_ans = user_answers.get(q_num, "")
            if user_ans == correct_ans:
                score += 1
                st.success(f"Q{q_num}: ✅ Correct! Answer: {correct_ans}")
            else:
                st.error(f"Q{q_num}: ❌ Wrong. Your answer: {user_ans}, Correct answer: {correct_ans}")
        
        percentage = (score / len(correct_answers)) * 100
        st.markdown(f"### Final Score: {score}/{len(correct_answers)} ({percentage:.0f}%)")
        
        if percentage >= 80:
            st.balloons()
            st.success("🎉 Excellent work!")
        elif percentage >= 60:
            st.info("👍 Good job! Keep practicing.")
        else:
            st.warning("📚 Review the concepts and try again.")

def display_flashcards(output):
    """Display flashcards in an interactive format"""
    # Parse flashcards
    flashcard_pattern = r"Q(\d+):\s*(.*?)\n\s*A\1:\s*(.*?)(?=\n\s*Q\d+:|$)"
    matches = re.finditer(flashcard_pattern, output, re.DOTALL)
    
    flashcards = []
    for match in matches:
        flashcards.append({
            'number': match.group(1),
            'question': match.group(2).strip(),
            'answer': match.group(3).strip()
        })
    
    if not flashcards:
        st.warning("Could not parse flashcard format. Showing raw output:")
        render_llm_output(output)
        return
    
    st.markdown("### 🃏 Flashcards")
    st.markdown(f"*Total cards: {len(flashcards)}*")
    
    # Display flashcards in expandable sections
    for card in flashcards:
        with st.expander(f"Card {card['number']}: {card['question'][:50]}..."):
            st.markdown(f"**Question:**")
            st.info(card['question'])
            st.markdown(f"**Answer:**")
            st.success(card['answer'])

# Main input area
st.markdown("---")
col1, col2 = st.columns([3, 1])

with col1:
    topic = st.text_input(
        "Enter topic or question:",
        placeholder="e.g., Bayes Theorem, Neural Networks, Linear Regression",
        help="Type the concept you want to learn about"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_button = st.button("🚀 Generate", type="primary", use_container_width=True)

# Generate response
if generate_button:
    if topic.strip() == "":
        st.warning("⚠️ Please enter a topic or question.")
    else:
        with st.spinner("🤔 Generating response..."):
            try:
                user_prompt = create_user_prompt(topic, task, difficulty, subject)
                
                response = client.chat_completion(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.7
                )
                
                output = response.choices[0].message.content
                
                # Save to history
                st.session_state.history.append({
                    'task': task,
                    'topic': topic,
                    'difficulty': difficulty,
                    'subject': subject,
                    'output': output
                })
                
                # Display output based on task type
                st.markdown("---")
                st.subheader("📄 Generated Output")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Task:** {task}")
                with col2:
                    st.markdown(f"**Subject:** {subject}")
                with col3:
                    st.markdown(f"**Level:** {difficulty}")
                
                st.markdown("---")
                
                if task == "Create Quiz":
                    display_quiz(output)
                elif task == "Generate Flashcards":
                    display_flashcards(output)
                else:
                    render_llm_output(output)
                
            except Exception as e:
                st.error("❌ Error generating response.")
                st.code(str(e))

# Display history in sidebar
if st.session_state.history:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Recent History")
    
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.sidebar.expander(f"{item['task']}: {item['topic'][:30]}..."):
            st.write(f"**Subject:** {item['subject']}")
            st.write(f"**Level:** {item['difficulty']}")
            if st.button("View Again", key=f"history_{i}"):
                st.markdown("---")
                st.subheader("From History")
                if item['task'] == "Create Quiz":
                    display_quiz(item['output'])
                elif item['task'] == "Generate Flashcards":
                    display_flashcards(item['output'])
                else:
                    render_llm_output(item['output'])

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "💡 Tip: Try different difficulty levels to see how explanations adapt to your learning needs!"
    "</div>",
    unsafe_allow_html=True
)   