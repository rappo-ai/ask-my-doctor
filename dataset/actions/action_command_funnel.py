from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.conversation import get_funnel_stats


class ActionCommandFunnel(Action):
    def name(self) -> Text:
        return "action_command_funnel"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_admin_group(tracker.sender_id):
            return []

        funnel_stats_str = get_funnel_stats()
        dispatcher.utter_message(json_message={"text": funnel_stats_str})

        return []
