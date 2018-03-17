from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent, ParseMode, InlineQueryResultGif
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler

import logging

from telegram.utils.helpers import escape_markdown

import environ

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def help(bot, update):
	update.message.reply_text('Help!')


def echo(bot, update):
	new_message = "Fake: %s" % update.message.text
	if update.message.chat.type == "group":
		# Inline conversation
		pass
	if update.message.chat.type == "private":
		# Message sent to bot in direct
		update.message.reply_text(new_message)


def error(bot, update, error):
	logging.warning('Update "%s" caused error "%s"', update, error)


def inlinequery(bot, update):
	"""Handle the inline query."""
	query = update.inline_query.query

	query1 = "Deep fake text 1"
	query2 = "Deep fake text 2"
	query3 = "Deep fake text 3"

	size = 20

	results = [

		# InlineQueryResultGif(
		# 	id=uuid4(),
		# 	#thumb_url = "https://thumbs.gfycat.com/BlaringUnrealisticHorsechestnutleafminer-size_restricted.gif",
		# 	gif_url = "https://thumbs.gfycat.com/BlaringUnrealisticHorsechestnutleafminer-size_restricted.gif",
		# 	input_message_content=InputTextMessageContent("Test")
		# ),
		InlineQueryResultArticle(
			id=uuid4(),
			title=query1,
			input_message_content=InputTextMessageContent(
				query1)),
		InlineQueryResultArticle(
			id=uuid4(),
			thumb_heigth = size,
			thumb_width = size,
			thumb_url = "https://www.dropbox.com/s/mvnurxd1imk13bq/dota-2-logo-C88DABB066-seeklogo.com.png?dl=1",
			title=query2,
			input_message_content=InputTextMessageContent(
				"*{}*".format(escape_markdown(query2)),
				parse_mode=ParseMode.MARKDOWN)),
		InlineQueryResultArticle(
			id=uuid4(),
			title=query3,
			input_message_content=InputTextMessageContent(
				"_{}_".format(escape_markdown(query3)),
				parse_mode=ParseMode.MARKDOWN))]

	update.inline_query.answer(results)


def main():
	env = environ.Env(BOT_TOKEN=(str, ""), )
	updater = Updater(env("BOT_TOKEN"))

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(MessageHandler(Filters.text, echo))

	# on noncommand i.e message - echo the message on Telegram
	dp.add_handler(InlineQueryHandler(inlinequery))

	# log all errors
	dp.add_error_handler(error)

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
