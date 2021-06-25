from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction


class ValidateAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_appointment_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[List[Text]]:

        return slots_mapped_in_domain
