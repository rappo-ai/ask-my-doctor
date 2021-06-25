from typing import Text

# tbdvimal

doctors = [
    {
        "name": "Dr. Murali",
        "speciality": "General Surgeon",
        "fee": "600",
        "bio": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
        "photo": "https://path.to.photo",
        "time_slots": [
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
        ],
    },
    {
        "name": "Dr. Lata",
        "speciality": "Paediatrician",
        "fee": "400",
        "bio": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
        "photo": "https://path.to.photo",
        "time_slots": [
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
        ],
    },
    {
        "name": "Dr. Asha",
        "speciality": "Gynaecologist",
        "fee": "700",
        "bio": "Lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum",
        "photo": "https://path.to.photo",
        "time_slots": [
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
            "17,17.25,17.5,17.75,18,18.25,18.5,18.75",
        ],
    },
]

specialities = [
    "General Surgeon",
    "Paediatrician",
    "Gynaecologist",
]


def get_specialities():
    return specialities


def get_doctors_for_speciality(speciality: Text):
    return [d for d in doctors if d["speciality"] == speciality]
