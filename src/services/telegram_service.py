import asyncio
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger

from src.config import settings


class TelegramService:
    """Service for sending notifications via Telegram."""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.bot = None
        self.initialized = False

    async def initialize(self):
        """Initialize the Telegram bot."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram bot token or chat ID not configured. Notifications disabled.")
            return False

        try:
            self.bot = Bot(token=self.bot_token)
            # Test the connection by getting bot info
            bot_info = await self.bot.get_me()
            logger.info(f"Telegram bot initialized: {bot_info.first_name} (@{bot_info.username})")
            self.initialized = True
            return True
        except TelegramError as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}")
            self.initialized = False
            return False
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {str(e)}")
            self.initialized = False
            return False

    async def send_message(self, message, parse_mode="HTML"):
        """
        Send a message via Telegram.
        
        Args:
            message: The message to send
            parse_mode: Message parse mode (HTML, Markdown, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            try:
                initialized = await self.initialize()
                if not initialized:
                    logger.warning("Could not send Telegram message: Bot not initialized")
                    return False
            except Exception as e:
                logger.error(f"Error initializing Telegram bot: {str(e)}")
                return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("Telegram message sent successfully")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False

    def send_message_sync(self, message, parse_mode="HTML"):
        """
        Synchronous wrapper for send_message.
        
        Args:
            message: The message to send
            parse_mode: Message parse mode (HTML, Markdown, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there's no event loop in the current thread, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(self.send_message(message, parse_mode))
        except Exception as e:
            logger.error(f"Error in send_message_sync: {str(e)}")
            return False

    async def send_job_notification(self, job_data, website_name):
        """
        Send a notification about a new job vacancy.
        
        Args:
            job_data: The job data
            website_name: The name of the website
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Format the job notification message
            message = (
                f"<b>🔔 New Job Vacancy</b>\n\n"
                f"<b>Title:</b> {job_data.get('title', 'Unknown')}\n"
                f"<b>Company:</b> {job_data.get('company', 'Unknown')}\n"
                f"<b>Location:</b> {job_data.get('location', 'Unknown')}\n"
                f"<b>Website:</b> {website_name}\n\n"
            )
            
            # Add job URL if available
            if job_data.get('url'):
                message += f"<a href='{job_data['url']}'>View Job</a>"
            
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending job notification: {str(e)}")
            return False

    def send_job_notification_sync(self, job_data, website_name):
        """
        Synchronous wrapper for send_job_notification.
        
        Args:
            job_data: The job data
            website_name: The name of the website
            
        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(self.send_job_notification(job_data, website_name))
        except Exception as e:
            logger.error(f"Error in send_job_notification_sync: {str(e)}")
            return False

    async def send_error_notification(self, error_message, website_url=None):
        """
        Send a notification about an error.
        
        Args:
            error_message: The error message
            website_url: The URL of the website (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Format the error notification message
            message = f"<b>❌ Error</b>\n\n{error_message}"
            
            if website_url:
                message += f"\n\n<b>Website:</b> {website_url}"
            
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending error notification: {str(e)}")
            return False

    def send_error_notification_sync(self, error_message, website_url=None):
        """
        Synchronous wrapper for send_error_notification.
        
        Args:
            error_message: The error message
            website_url: The URL of the website (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(self.send_error_notification(error_message, website_url))
        except Exception as e:
            logger.error(f"Error in send_error_notification_sync: {str(e)}")
            return False


# Singleton instance
telegram_service = TelegramService()