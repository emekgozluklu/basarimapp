EXAM_TYPES = [
    (0, 'YGS'),
    (1, 'LYS1'),
    (2, 'LYS2'),
    (3, 'LYS3'),
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
        "Native Language": 50,
        "Foreign Language": 30,
    },
]


def validate_exam_field_form(form_data, num_of_questions):
    print(form_data)
    if len(form_data) != num_of_questions + 1:  # +1 for submit
        return False
    print("FIRST CHECK")
    q = 1
    for key in form_data.keys():
        if str(q) in key or key == "submit":
            print(key, q)
            q += 1
            continue
        else:
            return False
    print("TRUE")
    return True
