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