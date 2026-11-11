import html
from datetime import datetime
from io import BytesIO

import streamlit as st
from google import genai
from google.genai import types
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


st.set_page_config(
    page_title="PromptLab AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 44px; font-weight: 800; text-align: center; margin-bottom: 0;}
    .subtitle {text-align: center; color: #777; font-size: 18px; margin-bottom: 25px;}
    .answer-box {padding: 20px; border-radius: 14px; border: 1px solid #ddd;}
    .small-note {color:#777; font-size:13px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🧪 PromptLab AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Advanced Prompt Engineering Laboratory powered by Google Gemini</div>',
    unsafe_allow_html=True,
)

# ------------------------- Session state -------------------------
for key, default in {
    "messages": [],
    "last_prompt": "",
    "last_answer": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------------- API setup -------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error(
        "❌ Gemini API key not found. Add GEMINI_API_KEY to "
        ".streamlit/secrets.toml (local) or Streamlit Cloud Secrets."
    )
    st.info("See README.md for setup instructions.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as exc:
    st.error(f"❌ Could not initialize Gemini: {exc}")
    st.stop()

# ------------------------- Sidebar -------------------------
with st.sidebar:
    st.header("⚙️ PromptLab Controls")

    model = st.selectbox(
        "🤖 Gemini Model",
        [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
        ],
        index=0,
    )

    temperature = st.slider(
        "🌡️ Temperature", 0.0, 2.0, 0.7, 0.1,
        help="Lower = more predictable. Higher = more varied.",
    )
    max_tokens = st.slider("📝 Maximum Output Tokens", 100, 5000, 1200, 100)

    st.divider()
    st.subheader("📚 Prompting Technique")
    technique = st.selectbox(
        "Choose a technique",
        [
            "Zero-shot",
            "Few-shot",
            "Chain-of-Thought",
            "Role",
            "Instruction",
            "Contextual",
            "Structured",
        ],
    )

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_prompt = ""
        st.session_state.last_answer = ""
        st.rerun()

    st.info(
        "💡 Experiment with the same task using different prompting "
        "techniques and compare the results."
    )

technique_info = {
    "Zero-shot": "Perform the task directly without examples.",
    "Few-shot": "Use examples to demonstrate the desired response pattern.",
    "Chain-of-Thought": "Use careful reasoning internally and provide a concise rationale rather than hidden chain-of-thought.",
    "Role": "Assign an expert role/persona to guide the response.",
    "Instruction": "Give explicit, ordered instructions and constraints.",
    "Contextual": "Supply background information before the task.",
    "Structured": "Require a specific output format.",
}
st.info(f"**{technique}:** {technique_info[technique]}")

# ------------------------- Main inputs -------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("✍️ Your Task")
    user_input = st.text_area(
        "Enter your question or task",
        height=180,
        placeholder="Example: Explain Generative AI to engineering students.",
    )

with col2:
    st.subheader("🎯 Response Parameters")
    audience = st.text_input("Target Audience", "Engineering students")
    tone = st.selectbox(
        "Tone", ["Professional", "Simple", "Academic", "Friendly", "Technical", "Concise"]
    )
    language = st.selectbox("Response Language", ["English", "Kannada", "Hindi"])

few_shot_examples = ""
context = ""
structure = ""

if technique == "Few-shot":
    st.subheader("🧩 Few-shot Examples")
    e1_in = st.text_input("Example 1 - Input", "Python is a programming language.")
    e1_out = st.text_input("Example 1 - Expected Output", "Python → Programming Language")
    e2_in = st.text_input("Example 2 - Input", "Delhi is the capital of India.")
    e2_out = st.text_input("Example 2 - Expected Output", "Delhi → Capital of India")
    few_shot_examples = f"""
Example 1:
Input: {e1_in}
Output: {e1_out}

Example 2:
Input: {e2_in}
Output: {e2_out}
"""

if technique == "Contextual":
    st.subheader("📖 Context")
    context = st.text_area(
        "Provide background/context",
        height=150,
        placeholder="Example: The students have basic Python knowledge.",
    )

if technique == "Structured":
    st.subheader("📋 Required Output Structure")
    structure = st.text_area(
        "Define the output format",
        height=150,
        value="""1. Definition
2. Key Features
3. Example
4. Advantages
5. Applications""",
    )

def build_prompt() -> str:
    base = f"""
You are an advanced AI teaching assistant.

Target audience:
{audience}

Preferred tone:
{tone}

Preferred language:
{language}

Task:
{user_input}
""".strip()

    if technique == "Zero-shot":
        return f"""Use ZERO-SHOT prompting.
Do not rely on examples.
{base}
Perform the task directly and clearly."""

    if technique == "Few-shot":
        return f"""Use FEW-SHOT prompting.
Learn the expected response pattern from these examples:
{few_shot_examples}
Now perform the following task:
{base}"""

    if technique == "Chain-of-Thought":
        return f"""Use a reasoning-oriented approach.
Analyze the problem carefully before answering.
Do not reveal private chain-of-thought or hidden reasoning.
Provide a concise rationale or key reasoning steps followed by the final answer.
{base}"""

    if technique == "Role":
        return f"""Use ROLE prompting.
Act as an expert professor and AI educator.
- Explain accurately.
- Use practical examples.
- Adapt to the target audience.
- Avoid unnecessary complexity.
{base}"""

    if technique == "Instruction":
        return f"""Use INSTRUCTION prompting.
Follow these instructions carefully:
1. Understand the task.
2. Answer exactly what is requested.
3. Use clear headings.
4. Use examples where appropriate.
5. Avoid irrelevant information.
6. Match the requested tone.
7. Keep the response classroom-friendly.
{base}"""

    if technique == "Contextual":
        return f"""Use CONTEXTUAL prompting.

Background context:
{context}

Based on the context above, answer this task:
{base}
Ensure the answer is relevant to the supplied context."""

    return f"""Use STRUCTURED prompting.
Task:
{base}

Return the answer using exactly this structure:
{structure}
Use headings and bullet points where appropriate."""

if user_input.strip():
    with st.expander("🔍 View Generated Prompt", expanded=False):
        st.code(build_prompt(), language="text")

generate = st.button(
    "🚀 Generate Answer with Gemini",
    type="primary",
    use_container_width=True,
)

if generate:
    if not user_input.strip():
        st.warning("⚠️ Please enter a prompt/question.")
    else:
        final_prompt = build_prompt()
        st.session_state.last_prompt = final_prompt

        with st.spinner("🤖 Gemini is generating..."):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                answer = getattr(response, "text", None) or "No response was returned."
                st.session_state.last_answer = answer
                st.session_state.messages.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "technique": technique,
                        "prompt": user_input,
                        "answer": answer,
                    }
                )
            except Exception as exc:
                st.error(
                    "❌ Gemini API Error\n\n"
                    f"{exc}\n\n"
                    "Check your API key, internet connection, quota, and selected model."
                )

# ------------------------- Current answer -------------------------
if st.session_state.last_answer:
    st.divider()
    st.subheader("🤖 Gemini Answer")
    st.markdown(
        f'<div class="answer-box">{st.session_state.last_answer}</div>',
        unsafe_allow_html=True,
    )

# ------------------------- PDF export -------------------------
def create_pdf(prompt: str, answer: str, technique_name: str) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    styles["Title"].alignment = TA_CENTER
    story = [
        Paragraph("PromptLab AI - Gemini Response", styles["Title"]),
        Spacer(1, 15),
        Paragraph(f"<b>Prompting Technique:</b> {html.escape(technique_name)}", styles["BodyText"]),
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["BodyText"],
        ),
        Spacer(1, 15),
        Paragraph("Prompt", styles["Heading2"]),
        Paragraph(html.escape(prompt).replace("\n", "<br/>"), styles["BodyText"]),
        Spacer(1, 15),
        Paragraph("Gemini Answer", styles["Heading2"]),
        Paragraph(html.escape(answer).replace("\n", "<br/>"), styles["BodyText"]),
    ]
    doc.build(story)
    buffer.seek(0)
    return buffer

if st.session_state.last_answer:
    st.divider()
    st.subheader("📥 Download")
    d1, d2 = st.columns(2)

    with d1:
        pdf_file = create_pdf(
            st.session_state.last_prompt,
            st.session_state.last_answer,
            technique,
        )
        st.download_button(
            "📄 Download Answer as PDF",
            data=pdf_file,
            file_name="PromptLab_Gemini_Answer.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with d2:
        text_content = f"""PROMPTLAB AI - GEMINI RESPONSE
================================

Prompting Technique:
{technique}

Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PROMPT
------
{st.session_state.last_prompt}

GEMINI ANSWER
-------------
{st.session_state.last_answer}
"""
        st.download_button(
            "📝 Download Answer as TXT",
            data=text_content,
            file_name="PromptLab_Gemini_Answer.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ------------------------- History -------------------------
st.divider()
st.subheader("💬 Chat History")

if not st.session_state.messages:
    st.info("No conversation history yet. Generate your first answer.")
else:
    for message in reversed(st.session_state.messages):
        with st.expander(
            f"🗨️ {message['technique']} | {message['timestamp']}"
        ):
            st.markdown("### 👤 User Prompt")
            st.write(message["prompt"])
            st.markdown("### 🤖 Gemini Answer")
            st.markdown(message["answer"])

if st.session_state.messages:
    conversation_text = "\n".join(
        [
            f"""==================================================
Conversation {i}
==================================================
Time: {m['timestamp']}
Prompting Technique: {m['technique']}

USER PROMPT:
{m['prompt']}

GEMINI ANSWER:
{m['answer']}
"""
            for i, m in enumerate(st.session_state.messages, 1)
        ]
    )
    st.download_button(
        "📚 Download Complete Chat History",
        data=conversation_text,
        file_name="PromptLab_Chat_History.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.divider()
st.markdown(
    """
    <div style="text-align:center; color:gray;">
    🧪 <b>PromptLab AI</b> · Zero-shot · Few-shot · Reasoning · Role ·
    Instruction · Contextual · Structured
    <br><br>
    Powered by Google Gemini + Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
