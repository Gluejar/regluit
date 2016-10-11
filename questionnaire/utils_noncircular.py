#!/usr/bin/python

from .models import RunInfoHistory, Answer

def get_completed_answers_for_questions(questionnaire_id, question_list):
    completed_questionnaire_runs = RunInfoHistory.objects.filter(questionnaire__id=questionnaire_id)
    completed_answers = []
    for run in completed_questionnaire_runs:
        specific_answers = Answer.objects.filter(run=run.run, question_id__in=question_list)
        answer_set = []
        for answer in specific_answers:
            if answer.answer != '[]':
                answer_set.append([int(answer.question_id), answer.answer])
        if len(answer_set) > 0:
            completed_answers.append(answer_set)
    return completed_answers

if __name__ == "__main__":
    import doctest
    doctest.testmod()
