import json
import os
from typing import Optional, Dict


class EngineeringCodeConverter:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'engineering_code.json'
            )
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"min_code": 819, "max_code": 4095}
    
    @property
    def min_code(self) -> int:
        return self.config.get("min_code", 819)
    
    @property
    def max_code(self) -> int:
        return self.config.get("max_code", 4095)
    
    def convert(self, value: float, min_eu: float, max_eu: float) -> Optional[int]:
        if value is None or min_eu is None or max_eu is None:
            return None
        if min_eu == max_eu:
            return None
        try:
            range_code = self.max_code - self.min_code
            range_eu = max_eu - min_eu
            code = self.min_code + range_code * (value - min_eu) / range_eu
            return int(round(code))
        except Exception:
            return None


_converter_instance = None

def get_converter() -> EngineeringCodeConverter:
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = EngineeringCodeConverter()
    return _converter_instance

def convert_to_engineering_code(value: float, min_eu: float, max_eu: float) -> Optional[int]:
    return get_converter().convert(value, min_eu, max_eu)