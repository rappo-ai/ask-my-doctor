import base64
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Text
from zipfile import ZipFile, ZIP_DEFLATED

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.utils.admin_config import is_admin_group
from actions.utils.command import extract_doctor_command
from actions.utils.date import SERVER_TZINFO
from actions.utils.doctor import get_doctor_for_user_id, is_approved_doctor
from actions.utils.order import (
    format_order_for_csv,
    format_order_header_for_csv,
    get_orders,
)
from actions.utils.text import format_count


class ActionCommandListOrders(Action):
    def name(self) -> Text:
        return "action_command_listorders"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        _is_admin_group = is_admin_group(tracker.sender_id)
        if not (_is_admin_group or is_approved_doctor(tracker.sender_id)):
            return []

        message_text = tracker.latest_message.get("text")
        command = extract_doctor_command(message_text, False)
        if command:
            doctor_id = (
                command["doctor_id"]
                if _is_admin_group
                else get_doctor_for_user_id(tracker.sender_id)["_id"]
            )
            orders = get_orders(
                doctor_id=doctor_id,
            )
            num_orders = orders.count()
            dispatcher.utter_message(
                json_message={
                    "text": f"Found {num_orders} {format_count('order', 'orders', num_orders)}"
                    + (
                        f" for doctor '#{doctor_id}'"
                        if (_is_admin_group and doctor_id)
                        else ""
                    )
                }
            )
            if num_orders:
                current_date_str = datetime.now(tz=SERVER_TZINFO).strftime(
                    "%d-%m-%y_%H-%M%p"
                )
                optional_doctor_id = (
                    f"_{doctor_id}" if (_is_admin_group and doctor_id) else ""
                )
                file_name_base = f"orders{optional_doctor_id}_{current_date_str}"
                file_name_csv = f"{file_name_base}.csv"
                file_name_zip = f"{file_name_base}.zip"
                orders_csv_list = [format_order_header_for_csv()]
                for o in orders:
                    orders_csv_list.append(format_order_for_csv(o))
                orders_csv = "\n".join(orders_csv_list)
                f = BytesIO()
                z = ZipFile(f, mode="w", compression=ZIP_DEFLATED)
                z.writestr(file_name_csv, str.encode(orders_csv, "utf-8"))
                z.close()
                bytes = f.getvalue()
                base64_str = base64.b64encode(bytes).decode("ascii")
                dispatcher.utter_message(
                    json_message={
                        "zip": base64_str,
                        "zip_file_name": file_name_zip,
                        "caption": "List of orders",
                    }
                )
        else:
            usage = "/listorders"
            if _is_admin_group:
                usage = "/listorders <DOCTOR ID>[OPTIONAL]"
            dispatcher.utter_message(
                json_message={
                    "text": f"The command format is incorrect. Usage:\n\n{usage}"
                }
            )
        return []
