from typing import Optional, Text


import re
from typing import Any, AnyStr, Match, Text, Dict, List


def extract_command(message_text: Text, is_admin_group):

    if is_admin_group:
        regex = r"^(/\w+)(\s+#(\w+))(\s(.+))?$"
    else:
        regex = r"^(/\w+)(\s+#(\w+))?(\s(.+))?$"

    matches: Match[AnyStr @ re.search] = re.search(regex, message_text)
    if matches == None:
        return None

    return {
        "name": matches.group(1),
        "doctor_id": matches.group(3),
        "args": matches.group(5),
    }
