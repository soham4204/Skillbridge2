import streamlit as st
import os
import io
import base64
import pdf2image
from dotenv import load_dotenv
import google.generativeai as genai
from web_scraping import scrape_linkedin_job, get_gemini_response_part2

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
        # Add formatting instructions to all prompts
        formatting_instructions = """
        Format your response with:
        - Use **bold text** for all headings and important points
        - Use bullet points for lists
        - Keep paragraphs short (2-3 sentences max)
        - Use _italics_ for emphasis
        - Include a brief summary at the top
        - Use markdown formatting throughout
        """
        
        enhanced_prompt = formatting_instructions + "\n\n" + prompt
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([input_text, pdf_content[0], enhanced_prompt])
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

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Default to light theme

# Theme color definitions with enhanced light theme
themes = {
    'light': {
        'primary_blue': "#0066cc",         # Slightly deeper blue for better contrast
        'secondary_blue': "#0056b3",       # Darker blue for secondary elements
        'light_blue': "#e6f2ff",           # Very light blue for subtle highlights
        'highlight_blue': "#3a7bd5",       # Medium-bright blue for highlights
        'background': "#f8f9fa",           # Light background
        'card': "#ffffff",                 # White for cards
        'card_border': "#e9ecef",          # Light gray border for cards
        'text': "#212529",                 # Dark text
        'text_muted': "#6c757d",           # Muted text
        'input_bg': "#ffffff",             # White input background
        'input_border': "#ced4da",         # Light gray input border
        'success': "#28a745",              # Green for success messages
        'warning': "#ffc107",              # Yellow for warnings
        'divider': "rgba(0, 102, 204, 0.2)" # Transparent blue for divider
    },
    'dark': {
        'primary_blue': "#007BFF",         # Bright blue for primary actions
        'secondary_blue': "#0056b3",       # Darker blue for secondary elements
        'light_blue': "#e6f2ff",           # Very light blue for subtle highlights
        'highlight_blue': "#3a7bd5",       # Medium-bright blue for highlights
        'background': "#121212",           # Very dark background
        'card': "#1E1E1E",                 # Slightly lighter dark for cards
        'card_border': "#333333",          # Dark gray border for cards
        'text': "#E0E0E0",                 # Light gray for text
        'text_muted': "#9E9E9E",           # Muted gray for secondary text
        'input_bg': "#2d2d2d",             # Darker input background
        'input_border': "#444444",         # Dark gray input border
        'success': "#28a745",              # Green for success messages
        'warning': "#ffc107",              # Yellow for warnings
        'divider': "rgba(0, 123, 255, 0.3)" # Transparent blue for divider
    }
}

