from steam.client import SteamClient, EResult
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, ConversationHandler
from os import getenv

TOKEN = getenv("token")
USERNAME, PASSWORD, GAME = 0, 1, 2
GUARD, MAIL = 0, 1
client = SteamClient()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello,\nThis bot increases the hours played of games on Steam\\.\nType *_/help_* to learn how to use it\\.\n\n[_Source Code_](https://github.com/tingirifistik/Steam-HourBooster)\n[_Twitter_](https://twitter.com/_tingirifistik)", parse_mode='MarkdownV2')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("*_/config_* \\-\\-\\> Saves your Steam username, password, and the games you want to increase hours played\\.\n\n*_/run_* \\-\\-\\> Begins the process of increasing hours played\\.", parse_mode='MarkdownV2')
    
async def what(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I couldn't understand what you wrote.")

async def run(update: Update, context: CallbackContext) -> None:
    try:
        with open("config", "r", encoding="UTF-8") as f:
            r = f.read()
            global username, password, games
            username, password, games = r.split(":")[0], r.split(":")[1].split("\n")[0], r.split("\n")[1].split(",")
        account_login = client.login(username=username, password=password)
        if account_login == 85:
            await update.message.reply_text("Please enter your Steam Guard code.")
            return GUARD
        elif account_login == 63:
            await update.message.reply_text("Please enter the Steam Guard code sent to your email.")
            return MAIL
        elif account_login == 1:
            await update.message.reply_text("You have successfully logged in. Games are running.")
            client.games_played(games)
            client.run_forever()
        else:
            await update.message.reply_text(f"Error Code: {str(account_login)}")
            return ConversationHandler.END
    except FileNotFoundError:
        await update.message.reply_text("Save config file first!")
    
async def guard(update: Update, context: CallbackContext) -> None:
    guard_code = update.message.text
    account_login = client.login(username=username, password=password, two_factor_code=guard_code)
    if account_login == 1:
        await update.message.reply_text("You have successfully logged in. Games are running.")
        client.games_played(games)
        client.run_forever()
    else:
        await update.message.reply_text("The guard code is wrong!")
        return ConversationHandler.END

async def mail(update: Update, context: CallbackContext) -> None:
    mail_code = update.message.text
    account_login = client.login(username=username, password=password, auth_code=mail_code)
    if account_login == 1:
        await update.message.reply_text("You have successfully logged in. Games are running.")
        client.games_played(games)
        client.run_forever()
    else:
        await update.message.reply_text("The verification code is wrong!")
        return ConversationHandler.END

async def config(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Enter your Steam username..")
    return USERNAME

async def get_username(update: Update, context: CallbackContext) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Enter your Steam password..")
    return PASSWORD

async def get_password(update: Update, context: CallbackContext) -> int:
    context.user_data['password'] = update.message.text
    await update.message.reply_text("Enter the game IDs, separated by commas..")
    return GAME
    
async def get_games(update: Update, context: CallbackContext) -> int:
    context.user_data['games'] = update.message.text
    await update.message.reply_text("Your settings have been saved..")
    with open("config", "w", encoding="utf-8") as file:
        file.write(f"{context.user_data['username']}:{context.user_data['password']}\n{context.user_data['games']}")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    config_handler = ConversationHandler(
        entry_points=[CommandHandler("config", config)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            GAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_games)]
        },
        fallbacks=[]
    )
    login_handler = ConversationHandler(
        entry_points=[CommandHandler("run", run)],
        states={
            GUARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, guard)],
            MAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, mail)]
        },
        fallbacks=[]
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(config_handler)
    application.add_handler(login_handler)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, what))

    application.run_polling()


if __name__ == "__main__":
    main()
