from typing import Text

from actions.helpers.reply_button_action import ReplyButtonAction


class ActionAskDoctorSignupAvailability(ReplyButtonAction):
    def name(self) -> Text:
        return "action_ask_doctor_signup__availability"

    def __init__(self) -> None:
        super().__init__()
        self.text = (
            f"What is your general availability to take appointments on Ask My Doctor?"
        )
        self.reply_markup = {
            "keyboard": [["Weekdays"], ["Weekends"]],
        }
