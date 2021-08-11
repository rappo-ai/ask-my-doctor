import logging
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.user import get_user_for_user_id, update_user

logger = logging.getLogger(__name__)


class ActionDemo(Action):
    def name(self) -> Text:
        return "action_demo"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        telegram_user_id = tracker.get_slot("telegram_user_id") or ""
        user = get_user_for_user_id(telegram_user_id)
        if not user:
            logger.warn("/demo user not found")
            return []

        new_demo_mode = not bool(user.get("is_demo_mode") or False)
        update_user(user.get("_id"), demo_mode={"value": new_demo_mode})

        text = f"DEMO mode set to {'ON' if new_demo_mode else 'OFF'}."
        dispatcher.utter_message(text=text)

        return []
