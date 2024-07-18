import os
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext


# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('API_KEY')


# Функция для получения живых матчей
def get_live_matches() -> list[dict]:
    try:
        response = requests.get(f'http://api.steampowered.com/IDOTA2Match_570/GetLiveLeagueGames/v1?key={API_KEY}')
        response.raise_for_status()
        matches = response.json().get('result', {}).get('games', [])
        return matches
    except requests.exceptions.RequestException as e:
        print(f"Error fetching live matches: {e}")
        return []


# Функция для фильтрации матчей по типу серии
def filter_live_matches(all_matches: list[dict]) -> list[dict]:
    filtered_matches = [match for match in all_matches if match.get('series_type', 0) > 0]
    return filtered_matches


# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    response_message = '''Привет, я бот, который предоставит тебе информацию о лайв играх Dota2 популярных лиг.
    Для того, чтобы получить информацию о возможностях бота, введи команду /help'''
    update.message.reply_text(response_message)


# Функция для обработки команды /help
def help(update: Update, context: CallbackContext) -> None:
    response_message = '''Доступные команды:
    /all_matches - Показать все текущие матчи
    /get_the_most_watched_match - Показать самый популярный матч
    /help - Показать эту помощь'''
    update.message.reply_text(response_message)


# Функция для обработки команды /get_the_most_watched_match
def get_the_most_watched_match(update: Update, context: CallbackContext) -> None:
    matches = filter_live_matches(get_live_matches())
    if not matches:
        update.message.reply_text('Нет матчей, которые могли бы быть интересны:(')
        return
    best = max(matches, key=lambda x: x['spectators'])
    update.message.reply_text( f'{best['radiant_team']['team_name']} -- {best['dire_team']['team_name']} ({best['spectators']} зрителей)')


# Функция для обработки команды /all_matches
def all_matches(update: Update, context: CallbackContext) -> None:
    all_match = get_live_matches()
    filtered_matches = filter_live_matches(all_match)
    
    if not filtered_matches:
        update.message.reply_text('Нет матчей, которые могли бы быть интересны:(')
    else:
        for match in filtered_matches:
            update.message.reply_text( f'{match['radiant_team']['team_name']} -- {match['dire_team']['team_name']} ({match['spectators']} зрителей)')


# Основная функция для запуска бота
def main():
    updater = Updater(TOKEN)
    
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("all_matches", all_matches))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("get_the_most_watched_match", get_the_most_watched_match))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
