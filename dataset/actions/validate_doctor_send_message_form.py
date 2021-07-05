from typing import Any, Dict, Optional, List, Text

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from actions.utils.json import get_json_key


class ValidateDoctorSendMessageForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_doctor_send_message_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Optional[List[Text]]:
        required_slots = slots_mapped_in_domain + ["doctor_send_message__message_id"]
        return required_slots

    async def extract_doctor_send_message__message_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        metadata = tracker.latest_message.get("metadata")

        return {
            "doctor_send_message__message_id": get_json_key(
                metadata, "message.message_id"
            )
        }