# Theme toggle in sidebar with improved styling
with st.sidebar:
    st.title("Settings")
    
    # Custom CSS for the toggle
    st.markdown("""
    <style>
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Fixed theme toggle with better styling
    theme_container = st.container()
    with theme_container:
        st.write("### Theme Selection")
        
        # Changed to two columns with better sizing and styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.markdown("🌙")
        with col2:
            # Using selectbox instead of toggle for more reliable theme switching
            selected_theme = st.selectbox(
                "",
                options=["Light", "Dark"],
                index=0 if st.session_state.theme == 'light' else 1,
                label_visibility="collapsed"
            )
            st.session_state.theme = selected_theme.lower()
        with col3:
            st.markdown("☀️")

    st.markdown(f"<p style='color: {themes[st.session_state.theme]['primary_blue']}; font-weight: 500;'>Current: {st.session_state.theme.capitalize()} Mode</p>", unsafe_allow_html=True)

# Get current theme colors
theme = themes[st.session_state.theme]

# Apply theme styling with improved light mode and file uploader
st.markdown(f"""
    <style>
    /* Override Streamlit's default styling */
    .stApp {{
        background-color: {theme['background']};
        color: {theme['text']};
    }}
    
    /* Main container */
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        background-color: {theme['background']};
    }}
    
    /* Navbar */
    .navbar {{
        background: linear-gradient(to right, {theme['primary_blue']}, {theme['highlight_blue']});
        padding: 1.5rem;
        color: white;
        font-size: 30px;
        font-weight: bold;
        text-align: center;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}
    
    /* Headers */
    h1, h2, h3, .stMarkdown p {{
        color: {theme['text']};
    }}
    
    .section-header {{
        color: {theme['primary_blue']};
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {theme['divider']};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background-color: {theme['background']};
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid {theme['card_border']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {theme['card']};
        color: {theme['text']};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        border: 1px solid {theme['card_border']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {theme['primary_blue']} !important;
        color: white !important;
        border: 1px solid {theme['primary_blue']} !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {theme['primary_blue']};
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
    }}
    
    .stButton button:hover {{
        background-color: {theme['highlight_blue']};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }}
    
    /* File uploader - Significantly improved for light mode */
    .stFileUploader {{
        margin-bottom: 0.75rem;
    }}
    
    .stFileUploader > div {{
        border: 2px dashed {theme['primary_blue']};
        padding: 20px;
        border-radius: 8px;
        background-color: {theme['light_blue' if st.session_state.theme == 'light' else 'card']};
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }}
    
    .stFileUploader > div:hover {{
        border-color: {theme['highlight_blue']};
    }}
    
    .stFileUploader button {{
        background-color: {theme['primary_blue']};
        color: white;
        border-radius: 6px;
        font-weight: 500;
    }}
    
    /* Selectbox and Multiselect */
    .stSelectbox label, .stMultiSelect label, .stTextArea label {{
        color: {theme['primary_blue']};
        font-weight: 500;
        font-size: 16px;
        margin-bottom: 0.3rem;
    }}
    
    div[data-baseweb="select"] {{
        background-color: {theme['input_bg']};
        border-radius: 6px;
        border: 1px solid {theme['input_border']};
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }}
    
    div[data-baseweb="select"] div {{
        background-color: {theme['input_bg']};
        color: {theme['text']};
    }}
    
    div[data-baseweb="select"]:focus-within {{
        border-color: {theme['primary_blue']};
        box-shadow: 0 0 0 2px rgba(58, 123, 213, 0.2);
    }}
    
    /* Input text areas */
    .stTextArea textarea {{
        border-radius: 6px;
        border: 1px solid {theme['input_border']};
        background-color: {theme['input_bg']};
        color: {theme['text']};
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }}
    
    .stTextArea textarea:focus {{
        border-color: {theme['primary_blue']};
        box-shadow: 0 0 0 2px rgba(58, 123, 213, 0.2);
    }}
    
    /* Result containers */
    .result-container {{
        background-color: {theme['card']};
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid {theme['primary_blue']};
        margin-top: 1rem;
        margin-bottom: 1rem;
        color: {theme['text']};
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }}
    
    /* Enhanced styling for markdown content in results */
    .result-container h1, 
    .result-container h2, 
    .result-container h3, 
    .result-container h4 {{
        color: {theme['primary_blue']};
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}
    
    .result-container ul, 
    .result-container ol {{
        padding-left: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    .result-container li {{
        margin-bottom: 0.5rem;
    }}
    
    .result-container strong {{
        color: {theme['primary_blue']};
        font-weight: 600;
    }}
    
    .result-container p {{
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }}
    
    /* Section dividers */
    .divider {{
        height: 3px;
        background: linear-gradient(to right, transparent, {theme['primary_blue']}, transparent);
        margin: 2rem 0;
        border-radius: 2px;
        opacity: 0.7;
    }}
    
    /* Upload success indicator */
    .upload-success {{
        background-color: rgba(40, 167, 69, 0.1);
        color: {theme['success']};
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid {theme['success']};
        margin-top: 0.75rem;
        display: flex;
        align-items: center;
        font-weight: 500;
    }}
    
    .upload-success svg {{
        margin-right: 0.5rem;
    }}
    
    /* Tab content container */
    .tab-content {{
        padding: 1.75rem;
        background-color: {theme['card']};
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        margin-top: 0.75rem;
        border: 1px solid {theme['card_border']};
    }}
    
    /* Warning messages */
    .stAlert {{
        background-color: {theme['card']};
        color: {theme['text']};
        border-color: {theme['highlight_blue']};
        border-radius: 6px;
    }}
    
    /* Tooltip */
    .stTooltipIcon {{
        color: {theme['primary_blue']};
    }}
    
    /* File uploader text styling */
    .uploadtext {{
        color: {theme['text']};
        text-align: center;
        font-weight: 500;
        margin-bottom: 10px;
    }}
    
    /* Card container styling */
    .card-container {{
        background-color: {theme['card']};
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid {theme['card_border']};
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        height: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# App header with logo styling
st.markdown("<div class='navbar'>SkillBridgeAI</div>", unsafe_allow_html=True)

# Create columns for better layout
col1, col2 = st.columns([1, 1])

# Left Column - User Inputs
with col1:
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<p class='section-header'>Your Information</p>", unsafe_allow_html=True)
    
    expected_role = st.selectbox("Select Expected Job Role:", list(job_roles_skills.keys()))
    
    skill_options = job_roles_skills.get(expected_role, [])
    skills = st.multiselect("Select Your Skills:", skill_options)
    
    # Custom file uploader with better formatting
    st.markdown("<p style='color: {}; font-weight: 500; font-size: 16px;'>Upload Your Resume</p>".format(theme['primary_blue']), unsafe_allow_html=True)
    st.markdown("<div class='uploadtext'>PDF files only</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"])
    
    if uploaded_file:
        st.markdown("<div class='upload-success'>✅ Resume uploaded successfully</div>", unsafe_allow_html=True)
        pdf_content = input_pdf_setup(uploaded_file)
    else:
        pdf_content = None
    
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<p class='section-header'>Job Details</p>", unsafe_allow_html=True)

    # Radio button to select input method
    input_method = st.radio("Choose Input Method:", 
                            ("Enter Manually", "Paste Job URL"))

    job_description = ""

    if input_method == "Paste Job URL":
        job_url = st.text_input("Paste Job URL:", 
                                help="Enter the URL of the job post to extract details automatically")

        if st.button("Submit"):
            if job_url:
                with st.spinner("Fetching job details..."):
                    # Scrape job details
                    job_details = scrape_linkedin_job(job_url)

                    if "error" in job_details:
                        job_description = job_details["error"]
                    else:
                        # Process job details with Gemini AI
                        job_description = get_gemini_response_part2(job_details)
            else:
                st.warning("Please enter a job URL.")

    # Display the processed job description
    st.text_area("Job Description:", job_description, height=305)

    st.markdown("</div>", unsafe_allow_html=True)


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
            
            Begin with a clear overall summary showing the fit percentage. Then use sections with bold headings for:
            1. Strengths
            2. Areas for Improvement
            3. Overall Assessment
            
            Keep your response concise and visually structured.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content or [""], prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.markdown(response, unsafe_allow_html=False)
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
            Analyze the importance of missing skills for this role.
            
            Begin with a brief summary, then create 3 clear categories:
            1. **Critical Skills to Acquire** - Skills that are mandatory for the role
            2. **Important Skills to Develop** - Skills that would significantly improve fit
            3. **Nice-to-Have Skills** - Skills that would be beneficial but aren't essential
            
            For each skill, provide a brief 1-sentence explanation of its importance.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content or [""], prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.markdown(response, unsafe_allow_html=False)
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
            
            Start with a brief intro explaining the importance of these skills for the role.
            
            For each missing skill, provide ONE top recommendation in this format:
            
            **[Skill Name]**
            - **Course:** [Name of course]
            - **Platform:** [Platform name]
            - **Why It's Valuable:** [1-sentence explanation]
            
            Prioritize the most critical skills to learn first. Keep recommendations specific rather than generic.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content or [""], prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.markdown(response, unsafe_allow_html=False)
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
            Provide concise, visual feedback on the resume using this structure:
            
            **Resume Score:** [X/10]
            
            **Strengths:**
            • [Bullet point list of 3-4 key strengths]
            
            **Areas for Improvement:**
            • [Bullet point list of 3-4 key improvements]
            
            **Quick Recommendations:**
            • [3-5 specific, actionable suggestions]
            
            **Overall Assessment:**
            [2-3 sentences with final verdict]
            
            Use bold for all headings and key terms. Keep each bullet point to 1-2 sentences maximum.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content, prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.markdown(response, unsafe_allow_html=False)
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
            
            Begin with a large, clear overall match percentage, then break it down into these categories:
            
            **Technical Skills:** [X%]
            • Brief explanation of technical skills match
            
            **Experience:** [X%]
            • Brief explanation of experience match
            
            **Education/Certifications:** [X%]
            • Brief explanation of education match
            
            **Overall Assessment:**
            [2-3 sentences with final recommendation]
            
            Use visual progress indicators with each percentage.
            Keep explanations to 1-2 sentences each.
            """
            
            input_text = f"Job Role: {expected_role}\nJob Description: {job_description}"
            response = get_gemini_response(input_text, pdf_content, prompt)
            
            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
            st.markdown(response, unsafe_allow_html=False)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("Please upload a resume.")
    st.markdown("</div>", unsafe_allow_html=True)