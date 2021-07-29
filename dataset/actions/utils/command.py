from typing import Optional, Text


import re
from typing import Any, AnyStr, Match, Text, Dict, List


def match_command(message_text: Text, _is_admin_group=True):
    regex = r"^(/\w+)(\s+#(\w+))?(\s(.+))?$"
    if _is_admin_group:
        regex = r"^(/\w+)(\s+#(\w+))(\s(.+))?$"
        matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
        if matches == None:
            return None

        return {
            "name": matches.group(1),
            "doctor_id": matches.group(3),
            "args": matches.group(5),
        }

    matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
    if matches == None:
        return None

    return {
        "name": matches.group(1),
        "args": matches.group(5),
    }
