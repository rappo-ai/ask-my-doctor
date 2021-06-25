from typing import Text

from actions.helpers.reply_button_action import ReplyButtonAction
from actions.utils.common import get_doctors


class ActionAskAppointmentSpeciality(ReplyButtonAction):
    def name(self) -> Text:
        return "action_ask_appointment__doctor"

    def __init__(self) -> None:
        super().__init__()
        self.text = f"Please choose a doctor:"
        self.reply_markup = {
            "keyboard": [[s] for s in get_doctors()],
        }
