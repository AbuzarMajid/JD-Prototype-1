import re
def get_unaswered_questions(response):
        unanswered_pattern = r"Unanswered Questions:(.*?)Open-ended Questions:"
        open_ended_pattern = r"Open-ended Questions:(.*?)$"

    # Use re.findall to extract the questions
        unanswered_questions = re.findall(unanswered_pattern, response, re.DOTALL)[0].strip().split('\n')
        open_ended_questions = re.findall(open_ended_pattern, response, re.DOTALL)[0].strip().split('\n')

    # Remove leading numbers and whitespace from each question
        unanswered_questions = [re.sub(r"^\d+\.\s*", "", q.strip()) for q in unanswered_questions]
        open_ended_questions = [re.sub(r"^\d+\.\s*", "", q.strip()) for q in open_ended_questions]

        questions_asked = unanswered_questions + open_ended_questions

        return questions_asked
    
def questions_dict(self, unanswered_questions):
        ques_dict = {}
        for question in unanswered_questions:
            answer = input(question)
            ques_dict[question] = answer