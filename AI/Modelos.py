from enum import Enum
from enum import Enum

class Modelos(Enum):
    DeepSeek = {
        "name": "deepseek-r1t2-chimera",
        "model": "tngtech/deepseek-r1t2-chimera:free",
        "provider": "deepseek"
    }
    GEMINI_25_FLASH = {
        "name": "gemini-2.5-flash",
        "model": "google/gemini-2.5-flash",
        "provider": "gemini"
    }
    GPT_OSS_20B = {
        "name": "gpt-oss-20b",
        "model": "openai/gpt-oss-20b:free",
        "provider": "openai"
    }

    @property
    def value(self):
        return self._value_["name"]

    @property
    def valor(self):
        return self._value_
    
    @property
    def model(self):
        return self._value_["model"]