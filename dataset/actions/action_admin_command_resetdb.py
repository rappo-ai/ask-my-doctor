from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.db.store import reset_actions_db


class ActionAdminCommandResetDB(Action):
    def name(self) -> Text:
        return "action_admin_command_resetdb"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        reset_actions_db()
        dispatcher.utter_message(
            json_message={"text": "The actions DB has been reset."}
        )

        return []
