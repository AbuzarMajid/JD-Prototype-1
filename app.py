import streamlit as st
import langchain
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import re
from utils import unansques
import logging

# api key
load_dotenv("C:\\Users\\abuza\\Desktop\\jobd\\api.env")
API_KEY = os.getenv("API_KEY")
os.environ['OPENAI_API_KEY'] = API_KEY
llm = ChatOpenAI(temperature=0, model="text-davinci-003", max_tokens=500)
st.title("AI Powered Job Description Generator")
st.sidebar.subheader("Chat History")

conversation = st.sidebar.empty()

if not hasattr(st.session_state, "questions"):
     st.session_state.questions = False
if not hasattr(st.session_state, 'api_called'):
    st.session_state.api_called = False

if not hasattr(st.session_state, 'entry_1'):
      st.session_state.entry_1 = False

if not hasattr(st.session_state, 'entry_2'):
      st.session_state.entry_2 = False

if not hasattr(st.session_state, 'entry_3'):
      st.session_state.entry_3 = False

if not hasattr(st.session_state, 'entry_4'):
      st.session_state.entry_4 = False



# getiing inital
role_title = st.text_input("Role Title", key="job role", placeholder="Enter your Role Title")
if role_title:
    with st.chat_message("User"):
        st.markdown(f"Job Role: {role_title}")

        
job_description = st.text_area("Job Description", key="job description", placeholder="Enter your raw Job Description", height=400)
job_description = job_description.rstrip(".")
if job_description:
    with st.chat_message("User"):
        st.markdown(f"Job Description: {job_description}")

Questions = f"""1. Role Definition: Can you please provide a brief overview of the role we're looking to fill?Make a summary of the overall job description for that.
2. Key Responsibilities: What are the top 3-5 key responsibilities for this role?
3. Experience(make a list if more than 1): What specific skills and experiences are very essential for this role?
4. Education and Certifications: What educational qualifications or certifications are required or desirable for this role?
5. What are the must have or essential skills for this role?(max 4)- Make sure to include only crucial or necessary skills from the job description
6. What are the good-to-have skills for this role?(max 2)-This can include preferred skills, experience or expertise
7. Growth Opportunities: What growth opportunities are available for this role within the organization?
8. Tools and Software: Are there any specific tools, software, or equipment that the candidate should be familiar with?
9. Budget and Compensation: What is the budget for this position? What is the proposed salary range?
10. Technical Job Functions: What are the technical job functions related to this role?
11. Project and Task Management: Does this role include project management and require the use of different project management methodologies such as scrum, sprint, kanban?
12. Seniority Level(Suggest on the basis of description if not provided explicitlely): What is the seniority level of this role?
Entry-level/Mid-level, hands-on/Senior-level, hands-on/Manager, hands-on/Manager, with direct reports
13. Work Environment: What is the work environment?
Remote/Hybrid(partly remote)/In-office
14. Acceptable Work Location/s: What are the acceptable work locations?
Any location (Global), Within the USA,LATAM (Latin America),EU (European Union),APAC (Asia-Pacific),Specific countries (please specify below), City, State OR Metropolitan area
15. Which specific industry the role belongs to?

"""

