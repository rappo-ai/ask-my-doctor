from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_super_admin
from actions.db.store import reset_actions_db


class ActionCommandResetDB(Action):
    def name(self) -> Text:
        return "action_command_resetdb"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_super_admin(tracker.sender_id):
            return []

        reset_actions_db()
        dispatcher.utter_message(
            json_message={"text": "The actions DB has been reset."}
        )

        return []