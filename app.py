import streamlit as st
import os
import io
import base64
import pdf2image
from dotenv import load_dotenv
import google.generativeai as genai

def input_pdf_setup(uploaded_file):
    with st.spinner("Processing PDF... Please wait ⏳"):
        images = pdf2image.convert_from_bytes(
            uploaded_file.read(), 
            dpi=100, 
            poppler_path="/usr/bin/"
        )
    return images
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Job Roles and Skills
job_roles_skills = {
    "Full Stack Developer": ["HTML/CSS", "JavaScript", "Node.js", "Frontend Frameworks", "Backend Development", "Version Control", "Database Management", "Mobile App Development", "APIs", "Testing/Debugging", "System Design and Architecture"],
    "AI/ML Engineer": ["Python", "Machine Learning Frameworks", "Deep Learning", "Data Science Tools", "NLP", "Computer Vision", "Data Visualization", "Big Data Tools", "Model Deployment", "Data Analysis and Statistics"],
    "Cloud and DevOps Engineer": ["Cloud Platforms", "Infrastructure as Code", "Containerization", "Orchestration", "CI/CD", "Monitoring and Logging", "Scripting", "Configuration Management", "Networking", "System Design and Architecture", "Operating Systems"],
    "Software Engineer": ["Version Control", "Database Management", "Networking and Security Protocols", "Blockchain Development", "Cybersecurity", "Security Tools", "Cryptography", "Identity Management", "DevSecOps"]
}

def get_gemini_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_text, pdf_content[0], prompt])
        return response.text if response and hasattr(response, "text") else "Error: No response received."
    except Exception as e:
        return f"Error generating response: {str(e)}"

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
        return [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr).decode()}]
    return None

# Streamlit App
st.set_page_config(page_title="SkillBridgeAI", layout="wide")

# Define color palette - dark theme with blue accents
primary_blue = "#007BFF"         # Bright blue for primary actions
secondary_blue = "#0056b3"       # Darker blue for secondary elements
light_blue = "#e6f2ff"           # Very light blue for subtle highlights
highlight_blue = "#3a7bd5"       # Medium-bright blue for highlights
background_dark = "#121212"      # Very dark background (almost black)
card_dark = "#1E1E1E"            # Slightly lighter dark for cards
text_light = "#E0E0E0"           # Light gray for text
text_muted = "#9E9E9E"           # Muted gray for secondary text

# Comprehensive styling for dark theme
st.markdown(f"""
    <style>
    /* Override Streamlit's default styling */
    .stApp {{
        background-color: {background_dark};
        color: {text_light};
    }}
    
    /* Main container */
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        background-color: {background_dark};
    }}
    
    /* Navbar */
    .navbar {{
        background: linear-gradient(to right, {primary_blue}, {highlight_blue});
        padding: 1.2rem;
        color: white;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }}
    
    /* Headers */
    h1, h2, h3, .stMarkdown p {{
        color: {text_light};
    }}
    
    .section-header {{
        color: {primary_blue};
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background-color: {background_dark};
        border-radius: 4px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_dark};
        color: {text_light};
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {primary_blue} !important;
        color: white !important;
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {primary_blue};
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
    }}
    
    .stButton button:hover {{
        background-color: {highlight_blue};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }}
    
    /* File uploader */
    .stFileUploader div {{
        border: 2px dashed {highlight_blue};
        padding: 15px;
        border-radius: 4px;
        background-color: {card_dark};
    }}
    
    .stFileUploader button {{
        background-color: {primary_blue};
        color: white;
    }}
    
    /* Selectbox and Multiselect */
    .stSelectbox label, .stMultiSelect label, .stTextArea label {{
        color: {primary_blue};
        font-weight: 500;
        font-size: 16px;
    }}
    
    div[data-baseweb="select"] {{
        background-color: {card_dark};
        border-radius: 4px;
        border-color: {highlight_blue};
        color: {text_light};
    }}
    
    div[data-baseweb="select"] div {{
        background-color: {card_dark};
        color: {text_light};
    }}
    
    div[data-baseweb="select"]:focus-within {{
        border-color: {primary_blue};
        box-shadow: 0 0 0 2px rgba(58, 123, 213, 0.2);
    }}
    
    /* Input text areas */
    .stTextArea textarea {{
        border-radius: 4px;
        border-color: {highlight_blue};
        background-color: {card_dark};
        color: {text_light};
    }}
    
    .stTextArea textarea:focus {{
        border-color: {primary_blue};
        box-shadow: 0 0 0 2px rgba(58, 123, 213, 0.2);
    }}
    
    /* Result containers */
    .result-container {{
        background-color: {card_dark};
        padding: 1.5rem;
        border-radius: 4px;
        border-left: 4px solid {primary_blue};
        margin-top: 1rem;
        color: {text_light};
    }}
    
    /* Section dividers */
    .divider {{
        height: 2px;
        background: linear-gradient(to right, {background_dark}, {primary_blue}, {background_dark});
        margin: 1.5rem 0;
        border-radius: 1px;
    }}
    
    /* Upload success indicator */
    .upload-success {{
        background-color: rgba(0, 153, 77, 0.2);
        color: #00cc66;
        padding: 0.75rem;
        border-radius: 4px;
        border-left: 4px solid #00cc66;
        margin-top: 0.5rem;
    }}
    
    /* Tab content container */
    .tab-content {{
        padding: 1.5rem;
        background-color: {card_dark};
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-top: 0.5rem;
    }}
    
    /* Warning messages */
    .stAlert {{
        background-color: {card_dark};
        color: {text_light};
        border-color: {highlight_blue};
    }}
    
    /* Tooltip */
    .stTooltipIcon {{
        color: {primary_blue};
    }}
    </style>
""", unsafe_allow_html=True)

