import re
from typing import Any, AnyStr, Match, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import set_admin_group_id


class ActionAdminCommandGroupId(Action):
    def name(self) -> Text:
        return "action_admin_command_groupid"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)\s+(-?\d+)$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches:
            group_id = matches.group(2)
            set_admin_group_id(group_id)
            dispatcher.utter_message(
                json_message={"text": f"Admin group id updated to {group_id}."}
            )
        else:
            dispatcher.utter_message(
                json_message={
                    "text": "The command format is incorrect.\n\n/groupid <GROUP_CHAT_ID>"
                }
            )

        return []