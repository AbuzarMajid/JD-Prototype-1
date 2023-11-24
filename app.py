import streamlit as st
import openai
import time
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import pinecone
import json
from utils import ans_ques, unans_ques
from langchain.chat_models import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationChain

load_dotenv("C:\\Users\\abuza\\Desktop\\jobd - Copy\\JD-Prototype-1\\api.env")
API_KEY = os.getenv("API_KEY")
openai.api_key= API_KEY

pinecone_api_key = os.getenv("pinecone_api_key")
pinecone.init(      
	api_key=pinecone_api_key,      
	environment='asia-northeast1-gcp'      
)
index = pinecone.Index('skills-database')
llm = ChatOpenAI(model='gpt-4', temperature=0.0, openai_api_key=API_KEY)
# memory = ConversationBufferMemory(max_token_limit=2000, llm=llm)

# chat_llm_chain = ConversationChain(
#     llm=llm,
#     verbose=True,
#     memory=memory
# )
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

if "messages" not in st.session_state:
    st.session_state.messages = []

if not hasattr(st.session_state, 'intelligent_questions'):
    st.session_state.intelligent_questions=False

if not hasattr(st.session_state, 'int_qa_dict'):
    st.session_state.int_qa_dict={}

if not hasattr(st.session_state, 'chatbot'):
    st.session_state.chatbot = False

if not hasattr(st.session_state, 'response_string'):
    st.session_state.response_string = ''

if not hasattr(st.session_state, 'chain_1'):
    st.session_state.chain_1 = True

if not hasattr(st.session_state, 'chain_remaining'):
    st.session_state.chain_remaining = False

if not hasattr(st.session_state, 'int_ques'):
     st.session_state.int_ques = []

if not hasattr(st.session_state , "human_input"):
     st.session_state.human_input = ""

if not hasattr(st.session_state , "int_ques_next"):
     st.session_state.int_ques_next = False

if not hasattr(st.session_state, 'FR'):
     st.session_state.FR = ''

# getiing inital
category = st.selectbox('Select the Category for this Role', ('category','Data Science', 'Data Engineering', 'Machine Learning', 'Data Analyst', 'AI Experts', 'Roboticist'), placeholder='Select the Category for this Role')

role_title = st.text_input("Role Title", key="job role", placeholder="Enter your Role Title")
if role_title:
    with st.chat_message("User"):
        st.markdown(f"Job Role: {role_title}")

seniority_level = st.selectbox('Select the Seniority Level for this Role', ('seniority level', 'Entry-level', 'Mid-level, hands-on', 'Senior-level, hands-on', 'Manager, hands-on', 'Manager, with direct reports'), placeholder='Select the Seniority Level for this Role')
        
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

Output: All output will be in JSON. The output JSON will use the keys "answered_questions" and "unanswered_questions", with each value as a string.

Here are the instructions for the answered_questions key:

Using the Job Description provided, answer the pertinent questions provided. Think carefully for each question and go step-by-step. If the information is included in the Job Description, answer the question and return it in the following format: question number, question title, and your answer. If the information is not in the Job Description, you will follow the instructions bellow for unanswered_questions. 

Here are the instructions for unanswered_questions key:

For any of the answer not given to the Pertinent Questions in Answered Questions, list them here using this format: question number, quesiton title, question

