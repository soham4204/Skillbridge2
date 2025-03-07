import os
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

def scrape_linkedin_job(url):
    """Scrapes job details from a LinkedIn job listing."""
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Fetch the webpage
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return {"error": f"Failed to fetch job page. Status code: {response.status_code}"}

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    return soup


def get_gemini_response_part2(job_data):
    """Uses Gemini AI to format and summarize job details."""
    
    try:
        # Define the prompt
        prompt = """
        You will be given raw job details extracted from a webpage. 
        Your task is to extract the following information:
        - Job Title
        - Company Name
        - Location
        - Job Type (Full-time, Part-time, Contract, etc.)
        - Salary (if mentioned)
        - Required Experience
        - Job Description
        - Skills Required
        - Application Link (if available)
        - Any other relevant details

        If any piece of information is not found, mention "Not Found" for that field.

        Extract the information in the following structured format:

        Job Title: <Extracted Job Title or "Not Found">
        Company Name: <Extracted Company Name or "Not Found">
        Location: <Extracted Location or "Not Found">
        Job Type: <Extracted Job Type or "Not Found">
        Salary: <Extracted Salary or "Not Found">
        Required Experience: <Extracted Experience or "Not Found">
        Job Description: <Extracted Job Description or "Not Found">
        Skills Required: <Extracted Skills or "Not Found">
        Application Link: <Extracted Link or "Not Found">
        Other Details: <Extracted Other Details or "Not Found">

        Here is the job details data:

        {job_data}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt.format(job_data=str(job_data)))

        return response.text if response and hasattr(response, "text") else "Error: No response received."

    except Exception as e:
        return f"Error generating response: {str(e)}"


# if __name__ == "__main__":
#     job_url = "https://www.linkedin.com/jobs/view/human-resources-manager-at-med-talent-4176407666?trk=public_jobs_topcard-title"

#     # Scrape job details
#     job_details = scrape_linkedin_job(job_url)
    
#     if "error" in job_details:
#         print(job_details["error"])
#     else:
#         # Process and format with Gemini
#         formatted_response = get_gemini_response(job_details)
#         print(formatted_response)
