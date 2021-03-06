from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.branding import get_bot_help_message
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
                + "/funnel - action funnel statistics for all patients\n"
                + "/reject <DOCTOR ID> <REASON> - reject a doctor\n"
                + "/listdoctors <SPECIALITY>[OPTIONAL] <LISTING STATUS>[OPTIONAL] <ONBOARDING STATUS>[OPTIONAL] - list all doctors based on speciality, listing status or onboarding status (any one filter)\n"
                + "/contactdoctor <ORDER ID>[OPTIONAL] <DOCTOR ID>[OPTIONAL] - broadcast a message to all doctors; or contact a single doctor by ORDER ID or DOCTOR ID\n"
                + "/contactpatient <ORDER ID> - contact the patient for an order\n"
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

        text = get_bot_help_message() + "\n" + "Click /menu to view the main menu.\n"
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
