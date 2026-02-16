import streamlit as st
import PyPDF2
from docx import Document
from skills import skills_list, roles

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# ---------- UI STYLE ----------
st.markdown("""
<style>

.big-title{
font-size:48px;
font-weight:800;
text-align:center;
background: linear-gradient(90deg,#00c6ff,#0072ff);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
margin-bottom:10px;
}

.sub-title{
text-align:center;
font-size:18px;
color:#9aa0a6;
margin-bottom:35px;
}

.card{
background:rgba(255,255,255,0.05);
padding:25px;
border-radius:16px;
box-shadow:0 8px 20px rgba(0,0,0,0.25);
margin-bottom:20px;
}

.skill-pill{
display:inline-block;
background:linear-gradient(135deg,#00c853,#64dd17);
color:white;
padding:8px 14px;
margin:6px;
border-radius:20px;
font-size:14px;
font-weight:600;
}

.missing-pill{
display:inline-block;
background:linear-gradient(135deg,#ff4b4b,#ff0000);
color:white;
padding:8px 14px;
margin:6px;
border-radius:20px;
font-size:14px;
font-weight:600;
}

.section-title{
font-size:22px;
font-weight:700;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="big-title">AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Smart AI system to evaluate resumes, skills & job readiness</div>', unsafe_allow_html=True)

# ---------- FUNCTIONS ----------
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text.lower()

def detect_skills(resume_text):
    detected = []
    for skill in skills_list:
        if skill in resume_text:
            detected.append(skill)
    return detected

def resume_quality_score(resume_text, skills_found):
    score = 0
    score += len(skills_found) * 5

    if "project" in resume_text:
        score += 15
    if "internship" in resume_text:
        score += 15
    if "certification" in resume_text:
        score += 10
    if "education" in resume_text or "btech" in resume_text:
        score += 10

    if score > 100:
        score = 100

    return score

# ---------- INPUT ----------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
role_choice = st.selectbox("Select Job Role", list(roles.keys()))

# ---------- MAIN LOGIC ----------
if uploaded_file is not None:

    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    skills_found = detect_skills(resume_text)
    role_skills = roles[role_choice]

    matched = [skill for skill in skills_found if skill in role_skills]
    missing = [skill for skill in role_skills if skill not in skills_found]

    score = int((len(matched) / len(role_skills)) * 100)
    quality = resume_quality_score(resume_text, skills_found)

    col1, col2 = st.columns(2)

    # ---------- DETECTED SKILLS ----------
    with col1:
        st.markdown('<div class="section-title">Detected Skills</div>', unsafe_allow_html=True)

        skills_html = ""
        for skill in skills_found:
            skills_html += f'<span class="skill-pill">{skill}</span>'

        st.markdown(f'<div class="card">{skills_html}</div>', unsafe_allow_html=True)

        # ---------- MISSING SKILLS ----------
        st.markdown('<div class="section-title">Missing Skills</div>', unsafe_allow_html=True)

        if len(missing) == 0:
            st.markdown('<div class="card">No missing skills. Great profile!</div>', unsafe_allow_html=True)
        else:
            missing_html = ""
            for skill in missing:
                missing_html += f'<span class="missing-pill">{skill}</span>'

            st.markdown(f'<div class="card">{missing_html}</div>', unsafe_allow_html=True)

    # ---------- SCORES ----------
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Match Score</div>', unsafe_allow_html=True)
        st.progress(score / 100)
        st.write(str(score) + "% match for " + role_choice)

        st.markdown('<div class="section-title">Resume Quality Score</div>', unsafe_allow_html=True)
        st.progress(quality / 100)
        st.write(str(quality) + " / 100 Resume Strength")

        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- SUGGESTIONS ----------
    st.subheader("Suggestions to Improve")

    if score >= 80:
        st.success("Excellent resume for this role. You are job ready!")
    elif score >= 60:
        st.warning("Good profile. Add a few more skills to improve chances.")
    else:
        st.error("Your resume needs improvement for this role.")

    if "project" not in resume_text:
        st.write("- Add academic or personal projects")

    if "internship" not in resume_text:
        st.write("- Add internship experience")

    if "certification" not in resume_text:
        st.write("- Add relevant certifications")

    if len(missing) > 0:
        st.write("- Consider learning: " + ", ".join(missing))
