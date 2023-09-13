import streamlit as st
import langchain
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import re
from utils import get_unaswered_questions

# api key
load_dotenv("C:\\Users\\abuza\\Desktop\\jobd\\api.env")
API_KEY = os.getenv("API_KEY")
os.environ['OPENAI_API_KEY'] = API_KEY
llm = ChatOpenAI(temperature=0, model="text-davinci-003", max_tokens=500)
st.title("Job Description Generator")
st.sidebar.subheader("Chat")

conversation = st.sidebar.empty()

if not hasattr(st.session_state, "questions"):
     st.session_state.questions = False

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

Questions = f"""1. Role Definition: Can you please provide a brief overview of the role we're looking to fill?Make a summary of overall job description for that.
2. Key Responsibilities: What are the top 3-5 key responsibilities for this role?
3. Experience(make a list if more than 1): What specific skills and experiences are essential for this role?
4. Education and Certifications: What educational qualifications or certifications are required or desirable for this role?
5. What are the must have skills for this role?(not more than 4)
6. What are the good to have skills for this role?(not more than 2)
7. Growth Opportunities: What growth opportunities are available for this role within the organization?
8. Tools and Software: Are there any specific tools, software, or equipment that the candidate should be familiar with?
9. Budget and Compensation: What is the budget for this position? What is the proposed salary range?
10. Technical Job Functions: What are the technical job functions related to this role?
11. Project and Task Management: Does this role include project management and require the use of different project management methodologies such as scrum, sprint, kanban?
12. Seniority Level(Suggest on the basis of description if not provided explicitlely): What is the seniority level of this role?
Entry-level/Mid-level, hands-on/Senior-level, hands-on/Manager, hands-on/Manager, with direct reports
13. Work Environment(you can select more than 1): What is the work environment?
Remote/Hybrid(partly remote)/In-office
14. Acceptable Work Location/s: What are the acceptable work locations?
Any location (Global), Within the USA,LATAM (Latin America),EU (European Union),APAC (Asia-Pacific),Specific countries (please specify below), City, State OR Metropolitan area
15. Which specific industry the role belong to?
"""

prompt = f"""You are a job description reviewer.
    You are responsible of reviewing a given job description along with questions, 
    You need to capture/extract the answers from the job description and map them to the relevant question.
    
    
    =======================================
    Questions:
        '''{Questions}'''

    Role Title:
        '''{role_title}'''

    Human:
        '''{job_description}'''
    =======================================
    Answered Questions:
    <<Question number. Question title: Answer>>
    
    Unanswered Questions:
    <<Question number. Question title:Not Provided>>
    ========================================
    Open-ended Questions:(Use your knowledge and ask about specifically any technical skills, knowledge, framework etc. needed to succeed as a {role_title})
    <<<<Question number. Question title: Question >>"""

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=1000)


def display_messages(messages):
    chat_text = ""
    for message in messages:
        chat_text += f"**{message['sender']}:** {message['message']}\n\n"
    return chat_text

# Check if the "Generate" button has been pressed
if not hasattr(st.session_state, 'generate_pressed'):
    st.session_state.generate_pressed = False

if not hasattr(st.session_state, 'api_called'):
    st.session_state.api_called = False

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
    if st.session_state.generate_pressed and not st.session_state.api_called:
        #llm1 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=1000)
        st.session_state.questions = get_unaswered_questions(st.session_state.key_information)
        st.session_state.api_called = True

        #print(Questions)
        
        
    if st.session_state.questions:
            #print(Questions)
            # Rest of the code for handling questions and answers
            # ...
            unanswered = "There are some unanswered questions in the job description. Kindly answer the questions"
            exists = any(message['message'] == unanswered for message in st.session_state.messages)
            with st.chat_message("Assistant"):
                    st.markdown("There are some unanswered questions in the job description. Kindly answer the questions")
                    
            if not exists:
                    st.session_state.messages.append({"sender": "Assistant", "message": "In order to effectively create the job description We need answers to the following questions"})
                    conversation.write(display_messages(st.session_state.messages))
            role_description = st.session_state.questions
            # if re.findall(r'\d+\.\s(.+)', role_description):
            #      questions = re.findall(r'\d+\.\s(.+)', role_description)
            # else:
            #      questions = re.findall(r'- (.+\?)', role_description)

            #text = questions

            # Use regular expressions to extract questions
            #questions = re.findall(r'\d+\.\s(.*?)\?', text)
            list_questions = []
            for question in range(len(st.session_state.questions)):
                        
                               
                        answer = st.text_input(f'Question: {st.session_state.questions[question]}', key = f"{question}+++")
                                        
                        if answer:
                            list_questions.append(answer)
                            conversation.empty()
                            exists = any(message['message'] == answer for message in st.session_state.messages)
                            if not exists:
                                st.session_state.messages.append({"sender": "user", "message": f"{st.session_state.questions[question]}: {answer}"})
                            conversation.write(display_messages(st.session_state.messages))
                            with st.chat_message("user"):
                                st.write(answer)
                            with open('CONTEXT.txt', "a") as f:
                                f.write("\nQuestion:" + st.session_state.questions[question] + "\n" + "Answer:" + answer + "\n\n")

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
            

                
                Final_response = llm.predict(f""" You are a Professional Job Description Builder, You will be given an intake questions & answers for different 
    aspects, and you need to generate a Detailed Job Description.
    
    Questions & Answers Pairs:
    {context_normalized}
    
    Generated Job Description:
                
                """) 
                with st.chat_message("assistant"):
                        st.session_state.messages.append({"sender": "assistant", "message": f"{Final_response}"})
                        conversation.write(display_messages(st.session_state.messages))               
                        st.write(Final_response)