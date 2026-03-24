"""Basic command handlers for the bot."""

import logging
from backend_client import BackendClient

logger = logging.getLogger(__name__)

# Создаём клиент для бэкенда
try:
    backend = BackendClient()
    logger.info("Backend client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize backend client: {e}")
    backend = None


def start_handler() -> str:
    """Handle /start command."""
    return (
        "🤖 *Привет! Я бот для отслеживания прогресса в лабораторных работах*\n\n"
        "Доступные команды:\n"
        "• `/start` — показать это приветствие\n"
        "• `/help` — список всех команд\n"
        "• `/health` — проверить статус бэкенда\n"
        "• `/labs` — список лабораторных работ\n"
        "• `/scores <lab>` — результаты по лабораторной\n\n"
        "Пример использования:\n"
        "`/scores lab-04` — показать результаты 4-й лабораторной\n\n"
        "Всё готово к работе! 🚀"
    )


def help_handler() -> str:
    """Handle /help command."""
    return (
        "📋 *Список доступных команд:*\n\n"
        "*/start* — показать приветствие и список команд\n"
        "*/help* — показать это сообщение\n"
        "*/health* — проверить состояние бэкенда\n"
        "*/labs* — показать все доступные лабораторные работы\n"
        "*/scores <lab>* — показать результаты по лабораторной\n\n"
        "*Примеры:*\n"
        "`/scores lab-01` — результаты 1-й лабораторной\n"
        "`/scores lab-04` — результаты 4-й лабораторной\n\n"
        "*Совет:* Используйте `/labs`, чтобы увидеть все доступные лабораторные"
    )


def health_handler() -> str:
    """Handle /health command."""
    if backend is None:
        return (
            "❌ *Бэкенд недоступен*\n\n"
            "Не удалось инициализировать клиент бэкенда.\n"
            "Проверьте:\n"
            "• Настроен ли `LMS_API_KEY` в `.env.bot.secret`\n"
            "• Правильно ли указан `LMS_API_URL`\n"
            "• Запущены ли Docker-контейнеры с бэкендом"
        )
    
    try:
        is_healthy, result = backend.check_health()
        
        if is_healthy:
            return (
                f"✅ *Бэкенд работает!*\n\n"
                f"📊 Статус: здоров\n"
                f"📦 Загружено элементов: {result}\n"
                f"🔗 URL: {backend.base_url}\n\n"
                f"Всё готово к работе!"
            )
        else:
            return (
                f"⚠️ *Бэкенд работает с проблемами*\n\n"
                f"📊 Статус: нестабильный\n"
                f"🔗 URL: {backend.base_url}\n"
                f"❌ Ошибка: {result}\n\n"
                f"Некоторые данные могут быть недоступны."
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            f"❌ *Бэкенд недоступен*\n\n"
            f"Ошибка: {str(e)}\n\n"
            f"Проверьте:\n"
            f"• Запущены ли контейнеры: `docker ps`\n"
            f"• Доступен ли бэкенд по адресу: {backend.base_url}\n"
            f"• Правильно ли настроен `LMS_API_KEY`"
        )


def labs_handler() -> str:
    """Handle /labs command."""
    if backend is None:
        return (
            "❌ *Ошибка*\n\n"
            "Клиент бэкенда не инициализирован.\n"
            "Проверьте настройки в `.env.bot.secret`"
        )
    
    try:
        labs_list = backend.get_labs()
        
        if not labs_list:
            return (
                "⚠️ *Лабораторные работы не найдены*\n\n"
                "Возможные причины:\n"
                "• Данные ещё не загружены в бэкенд\n"
                "• Запустите ETL-синхронизацию:\n"
                "  `curl -X POST http://localhost:42002/pipeline/sync \\\n"
                "   -H \"Authorization: Bearer YOUR_LMS_API_KEY\" \\\n"
                "   -H \"Content-Type: application/json\" -d '{}'`\n"
                "• Проверьте, что бэкенд работает и содержит данные"
            )
        
        # Форматируем список лабораторных
        message = "📚 *Доступные лабораторные работы:*\n\n"
        
        for lab in labs_list:
            lab_id = lab.get("id", "unknown")
            lab_name = lab.get("name", "Без названия")
            message += f"📘 *{lab_id}* — {lab_name}\n"
        
        message += "\n💡 *Чтобы посмотреть результаты:*\n"
        message += "`/scores lab-01` — замените lab-01 на нужную лабораторную\n\n"
        message += "Пример: `/scores lab-04`"
        
        return message
        
    except Exception as e:
        logger.error(f"Failed to get labs: {e}")
        return (
            f"❌ *Ошибка при загрузке лабораторных*\n\n"
            f"Детали: {str(e)}\n\n"
            f"Проверьте:\n"
            f"• Доступность бэкенда: `/health`\n"
            f"• Логи бэкенда: `docker compose logs backend`"
        )


