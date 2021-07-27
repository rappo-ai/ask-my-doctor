import os

BOT_DISPLAY_NAME_KEY = "BOT_DISPLAY_NAME"
BOT_HELP_MESSAGE_KEY = "BOT_HELP_MESSAGE"
BOT_SUPPORT_USERNAME_KEY = "BOT_SUPPORT_USERNAME"


def get_bot_display_name():
    return os.environ.get(BOT_DISPLAY_NAME_KEY) or "Doctor Consultation Bot"


def get_bot_help_message():
    return os.environ.get(BOT_HELP_MESSAGE_KEY) or (
        "You can reach out to us for help in any of the following ways:\n"
        + "\n"
        + "- Message us @doctorconsultationsupport\n"
        + "- Email us at support@doctorconsultation.com\n"
        + "- Call us at 9876543210 (Mon-Fri 9 AM-6PM)\n"
    )


def get_bot_support_username():
    return os.environ.get(BOT_SUPPORT_USERNAME_KEY) or "@doctorconsultationbotsupport"
