from typing import Any, Text, Dict

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

from actions.utils.date import format_appointment_date, format_appointment_time
from actions.utils.doctor import (
    get_available_time_slots,
    get_available_appointment_dates,
)


class ValidateAppointmentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_appointment_form"

    def validate_appointment__date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        doctor_id = tracker.get_slot("appointment__doctor_id")
        upcoming_dates = [
            format_appointment_date(d)
            for d in get_available_appointment_dates(doctor_id)
        ]
        if slot_value in upcoming_dates:
            return {"appointment__date": slot_value}
        else:
            dispatcher.utter_message(json_message={"text": "Invalid input."})
            return {"appointment__date": None}

    def validate_appointment__time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        doctor_id = tracker.get_slot("appointment__doctor_id")
        appointment_date = tracker.get_slot("appointment__date")
        availaible_time_slots = [
            format_appointment_time(s)
            for s in get_available_time_slots(doctor_id, appointment_date)
        ]
        if slot_value in availaible_time_slots:
            return {"appointment__time": slot_value}
        else:
            dispatcher.utter_message(json_message={"text": "Invalid input."})
            return {"appointment__time": None}
