import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_admin_group_id
from actions.utils.doctor import get_doctor, get_doctor_for_user_id, update_doctor
from actions.utils.validate import validate_consulation_fee


class ActionDoctorCommandSetFee(Action):
    def name(self) -> Text:
        return "action_doctor_command_setfee"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get("text")
        is_admin = tracker.sender_id == get_admin_group_id()
        regex = r"^(/\w+)(\s+#(\w+))?(.+)$"
        if is_admin:
            regex = r"^(/\w+)(\s+#(\w+))(.+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        fee = matches and validate_consulation_fee(matches.group(4))
        if matches and fee:
            doctor = {}
            doctor_id = ""
            if is_admin:
                doctor_id = matches.group(3)
                doctor = get_doctor(doctor_id)
            else:
                doctor = get_doctor_for_user_id(tracker.sender_id)
                doctor_id = str(doctor["_id"])
            doctor["fee"] = int(fee)
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "chat_id": get_admin_group_id(),
                    "text": f"{doctor['name']} with ID #{doctor_id}, consultation fee has been updated to Rs. {fee}.",
                }
            )
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (f"Your consultation fee has been updated to Rs. {fee}.\n"),
                }
            )
        else:
            usage = "/setfee <CONSULTATION FEE>"
            if is_admin:
                usage = "/setfee <DOCTOR ID> <CONSULTATION FEE>"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nConsultation fee must be a number in multiples of 50. The minimum fee is 100. The amount is automatically converted to Rupees, so no need to add the Rupee prefix / suffix."
                }
            )

        return []
