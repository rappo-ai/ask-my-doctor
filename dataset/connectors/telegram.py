import json
import logging
from copy import deepcopy
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardButton,
    Update,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Message,
)
from typing import Dict, Text, Any, List, Optional, Callable, Awaitable

from google_auth_oauthlib.helpers import credentials_from_session
from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel
from rasa.shared.constants import INTENT_MESSAGE_PREFIX
from rasa.shared.core.constants import USER_INTENT_RESTART
from requests_oauthlib import OAuth2Session

logger = logging.getLogger(__name__)


class TelegramOutput(TeleBot, OutputChannel):
    """Output channel for Telegram."""

    # skipcq: PYL-W0236
    @classmethod
    def name(cls) -> Text:
        return "telegram"

    def __init__(self, access_token: Optional[Text]) -> None:
        super().__init__(access_token)

    async def send_text_message(
        self,
        recipient_id: Text,
        text: Text,
        reply_markup=ReplyKeyboardRemove(),
        **kwargs: Any,
    ) -> None:
        for message_part in text.strip().split("\n\n"):
            self.send_message(recipient_id, message_part, reply_markup=reply_markup)

    async def send_image_url(
        self,
        recipient_id: Text,
        image: Text,
        reply_markup=ReplyKeyboardRemove(),
        **kwargs: Any,
    ) -> None:
        self.send_photo(recipient_id, image, reply_markup=reply_markup)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        button_type: Optional[Text] = "inline",
        **kwargs: Any,
    ) -> None:
        """Sends a message with keyboard.

        For more information: https://core.telegram.org/bots#keyboards

        :button_type inline: horizontal inline keyboard

        :button_type vertical: vertical inline keyboard

        :button_type reply: reply keyboard
        """
        if button_type == "inline":
            reply_markup = InlineKeyboardMarkup()
            button_list = [
                InlineKeyboardButton(s["title"], callback_data=s["payload"])
                for s in buttons
            ]
            reply_markup.row(*button_list)

        elif button_type == "vertical":
            reply_markup = InlineKeyboardMarkup()
            [
                reply_markup.row(
                    InlineKeyboardButton(s["title"], callback_data=s["payload"])
                )
                for s in buttons
            ]

        elif button_type == "reply":
            reply_markup = ReplyKeyboardMarkup(
                resize_keyboard=False, one_time_keyboard=True
            )
            # drop button_type from button_list
            button_list = [b for b in buttons if b.get("title")]
            for idx, button in enumerate(buttons):
                if isinstance(button, list):
                    reply_markup.add(KeyboardButton(s["title"]) for s in button)
                else:
                    reply_markup.add(KeyboardButton(button["title"]))
        else:
            logger.error(
                "Trying to send text with buttons for unknown "
                "button type {}".format(button_type)
            )
            return

        self.send_message(recipient_id, text, reply_markup=reply_markup)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        json_message = deepcopy(json_message)

        recipient_id = json_message.pop("chat_id", recipient_id)
        reply_markup_json: Dict = json_message.pop("reply_markup", None)
        reply_markup = ReplyKeyboardRemove()
        if reply_markup_json:
            keyboard_type = reply_markup_json.get("type", "reply")
            if keyboard_type == "reply":
                reply_markup = ReplyKeyboardMarkup(
                    resize_keyboard=reply_markup_json.get("resize_keyboard", False),
                    one_time_keyboard=reply_markup_json.get("one_time_keyboard", True),
                )
                [
                    reply_markup.add(KeyboardButton(col))
                    for row in reply_markup_json.get("keyboard", [])
                    for col in row
                ]
            elif keyboard_type == "inline":
                reply_markup = InlineKeyboardMarkup()
                [
                    reply_markup.add(
                        InlineKeyboardButton(col["title"], callback_data=col["payload"])
                    )
                    for row in reply_markup_json.get("keyboard", [])
                    for col in row
                ]

        send_functions = {
            ("text",): "send_message",
            ("photo",): "send_photo",
            ("audio",): "send_audio",
            ("document",): "send_document",
            ("sticker",): "send_sticker",
            ("video",): "send_video",
            ("video_note",): "send_video_note",
            ("animation",): "send_animation",
            ("voice",): "send_voice",
            ("media",): "send_media_group",
            ("latitude", "longitude", "title", "address"): "send_venue",
            ("latitude", "longitude"): "send_location",
            ("phone_number", "first_name"): "send_contact",
            ("game_short_name",): "send_game",
            ("action",): "send_chat_action",
            (
                "title",
                "decription",
                "payload",
                "provider_token",
                "start_parameter",
                "currency",
                "prices",
            ): "send_invoice",
            ("from_chat_id", "message_id"): "copy_message",
        }

        for params in send_functions.keys():
            if all(json_message.get(p) is not None for p in params):
                args = [json_message.pop(p) for p in params]
                if send_functions[params] not in [
                    "send_media_group",
                    "send_game",
                    "send_chat_action",
                    "send_invoice",
                ]:
                    json_message["reply_markup"] = reply_markup
                api_call = getattr(self, send_functions[params])
                api_call(recipient_id, *args, **json_message)


