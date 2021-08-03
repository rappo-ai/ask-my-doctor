import re
from typing import AnyStr, Match, Text


def extract_doctor_command(message_text: Text, assert_doctor_id: bool):
    if assert_doctor_id:
        regex = r"^(/\w+)(\s+#(\w+))(\s(.+))?$"
    else:
        regex = r"^(/\w+)(\s+#(\w+))?(\s(.+))?$"

    matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
    return matches and {
        "name": matches.group(1),
        "doctor_id": matches.group(3),
        "args": matches.group(5),
    }
