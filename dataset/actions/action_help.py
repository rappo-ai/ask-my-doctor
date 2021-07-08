from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.doctor import get_doctor_command_help, is_approved_doctor


class ActionHelp(Action):
    def name(self) -> Text:
        return "action_help"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if is_admin_group(tracker.sender_id):
            text = (
                "Here is the list of admin commands:\n"
                + "\n"
                + "/addspeciality <SPECIALITY> - add a speciality\n"
                + "/deletespeciality <SPECIALITY> - delete a speciality\n"
                + "/approve <DOCTOR ID> - approve a doctor\n"
                + "/reject <DOCTOR ID> <REASON> - reject a doctor\n"
                + "\n"
                + "Additional commands to update doctor profiles:\n"
                + "\n"
                + get_doctor_command_help(True)
            )
            json_message = {"text": text}
            dispatcher.utter_message(json_message=json_message)
            return []

        if is_approved_doctor(tracker.sender_id):
            text = (
                "Here is the list of commands to view or update your doctor profile:\n"
                + "\n"
                + get_doctor_command_help()
            )
            json_message = {"text": text}
            dispatcher.utter_message(json_message=json_message)

        text = (
            "You can reach out to us for help in any of the following ways:\n"
            + "\n"
            + "- Message us @askmydoctorsupport\n"
            + "- Email us at support@askmydoctor.com\n"
            + "- Call us at 9876543210 (Mon-Fri 9 AM-6PM)\n"
            + "\n"
            + "Click /menu to view the main menu.\n"
        )
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
