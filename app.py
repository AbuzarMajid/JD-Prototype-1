import streamlit as st
import langchain
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import re

# api key
load_dotenv("C:\\Users\\abuza\\Desktop\\jobd\\api.env")
API_KEY = os.getenv("API_KEY")
os.environ['OPENAI_API_KEY'] = API_KEY
llm = ChatOpenAI(temperature=0, model="text-davinci-003", max_tokens=500)
st.title("Job Description Generator")
st.sidebar.subheader("Chat")

conversation = st.sidebar.empty()

# getiing inital
role_title = st.text_input("Job Role", key="job role")
if role_title:
    with st.chat_message("User"):
        st.markdown(f"Job Role: {role_title}")

job_description = st.text_input("Job Description", key="job description")
job_description = job_description.rstrip(".")
if job_description:
    with st.chat_message("User"):
        st.markdown(f"Job Description: {job_description}")

prompt = f"""Task: Analyze the {job_description} by using a certain criteria provided below for role of {role_title}

Read and understand the provided description thoroughly and find the answers of the following questions:

1. Role Definition: Can you please provide a brief overview of the role we're looking to fill?
2. Key Responsibilities: What are the top 3-5 key responsibilities for this role?
3. Experience(make a list if more than 1): What specific skills and experiences are essential for this role?
4. Education and Certifications: What educational qualifications or certifications are required or desirable for this role?
5. What are the must have skills for this role?(make a list if more than one)
6. What are the good have skills for this role?(make a list if more than one)
7. Growth Opportunities: What growth opportunities are available for this role within the organization?
8. Tools and Software: Are there any specific tools, software, or equipment that the candidate should be familiar with?
9. Budget and Compensation: What is the budget for this position? What is the proposed salary range?
10. Then check that the provided job description falls under which of the following Job Functions:

--Data-Related (Data Scientist, Data Engineer / Data Architect, BI Analyst / Developer, Quant (Quantitative Scientist/Analyst))

If it is data related, check the provided job description to find the information regarding the skills/tools below. If you cannot find an answer generate a question regarding that
 Data Science and Analytics:
- Data Analysis
- Statistical Analysis
- Data Mining
- Data Visualization (Data Visualization Tools, Dashboard Design, Power BI, Tableau, D3.js, Vega-Lite, Seaborn)
- Big Data Technologies (Big Data Platforms, Real-time Analytics, Real-time Data Processing, Hadoop, Spark, Flink, Hive, MapReduce, S3, EC2)
- Data Processing, Engineering, and Storage (ETL Processes, Data Augmentation, Feature Engineering, Data Imputation, Missing Data Analysis)


–Machine Learning (Machine Learning Engineer / AI Engineer, Machine Learning Researcher, MLOps Engineer, NLP Engineer, Computer Vision Engineer, Robotics Engineer)

If it is Machine learning related, check the provided job description to find the information regarding the skills/tools below. If you cannot find an answer generate a question regarding that
- Machine Learning Techniques and Algorithms (Machine Learning Algorithms, Machine Learning Basics, Deep Learning Frameworks, Reinforcement Learning, Natural Language Processing, Neural Networks)

11. Project and Task Management (Task and Issue Tracking, Project Management Methodologies, Scrum, Kanban, Agile Methodologies)

12. Seniority Level: 
Entry-level/Mid-level, hands-on/Senior-level, hands-on/Manager, hands-on/Manager, with direct reports

13. Work Environment(you can select more than 1): 
Remote/Hybrid(partly remote)/In-office

14. Acceptable Work Location/s:

[  ] Any location (Global)
[  ] Within the USA
[  ] LATAM (Latin America)
[  ] EU (European Union)
[  ] APAC (Asia-Pacific)
[  ] Specific countries (please specify below)
[  ] City, State OR Metropolitan area

15. Preferred Time Zone Overlap:

[  ] Open to All-Time Zones
[  ] Same as Company's Time Zone (e.g., EST, CST, PST)
[  ] Minimum 5-Hour Overlap with Company's Time Zone Per Day
[  ] Minimum 3-Hour Overlap with Company's Time Zone Per Day
[  ] Minimum 1-Hour Overlap with Company's Time Zone Per Day

16. Industry(select most relevant): 

Healthcare
Marketing
Finance
Retail
Energy
Manufacturing
Education
Public Sector
Media and Entertainment
Transportation & Logistics
Agriculture
Real Estate
Human Resources
E-commerce
Telecommunications
Travel & Hospitality
"""

llm = ChatOpenAI(temperature=0, model="gpt-4", max_tokens=1000)


def display_messages(messages):
    chat_text = ""
    for message in messages:
        chat_text += f"**{message['sender']}:** {message['message']}\n\n"
    return chat_text

# Check if the "Generate" button has been pressed
if not hasattr(st.session_state, 'generate_pressed'):
    st.session_state.generate_pressed = False

# if not hasattr(st.session_state, 'key_information'):
#     st.session_state.key_information = False

