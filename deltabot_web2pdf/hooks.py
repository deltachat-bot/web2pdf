"""Event Hooks"""

import re
from argparse import Namespace
from tempfile import NamedTemporaryFile

import pdfkit
from deltabot_cli import BotCli
from deltachat2 import Bot, ChatType, CoreEvent, EventType, MsgData, NewMsgEvent, events
from rich.logging import RichHandler

from ._version import __version__

cli = BotCli("web2pdf")
cli.add_generic_option("-v", "--version", action="version", version=__version__)
cli.add_generic_option(
    "--no-time",
    help="do not display date timestamp in log messages",
    action="store_false",
)


@cli.on_init
def _on_init(bot: Bot, args: Namespace) -> None:
    bot.logger.handlers = [
        RichHandler(show_path=False, omit_repeated_times=False, show_time=args.no_time)
    ]
    for accid in bot.rpc.get_all_account_ids():
        if not bot.rpc.get_config(accid, "displayname"):
            bot.rpc.set_config(accid, "displayname", "Web to PDF")
            status = "I am a Delta Chat bot, send me /help for more info"
            bot.rpc.set_config(accid, "selfstatus", status)
            bot.rpc.set_config(accid, "delete_device_after", str(60 * 60 * 24))


@cli.on(events.RawEvent)
def _log_event(bot: Bot, accid: int, event: CoreEvent) -> None:
    if event.kind == EventType.INFO:
        bot.logger.debug(event.msg)
    elif event.kind == EventType.WARNING:
        bot.logger.warning(event.msg)
    elif event.kind == EventType.ERROR:
        bot.logger.error(event.msg)
    elif event.kind == EventType.MSG_DELIVERED:
        bot.rpc.delete_messages(accid, [event.msg_id])
    elif event.kind == EventType.SECUREJOIN_INVITER_PROGRESS:
        if event.progress == 1000:
            if not bot.rpc.get_contact(accid, event.contact_id).is_bot:
                bot.logger.debug("QR scanned by contact id=%s", event.contact_id)
                chatid = bot.rpc.create_chat_by_contact_id(accid, event.contact_id)
                _send_help(bot, accid, chatid)


@cli.after(events.NewMessage)
def delete_msgs(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    """Delete messages after processing"""
    msg = event.msg
    bot.rpc.delete_messages(accid, [msg.id])
    bot.logger.debug(f"[chat={msg.chat_id}] Deleted message={msg.id}")


@cli.on(events.NewMessage(is_info=False))
def _web2pdf_filter(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    if bot.has_command(event.command):
        return
    msg = event.msg
    chat = bot.rpc.get_basic_chat_info(accid, msg.chat_id)
    match = re.search(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|"
        r"(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        msg.text,
    )
    if match:
        url = match.group()
    elif msg.text and chat.chat_type == ChatType.SINGLE:
        url = msg.text
    else:
        return
    with NamedTemporaryFile(suffix=".pdf") as file:
        try:
            pdfkit.from_url(url, file.name)
            reply = MsgData(file=file.name, quoted_message_id=msg.id)
            bot.rpc.send_msg(accid, msg.chat_id, reply)
        except Exception as ex:  # noqa: W0718
            bot.logger.exception(ex)
            text = "Failed to retrieve web site, is the URL correct?"
            reply = MsgData(text=text, quoted_message_id=msg.id)
            bot.rpc.send_msg(accid, msg.chat_id, reply)


@cli.on(events.NewMessage(command="/help"))
def _help(bot: Bot, accid: int, event: NewMsgEvent) -> None:
    _send_help(bot, accid, event.msg.chat_id)


def _send_help(bot: Bot, accid: int, chatid: int) -> None:
    text = (
        "I'm a bot, I allow to retrieve HTML pages as PDF."
        " Just send me any link to a website you would like to save as PDF."
    )
    bot.rpc.send_msg(accid, chatid, MsgData(text=text))
