from actions.utils.json import get_json_key


def get_chat_type(metadata):
    return get_json_key(metadata, "message.chat.type") or get_json_key(
        metadata, "callback_query.message.chat.type"
    )


def get_first_name(metadata):
    return get_json_key(metadata, "message.from.first_name") or get_json_key(
        metadata, "callback_query.from.first_name"
    )