if role_title and job_description:
    if not st.session_state.generate_pressed:
        key_information = llm.predict(prompt)
        
        if st.button("GENERATE JOB DESCRIPTION", key="gen1"):

            st.session_state.generate_pressed = True
            st.session_state.messages = []
            st.session_state.messages.append({"sender": "user", "message": f"Job Role: {role_title}, Job Description: {job_description}"})
            conversation.write(display_messages(st.session_state.messages))
            
            # Set the key_information in session state
            st.session_state.key_information = key_information
            
            with open('CONTEXT.txt', "w", encoding="utf-8") as f:
                f.write(f"Job Role: {role_title}\n\njob_description: {job_description}\n\nJob Description Main Points: \n{key_information}")


    # Rest of the code continues to run based on user input
    if st.session_state.generate_pressed:
        llm1 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=1000)
        Questions = llm.predict(st.session_state.key_information + "\nGenerate the questions regarding any main point, skills and tools that you dont find in the job description.")


        #print(Questions)
        
        
        if Questions:
            print(Questions)
            # Rest of the code for handling questions and answers
            # ...
            unanswered = "There are some unanswered questions in the job description. Kindly answer the questions"
            exists = any(message['message'] == unanswered for message in st.session_state.messages)
            with st.chat_message("Assistant"):
                    st.markdown("There are some unanswered questions in the job description. Kindly answer the questions")
                    
            if not exists:
                    st.session_state.messages.append({"sender": "Assistant", "message": "In order to effectively create the job description We need answers to the following questions"})
                    conversation.write(display_messages(st.session_state.messages))
            role_description = Questions
            # if re.findall(r'\d+\.\s(.+)', role_description):
            #      questions = re.findall(r'\d+\.\s(.+)', role_description)
            # else:
            #      questions = re.findall(r'- (.+\?)', role_description)

            text = Questions

            # Use regular expressions to extract questions
            questions = re.findall(r'\d+\.\s(.*?)\?', text)
            list_questions = []
            for question in range(len(questions)):
                        
                               
                        answer = st.text_input(f'Question: {questions[question]}', key = f"{question}+++")
                                        
                        if answer:
                            list_questions.append(answer)
                            conversation.empty()
                            exists = any(message['message'] == answer for message in st.session_state.messages)
                            if not exists:
                                st.session_state.messages.append({"sender": "user", "message": f"{questions[question]}: {answer}"})
                            conversation.write(display_messages(st.session_state.messages))
                            with st.chat_message("user"):
                                st.write(answer)
                            with open('CONTEXT.txt', "a") as f:
                                f.write("\nQuestion:" + questions[question] + "\n" + "Answer:" + answer + "\n\n")

            with open("CONTEXT.txt", "r") as f:
                context_raw = f.read()
            context_raw = context_raw.split("\n\n")
            context_cleaned = []
            for i in context_raw:
                     if i in context_cleaned:
                          continue
                     else:
                          context_cleaned.append(i)

            context_normalized = "\n\n".join(context_cleaned)
                

            if st.button("GENERATE JOB DESCRIPTION", key = "gen2"):


                    

                
                 final_response = llm.predict(f"""Using the {context_normalized} provided, act as a specialized HR consultant to generate a thorough and compelling job description. You are required to STRICTLY utilize the information given in the context to create the job description. Here is the structure your response should follow:

                Job Title: Review the job title provided in the context. If it's clear, concise, and accurately reflects the role, keep it. If not, modify it to better match the role requirements and be easily understood by qualified candidates. Use industry-standard or recognizable job titles.

                Company Information: Based on the provided job description, write a paragraph of 3 to 4 sentences describing the company's culture, values, and industry. Use this information to portray the company as an attractive workplace.

                Job Overview & Expectations: From the provided job description, distill a paragraph of 3 to 4 sentences that give a succinct overview of the role and outline the company's expectations from the successful candidate.

                Job Duties and Responsibilities: Based on the initial job description, write 4 to 7 bullet points that clearly define the core tasks and duties involved in the role. These should be specific, actionable, and strongly tied to the job title.

                Qualifications and Skills: Divide this section into two parts based on the information given in the context. For Required qualifications and skills, list 4 to 7 bullet points of the necessary qualifications or skills for the role. For Preferred qualifications and skills, state 2 to 5 bullet points of desirable but not compulsory skills or qualifications.

                Call to Action: Generate 1 to 2 motivating sentences that include the application deadline, and an email address and/or a link for applications.

                The goal is to enhance the given job description while emphasizing the importance of the job title in attracting suitable applicants. Utilize clear, professional, and compelling language to create a job description that is appealing and easy to understand for the qualified candidates. Also follow the following best practices:
                - Replace ‘the ideal candidate’ with ‘you’
                - delete buzzwords and unnecessary qualifications
                - Use engaging subheads (e.g. “What we expect of you”)
                - Describe a day in the life 
                - Talk problems and projects
                - Set reasonable requirements
                - Use clear language
                - Avoid words related to Sexism, Racism, Tokenism, Ableism, Ageism, Elitism, Religion
                instructions
                - if the provided content 
                
                """) 
                 with st.chat_message("assistant"):
                        st.session_state.messages.append({"sender": "assistant", "message": f"{final_response}"})
                        conversation.write(display_messages(st.session_state.messages))               
                        st.write(final_response)
