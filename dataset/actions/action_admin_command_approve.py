import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import get_doctor, update_doctor
from actions.utils.meet import get_google_auth_url


class ActionAdminCommandApprove(Action):
    def name(self) -> Text:
        return "action_admin_command_approve"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)\s+#(\w+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            doctor_id = matches.group(2)
            doctor = get_doctor(doctor_id)
            doctor["onboarding_status"] = "approved"
            update_doctor(doctor)
            dispatcher.utter_message(
                json_message={
                    "text": f"{doctor['name']} with ID {doctor_id} has been approved. Please use /activate #{doctor_id} to make this doctor's listing live."
                }
            )
            google_auth_url = get_google_auth_url(doctor["user_id"])
            dispatcher.utter_message(
                json_message={
                    "chat_id": doctor["user_id"],
                    "text": (
                        f"Your application has been approved. Please use /activate to make your listing live.\n"
                        + "\n"
                        + "Here are the full list of commands you can use:\n"
                        + "\n"
                        + "/activate - activate listing\n"
                        + "/deactivate - deactivate listing\n"
                        + "/setname <NAME> - update name\n"
                        + "/setphoto - update profile photo by replying to image message\n"
                        + "/setphonenumber <PHONE NUMBER>- update phone number\n"
                        + "/setspeciality <SPECIALITY> - update speciality\n"
                        + "/setdescription <DESCRIPTION> - update description\n"
                        + "/settimeslots <TIME SLOT LIST> - update available time slots for the upcoming week\n"
                        + "/setfee <CONSULTATION FEE> - update consultation fee\n"
                        + "/setgoogleid - update Google ID for meetings\n"
                        + "\n"
                        + f"To update your Google ID for creating meetings, please click this link -> {google_auth_url}\n"
                        + "\n"
                        + "To update your bank account details or for any other queries, please contact the admin @askmydoctorsupport.\n"
                    ),
                }
            )
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "The command format is incorrect. Usage:\n\n/approve <DOCTOR ID>"
                }
            )

        return []
