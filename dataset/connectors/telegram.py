from bson.objectid import ObjectId
from copy import deepcopy
from dotenv import load_dotenv
import json
import logging
import os
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
from urllib.parse import urlunparse

from rasa.core.channels.channel import InputChannel, UserMessage, OutputChannel
from rasa.shared.constants import INTENT_MESSAGE_PREFIX
from rasa.shared.core.constants import USER_INTENT_RESTART

logger = logging.getLogger(__name__)

load_dotenv()


class MongoDataStore:
    """Stores data in Mongo.

    Property methods:
        conversations: returns the current conversation
    """

    def __init__(
        self,
        host: Optional[Text] = "mongodb://mongo:27017",
        db: Optional[Text] = "rappo",
        username: Optional[Text] = None,
        password: Optional[Text] = None,
        auth_source: Optional[Text] = "admin",
    ) -> None:
        from pymongo import MongoClient
        from pymongo.database import Database

        self.client = MongoClient(
            host,
            username=username,
            password=password,
            authSource=auth_source,
        )

        self.db = Database(self.client, db)


_db_store = MongoDataStore()

db = _db_store.db


def get_order(id):
    return db.order.find_one({"_id": ObjectId(id)})


def get_lock_for_id(lock_id):
    return db.timeslot_lock.find_one({"_id": ObjectId(lock_id)})


def get_json_key(dict, key, default=None):
    try:
        key_split = key.split(".", 1)
        key_split_len = len(key_split)
        if key_split_len == 2:
            return get_json_key(dict[key_split[0]], key_split[1], default)
        elif key_split_len == 1:
            return dict[key_split[0]]
    except:
        return default
    return default


def get_query_param(params, key):
    return next(iter(params[key]), "")


