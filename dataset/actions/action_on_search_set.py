from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.doctor import (
    LISTING_STATUS_ENABLED,
    ONBOARDING_STATUS_APPROVED,
    get_doctors,
    print_doctor_summary,
)


class ActionOnSearchSet(Action):
    def name(self) -> Text:
        return "action_on_search_set"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        speciality = tracker.get_slot("search__speciality")

        if not speciality:
            dispatcher.utter_message(
                json_message={
                    "text": "There are no specialities to choose from. Please use /help to contact support."
                }
            )
            return []

        doctors = get_doctors(
            speciality=speciality,
            onboarding_status=ONBOARDING_STATUS_APPROVED,
            listing_status=LISTING_STATUS_ENABLED,
        )
        if not doctors.count():
            dispatcher.utter_message(
                json_message={
                    "text": f"Currently there are no doctors available for speciality '{speciality}'."
                }
            )
            return []
        else:
            dispatcher.utter_message(json_message={"text": "Please choose a doctor:"})
        for d in doctors:
            reply_markup = {
                "keyboard": [
                    [
                        {
                            "title": "Book",
                            "payload": f"/EXTERNAL_create_appointment{{\"d_id\":\"{str(d['_id'])}\"}}",
                        }
                    ]
                ],
                "type": "inline",
            }
            caption = print_doctor_summary(d)

            json_message = {
                "photo": d["photo"],
                "caption": caption,
                "reply_markup": reply_markup,
            }
            dispatcher.utter_message(json_message=json_message)

        return []
