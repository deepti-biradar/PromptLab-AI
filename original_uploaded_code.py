import streamlit as st
from google import genai
from google.genai import types
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PromptLab - Advanced Prompt Engineering",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0px;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 18px;
    margin-bottom: 25px;
}

.prompt-card {
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    margin-bottom: 10px;
}

.answer-box {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    background-color: #fafafa;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🧪 PromptLab</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Advanced Prompt Engineering Laboratory powered by Google Gemini'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""


# ============================================================
# GEMINI API
# ============================================================

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = ""

if not GEMINI_API_KEY:
    st.error(
        "❌ Gemini API key not found. "
        "Please create .streamlit/secrets.toml and add GEMINI_API_KEY."
    )
    st.stop()

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"❌ Unable to initialize Gemini client: {e}")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ PromptLab Controls")

    model = st.selectbox(
        "🤖 Select Gemini Model",
        [
            "gemini-3.7-flash",
            "gemini-3.5-flash-lite"
        ],
        index=0
    )

    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values produce more varied responses."
    )

    max_tokens = st.slider(
        "📝 Maximum Output Tokens",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )

    st.divider()

    st.subheader("📚 Prompting Techniques")

    technique = st.selectbox(
        "Choose Prompt Technique",
        [
            "Zero-shot",
            "Few-shot",
            "Chain-of-Thought",
            "Role",
            "Instruction",
            "Contextual",
            "Structured"
        ]
    )

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_prompt = ""
        st.session_state.last_answer = ""
        st.rerun()

    st.divider()

    st.info(
        "💡 PromptLab helps students experiment with "
        "different prompt engineering techniques."
    )


# ============================================================
# PROMPT TECHNIQUE DESCRIPTIONS
# ============================================================

technique_info = {

    "Zero-shot":
        "Ask Gemini to perform a task without providing examples.",

    "Few-shot":
        "Provide examples so Gemini can learn the expected pattern.",

    "Chain-of-Thought":
        "Ask Gemini to reason through a problem and provide a concise reasoning summary.",

    "Role":
        "Assign a specific expert role or persona to Gemini.",

    "Instruction":
        "Provide explicit instructions describing exactly what Gemini should do.",

    "Contextual":
        "Give background information or context before asking the question.",

    "Structured":
        "Specify the required output format, such as headings, tables, bullets or JSON."
}


st.info(
    f"**{technique} Prompting:** {technique_info[technique]}"
)


# ============================================================
# MAIN INPUT AREA
# ============================================================

col1, col2 = st.columns([2, 1])

with col1:

    st.subheader("✍️ Your Prompt")

    user_input = st.text_area(
        "Enter your task/question",
        height=180,
        placeholder="Example: Explain Generative AI to engineering students."
    )


with col2:

    st.subheader("🎯 Prompt Parameters")

    audience = st.text_input(
        "Target Audience",
        value="Engineering students"
    )

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Simple",
            "Academic",
            "Friendly",
            "Technical",
            "Concise"
        ]
    )

    language = st.selectbox(
        "Response Language",
        [
            "English",
            "Kannada",
            "Hindi"
        ]
    )


# ============================================================
# FEW-SHOT EXAMPLES
# ============================================================

few_shot_examples = ""

if technique == "Few-shot":

    st.subheader("🧩 Few-shot Examples")

    example1_input = st.text_input(
        "Example 1 - Input",
        value="Python is a programming language."
    )

    example1_output = st.text_input(
        "Example 1 - Expected Output",
        value="Python → Programming Language"
    )

    example2_input = st.text_input(
        "Example 2 - Input",
        value="Delhi is the capital of India."
    )

    example2_output = st.text_input(
        "Example 2 - Expected Output",
        value="Delhi → Capital of India"
    )

    few_shot_examples = f"""
Example 1:
Input: {example1_input}
Output: {example1_output}

Example 2:
Input: {example2_input}
Output: {example2_output}
"""


# ============================================================
# CONTEXT INPUT
# ============================================================

context = ""

if technique == "Contextual":

    st.subheader("📖 Context")

    context = st.text_area(
        "Provide background/context",
        height=150,
        placeholder=(
            "Example: The students are third-semester AI & Data Science "
            "students with basic Python knowledge."
        )
    )


# ============================================================
# STRUCTURED OUTPUT
# ============================================================

structure = ""

if technique == "Structured":

    st.subheader("📋 Required Output Structure")

    structure = st.text_area(
        "Define the output format",
        height=150,
        value="""1. Definition
2. Key Features
3. Example
4. Advantages
5. Applications"""
    )


# ============================================================
# GENERATE PROMPT
# ============================================================

def build_prompt():

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
"""

    if technique == "Zero-shot":

        prompt = f"""
Use ZERO-SHOT prompting.

Do not rely on examples.

{base}

Perform the task directly and provide a clear answer.
"""

    elif technique == "Few-shot":

        prompt = f"""
Use FEW-SHOT prompting.

Learn the expected response pattern from these examples:

{few_shot_examples}

Now perform the following task:

{base}
"""

    elif technique == "Chain-of-Thought":

        prompt = f"""
Use a reasoning-oriented approach.

Analyze the problem carefully before answering.

Do not reveal private chain-of-thought or hidden reasoning.
Instead, provide:
1. Key reasoning steps or a concise rationale
2. Final answer

{base}
"""

    elif technique == "Role":

        prompt = f"""
Use ROLE prompting.

