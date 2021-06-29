admin_config = {
    "advance_appointment_days": 7,
    "commission_rate": 20,
    "meeting_duration_minutes": 15,
    "specialities": [
        "General Surgeon",
        "Paediatrician",
        "Gynaecologist",
    ],
}


def get_admin_group_id():
    return admin_config.get("group_id")


def set_admin_group_id(group_id):
    admin_config["group_id"] = group_id


def get_advance_appointment_days():
    return admin_config.get("advance_appointment_days")


def set_advance_appointment_days(days: int):
    admin_config["advance_appointment_days"] = days


def get_commission_rate():
    return admin_config.get("commission_rate", 20)


def set_commission_rate(rate):
    admin_config["commission_rate"] = rate


def get_meeting_duration_in_minutes():
    return admin_config.get("meeting_duration_minutes")


def set_meeting_duration_in_minutes(minutes: int):
    admin_config["meeting_duration_minutes"] = minutes


def get_specialities():
    return admin_config.get("specialities")


def set_specialities(specialities: list):
    admin_config["specialities"] = specialities
