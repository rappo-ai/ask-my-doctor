import re
from typing import Text

# from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/utils/helpers.py
def escape_markdown(
    text: str, version: int = 2, entity_type: str = None, enabled: bool = True
) -> str:
    """
    Helper function to escape telegram markup symbols.
    Args:
        text (:obj:`str`): The text.
        version (:obj:`int` | :obj:`str`): Use to specify the version of telegrams Markdown.
            Either ``1`` or ``2``. Defaults to ``2``.
        entity_type (:obj:`str`, optional): For the entity types ``PRE``, ``CODE`` and the link
            part of ``TEXT_LINKS``, only certain characters need to be escaped in ``MarkdownV2``.
            See the official API documentation for details. Only valid in combination with
            ``version=2``, will be ignored else.
    """
    if not enabled:
        return text
    if int(version) == 1:
        escape_chars = r"_*`["
    elif int(version) == 2:
        if entity_type in ["pre", "code"]:
            escape_chars = r"\`"
        elif entity_type == "text_link":
            escape_chars = r"\)"
        else:
            escape_chars = r"_*[]()~`>#+-=|{}.!"
    else:
        raise ValueError("Markdown version must be either 1 or 2!")

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def get_user_link(user_id: Text, mention_text: Text):
    return f"[{mention_text}](tg://user?id={user_id})"