class TelegramInput(InputChannel):
    """Telegram input channel"""

    @classmethod
    def name(cls) -> Text:
        return "telegram"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(
            credentials.get("access_token"),
            credentials.get("verify"),
            credentials.get("webhook_url"),
            credentials.get("drop_pending_updates", "true").lower()
            in ["true", "1", "t"],
        )

    def __init__(
        self,
        access_token: Optional[Text],
        verify: Optional[Text],
        webhook_url: Optional[Text],
        drop_pending_updates: Optional[bool] = True,
        debug_mode: bool = True,
    ) -> None:
        self.access_token = access_token
        self.verify = verify
        self.webhook_url = webhook_url
        self.drop_pending_updates = drop_pending_updates
        self.debug_mode = debug_mode

    @staticmethod
    def _is_text_message(message: Message) -> bool:
        return message and (message.text is not None)

    @staticmethod
    def _is_photo_message(message: Message) -> bool:
        return message and (message.photo is not None)

    @staticmethod
    def _is_location_message(message: Message) -> bool:
        return message and (message.location is not None)

    @staticmethod
    def _is_edited_message(message: Update) -> bool:
        return message and (message.edited_message is not None)

    @staticmethod
    def _is_button(message: Update) -> bool:
        return message and (message.callback_query is not None)

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        telegram_webhook = Blueprint("telegram_webhook", __name__)
        out_channel = self.get_output_channel()

        @telegram_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @telegram_webhook.route("/oauth", methods=["GET"])
        async def google_oauth(request: Request) -> Any:
            if request.method == "GET":
                try:
                    disable_nlu_bypass = True
                    args = request.args

                    token_url = "https://oauth2.googleapis.com/token"
                    client_secret = "fQ28EXqDQHeV0k0UFJr-N8xu"
                    client_id = "881461713261-dhrt5ug8hf8tr2uiqsiihnj24492flt6.apps.googleusercontent.com"
                    client_config = {
                        "client_id": "881461713261-dhrt5ug8hf8tr2uiqsiihnj24492flt6.apps.googleusercontent.com",
                        "project_id": "spread-313410",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": "fQ28EXqDQHeV0k0UFJr-N8xu",
                    }
                    print(request.args)
                    print("state", args["state"][0])
                    print("code", args["code"][0])

                    # Fetch the access token
                    google = OAuth2Session(client_id, state=args["state"][0])

                    google.fetch_token(
                        token_url, client_secret=client_secret, code=args["code"][0]
                    )
                    creds = credentials_from_session(
                        google, client_config=client_config
                    )
                    print("creds:", creds)

                    # print("user_id--",user_id)
                    doctor = get_doctor_for_user_id(user_id)
                    sender_id = get_json_key(doctor, "metadata.doctor.user_id", "")
                    print("user_id", user_id)
                    print("sender_id", sender_id)
                    printstat = f'/EXTERNAL_on_google_auth{{"credentials"={creds}}}'
                    await on_new_message(
                        UserMessage(
                            printstat,
                            out_channel,
                            sender_id,
                            input_channel=self.name(),
                            metadata={},
                        )
                    )
                except Exception as e:
                    logger.error(e)

                return response.redirect("https://t.me/tuil_askdoctorbot")

        @telegram_webhook.route("/set_webhook", methods=["GET", "POST"])
        async def set_webhook(_: Request) -> HTTPResponse:
            s = out_channel.setWebhook(self.webhook_url)
            if s:
                logger.info("Webhook Setup Successful")
                return response.text("Webhook setup successful")
            else:
                logger.warning("Webhook Setup Failed")
                return response.text("Invalid webhook")

        @telegram_webhook.route("/webhook", methods=["GET", "POST"])
        async def message(request: Request) -> Any:
            if request.method == "POST":
                disable_nlu_bypass = True
                request_dict = request.json
                update = Update.de_json(request_dict)
                if not out_channel.get_me().username == self.verify:
                    logger.debug("Invalid access token, check it matches Telegram")
                    return response.text("failed")

                if self._is_button(update):
                    out_channel.answer_callback_query(update.callback_query.id)
                    msg = update.callback_query.message
                    text = update.callback_query.data
                    disable_nlu_bypass = False
                elif self._is_edited_message(update):
                    # skip edited messages for now
                    # msg = update.edited_message
                    # text = update.edited_message.text
                    return response.text("success")
                else:
                    msg = update.message
                    if self._is_text_message(msg):
                        text = msg.text.replace("/bot", "")
                    elif self._is_photo_message(msg):
                        text = json.dumps(request_dict)
                    elif self._is_location_message(msg):
                        text = '{{"lng":{0}, "lat":{1}}}'.format(
                            msg.location.longitude, msg.location.latitude
                        )
                    else:
                        return response.text("success")
                sender_id = msg.chat.id
                metadata = self.get_metadata(request) or {}
                try:
                    if text == (INTENT_MESSAGE_PREFIX + USER_INTENT_RESTART):
                        await on_new_message(
                            UserMessage(
                                text,
                                out_channel,
                                sender_id,
                                input_channel=self.name(),
                                metadata=metadata,
                            )
                        )
                        await on_new_message(
                            UserMessage(
                                "/start",
                                out_channel,
                                sender_id,
                                input_channel=self.name(),
                                metadata=metadata,
                            )
                        )
                    else:
                        await on_new_message(
                            UserMessage(
                                text,
                                out_channel,
                                sender_id,
                                input_channel=self.name(),
                                metadata=metadata,
                                disable_nlu_bypass=disable_nlu_bypass,
                            )
                        )
                except Exception as e:
                    logger.error(f"Exception when trying to handle message.{e}")
                    logger.debug(e, exc_info=True)
                    pass

                return response.text("success")

        return telegram_webhook

    def get_output_channel(self) -> TelegramOutput:
        """Loads the telegram channel."""
        channel = TelegramOutput(self.access_token)
        channel.set_webhook(
            url=self.webhook_url, drop_pending_updates=self.drop_pending_updates
        )

        return channel

    def get_metadata(self, request: Request) -> Dict[Text, Any]:
        return request.json
