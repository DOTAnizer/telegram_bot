from uuid import uuid4

import aiohttp
import async_timeout
from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, StringCommandHandler

import logging

import environ

from telegram.ext.dispatcher import run_async


from urllib.parse import urlencode
from urllib.request import Request, urlopen

import timeout_decorator

import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

base_url = 'http://5.153.56.86:5000'

dota_db = [
	"Dota Prase test1",
	"Dota Phrase 123123",
]

from itertools import cycle
gen_dota_db = cycle(dota_db)


ods_db = [
	"ODs Prase test1",
	"ODs Phrase 123123",
]

gen_ods_db = cycle(ods_db)

#@timeout_decorator.timeout(5, use_signals=False)
def fetch_answer(text, direction_to):
	url = base_url

	post_fields = {'msg': text}     # Set POST fields here

	try:
		request = Request(url, urlencode(post_fields).encode())
		text = json.loads(urlopen(request, timeout=10).read().decode()).get(direction_to)
	except:
		pass
	return text

from requests_futures.sessions import FuturesSession

session = FuturesSession(max_workers=10)

def fetch_answer_async(text, direction_to, send_notification = None, hard_cutoff = None):
	url = base_url
	#
	post_fields = {'msg': text}  # Set POST fields here
	result = session.post(url=url, data=post_fields)
	count = 0
	while count < 10:
		if (hard_cutoff is not None) and (count > hard_cutoff):
			if direction_to == "dota":
				text = next(gen_dota_db)
			if direction_to == "ods":
				text = next(gen_ods_db)
			break
		if result._state == 'FINISHED':
			text = json.loads(result.result().content).get(direction_to)
			break
		else:
			if send_notification:
				send_notification()

		time.sleep(0.5)
		count = count + 0.5
	return text

# async def fetch(session, url, data):
# 	async with async_timeout.timeout(10):
# 		async with session.post(url, data=data) as response:
# 			return await response.text()
#
#
# async def fetch_answer_async(text, direction_to):
# 	async with aiohttp.ClientSession() as session:
# 		url = base_url
#
# 		post_fields = {'msg': text}  # Set POST fields here
#
# 		try:
# 			json = await fetch(session, url=url, data=data)
#
# 			text = json.loads(json).get(direction_to)
# 		except:
# 			pass
# 		return text

def detect_command(text):
	type = None
	string = None
	# /dota 123"
	# /dota@ods_deeptest_bot
	if text.startswith("/dota") or text.startswith("/dota%s" % bot_name):
		type = "dota"
		string = text.replace("/dota%s" % bot_name, '').replace("/dota", '')

	if text.startswith("/ods") or text.startswith("/ods%s" % bot_name):
		type = "ods"
		string = text.replace("/ods%s" % bot_name, '').replace("/ods", '')

	return {"type": type, "text": string}

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def help(bot, update):
	update.message.reply_text('Help!')

def dota(bot, update):
	#update.message.reply_text('Dota!')

	chat_id = update.message.chat_id

	def send_notification():
		bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

	command = detect_command(update.message.text)
	bot.send_message(chat_id=update.message.chat_id, text=answer(command.get("text"), type=command.get("type"), send_notification=send_notification))

def ods(bot, update):

	chat_id = update.message.chat_id

	def send_notification():
		bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

	command = detect_command(update.message.text)
	bot.send_message(chat_id=update.message.chat_id, text=answer(command.get("text"), type=command.get("type"), send_notification=send_notification))

import time

# Defaults
bot_name = "@ods_deeptest_bot"

def answer(text, type = "dota", send_notification = None, hard_cutoff = None):
	new_text = text
	if not text.strip():
		return "Введите текст в формате: `%s и затем через пробел текст для стилизации`" % bot_name
	try:
		#new_text = "Fake ods: %s" % ''.join(reversed(text))
		new_text = fetch_answer_async(text, type, send_notification=send_notification, hard_cutoff=hard_cutoff)
	except timeout_decorator.timeout_decorator.TimeoutError:
		new_text = "Произошла ошибка, что-то пошло не так"
	return new_text

