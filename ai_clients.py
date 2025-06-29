from abc import ABC, abstractmethod
from openai import OpenAI
import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)

class AIClientBase(ABC):
    """Базовый класс для AI клиентов"""
    
    @abstractmethod
    def get_completion(self, prompt: str, max_tokens: int = 50, temperature: float = 0.9) -> str:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass

class OpenAIClient(AIClientBase):
    """Клиент для OpenAI API"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=5
        )
        self.model = "gpt-4o-mini"
    
    def get_completion(self, prompt: str, max_tokens: int = 50, temperature: float = 0.9) -> str:
        try:
            logger.info(f"[OpenAI] Отправляем запрос к {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"[OpenAI] Получен ответ: '{result}'")
            return result
            
        except Exception as e:
            logger.error(f"[OpenAI] Ошибка: {type(e).__name__}: {e}")
            raise e
    
    def get_provider_name(self) -> str:
        return "OpenAI"

class DeepSeekClient(AIClientBase):
    """Клиент для DeepSeek API"""
    
    def __init__(self, api_key: str):
        # DeepSeek совместим с OpenAI API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            timeout=60.0,
            max_retries=5
        )
        self.model = "deepseek-chat"
    
    def get_completion(self, prompt: str, max_tokens: int = 50, temperature: float = 0.9) -> str:
        try:
            logger.info(f"[DeepSeek] Отправляем запрос к {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"[DeepSeek] Получен ответ: '{result}'")
            return result
            
        except Exception as e:
            logger.error(f"[DeepSeek] Ошибка: {type(e).__name__}: {e}")
            raise e
    
    def get_provider_name(self) -> str:
        return "DeepSeek"

class MultiAIClient:
    """Клиент с поддержкой множественных AI провайдеров"""
    
    def __init__(self, openai_key: Optional[str] = None, deepseek_key: str = None, provider: str = "deepseek"):
        self.clients = {}
        self.fallback_clients = []
        
        # Инициализируем DeepSeek клиент (основной)
        if deepseek_key:
            self.clients["deepseek"] = DeepSeekClient(deepseek_key)
            self.fallback_clients.append("deepseek")
        
        # Инициализируем OpenAI клиент (резервный)
        if openai_key:
            self.clients["openai"] = OpenAIClient(openai_key)
            self.fallback_clients.append("openai")
        
        self.provider = provider.lower()
        logger.info(f"[MultiAI] Инициализирован с провайдером: {self.provider}")
        logger.info(f"[MultiAI] Доступные клиенты: {list(self.clients.keys())}")
    
    def get_completion(self, prompt: str, max_tokens: int = 50, temperature: float = 0.9) -> str:
        """Получить ответ от AI с fallback логикой"""
        
        # Определяем порядок попыток
        if self.provider == "mixed":
            # Случайный выбор для разнообразия
            primary_client = random.choice(list(self.clients.keys()))
            fallback_order = [c for c in self.fallback_clients if c != primary_client]
        elif self.provider in self.clients:
            # Используем указанный провайдер как основной
            primary_client = self.provider
            fallback_order = [c for c in self.fallback_clients if c != primary_client]
        else:
            # Fallback на первый доступный
            primary_client = self.fallback_clients[0] if self.fallback_clients else None
            fallback_order = self.fallback_clients[1:] if len(self.fallback_clients) > 1 else []
        
        if not primary_client:
            logger.error("[MultiAI] Нет доступных AI клиентов!")
            return "Омлет с овощами"  # fallback блюдо
        
        # Пробуем основной клиент
        try:
            logger.info(f"[MultiAI] Используем основной клиент: {primary_client}")
            result = self.clients[primary_client].get_completion(prompt, max_tokens, temperature)
            if result and result.strip():
                return result
        except Exception as e:
            logger.warning(f"[MultiAI] Основной клиент {primary_client} не сработал: {e}")
        
        # Пробуем fallback клиенты
        for fallback_client in fallback_order:
            try:
                logger.info(f"[MultiAI] Пробуем fallback клиент: {fallback_client}")
                result = self.clients[fallback_client].get_completion(prompt, max_tokens, temperature)
                if result and result.strip():
                    logger.info(f"[MultiAI] Успешно получен ответ от {fallback_client}")
                    return result
            except Exception as e:
                logger.warning(f"[MultiAI] Fallback клиент {fallback_client} не сработал: {e}")
        
        # Если все клиенты не сработали
        logger.error("[MultiAI] Все AI клиенты не сработали!")
        return "Омлет с овощами"  # fallback блюдо
    
    def get_active_provider(self) -> str:
        """Получить информацию об активном провайдере"""
        if self.provider == "mixed":
            return f"Mixed ({', '.join(self.clients.keys())})"
        elif self.provider in self.clients:
            return self.clients[self.provider].get_provider_name()
        else:
            return "Unknown"