from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import get_doctor_commission_rate


class ActionAskDoctorSignupConsultationFee(Action):
    def name(self) -> Text:
        return "action_ask_doctor_signup__consultation_fee"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        doctor_commission_rate = get_doctor_commission_rate()
        text = (
            "What is your consultation fee in Rupees?\n"
            + "\n"
            + "Please note the following:\n"
            + "\n"
            + "- enter a number in multiples of 50 (for example 350 for Rs. 350)\n"
            + "- Thedal doesn't charge any commission on the consultation fee you provide\n"
            + "- Thedal bears the cost of payment gateway to the tune of 2-3%\n"
        )
        json_message = {"text": text}
        dispatcher.utter_message(json_message=json_message)

        return []