'''
llm = ChatOpenAI(temperature=0, model="gpt-4", max_tokens=1500, openai_api_key=API_KEY)
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
        
        print("Entered Main")
        if st.button("REVIEW JOB DESCRIPTION", key="gen1"):
            print("Entered Review")
            st.session_state.generate_pressed = True
            st.session_state.messages = []
            st.session_state.messages.append({"sender": "user", "message": f"Job Role: {role_title}, Job Description: {job_description}"})
            conversation.write(display_messages(st.session_state.messages))
    # Rest of the code continues to run based on user input
    if st.session_state.generate_pressed and not st.session_state.api_called:
        key_info_response = llm.predict(prompt)
        key_information = json.loads(key_info_response)
        print(key_information)
        with open ('CONTEXT.txt', "a") as f:
            answered_questions_generic = ans_ques(response=key_information)
            response = f.write(answered_questions_generic)
        print('answered questions written in context file')
        unanswered_question_generic = unans_ques(response=key_information)
        st.session_state.questions = unanswered_question_generic
        print('Parsed')
        st.session_state.api_called = True
        # print(key_information)

        # context_raw = st.session_state.key_information
        # context_raw = context_raw.split("\n\n")
        # context_cleaned = []
        # for i in context_raw:
        #              if i in context_cleaned:
        #                   continue
        #              else:
        #                   context_cleaned.append(i)

        # context_normalized = "\n\n".join(context_cleaned)
        
    if st.session_state.questions:
        unanswered = "There are some unanswered questions in the job description. Kindly answer the questions"
        exists = any(message['message'] == unanswered for message in st.session_state.messages)
        with st.chat_message("Assistant"):
                st.markdown("There are some unanswered questions in the job description. Kindly answer the questions")
        st.write(st.session_state.questions) 
        if not exists:
                st.session_state.messages.append({"sender": "Assistant", "message": "In order to effectively create the job description We need answers to the following questions"})
                conversation.write(display_messages(st.session_state.messages))
        role_description = st.session_state.questions
        i = 0
        qa_dict = {}
        list_questions = []
        for question in role_description:
            answer = st.text_input(f'{question}', key = f"{question}+++")   
            question = question.split(':')[0]
            if answer:
                list_questions.append(answer)
                conversation.empty()
                exists = any(message['message'] == answer for message in st.session_state.messages)
                if not exists:
                    st.session_state.messages.append({"sender": "user", "message": f"{question}: {answer}"})
                conversation.write(display_messages(st.session_state.messages))
                with st.chat_message("user"):
                    st.write(answer)
                qa_dict[f'{question}'] = f'{answer}'
                i = i+1
                if i == len(role_description):
                    st.session_state.write = True
    if st.session_state.write and not st.session_state.int_ques_next:
        st.session_state.qa_dict = qa_dict
        with open('CONTEXT.txt', "a") as f:
            for question, answer in qa_dict.items():
                f.write('\n' + question + ': ' + answer)
            print('Generic question part completed')
            st.session_state.intelligent_questions=True
            st.session_state.write = False
            st.session_state.int_ques_next = True


    if st.session_state.intelligent_questions:
        if st.button('Job Role Specific Questions'):
            st.write('Generating Job Specific Questions')
            llm_query = ChatOpenAI(model='gpt-4', temperature=0.0, openai_api_key=API_KEY)
            print('Generating Query')
            query  = llm_query.predict(f"""
            Role : You are a human resources agent who specializes in cantidates in the Artificial Intellegence, Machine Learning, and Data Engineering space.
            Task: Extract the technical skills from the provided Job Description, ordering them from most fundamental to most niche
            Job Description:
            <<{job_description.strip()}>>
            Output Format:
            Skills:
            -
            -
            """)
            st.write(f'query: {query}')
            print('Entered DB')
            embedding_response = openai.Embedding.create(
            input=query,
            model="text-embedding-ada-002")
            query_embeddings = embedding_response['data'][0]['embedding']
            DB_response = index.query(
                query_embeddings,
                top_k=2,
                include_metadata=True,
                namespace=category
            )
            response_list =[]
            answer_first = ''
            print(DB_response)
            for i in range(2):
                response_final = DB_response['matches'][i]['metadata']['description']
                context = response_list.append(response_final)
            st.session_state.response_string = '\n'.join(response_list)
            suggested_title = DB_response['matches'][0]['metadata']['role title']
            print (f'context: {st.session_state.response_string}')
            st.write (f'The role falls in the catefory of {category} and more specifically it is {suggested_title}')
            # Chatbot work
            print('Chatbot Enabled')
            st.session_state.chatbot = True
            st.session_state.chain_1 = True
            st.session_state.intelligent_questions = False
            st.session_state.chain_remaining = False
            st.session_state.counter = 0


# Set the initial chatbot state
    
    if st.session_state.chatbot:
        if st.session_state.chain_1:
            print('chain_1')
            st.session_state.int_ques=[{"role": "user", "content": f'''
                Role: You are an expert recruitment marketing specialist that is reviewing a Job Description submitted by a hiring manager. You have to question the user for details
                Task: You are trying to determine, based on a hiring manager's Job Description and the Job's Seniority Level, if they have included all the requisite technical skills in their job description that a candidate should posses to apply for the Job. Given the Job's Seniority level, you will compare the hiring manager's Job Description, with Standard Skillset and Suggested Title.
                -Go step by step in a friendly and INTERACTIVE, ENGAGING way. 
                -Only one question in 1 term. The question should be from the perspective of the hiring manager3
                -Do  not give a sense that we have made a skill set
                Seniority Level: Manager-Hands On

                Job Description: {job_description}

                Standard Skillset and Title: {st.session_state.response_string}

                Output format: Question...?
                ###
                '''}]
            st.session_state.chain_1 = False
        if not st.session_state.chain_remaining:
            print('remaining')
            questions = openai.ChatCompletion.create(
                model="gpt-4",
                messages = st.session_state.int_ques,
                temperature = 0.0)
            questions = questions['choices'][0]['message']['content']
            st.session_state.int_ques_next = questions
            st.session_state.chain_remaining=True
        st.session_state.human_input = st.text_input(st.session_state.int_ques_next)
        if st.session_state.human_input!='':
            with st.chat_message('User'):
                st.markdown(f'Answer: {st.session_state.human_input}')
            print(st.session_state.human_input)
        # if st.button('next'):
            print('entered')
            st.session_state.counter = st.session_state.counter+1
            st.session_state.int_ques.append({"role":"assistant","content":st.session_state.int_ques_next})
            st.session_state.int_ques.append({"role":"user", "content": st.session_state.human_input})
            st.session_state.int_qa_dict[f'{st.session_state.int_ques_next}'] = f'{st.session_state.human_input}'
            print(st.session_state.int_qa_dict)
            print(st.session_state.int_ques)
            st.session_state.chain_remaining = False
            if st.session_state.counter !=5:
                st.button('Next Question')
            if st.session_state.counter == 5:
                st.text('Thanks for Clarification')
                st.session_state.chatbot = False
                st.session_state.entry_1= True
                with open('CONTEXT.txt', "a") as f:
                    for question, answer in st.session_state.int_qa_dict.items():
                        f.write('\n' + question + ': ' + answer)

                with open('CONTEXT.txt', "r") as f:
                    final_response = f.read()
                    st.write(final_response)
                    st.session_state.FR = final_response

    if st.session_state.entry_1:
        if st.button("GENERATE FINAL JOB DESCRIPTION", key = "gen2"):
                llm1 = ChatOpenAI(model='gpt-4',temperature=0, max_tokens=1500, openai_api_key=API_KEY)
                Final_Response = llm1.predict(f"""Role: You are HopHR Agent, a recruiting expert for talent in Machine Learning, Artificial Intelligence, and Data Science. You are creating the final draft of a Job Description for a hiring manager.
Task: Using the HopHR Guidelines, you will take Job Title, Job Level,  User Answers, and Parsed Job Description to generate a professional Job Description for the hiring manager.
Job Title: {role_title}
Job Level: {seniority_level}
Parsed Job Description: {st.session_state.FR}
HopHR Guidelines:
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
Example: "US based applicants only", "If you require an accommodation during the job application process, please notify accessibility@pinterest.com for support."
Output: Explicitly label each major section in the way it is detailed below, but do not number them or explicitly use the sub-categories in your draft.""") 
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
