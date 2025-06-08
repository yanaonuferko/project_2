#!/usr/bin/env python3
"""
Система локализации для бота
"""
import json
import os
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

# Поддерживаемые языки
SUPPORTED_LANGUAGES = {
    'en': '🇺🇸 English',
    'ru': '🇷🇺 Русский'
}

DEFAULT_LANGUAGE = 'en'

class LocalizationManager:
    """Менеджер локализации для управления переводами"""
    
    def __init__(self, locales_dir: str = "locales"):
        """
        Инициализация менеджера локализации
        
        Args:
            locales_dir: Путь к директории с файлами локализации
        """
        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.user_languages: Dict[int, str] = {}  # user_id -> language_code
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Загрузка всех переводов из файлов"""
        try:
            for language_code in SUPPORTED_LANGUAGES.keys():
                file_path = self.locales_dir / f"{language_code}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[language_code] = json.load(f)
                    logger.info(f"Loaded translations for language: {language_code}")
                else:
                    logger.warning(f"Translation file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
    
    def set_user_language(self, user_id: int, language_code: str) -> bool:
        """
        Установка языка для пользователя
        
        Args:
            user_id: ID пользователя
            language_code: Код языка
            
        Returns:
            bool: True если язык установлен успешно
        """
        if language_code in SUPPORTED_LANGUAGES:
            self.user_languages[user_id] = language_code
            logger.info(f"Set language {language_code} for user {user_id}")
            return True
        return False
    
    def get_user_language(self, user_id: int) -> str:
        """
        Получение языка пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            str: Код языка пользователя или язык по умолчанию
        """
        return self.user_languages.get(user_id, DEFAULT_LANGUAGE)
    
    def get_text(self, user_id: int, key: str, **kwargs) -> str:
        """
        Получение локализованного текста для пользователя
        
        Args:
            user_id: ID пользователя
            key: Ключ перевода (может быть вложенным, например 'keyboard.confirm')
            **kwargs: Параметры для форматирования строки
            
        Returns:
            str: Локализованный текст
        """
        language = self.get_user_language(user_id)
        return self._get_translation(language, key, **kwargs)
    
    def _get_translation(self, language: str, key: str, **kwargs) -> str:
        """
        Получение перевода для указанного языка и ключа
        
        Args:
            language: Код языка
            key: Ключ перевода
            **kwargs: Параметры для форматирования
            
        Returns:
            str: Переведенный текст
        """
        try:
            # Получаем переводы для языка
            translations = self.translations.get(language, {})
            
            # Поддержка вложенных ключей (например, 'keyboard.confirm')
            keys = key.split('.')
            current = translations
            
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    # Fallback на английский, если ключ не найден
                    if language != DEFAULT_LANGUAGE:
                        return self._get_translation(DEFAULT_LANGUAGE, key, **kwargs)
                    else:
                        logger.warning(f"Translation key not found: {key}")
                        return f"[{key}]"
            
            # Форматирование строки с параметрами
            if isinstance(current, str) and kwargs:
                return current.format(**kwargs)
            
            return str(current)
            
        except Exception as e:
            logger.error(f"Error getting translation for key '{key}': {e}")
            return f"[{key}]"
    
    def get_language_keyboard_data(self) -> Dict[str, str]:
        """
        Получение данных для клавиатуры выбора языка
        
        Returns:
            Dict[str, str]: Словарь {language_code: display_name}
        """
        return SUPPORTED_LANGUAGES.copy()

# Глобальный экземпляр менеджера локализации
localization_manager = LocalizationManager()

def get_text(user_id: int, key: str, **kwargs) -> str:
    """
    Удобная функция для получения локализованного текста
    
    Args:
        user_id: ID пользователя
        key: Ключ перевода
        **kwargs: Параметры для форматирования
        
    Returns:
        str: Локализованный текст
    """
    return localization_manager.get_text(user_id, key, **kwargs)

def set_user_language(user_id: int, language_code: str) -> bool:
    """
    Установка языка пользователя
    
    Args:
        user_id: ID пользователя
        language_code: Код языка
        
    Returns:
        bool: True если успешно
    """
    return localization_manager.set_user_language(user_id, language_code)

def get_user_language(user_id: int) -> str:
    """
    Получение языка пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        str: Код языка
    """
    return localization_manager.get_user_language(user_id)

def get_supported_languages() -> Dict[str, str]:
    """
    Получение списка поддерживаемых языков
    
    Returns:
        Dict[str, str]: Словарь поддерживаемых языков
    """
    return SUPPORTED_LANGUAGES.copy()