Act as an expert professor and AI educator.

Your responsibilities:
- Explain concepts accurately.
- Use practical examples.
- Adapt the explanation to the target audience.
- Avoid unnecessary complexity.

{base}
"""

    elif technique == "Instruction":

        prompt = f"""
Use INSTRUCTION prompting.

Follow these instructions carefully:

1. Understand the task.
2. Answer exactly what is requested.
3. Use clear headings.
4. Use examples where appropriate.
5. Avoid irrelevant information.
6. Match the requested tone.
7. Produce a classroom-friendly response.

{base}
"""

    elif technique == "Contextual":

        prompt = f"""
Use CONTEXTUAL prompting.

Background context:

{context}

Based on the context above, answer the following task:

{base}

Ensure that the answer is relevant to the provided context.
"""

    elif technique == "Structured":

        prompt = f"""
Use STRUCTURED prompting.

Task:

{base}

Return the answer using exactly this structure:

{structure}

Use headings and bullet points where appropriate.
"""

    else:
        prompt = base

    return prompt


# ============================================================
# PROMPT PREVIEW
# ============================================================

if user_input:

    with st.expander("🔍 View Generated Prompt"):

        generated_prompt_preview = build_prompt()

        st.code(
            generated_prompt_preview,
            language="text"
        )


# ============================================================
# GENERATE BUTTON
# ============================================================

generate = st.button(
    "🚀 Generate Answer with Gemini",
    type="primary",
    use_container_width=True
)


# ============================================================
# GEMINI GENERATION
# ============================================================

if generate:

    if not user_input.strip():

        st.warning("⚠️ Please enter a prompt/question.")

    else:

        final_prompt = build_prompt()

        st.session_state.last_prompt = final_prompt

        with st.spinner("🤖 Gemini is generating your answer..."):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )

                answer = response.text

                if not answer:
                    answer = "No response was returned by Gemini."

                st.session_state.last_answer = answer

                # Store conversation
                st.session_state.messages.append(
                    {
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "technique": technique,
                        "prompt": user_input,
                        "answer": answer
                    }
                )

            except Exception as e:

                st.error(
                    f"""
❌ Gemini API Error

{str(e)}

Please check:

1. Your Gemini API key
2. Internet connection
3. API quota
4. Selected Gemini model
"""
                )


# ============================================================
# DISPLAY CURRENT ANSWER
# ============================================================

if st.session_state.last_answer:

    st.divider()

    st.subheader("🤖 Gemini Answer")

    st.markdown(
        '<div class="answer-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state.last_answer
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# PDF GENERATION
# ============================================================

def create_pdf(prompt, answer, technique):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    story.append(
        Paragraph(
            "PromptLab - Gemini Response",
            title_style
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>Prompting Technique:</b> {technique}",
            body_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            body_style
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Prompt",
            heading_style
        )
    )

    safe_prompt = (
        prompt.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )

    story.append(
        Paragraph(
            safe_prompt,
            body_style
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Gemini Answer",
            heading_style
        )
    )

    safe_answer = (
        answer.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )

    story.append(
        Paragraph(
            safe_answer,
            body_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# DOWNLOAD BUTTONS
# ============================================================

if st.session_state.last_answer:

    st.divider()

    st.subheader("📥 Download")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    with col1:

        pdf_file = create_pdf(
            st.session_state.last_prompt,
            st.session_state.last_answer,
            technique
        )

        st.download_button(
            label="📄 Download Answer as PDF",
            data=pdf_file,
            file_name="PromptLab_Gemini_Answer.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    with col2:

        text_content = f"""
PROMPTLAB - GEMINI RESPONSE
============================

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
            label="📝 Download Answer as TXT",
            data=text_content,
            file_name="PromptLab_Gemini_Answer.txt",
            mime="text/plain",
            use_container_width=True
        )


# ============================================================
# CHAT HISTORY
# ============================================================

st.divider()

st.subheader("💬 Chat History")

if len(st.session_state.messages) == 0:

    st.info(
        "No conversation history yet. Generate your first answer."
    )

else:

    for i, message in enumerate(
        reversed(st.session_state.messages)
    ):

        with st.expander(
            f"🗨️ {message['technique']} | "
            f"{message['timestamp']}"
        ):

            st.markdown("### 👤 User Prompt")

            st.write(
                message["prompt"]
            )

            st.markdown("### 🤖 Gemini Answer")

            st.markdown(
                message["answer"]
            )


# ============================================================
# COMPLETE CONVERSATION DOWNLOAD
# ============================================================

if st.session_state.messages:

    st.divider()

    conversation_text = ""

    for i, message in enumerate(
        st.session_state.messages,
        start=1
    ):

        conversation_text += f"""
==================================================
Conversation {i}
==================================================

Time:
{message['timestamp']}

Prompting Technique:
{message['technique']}

USER PROMPT:
{message['prompt']}

GEMINI ANSWER:
{message['answer']}

"""

    st.download_button(
        label="📚 Download Complete Chat History",
        data=conversation_text,
        file_name="PromptLab_Chat_History.txt",
        mime="text/plain",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
<div style="text-align:center; color:gray;">

🧪 <b>PromptLab</b> |
Advanced Prompt Engineering Laboratory

<br>

Zero-shot • Few-shot • Chain-of-Thought • Role •
Instruction • Contextual • Structured

<br><br>

Powered by Google Gemini + Streamlit

</div>
""",
    unsafe_allow_html=True
)