def get_bot_link(bot_username):
    return "https://t.me/" + bot_username


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
        try:
            json_message = deepcopy(json_message)

            recipient_id = json_message.pop("chat_id", recipient_id)
            reply_markup_json: Dict = json_message.pop("reply_markup", None)
            reply_markup = ReplyKeyboardRemove()
            if reply_markup_json:
                keyboard_type = reply_markup_json.get("type", "reply")
                if keyboard_type == "reply":
                    reply_markup = ReplyKeyboardMarkup(
                        resize_keyboard=reply_markup_json.get("resize_keyboard", False),
                        one_time_keyboard=reply_markup_json.get(
                            "one_time_keyboard", True
                        ),
                        row_width=reply_markup_json.get("row_width", 4),
                    )
                    [
                        reply_markup.add(*row)
                        for row in reply_markup_json.get("keyboard", [])
                    ]
                elif keyboard_type == "inline":
                    reply_markup = InlineKeyboardMarkup(
                        row_width=reply_markup_json.get("row_width", 4)
                    )
                    [
                        reply_markup.add(
                            *[
                                InlineKeyboardButton(
                                    col.get("title"),
                                    callback_data=col.get("payload"),
                                    url=col.get("url"),
                                )
                                for col in row
                            ]
                        )
                        for row in reply_markup_json.get("keyboard", [])
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
        except Exception as e:
            logger.error(e)


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
                    from requests_oauthlib import OAuth2Session

                    GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"

                    args = request.args
                    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
                    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
                    state = args["state"][0]
                    scheme = "https" if request.host.find("localhost") == -1 else "http"
                    redirect_uri = urlunparse(
                        (scheme, request.host, request.path, None, "", None)
                    )

                    google = OAuth2Session(
                        client_id, state=state, redirect_uri=redirect_uri
                    )

                    token = google.fetch_token(
                        GOOGLE_OAUTH_TOKEN_URL,
                        client_secret=client_secret,
                        code=args["code"][0],
                    )

                    sender_id = state
                    token_str = json.dumps(token)
                    message = f'/EXTERNAL_on_google_auth{{"credentials": {token_str}}}'
                    await on_new_message(
                        UserMessage(
                            message,
                            out_channel,
                            sender_id,
                            input_channel=self.name(),
                            metadata={},
                        )
                    )
                except Exception as e:
                    logger.error(e)

                bot_link = get_bot_link(self.verify)
                return response.redirect(bot_link)

        @telegram_webhook.route("/set_webhook", methods=["GET", "POST"])
        async def set_webhook(_: Request) -> HTTPResponse:
            s = out_channel.setWebhook(self.webhook_url)
            if s:
                logger.info("Webhook Setup Successful")
                return response.text("Webhook setup successful")
            else:
                logger.warning("Webhook Setup Failed")
                return response.text("Invalid webhook")

        @telegram_webhook.route("/payment_link", methods=["GET"])
        async def payment_link(request: Request) -> Any:
            if request.method == "GET":
                try:
                    args = request.args
                    order_id = get_query_param(args, "order_id")
                    order = get_order(order_id)
                    timeslot_lock_id = order.get("timeslot_lock_id")
                    timeslot_lock = get_lock_for_id(timeslot_lock_id)
                    if timeslot_lock and str(timeslot_lock.get("order_id")) == order_id:
                        payment_link_url = get_json_key(
                            order, "payment_link.metadata.short_url"
                        )
                        return response.redirect(payment_link_url)
                    bot_link = get_bot_link(self.verify)
                    REDIRECT_MS = 10000
                    return response.html(
                        f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0"><style>p{{font-size: large;}}</style></head><body><p>This payment link has expired. Please create a fresh booking.<br><br>You will be redirected back to the bot in {int(REDIRECT_MS/1000)} seconds. If the page does not redirect automatically, please click <a href="{bot_link}">this link</a> to go back to the bot.</p><script type="text/javascript"> setTimeout(function(){{window.location.href="{bot_link}";}}, {REDIRECT_MS});</script></body></html>'
                    )
                except Exception as e:
                    logger.error(e)

                return response.text("Something went wrong.")

        @telegram_webhook.route("/payment_callback", methods=["GET"])
        async def payment_callback(request: Request) -> Any:
            if request.method == "GET":
                try:
                    args = request.args
                    payment_status = {
                        "razorpay_payment_id": get_query_param(
                            args, "razorpay_payment_id"
                        ),
                        "razorpay_payment_link_id": get_query_param(
                            args, "razorpay_payment_link_id"
                        ),
                        "razorpay_payment_link_reference_id": get_query_param(
                            args, "razorpay_payment_link_reference_id"
                        ),
                        "razorpay_payment_link_status": get_query_param(
                            args, "razorpay_payment_link_status"
                        ),
                        "razorpay_signature": get_query_param(
                            args, "razorpay_signature"
                        ),
                    }
                    order_id = get_query_param(
                        args, "razorpay_payment_link_reference_id"
                    )
                    order = get_order(order_id)
                    sender_id = get_json_key(order, "metadata.patient.user_id")
                    payment_status_str = json.dumps(payment_status)
                    message = f'/EXTERNAL_payment_callback{{"payment_status": {payment_status_str}}}'

                    await on_new_message(
                        UserMessage(
                            message,
                            out_channel,
                            sender_id,
                            input_channel=self.name(),
                            metadata={},
                        )
                    )
                except Exception as e:
                    logger.error(e)

                bot_link = get_bot_link(self.verify)
                return response.redirect(bot_link)

        @telegram_webhook.route("/order_unlocked", methods=["POST"])
        async def order_unlocked(request: Request) -> Any:
            if request.method == "POST":
                try:
                    request_body: Dict = request.json
                    order_id = request_body.get("order_id")
                    sender_id = request_body.get("sender_id")
                    message = f'/EXTERNAL_order_unlocked{{"order_id": "{order_id}"}}'

                    await on_new_message(
                        UserMessage(
                            message,
                            out_channel,
                            sender_id,
                            input_channel=self.name(),
                            metadata={},
                        )
                    )
                except Exception as e:
                    logger.error(e)
                return response.text("success")

        @telegram_webhook.route("/webhook", methods=["GET", "POST"])
        async def message(request: Request) -> Any:
            if request.method == "POST":
                try:
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
                            text = msg.text
                            if text.startswith("/"):
                                text = text.replace(f"@{self.verify}", "")
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
