from typing import Text

from actions.helpers.reply_button_action import ReplyButtonAction
from actions.utils.common import get_upcoming_appointment_dates


class ActionAskAppointmentSpeciality(ReplyButtonAction):
    def name(self) -> Text:
        return "action_ask_appointment__date"

    def __init__(self) -> None:
        super().__init__()
        self.text = f"Please pick a date:"
        self.reply_markup = {
            "keyboard": [[s] for s in get_upcoming_appointment_dates()],
        }
