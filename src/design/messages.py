import enum
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass


class ParserException(Exception):
    pass


class MessageType(enum.Enum):
    TELEGRAM = enum.auto()
    MATTERMOST = enum.auto()
    SLACK = enum.auto()


@dataclass
class JsonMessage:
    message_type: MessageType
    payload: str


@dataclass
class MessageFaktory:
    """There is no need to describe anything here."""
    source: MessageType
    user_id: str
    user_name: str
    text: str
    chanel_id: str
    chanel_name: str
    raw_data: dict

    @classmethod
    def from_telegram(cls, payload: dict) -> 'MessageFaktory':
        message = cls(
            source=MessageType.TELEGRAM,
            user_id=str(payload.get("from", {}).get("id", '')),
            user_name=str(payload.get("from", {}).get("username", '')),
            text=payload.get("text", ""),
            chanel_id=str(payload.get("chat", {}).get("id", '')),
            chanel_name=payload.get("chat", {}).get("title", ''),
            raw_data=payload,
        )
        return message

    @classmethod
    def from_mattermost(cls, payload: dict) -> 'MessageFaktory':
        message = cls(
            source=MessageType.MATTERMOST,
            user_id=str(payload.get("user_id", '')),
            user_name=str(payload.get("username", '')),
            text=payload.get("text", ""),
            chanel_id=str(payload.get("chat_id", '')),
            chanel_name=payload.get("chat_title", ''),
            raw_data=payload,
        )
        return message

    @classmethod
    def from_slack(cls, payload: dict) -> 'MessageFaktory':
        message = cls(
            source=MessageType.MATTERMOST,
            user_id=str(payload.get("user_id", '')),
            user_name=str(payload.get("username", '')),
            text=payload.get("text", ""),
            chanel_id=str(payload.get("chat_id", '')),
            chanel_name=payload.get("chat_title", ''),
            raw_data=payload,
        )
        return message


class ParsedMessage(ABC):

    @abstractmethod
    def parse(self, payload: dict) -> MessageFaktory:
        pass


class TelegramParser(ParsedMessage):

    def parse(self, payload: dict) -> MessageFaktory:
        return MessageFaktory.from_telegram(payload)


class MattermostParser(ParsedMessage):
    def parse(self, payload: dict) -> MessageFaktory:
        return MessageFaktory.from_mattermost(payload)


class SlackParser(ParsedMessage):
    def parse(self, payload: dict) -> MessageFaktory:
        return MessageFaktory.from_slack(payload)


class ParserFactory:
    def __init__(self):
        self._parsers: dict[MessageType, ParsedMessage] = {
            MessageType.TELEGRAM: TelegramParser(),
            MessageType.MATTERMOST: MattermostParser(),
            MessageType.SLACK: SlackParser(),
        }

    def get_parser(self, message_type: MessageType) -> ParsedMessage:
        parser = self._parsers.get(message_type)
        if parser is None:
            raise ValueError(f"Парсер не нашёл сообщение такого типа {message_type}")
        return parser

    def register_parser(self, message_type: MessageType, parser: ParsedMessage) -> None:
        self._parsers[message_type] = parser


class MessageProcessor:

    def __init__(self, factory: ParserFactory = None):
        self.factory = factory or ParserFactory()

    def process(self, json_message: JsonMessage) -> MessageFaktory:
        try:
            payload = json.loads(json_message.payload)
        except json.JSONDecodeError as e:
            raise ValueError(f"Не удалось прочитать Json файл {e}")
        parser = self.factory.get_parser(json_message.message_type)

        return parser.parse(payload)


def main():
    telegram_message = JsonMessage(
        message_type=MessageType.TELEGRAM,
        payload='{"from": {'
                '"id": 12345, '
                '"username": "alice"},'
                '"chat": {'
                '"id": 67890, '
                '"title": "Python Chat"}, '
                '"text": "Hello telegram!"}'
    )

    mattermost_message = JsonMessage(
        message_type=MessageType.MATTERMOST,
        payload='{"user_id": "user_123",'
                ' "user_name": "bob",'
                ' "channel_id": "channel_456",'
                ' "channel_name": "General",'
                ' "text": "Hello from Mattermost!"}',
    )

    slack_message = JsonMessage(
        message_type=MessageType.SLACK,
        payload='{"user": "U12345",'
                ' "username": "charlie",'
                ' "channel": "C67890",'
                ' "channel_name": "random",'
                ' "text": "Hello from Slack!"}'
    )

    processor = MessageProcessor()

    for message in [telegram_message, mattermost_message, slack_message]:
        try:
            parsed = processor.process(message)
            print(f"Преобразование {parsed.source.value}: {parsed.user_name} -> {parsed.text}")
        except ParserException as e:
            print(f"Ошибка во время преобразования сообщения {e}")


if __name__ == '__main__':
    main()