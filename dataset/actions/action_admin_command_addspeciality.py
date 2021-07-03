import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_specialities, set_specialities


class ActionAdminCommandAddSpeciality(Action):
    def name(self) -> Text:
        return "action_admin_command_addspeciality"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)\s+([\w -]+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            speciality = matches.group(2).strip()
            specialities: list = get_specialities()
            if speciality in specialities:
                dispatcher.utter_message(
                    json_message={
                        "text": (
                            f'"{speciality}" speciality already exists. Current list of specialities:\n'
                            + "\n"
                            + "\n".join(specialities)
                        )
                    }
                )
                return []

            specialities.append(speciality)
            set_specialities(specialities)
            dispatcher.utter_message(
                json_message={
                    "text": (
                        f'"{speciality}" speciality added. Current list of specialities:\n'
                        + "\n"
                        + "\n".join(specialities)
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