from langchain.embeddings import OpenAIEmbeddings

def unansques(response):
    lines = response.split('\n')

# Initialize variables to store the extracted parts
    unanswered_questions = []
    open_ended_questions = []
    total_question = []
    # Flag to identify the section being processed
    current_section = None

    # Loop through the lines and extract the relevant sections
    for line in lines:
        if line.startswith("Unanswered Questions:"):
            current_section = "Unanswered Questions"
        elif line.startswith("Open-ended Questions:"):
            current_section = "Open-ended Questions"
        elif current_section:
            # Append the lines to the appropriate section
            if line.strip():
                if current_section == "Unanswered Questions":
                    unanswered_questions.append(line.strip())
                elif current_section == "Open-ended Questions":
                    open_ended_questions.append(line.strip())

    comb = unanswered_questions + open_ended_questions

    for question in comb:
        total_question.append(question.split('.')[1])
    return total_question
    
def questions_dict(self, unanswered_questions):
        ques_dict = {}
        for question in unanswered_questions:
            answer = input(question)
            ques_dict[question] = answer


def ans_ques(response: dict):
    answered_questions_write = dict(response['answered_questions'])
    answered_questions_write_list = []
    for number, question in answered_questions_write.items():
        if isinstance(question, dict):
            ques_title = list(question.keys())[0]
            question = list(question.values())[0]
            ques = f'{number}. {ques_title}: {question}'
            answered_questions_write_list.append(ques)            
        else:
            answered_questions_write_list.append(f'{number}: {question}')
    result = '\n'.join(answered_questions_write_list)
    return result

def unans_ques(response: dict):
    unanswered_questions_write = response['unanswered_questions']
    unanswered_questions_write_list = []
    for number, question in unanswered_questions_write.items():
        if isinstance(question, dict):
            ques_title = list(question.keys())[0]
            question = list(question.values())[0]
            ques = f'{number}. {ques_title}: {question}'
            unanswered_questions_write_list.append(ques)            
        else:
            unanswered_questions_write_list.append(f'{number}: {question}')
    return unanswered_questions_write_list

def read_and_separate_roles(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
    
    # Split the data into individual roles based on two newline characters
    role = data.split('\n---')
    return role
def make_embeddings(string):
    embeddings = OpenAIEmbeddings()
    result = embeddings.embed_documents(texts=string)
    return result[0]

def intelligent_questions_string(int_ques: dict):
    intelligent_questions_list = []
    for question, answer in int_ques.items():
        intelligent_questions_list.append(f'{question}: {answer}')
    int_questions_string = '\n'.join(intelligent_questions_list)
    return intelligent_questions_list