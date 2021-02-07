global_toke = '1659428553:AAGgA--dj07jMkXTFogcbfr5VEnXAbBVkbk'

import logging
import numpy as np
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

CHOOSING_1, TYPING_REPLY_1, TYPING_CHOICE_1 = range(3)

def nominate(update: Update, context: CallbackContext) -> None:
    reply_text = "KekScribe at your service, Sire. Whomst doth thou nominate to this most glorious competition?"

    update.message.reply_text(reply_text)
    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text in context.user_data.keys():
        reply_text = (
            f'I have record of Sir {text}! He has amassed a tidy sum of {context.user_data[text]} Keks'
        )
    else:
        reply_text = f'Sir {text}? Yes, I shall make note of him in our records most promptly!'
        context.user_data[text] = 0

    update.message.reply_text(reply_text)
    return ConversationHandler.END


def done(update: Update, context: CallbackContext) -> None:
    return ConversationHandler.END

def dub(update: Update, context: CallbackContext) -> None:
    if context.user_data:
        reply_text = (
        "I see you\'d like to alter a title with the Ministry of Records."
        +"\nPlease select a name from our records to proceed.")
        reply_keyboard = keyboard(context.user_data)
    else:
        reply_text = (
        "Unfortunately, we have no records to adjust, yet, Sire.")
        reply_keyboard = [['Nevermind...']]

    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text(reply_text, reply_markup=markup)
    return CHOOSING_1

def name_change(update: Update, context: CallbackContext) -> None:
    selection = update.message.text
    context.user_data['choice'] = selection

    reply_text = f'Certainly. What shall Sir {selection}\'s new Title be?'
    update.message.reply_text(reply_text)
    return TYPING_REPLY_1

def received_information(update: Update, context: CallbackContext) -> None:
    new_name = update.message.text
    old_name = context.user_data['choice']
    context.user_data[new_name] = context.user_data.pop(old_name,0)
    context.user_data.pop('choice',0)
    reply_text = ("By the divine powers vested in me, "+f"\nI dub thee, {new_name}.")
    update.message.reply_text(reply_text)
    return ConversationHandler.END


def no_change(update: Update, context: CallbackContext) -> None:
    reply_text = 'Until next time, Sire.'
    update.message.reply_text(reply_text)
    return ConversationHandler.END


def keyboard(ledger):
    name_list = list(ledger.keys())
    keyboard_keys = []
    if len(name_list) > 1:
        for index_e,name_e in enumerate(name_list[::2]):
            keyboard_keys.append([name_e])
            for index_o,name_o in enumerate(name_list[1::2]):
                if index_o < index_e:
                    pass
                else:
                    keyboard_keys[index_e].append(name_o)
    else:
        keyboard_keys = [name_list]
    keyboard_keys.append(['Nevermind...'])
    return keyboard_keys

def ledger_to_str(ledger):

    return "\n".join(ledger).join(['\n', '\n'])

def kekledger(update: Update, context: CallbackContext) -> None:
    if context.user_data:
        context.user_data.pop('choice',0)
        result = context.user_data.items() 
        data = list(result) 
        sorted_data = sorted(data,key= lambda k: k[1], reverse=True)

        ledger = []

        for index,challenger in enumerate(sorted_data):
            if index == 0:
                ledger.append(f'King of Kek, {challenger[0]} - {challenger[1]}')
            else:
                ledger.append(f'{challenger[0]} - {challenger[1]}')

        update.message.reply_text(
            f"Ehm, in accordance with the official records: {ledger_to_str(ledger)}"
        )
    else:
        update.message.reply_text(
            f"Unfortunately, the records are currently empty."
        )


def upkek(update: Update, context: CallbackContext) -> None:
    if context.args == []:
        update.message.reply_text(f"You must provide me a name to reference the records!")
        
    text = context.args[0]

    if text in context.user_data.keys(): 
        context.user_data[text] += 1
        context.bot.sendAnimation(chat_id=update.effective_chat.id,animation='https://media.tenor.com/images/ec1609f614c8f2698a1566f8f1f192ea/tenor.gif')
        update.message.reply_text(f"Hehe good one Sir {text}, that brings you to {context.user_data[text]} keks.")

    else: 
        update.message.reply_text(f"Unfortunately you have yet to register Sir {text}. Nominate him henceforth expeditiously!")
    
def scribe(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
    "\n*Hoofs clack and a buckling horse neighs as a shadowy figure approaches*" 
    +"\nYou beckoned, sire?" 
    +"\nAs a reminder, I am trained to respond to the following calls:"
    +"\n/scribe - To beckon me once more"
    +"\n/nominate - To nominate a fellow for addition to the Scrolls of Kek"
    +"\n/upkek - To grant one Kek to the fellow of your choice"
    +"\n/kekledger - To hear a recitation of the Rankings of Kek"
    +"\n/dub - To adjust your noble Title"    
    )

    
def main():
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='dubersationbot')
    updater = Updater(global_toke, persistence=pp)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    nominate_handler = ConversationHandler(
        entry_points=[CommandHandler('nominate', nominate, pass_args=True)],
        states={
            CHOOSING: [
                MessageHandler( Filters.text & ~(Filters.command | Filters.regex('^Done$')),regular_choice
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        name="my_dubersation",
        persistent=True,
        per_chat=True
    )
    dp.add_handler(nominate_handler)

    dub_handler = ConversationHandler(
        entry_points=[CommandHandler('dub', dub)],
        states={
            CHOOSING_1: [
                MessageHandler(
                    ~ Filters.regex('^Nevermind...$'), name_change
                ),
                MessageHandler(Filters.regex('^Nevermind...$'), no_change),
            ],
            TYPING_REPLY_1: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        name="dub",
        persistent=True,
        per_chat=True
    )

    dp.add_handler(dub_handler)

    ledger_handler = CommandHandler('kekledger', kekledger)
    dp.add_handler(ledger_handler)

    upkek_handler = CommandHandler('upkek', upkek, pass_args=True)
    dp.add_handler(upkek_handler)

    scribe_handler = CommandHandler('scribe', scribe, pass_args=True)
    dp.add_handler(scribe_handler)

    # scribe the Bot
    updater.scribe_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # scribe_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()