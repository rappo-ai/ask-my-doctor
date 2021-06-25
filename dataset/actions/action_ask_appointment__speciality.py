from typing import Text

from actions.helpers.reply_button_action import ReplyButtonAction
from actions.utils.common import get_specialities


class ActionAskAppointmentSpeciality(ReplyButtonAction):
    def name(self) -> Text:
        return "action_ask_appointment__speciality"

    def __init__(self) -> None:
        super().__init__()
        self.text = f"Please select the speciality you are looking for:"
        self.reply_markup = {
            "keyboard": [[s] for s in get_specialities()],
        }
