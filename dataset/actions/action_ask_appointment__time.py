from typing import Text

from actions.helpers.reply_button_action import ReplyButtonAction
from actions.utils.common import get_appointment_time_slots


class ActionAskAppointmentSpeciality(ReplyButtonAction):
    def name(self) -> Text:
        return "action_ask_appointment__time"

    def __init__(self) -> None:
        super().__init__()
        self.text = f"Please pick a time slot:"
        self.reply_markup = {
            "keyboard": [[s] for s in get_appointment_time_slots()],
        }
