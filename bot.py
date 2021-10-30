import logging
import os
import sys
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

#Configurar Logging
logging.basicConfig(
    level = logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s."
)
logger = logging.getLogger()

#Solicitar TOKEN
TOKEN = os.getenv("TOKEN")
mode = os.getenv("MODE")

if mode == "dev":
    #Acceso local (desarrollo)
    def run (updater):
            updater.start_polling()
            print("BOT CARGADO")
            updater.idle() #Permite finalizar el bot con Ctrl + c

elif mode == "prod":
    #Acceso a HEROKU (producción)
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        #Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0", port="PORT", url_path=TOKEN)
        updater.bot.set_webhook(f"https://javierplex.herokuapp.com/1902256101:AAE6Q1aA4W_YJtC6Yt6Im0WuXICmmnc1bcE")

else:
    logger.info("No se especificó el MODE.")
    sys.exit()

eventos = "Las peticiones son: "

def start(update, context):
    bot = context.bot
    chatId = update.message.chat_id
    #updateMsg = getattr(update, "message", None)
    userName = update.effective_user["first_name"]
    lastName = update.effective_user["last_name"]

    logger.info(f'El usuario {userName} {lastName} ha ingresado al grupo')

    bot.sendMessage(
        chat_id = chatId,
        parse_mode = "HTML",
        text = f'<b>Bienvenid@, {userName}</b> \n ¡Disfruta de todos los lanzamientos en JavierPlex!\n Puedes usarme para realizar peticiones de películas y series realizando lo siguiente: \n -Escribe /peticion y a continuación el nombre de la película, serie o documental que quieras solicitar'
    )

def getBotInfo(update, context):
    bot = context.bot
    chatId = update.message.chat_id
    userName = update.effective_user["first_name"]
    lastName = update.effective_user["last_name"]
    logger.info(f'El usuario {userName} {lastName} ha solicitado información sobre el bot')
    bot.sendMessage(
        chat_id = chatId,
        parse_mode = "HTML",
        text = f'Hola soy un bot creado para el canal de <b>JavierPlex</b>'
    )

def peticion(update, context):
    global eventos
    bot = context.bot
    chatId = update.message.chat_id
    userName = update.effective_user["first_name"]
    lastName = update.effective_user["last_name"]
    userId = update.effective_user["id"]
    args = context.args

    if not userisAdmin(chatId, userId, bot) == True:
        if len(args) == 0:
            logger.info(f'El usuario {userName} no ha ingresado argumentos.')
            bot.sendMessage(
                chat_id = chatId,
                text = f'{userName} por favor, escriba el texto después del comando para realizar una petición.'
            )
        else:
            evento = ' '.join(args)
            eventos = eventos + '\n>>' + evento

            logger.info(f'El usuario {userName} {lastName} ha realizado una peticion: {evento}')

            bot.sendMessage(
                chat_id = chatId,
                text = f'¡Gracias {userName}! Tu petición se ha realizado correctamente. Te llegará una notificación en cuanto esté disponible.'
            )

            bot.sendMessage(
                chat_id = 1578815450,
                text = f'El usuario {userName} {lastName} ha realizado la siguiente petición: {evento}'
            )
    else:
        logger.info(f'{userName} ha intentado agregar una petición pero no tiene permisos.')
        bot.sendMessage(
            chat_id = chatId,
            text = f'{userName}, no tienes permisos para agregar una petición.'
        )

def listaPeticiones(update, context):
    chatId = update.message.chat_id
    userName = update.effective_user['first_name']
    bot = context.bot

    logger.info(f'El ususario {userName} ha solicitado las peticiones.')
    bot.sendMessage(
        chat_id = chatId,
        text = eventos
    )

def echo(update, context):
    bot = context.bot
    updateMsg = getattr(update, 'message', None)
    messageId = updateMsg.message_id #Obtener el id del mensaje
    chatId = update.message.chat_id
    userName = update.effective_user['first_name']
    text = update.message.text #Obtener el texto que envió el usuario al chat
    logger.info(f'El usuario {userName} ha enviado un nuevo mensaje al grupo {chatId}')

    badWord = 'baboso'

    if badWord in text:
        deleteMessage(bot, chatId, messageId, userName)
        bot.sendMessage(
            chat_id = chatId,
            text = f'El mensaje de {userName} ha sido eliminado porque tenía malas palabras'
        )
    elif 'bot' in text and 'hola' in text:
        bot.sendMessage(
            chat_id = chatId,
            text = f'Hola, {userName} ¡Gracias por saludar!'
        )
#FIXME
def userisAdmin(chatId, userId, bot):
    try:
        groupAdmins = bot.get_chat_administrators(chatId)
        for admin in groupAdmins:
            if admin.user.id == userId:
                isAdmin = True
            else:
                isAdmin = False
        
        return isAdmin
    except Exception as e:
        print(e)

#FIXME
def deleteMessage(bot, chatId, messageId, userName):
    try:
        bot.delete_message(chatId, messageId)
        logger.info(f'El mensaje de {userName} se eliminó correctamente porque tenía malas palabras')
    except Exception as e:
        print(e)

if __name__ == "__main__":
    #Obtenemos información de nuestro bot
    my_bot = telegram.Bot(token = TOKEN) 
    print(my_bot.getMe())

    #Enlazamos nuestro updater con nuestro bot
    updater = Updater(my_bot.token, use_context=True)

    #Creamos un despachador
    dp = updater.dispatcher

    #Creamos los controladores
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("botInfo", getBotInfo))
    dp.add_handler(CommandHandler("peticion", peticion, pass_args = True))
    dp.add_handler(CommandHandler("listapeticiones", listaPeticiones))
    dp.add_handler(MessageHandler(Filters.text, echo)) #Va a estar leyendo los mensajes el bot

    run(updater)