prompt = f"""You are a job description reviewer who carefully reviews and answers each point in detail.
    You are responsible of reviewing a given job description along with questions, 
    You need to capture/extract the answers from the job description and map them to the relevant question.
    
    
    =======================================
    Questions:
        '''{Questions}'''

    Role Title:
        '''{role_title}'''

    Human:
        '''{job_description}'''
    ======================================
    Answered Questions:
    <<Question number. Question title: Answer>>
    ======================================
    Unanswered Questions: (the questions for which information is not provided)
    <<Question number. Question title:Not Provided>>
    ======================================
    Open-ended Questions:(3 questions from hiring manager, its most IMPORTANT part. Use your knowledge and ask specifically ask about any technical skills, knowledge, framework etc. needed to succeed as a {role_title}). It can include the questions about related skils and you have to think critically for that.
    <<<<Question number. Question title: Question >>
    
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



if role_title and job_description:
    if not st.session_state.generate_pressed:
        
        print("entered 1")
        if st.button("GENERATE JOB DESCRIPTION", key="gen1"):
            print("entered 2")
            st.session_state.generate_pressed = True
            st.session_state.messages = []
            st.session_state.messages.append({"sender": "user", "message": f"Job Role: {role_title}, Job Description: {job_description}"})
            conversation.write(display_messages(st.session_state.messages))
            
            
            with open('CONTEXT.txt', "w", encoding="utf-8") as f:
                f.write(f"Job Role: {role_title}\n\njob_description: {job_description}\n\n")

            # Set the key_information in session state

    # Rest of the code continues to run based on user input
    if st.session_state.generate_pressed and not st.session_state.api_called:
        #llm1 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=1000)
        key_information = llm.predict(prompt)     
        st.session_state.key_information = key_information

        context_raw = st.session_state.key_information
        context_raw = context_raw.split("\n\n")
        context_cleaned = []
        for i in context_raw:
                     if i in context_cleaned:
                          continue
                     else:
                          context_cleaned.append(i)

        context_normalized = "\n\n".join(context_cleaned)

        final = context_normalized.split('Unanswered Questions')[0]

        with open ('CONTEXT.txt', "a") as f:
                response = f.write(final)
        st.session_state.questions = unansques(key_information)

        st.session_state.api_called = True

        #print(f'{st.session_state.questions} + these are the questions found')
        
        
    if st.session_state.questions:
            #print(Questions)
            # Rest of the code for handling questions and answers
            # ...
            unanswered = "There are some unanswered questions in the job description. Kindly answer the questions"
            exists = any(message['message'] == unanswered for message in st.session_state.messages)
            with st.chat_message("Assistant"):
                    st.markdown("There are some unanswered questions in the job description. Kindly answer the questions")
            print(st.session_state.questions) 
            if not exists:
                    st.session_state.messages.append({"sender": "Assistant", "message": "In order to effectively create the job description We need answers to the following questions"})
                    conversation.write(display_messages(st.session_state.messages))
            role_description = st.session_state.questions


            list_questions = []
            for question in role_description:
                answer = st.text_input(f'Question: {question}', key = f"{question}+++")
                                
                if answer:
                    list_questions.append(answer)
                    conversation.empty()
                    exists = any(message['message'] == answer for message in st.session_state.messages)
                    if not exists:
                        st.session_state.messages.append({"sender": "user", "message": f"{question}: {answer}"})
                    conversation.write(display_messages(st.session_state.messages))
                    with st.chat_message("user"):
                        st.write(answer)
                    with open('CONTEXT.txt', "a") as f:
                        f.write("\nQuestion:" + question + "\n" + "Answer:" + answer + "\n")


            with open("CONTEXT.txt", "r") as f: 
                final_response = f.read()
            
            st.session_state.entry_1 = True
            st.session_state.FR = final_response

    if st.session_state.entry_1:
        st.empty()
        if st.button("GENERATE FINAL JOB DESCRIPTION", key = "gen2"):
            

                
                Final_Response = llm.predict(f""" You are MIKE and You role in our organization is to write Professional and Detailed Job Description Builder based on the information provided, You will be given an intake questions & answers for different 
    aspects, and you need to generate a Detailed Job Description. Think carefully and design the job description in your best way possible
    
    Questions & Answers Pairs:
    {st.session_state.FR}
    
    Generated Job Description:
                
                """) 
                with st.chat_message("assistant"):
                        st.session_state.messages.append({"sender": "assistant", "message": f"{Final_Response}"})
                        conversation.write(display_messages(st.session_state.messages))               
                        st.write(Final_Response)

                st.session_state.fr= Final_Response
                st.session_state.entry_1 = False
                st.session_state.entry_2 = True
                st.session_state.entry_4 = True
    if st.session_state.entry_4:
        if st.button('Review the Job description', key='rjd'):
            if st.session_state.entry_2:
            
                st.session_state.requested_changes = st.text_input("Requested changes", key="req_changes", placeholder="Write the changes you want in the final job description")
                with st.chat_message("User"):
                        st.markdown(f"Requested changes: {st.session_state.requested_changes}")
                        st.session_state.entry_3 =True
                        st.session_state.entry_2 = True

        elif st.session_state.entry_3:
                st.session_state.requested_changes = st.text_input("Requested changes", key="req_changes", placeholder="Write the changes you want in the final job description")
                with st.chat_message("User"):
                    st.markdown(f"Requested changes: {st.session_state.requested_changes}")
                    st.session_state.entry_3 =True
                    st.session_state.entry_2 = True 

    if st.session_state.entry_3: 
            if st.session_state.requested_changes != "":
                
                if st.button('Generate', key='generate_button'):
                        st.session_state.entry_2 = False
                        final_prompt = f"""Task: Modify the job description using the Requested Changes. Do not just paraphrase but also try to improve it in a highly professional manner

                        //{st.session_state.FR}//

                        Requested Changes:

                        {st.session_state.requested_changes}

                        The output should start from 'Modified Job Description' and implement the changes suggested in Requested Changes
                        """

                        # Assuming you have a function llm.predict() that generates the response
                        st.session_state.reviewed_response = llm.predict(final_prompt)

                        with st.chat_message("assistant"):
                            st.session_state.messages.append({"sender": "assistant", "message": f"{st.session_state.reviewed_response}"})

                        conversation.write(display_messages(st.session_state.messages))
                        st.write(st.session_state.reviewed_response)



#     if  st.session_state.entry_3:
            
#             if st.button('generate', key='fff'):
#                 print(st.session_state.requested_changes)
#                 st.write(st.session_state.requested_changes)

#                 st.session_state.reviewed_response = llm.predict(f"""Task: Modify the job description using the Requested Changes. Do not just paraphrase but also try to improve in a highly professional manner

# //{st.session_state.fr}//

# Requested Changes:
# {st.session_state.requested_changes}

# The output should start from 'Modified Job Description' and implement the changes suggested in Rquested Changes
# """)
#                 with st.chat_message("assistant"):
#                         st.session_state.messages.append({"sender": "assistant", "message": f"{st.session_state.reviewed_response}"})
#                 conversation.write(display_messages(st.session_state.messages))
#                 st.write(st.session_state.reviewed_response)
