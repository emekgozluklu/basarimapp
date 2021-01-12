EXAM_TYPES = [
    (0, 'YGS'),
    (1, 'LYS1'),
    (2, 'LYS2'),
    (3, 'LYS3'),
    (4, 'Quiz Maths'),
    (5, 'Quiz Science'),
    (6, 'Quiz Language'),
    (7, 'Quiz Social'),
]

EXAM_TYPE_FIELDS = [
    {
        "Native Language": 40,
        "Social Sciences": 40,
        "Fundamental Math": 40,
        "Science": 40
    },
    {
        "Native Language": 30,
        "Social Sciences": 30,
    },
    {
        "Native Language": 30,
        "Mathematics": 30,
    },
    {
        "Mathematics": 30,
        "Science": 30,
    },
    {
        "Mathematics": 10,
    },
    {
        "Science": 10,
    },
    {
        "Native Language": 10,
    },
    {
        "Social Sciences": 10,
    },
]


def validate_exam_field_form(form_data, num_of_questions):
    if len(form_data) != num_of_questions + 1:  # +1 for submit
        return False
    q = 1
    for key in form_data.keys():
        if str(q) in key or key == "submit":
            q += 1
            continue
        else:
            return False
    return True


def validate_answersheet_form(form_data, num_of_questions):
    if len(form_data) > num_of_questions + 1:  # +1 for submit
        return False
    return True


def check_answers(correct_answers, choices):
    corrects = wrongs = empties = 0

    for key in correct_answers.keys():
        if key == "submit":
            continue
        if key in choices:
            if correct_answers[key] == choices[key]:
                corrects += 1
            else:
                wrongs += 1
        else:
            empties += 1
    return corrects, wrongs, empties