@run_async
def echo(bot, update, chat_data = None):
	#new_message = "Fake: %s" % update.message.text
	#time.sleep(30)
	chat_id = update.message.chat_id

	def send_notification():
		bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
	if update.message.text.startswith(bot_name):
		bot.send_message(chat_id=chat_id, text=answer(update.message.text, send_notification=send_notification))
	else:
		if update.message.chat.type == "group":
			# Inline conversation
			pass
		if update.message.chat.type == "private":
			# Message sent to bot in direct
			update.message.reply_text(answer(update.message.text, send_notification=send_notification))


def error(bot, update, error):
	logging.warning('Update "%s" caused error "%s"', update, error)


# Выводим примеры
ods_title_start = "Примерчики из OpenDataScience"
ods_description_start = "Отправит в чат фразу из ODS"

dota_title_start = "Приемр из Дотки"
dota_description_start = "Отправит в чат фразу из дотки"


# Когда пользователь начал вводить
ods_id = uuid4()
ods_title = "ODS"
ods_description = "Сделай мне аля OpenDataScience"
ods_thumb = "https://www.dropbox.com/s/o2bkq6l9psqxyeu/1741547_1.jpg?dl=1"

dota_id = uuid4()
dota_title = "Dota"
dota_description = "Дотифицируй это"
dota_thumb="https://www.dropbox.com/s/5kf7behafeqzu4f/CBQg2NA.jpg?dl=1"

# Set by BotFather by /setcommands
commands_list = """
help - Справка
dota - dota_description sdf
ods - ods_description sdf
"""

@run_async
def inlinequery(bot, update):
	"""Handle the inline query."""

	query = update.inline_query.query
	if update.message:
		chat_id = update.message.chat_id
		bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
	
	if query.strip():
		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				title=ods_title,
				description=ods_description,
				input_message_content=InputTextMessageContent(
					answer(query, type="ods", hard_cutoff = 1), parse_mode=ParseMode.MARKDOWN),
				thumb_url=ods_thumb,
			),
			InlineQueryResultArticle(
				id=uuid4(),
				title=dota_title,
				description=dota_description,
				input_message_content=InputTextMessageContent(
					answer(query, type="dota", hard_cutoff = 1), parse_mode=ParseMode.MARKDOWN),
				thumb_url=dota_thumb,
			),
	
		]
	else:
		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				title=ods_title_start,
				description=ods_description_start,
				input_message_content=InputTextMessageContent(
					next(gen_ods_db), parse_mode=ParseMode.MARKDOWN),
				thumb_url=ods_thumb,
			),
			InlineQueryResultArticle(
				id=uuid4(),
				title=dota_title_start,
				description=dota_description_start,
				input_message_content=InputTextMessageContent(
					next(gen_dota_db), parse_mode=ParseMode.MARKDOWN),
				thumb_url=dota_thumb,
			),
	
		]
	update.inline_query.answer(results
	                           #, is_personal=True
	                           , cache_time=0
	                           , switch_pm_text="Потестить в директе у бота"
	                           , switch_pm_parameter="test"
	)


def main():
	env = environ.Env(BOT_TOKEN=(str, ""), )
	updater = Updater(env("BOT_TOKEN"), workers=10)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("dota", dota))
	dp.add_handler(CommandHandler("ods", ods))
	#dp.add_handler(StringCommandHandler("dota", dota))
	#dp.add_handler(StringCommandHandler("ods", ods))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler(Filters.text | Filters.entity("MENTION"), echo, pass_chat_data=True))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(InlineQueryHandler(inlinequery))

	# log all errors
	dp.add_error_handler(error)


	if not "state" == "async":
		# Start the Bot
		updater.start_polling()

		# Run the bot until you press Ctrl-C or the process receives SIGINT,
		# SIGTERM or SIGABRT. This should be used most of the time, since
		# start_polling() is non-blocking and will stop the bot gracefully.
		updater.idle()
	else:
		loop = aiohttp.asyncio.new_event_loop()
		aiohttp.asyncio.set_event_loop(loop)
		loop.run_until_complete(updater)


if __name__ == '__main__':
	main()