# App header with logo styling
st.markdown("<div class='navbar'>SkillBridgeAI</div>", unsafe_allow_html=True)

# Create columns for better layout
col1, col2 = st.columns([1, 1])

# Left Column - User Inputs
with col1:
    st.markdown("<p class='section-header'>Your Information</p>", unsafe_allow_html=True)
    
    expected_role = st.selectbox("Select Expected Job Role:", list(job_roles_skills.keys()))
    
    skill_options = job_roles_skills.get(expected_role, [])
    skills = st.multiselect("Select Your Skills:", skill_options)
    
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        st.markdown("<div class='upload-success'>✅ PDF Uploaded Successfully</div>", unsafe_allow_html=True)
        pdf_content = input_pdf_setup(uploaded_file)
    else:
        pdf_content = None

# Right Column - Job Description
with col2:
    st.markdown("<p class='section-header'>Job Details</p>", unsafe_allow_html=True)
    job_description = st.text_area("Enter Job Description:", height=345, help="Paste the job description to get more accurate analysis")

# Divider between inputs and results
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Tabs section
st.markdown("<p class='section-header'>Analysis</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Job Role Fit", "Skill Gap Analysis", "Course Recommendations", "Resume Review", "Percentage Match"])

with tab1:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Job Role Fit Prediction")
    if st.button("Predict Fit", key="fit_btn"):
        if skills:
            user_skills = set(skills)
            required_skills = set(job_roles_skills.get(expected_role, []))
            current_skills = user_skills & required_skills
            
            prompt = f"""
            Job Role Fit Prediction
            
            **Skills Provided**:
            - {', '.join(user_skills)}

            **Desired Job Role**:
            - {expected_role}

            **Job Description**:
            {job_description}

            **Current Skills**:
            - {', '.join(current_skills)}
            
            **Task**:
            Predict job role fit percentage and explain why the candidate is a good or bad fit for this role based on their skills and the job description.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, [""], prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.write(response)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please select your skills.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Skill Gap Analysis")
    if st.button("Analyze Skill Gap", key="gap_btn"):
        if skills:
            user_skills = set(skills)
            required_skills = set(job_roles_skills.get(expected_role, []))
            missing_skills = required_skills - user_skills
            current_skills = user_skills & required_skills
            
            prompt = f"""
            Skill Gap Analysis
            
            **Skills Provided**:
            - {', '.join(user_skills)}

            **Desired Job Role**:
            - {expected_role}

            **Job Description**:
            {job_description}

            **Missing Skills**:
            - {', '.join(missing_skills) if missing_skills else "No missing skills"}

            **Current Skills**:
            - {', '.join(current_skills)}
            
            **Task**:
            Analyze the importance of missing skills for this role. Explain which missing skills are most critical to acquire and why.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, [""], prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.write(response)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please select your skills.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Course Recommendations")
    if st.button("Get Recommendations", key="course_btn"):
        if skills:
            user_skills = set(skills)
            required_skills = set(job_roles_skills.get(expected_role, []))
            missing_skills = required_skills - user_skills
            
            prompt = f"""
            Course Recommendations
            
            **Skills Provided**:
            - {', '.join(user_skills)}

            **Desired Job Role**:
            - {expected_role}

            **Job Description**:
            {job_description}

            **Missing Skills**:
            - {', '.join(missing_skills) if missing_skills else "No missing skills"}
            
            **Task**:
            Recommend specific courses, learning resources, or training programs to help the candidate acquire the missing skills.
            For each recommendation, provide the name of the course/resource, the platform (e.g., Coursera, Udemy, etc.), 
            and a brief explanation of why it's beneficial.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, [""], prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.write(response)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please select your skills.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Resume Review")
    if st.button("Analyze Resume", key="resume_btn"):
        if pdf_content:
            prompt = f"""
            Resume Review
            
            You are an experienced HR Manager. Evaluate the resume for the selected job role.
            
            **Job Role**: {expected_role}
            **Job Description**: {job_description}
            
            **Task**:
            Provide detailed feedback on how well the resume matches the job requirements. Include:
            1. Overall impression of the resume
            2. Strengths in relation to the job role
            3. Areas for improvement
            4. Specific suggestions to enhance the resume for this role
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content, prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.write(response)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please upload a resume.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Percentage Match")
    if st.button("Check Match", key="match_btn"):
        if pdf_content:
            prompt = f"""
            Percentage Match Analysis
            
            **Job Role**: {expected_role}
            **Job Description**: {job_description}
            
            **Task**:
            Evaluate the resume against the job role and provide a percentage match. 
            Consider both the standard skills for this role and any specific requirements mentioned in the job description.
            Break down the percentage into different categories:
            1. Technical skills match
            2. Experience level match
            3. Education/certification match
            4. Overall fit
            
            Provide a single overall percentage at the beginning of your response, followed by the detailed breakdown.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content, prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.write(response)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please upload a resume.")
    st.markdown("</div>", unsafe_allow_html=True)