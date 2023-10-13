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
llm = ChatOpenAI(temperature=0, model="gpt-4", max_tokens=1000)
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

if not hasattr(st.session_state, 'qa_dict'):
      st.session_state.qa_dict = {}

if not hasattr(st.session_state, 'write'):
      st.session_state.write = False




# getiing inital
role_title = st.text_input("Role Title", key="job role", placeholder="Enter your Role Title")
if role_title:
    with st.chat_message("User"):
        st.markdown(f"Job Role: {role_title}")

seniority_level = st.selectbox('Select the Seniority Level for this Role', ('seniority level', 'Machine Learning Engineer', 'Data Engineer', 'Data Scientist'), placeholder='Select the Seniority Level for this Role')
if seniority_level:
    with st.chat_message("User"):
        st.markdown(f"Seniority_level: {seniority_level}")
        
job_description = st.text_area("Job Description", key="job description", placeholder="Enter your raw Job Description", height=400)
job_description = job_description.rstrip(".")
if job_description:
    with st.chat_message("User"):
        st.markdown(f"Job Description: {job_description}")

Questions = f"""1. Role Definition: Can you please provide a brief overview of the role we're looking to fill? Make a summary of the overall job description for that.
2. Key Responsibilities: What are the top 3-5 key responsibilities for this role?
3. Experience(make a list if more than 1): What specific skills and experiences are very essential for this role?
4. Education and Certifications: What educational qualifications or certifications are required or desirable for this role?
5. Tools and Software: Looking at the entire Job Description, Are there any specific tools, software, or equipment that the candidate should be familiar with?
6. What are the must have or essential skills for this role?(max 4)- Make sure to include only crucial or necessary skills from the job description and What are the good-to-have skills for this role?(max 2)-This can include preferred skills, experience or expertise
7. Growth Opportunities: What growth opportunities are available for this role within the organization?
8. Budget and Compensation: What is the budget for this position? What is the proposed salary range?
9. Project and Task Management: Does this role include project management and require the use of different project management methodologies such as scrum, sprint, kanban?
"""

