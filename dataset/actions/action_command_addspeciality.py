import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import (
    is_admin_group,
    get_specialities,
    print_specialities,
    set_specialities,
)


class ActionCommandAddSpeciality(Action):
    def name(self) -> Text:
        return "action_command_addspeciality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_admin_group(tracker.sender_id):
            return []

        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)\s+([^\n\t]+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            speciality = matches.group(2).strip()
            specialities: list = get_specialities()
            if speciality in specialities:
                dispatcher.utter_message(
                    json_message={
                        "text": (
                            f'"{speciality}" speciality already exists.\n'
                            + "\n"
                            + print_specialities(specialities)
                        )
                    }
                )
                return []

            specialities.append(speciality)
            set_specialities(specialities)
            dispatcher.utter_message(
                json_message={
                    "text": (
                        f'"{speciality}" speciality added.\n'
                        + "\n"
                        + print_specialities(specialities)
                    )
                }
            )
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "The command format is incorrect. Usage:\n\n/addspeciality <SPECIALITY>"
                }
            )

        return []
