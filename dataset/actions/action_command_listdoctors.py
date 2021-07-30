import re
from typing import Any, AnyStr, Dict, List, Match, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group, get_specialities
from actions.utils.doctor import (
    LISTING_STATUS_ENABLED,
    LISTING_STATUS_DISABLED,
    ONBOARDING_STATUS_APPROVED,
    ONBOARDING_STATUS_REJECTED,
    ONBOARDING_STATUS_SIGNUP,
    get_doctors,
    get_doctor_card,
)
from actions.utils.text import format_count
from actions.utils.validate import validate_speciality


class ActionCommandListDoctors(Action):
    def name(self) -> Text:
        return "action_command_listdoctors"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        if not is_admin_group(tracker.sender_id):
            return []

        message_text = tracker.latest_message.get("text")
        regex = r"^(/\w+)(\s+(.+))?$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        args = matches and matches.group(3)
        is_valid_speciality = args and validate_speciality(args)
        listing_status_list = [
            LISTING_STATUS_ENABLED,
            LISTING_STATUS_DISABLED,
        ]
        onboarding_status_list = [
            ONBOARDING_STATUS_APPROVED,
            ONBOARDING_STATUS_REJECTED,
            ONBOARDING_STATUS_SIGNUP,
        ]
        is_valid_listing_status = args and args in listing_status_list
        is_valid_onboarding_status = args and args in onboarding_status_list

        if matches and (
            not args
            or is_valid_speciality
            or is_valid_listing_status
            or is_valid_onboarding_status
        ):
            speciality = args if is_valid_speciality else None
            listing_status = args if is_valid_listing_status else None
            onboarding_status = args if is_valid_onboarding_status else None
            doctors = get_doctors(
                speciality=speciality,
                listing_status=listing_status,
                onboarding_status=onboarding_status,
            )
            num_doctors = doctors.count()
            dispatcher.utter_message(
                json_message={
                    "text": f"Found {num_doctors} {format_count('doctor', 'doctors', num_doctors)}"
                    + (f" for speciality '{speciality}'" if speciality else "")
                    + (
                        f" for listing status '{listing_status}'"
                        if listing_status
                        else ""
                    )
                    + (
                        f" for onboarding status '{onboarding_status}'"
                        if onboarding_status
                        else ""
                    )
                }
            )
            for d in doctors:
                dispatcher.utter_message(json_message=get_doctor_card(d))
        else:
            usage = "/listdoctors <SPECIALITY>[OPTIONAL] <LISTING STATUS>[OPTIONAL] <ONBOARDING STATUS>[OPTIONAL]"
            specialities = "\n".join(get_specialities())
            listing_statuses = "\n".join(listing_status_list)
            onboarding_statuses = "\n".join(onboarding_status_list)
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}\n\nIf specifying an optional filter, only one of SPECIALITY, LISTING STATUS or ONBOARDING STATUS can be specified.\n\nIf SPECIALITY is specified it must be from this list:\n\n{specialities}\n\nIf LISTING STATUS is specified it must be one of:\n\n{listing_statuses}\n\nIf ONBOARDING STATUS is specified it must be one of:\n\n{onboarding_statuses}\n\n"
                }
            )
        return []