prompt = f'''Role: You are an expert recruitment marketing specialist that is reviewing a Job Description submitted by a hiring manager. 

Task: You will be given the Job level and Role Title they are hiring for, as well as the Job Description text. You will use this information to map the answers the Pertinent Questions provided. But if you cant find an answer then no problem, you will just include that question in the unanswered questions list. But you need to think critically as wording can be chnaged but answer is usually available

Role Title: {role_title}

Seniority_Level: {seniority_level}

Job Description: {job_description}

Pertinent Questions: {Questions}

Output: All output will be in JSON. The output JSON will use the keys "answered_questions", "technical_aspects" and "unanswered_questions", with each value as a string.

Here are the instructions for the answered_questions key:

Using the Job Description provided, answer the pertinent questions provided. Think carefully for each question and go step-by-step. If the information is included in the Job Description, answer the question and return it in the following format: question number, question title, and your answer. If the information is not in the Job Description, you will follow the instructions bellow for unanswered_questions. 

Here are the instructions for unanswered_questions key:

For any of the answer not given to the Pertinent Questions in Answered Questions, list them here using this format: question number, quesiton title, question

Here are the instructions for technical_aspects key:

It should extract all the technical stuff written in the job description. Please make sure to not miss any piece of information

'''
llm = ChatOpenAI(temperature=0, model="gpt-4", max_tokens=1500)
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
    # Rest of the code continues to run based on user input
    if st.session_state.generate_pressed and not st.session_state.api_called:
        #llm1 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=1000)
        key_information = llm.predict(prompt)     
        st.session_state.key_information = key_information
        print(key_information)
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
            i = 0
            qa_dict = {}
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
                    qa_dict[f'Question: {question}'] = f'Answer: {answer}'
                    i = i+1
                    if i == len(role_description):
                         st.session_state.write = True
                    # with open('CONTEXT.txt', "a") as f:
                    #     f.write("\nQuestion:" + question + "\n" + "Answer:" + answer + "\n")

    if st.session_state.write:
            st.session_state.qa_dict = qa_dict
            with open('CONTEXT.txt', "a") as f:
                for question, answer in qa_dict.items():
                    f.write(question + '\n' + answer + '\n')
            with open("CONTEXT.txt", "r") as f: 
                final_response = f.read()
            
            st.session_state.entry_1 = True
            st.session_state.FR = final_response

            # context_raw_2 = st.session_state.FR
            # context_raw_2 = context_raw_2.split("\n\n")
            # context_cleaned_2 = []
            # for i in context_raw_2:
            #          if i in context_cleaned_2:
            #               continue
            #          else:
            #               context_cleaned_2.append(i)

            # context_normalized_2 = "\n\n".join(context_cleaned_2)

    if st.session_state.entry_1:
        st.empty()
        if st.button("GENERATE FINAL JOB DESCRIPTION", key = "gen2"):
                llm1 = ChatOpenAI(model='gpt-3.5-turbo',temperature=0.5, max_tokens=1500)
                Final_Response = llm1.predict(f""" 
                Task: You are Mike and you write a very efficient job description based on the Key information provided
Key Information:
<<{st.session_state.FR}>>
 
Output: The format of the generated job description should look like using proper headings, subheadings, paragraphs, bulleting as needed.
 <<
Instruction: 
(a) Tone and Writing Style Guidelines for Sections #1 & #2 (About company and role):

1- Inspirational: The tone should inspire and motivate potential candidates. Use language that paints a positive picture of the company and its impact.

2- Direct and Personal: Address the reader directly (e.g., "In your role..."). Make them feel that the description is speaking to them personally.

3- Clear and Concise: Keep sentences and paragraphs short. Avoid jargon or overly technical language unless necessary.

4- Inclusive: Ensure the language is inclusive, welcoming individuals from all backgrounds and experiences.

(b) Optional Sections that will be asked at the end to improve the JD: 

1- Sections 111, 112, 113, 114, 115, 211, 212, 224, 225, 32, 33, 4 and 5.

Job Description for [Position Title] at [Company Name]
1. About [Company Name]:
1.1. Opening Statement: Begin with a captivating sentence that captures the essence of the company's purpose. This could be about the impact the company has on its users, customers, or the world. 

Example: Millions of people across the world come to [Company Name] to [unique selling proposition or value proposition].

1.1.1. Company's vision for small/mid-size companies—our vision at [Company Name] is to [clear and concise statement of the company's long-term desired change resulting from its work].

1.1.2. Purpose and Mission: Describe what the company does, its mission, and the value it brings to its users or customers. Highlight the broader impact of the company’s services/products.

Example: Our mission is to help those people [describe mission here]. In your role, you’ll be challenged to take on work that upholds this mission and pushes [Company Name] forward.

1.1.3. Growth and Development: Address the individual reading the description directly, touching on personal and professional growth opportunities. This part should resonate with prospective employees' aspirations.

Example: You’ll grow as a person and leader in your field, all the while helping [users/customers] [key benefit].

1.1.4. Inclusivity Statement: Emphasize the company’s commitment to diversity, inclusion, and the value of unique perspectives. This should encourage applicants to reflect on how their unique backgrounds can contribute to the company.

Example: Creating a life you love also means finding a career that celebrates the unique perspectives and experiences that you bring. As you read through the expectations of the position, consider how your skills and experiences may complement the responsibilities of the role.

1.1.5. Unique Company Programs or Features: If the company has a unique working model, benefit, or feature, mention it here. This could be something that sets the company apart from others.

Example: Our new progressive work model is called [Unique Program Name], a term that’s uniquely [Company Name] to describe our [describe feature or benefit].

2. Role Overview:
2.1. Role Overview: As a [Position Title], you will play a pivotal role in [briefly describe what they will do]. This role will interact closely with [departments/teams they will collaborate with], contributing directly to [specific goal or project related to the company's mission].

2.1.1. Why This Role and Why Now: Given our drive to [specific goal or company objective], it's essential that we onboard a [Position Title] who can [specific role objectives]. Your diverse experiences, whether directly related to the job or not, can make a difference. We value all backgrounds and encourage you to consider how your unique journey can be part of our story.

2.1.2. How This Role Interacts:

2.1.2.1. Team Composition: You will be joining a dynamic team of [number of team members, e.g., "five members"] including [brief overview of roles, e.g., "two designers, one project manager, and two developers"].

2.1.2.2. Interdisciplinary Collaboration: our role will involve [specific interactions, e.g., "coordinating with the design team on visual elements and working with developers for implementation"]. Understanding the synergy between different departments will be crucial.

2.1.2.3. Post-Joining Expectation: Upon joining, you can expect an orientation session with [relevant team or department, e.g., "the product management team"], and regular check-ins with your supervisor to ensure smooth onboarding and integration into our workflow.

2.1.3. Key Responsibilities:

Subtitle: "What you’ll do:"

Description: List primary tasks and responsibilities expected from the candidate. Make it clear and actionable.

Example: "Deep strategic analysis to Answer growth ecosystem questions...", "Experimentation: Evolve our experimentation capabilities..."

2.2. Qualifications: 

2.2.1. What we’re looking for:

Description: Define the required qualifications, experience, and skills necessary for the role. Highlight any specific years of experience or technical skills.

Example: "8+ years of combined post-graduate academic and industry experience...", "Expertise in at least one scripting language (ideally Python/R)."

2.2.2. Traits and Qualities:

Description: Describe the qualities that make a candidate ideal for the role. This includes soft skills, mindset, and work ethics.

Example: "Strong business/product sense...", "Data skepticism and curiosity...", "Interest in repeatable analysis."

2.2.3. Must-Haves:

[Requirement 1]

[Requirement 2]

[Requirement 3]

2.2.4. Good-to-Haves:

[Requirement 1]

[Requirement 2]

[Requirement 3]

2.2.5. Why These Requirements?

The must-have requirements are critical for [specific reason, e.g., "ensuring a seamless interaction with our existing software and tools"]. The good-to-have skills will position you to [specific advantage or opportunity, e.g., "take lead on certain projects and collaborate effectively with other advanced teams"].

3. Location, Salary Information, Benefits and Perks:
Description: If applicable, provide information on the job's location, any remote possibilities, relocation clauses, and a salary range.

3.1.  Location

3.2. Salary Information

3.3. Benefits and Perks

[Benefit 1]

[Benefit 2]

[Benefit 3]

4. Company Commitments and Policies:
Description: Highlight the company's commitment to diversity, inclusivity, and other values. Provide details of the company's stand on these matters.

Example: "At Pinterest we believe the workplace should be equitable...", "Our Commitment to Diversity: Pinterest is an equal opportunity employer..."

5. Application Process and Additional Notes:
Description: Mention any specific instructions or notes regarding the application process. If there's an email for further inquiries or accommodations, include that too.

Example: "US based applicants only", "If you require an accommodation during the job application process, please notify accessibility@pinterest.com for support.">>

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