def scores_handler(lab_name: str = None) -> str:
    """Handle /scores command."""
    if not lab_name:
        return (
            "⚠️ *Не указана лабораторная работа*\n\n"
            "Использование: `/scores <название_лабораторной>`\n\n"
            "Примеры:\n"
            "• `/scores lab-01` — результаты 1-й лабораторной\n"
            "• `/scores lab-04` — результаты 4-й лабораторной\n\n"
            "💡 Посмотрите доступные лабораторные через `/labs`"
        )
    
    if backend is None:
        return (
            "❌ *Ошибка*\n\n"
            "Клиент бэкенда не инициализирован.\n"
            "Проверьте настройки в `.env.bot.secret`"
        )
    
    try:
        pass_rates = backend.get_pass_rates(lab_name)
        
        if not pass_rates:
            return (
                f"⚠️ *Нет данных для лабораторной {lab_name}*\n\n"
                f"Проверьте:\n"
                f"• Существует ли лабораторная с таким названием\n"
                f"• Загружены ли данные через ETL-синхронизацию\n\n"
                f"💡 Посмотрите доступные лабораторные: `/labs`"
            )
        
        # Форматируем результаты
        lab_display_name = pass_rates.get("lab_name", lab_name)
        message = f"📈 *Результаты сдачи: {lab_display_name}*\n\n"
        
        tasks = pass_rates.get("tasks", [])
        if not tasks:
            message += "Нет данных по заданиям для этой лабораторной.\n"
            return message
        
        for task in tasks:
            task_name = task.get("name", "Без названия")
            pass_rate = task.get("pass_rate", 0)
            attempts = task.get("attempts", 0)
            
            # Создаём визуальную шкалу (10 символов)
            bar_length = int(pass_rate / 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            
            # Определяем цветовую индикацию
            if pass_rate >= 80:
                status = "✅"
            elif pass_rate >= 60:
                status = "⚠️"
            else:
                status = "❌"
            
            message += f"{status} *{task_name}*\n"
            message += f"   `{bar}` {pass_rate:.1f}% ({attempts} попыток)\n\n"
        
        # Добавляем полезную информацию
        if tasks:
            avg_rate = sum(t.get("pass_rate", 0) for t in tasks) / len(tasks)
            message += f"📊 *Средний процент сдачи:* {avg_rate:.1f}%\n"
        message += f"📝 *Всего заданий:* {len(tasks)}"
        
        return message
        
    except Exception as e:
        logger.error(f"Failed to get scores for {lab_name}: {e}")
        error_msg = str(e).lower()
        
        # Пытаемся дать более конкретную ошибку
        if "404" in error_msg:
            return (
                f"❌ *Лабораторная {lab_name} не найдена*\n\n"
                f"Проверьте правильность названия.\n"
                f"💡 Используйте `/labs` чтобы увидеть доступные лабораторные"
            )
        elif "connection" in error_msg or "timeout" in error_msg:
            return (
                f"❌ *Бэкенд недоступен*\n\n"
                f"Ошибка: {str(e)}\n\n"
                f"Проверьте:\n"
                f"• Запущены ли Docker-контейнеры: `docker ps`\n"
                f"• Статус бэкенда: `/health`"
            )
        else:
            return (
                f"❌ *Ошибка при загрузке результатов*\n\n"
                f"Детали: {str(e)}\n\n"
                f"Проверьте логи: `docker compose logs backend`"
            )


def unknown_handler(command: str) -> str:
    """Handle unknown commands."""
    return (
        f"❓ *Неизвестная команда: {command}*\n\n"
        f"Доступные команды:\n"
        f"• `/start` — приветствие\n"
        f"• `/help` — список команд\n"
        f"• `/health` — статус бэкенда\n"
        f"• `/labs` — список лабораторных\n"
        f"• `/scores <lab>` — результаты по лабораторной\n\n"
        f"Введите `/help` для подробной информации"
    )