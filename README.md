# Student Helper AI 🎓

An AI-powered educational assistant for undergraduate and postgraduate students to learn Data Science, Mathematics, and Statistics concepts.

## Features

- **Explain Concepts**: Get detailed explanations adapted to your difficulty level (Beginner/Intermediate/Pro)
- **Generate Flashcards**: Create study flashcards with questions and answers
- **Create Quiz**: Generate multiple-choice quizzes with automatic scoring

## Tech Stack

- **Frontend**: Streamlit
- **AI Model**: HuggingFace Inference API (Qwen 2.5 7B Instruct)
- **Language**: Python 3.8+

## Installation & Setup

1. Clone the repository
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Create `.streamlit/secrets.toml` and add your HuggingFace token:
```toml
   HF_TOKEN = "your_token_here"
```
4. Run the application:
```bash
   streamlit run app.py
```

## Usage

1. Select a task from the sidebar (Explain/Flashcards/Quiz)
2. Choose your difficulty level
3. Select the subject area
4. Enter your topic or question
5. Click "Generate" to get AI-powered learning materials

## Subjects Covered

- Data Science (Neural Networks, Machine Learning, Data Analysis)
- Mathematics (Calculus, Linear Algebra, Statistics)
- Statistics (Probability, Hypothesis Testing, Distributions)

## Project Structure
```
student-helper-ai/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Future Enhancements

- Add more AI models
- Save learning progress
- Export study materials as PDF

## Author

Hafsa Shajahan
UG/PG Student Project - 2025