from typing import Text

from actions.helpers.reply_button_action import ReplyButtonAction
from actions.utils.sheets import get_specialities


class ActionAskDoctorSignupSpeciality(ReplyButtonAction):
    def name(self) -> Text:
        return "action_ask_doctor_signup__speciality"

    def __init__(self) -> None:
        super().__init__()
        self.text = f"Please select your speciality (or enter a new one):"
        self.reply_markup = {
            "keyboard": [[s] for s in get_specialities()],
        }
