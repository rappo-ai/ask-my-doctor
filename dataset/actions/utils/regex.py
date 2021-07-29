from typing import Optional, Text


import re
from typing import Any, AnyStr, Match, Text, Dict, List


def match_command(InputCommand: Text, _is_admin_group=True):
    regex = r"^(/\w+)(\s+#(\w+))?(\s)?(.+)?$"
    if _is_admin_group:
        regex = r"^(/\w+)(\s+#(\w+))?(\s)?(.+)?$"
        matches: Match[AnyStr @ re.search] = re.search(regex, InputCommand)
        Target = {
            "command": matches.group(1),
            "id": matches.group(3),
            "string": matches.group(5),
        }
        return Target

    matches: Match[AnyStr @ re.search] = re.search(regex, InputCommand)
    Target = {
        "command": matches.group(1),
        "string": matches.group(5),
    }

    return Target
