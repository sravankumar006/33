import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict

from openai import OpenAI
from app.core.config import settings


class InsightGeneratorError(Exception):
    pass


class InsightProvider(ABC):
    @abstractmethod
    def generate_insights(self, phone_data: Dict[str, Any]) -> Dict[str, str]:
        raise NotImplementedError


class OpenAIInsightProvider(InsightProvider):
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo'):
        if not api_key:
            raise InsightGeneratorError('OPENAI_API_KEY is not set.')

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_insights(self, phone_data: Dict[str, Any]) -> Dict[str, str]:
        prompt = self._build_prompt(phone_data)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'You are a concise and honest phone expert. Generate short summaries '
                            'for battery, performance, display, camera, software, and a brutally honest verdict. '
                            'Use plain English, avoid marketing language, and be direct about trade-offs.'
                        ),
                    },
                    {'role': 'user', 'content': prompt},
                ],
                temperature=0.4,
                max_tokens=600,
            )
        except Exception as exc:
            raise InsightGeneratorError(f'AI generation failed: {exc}') from exc

        try:
            ai_text = response.choices[0].message.content
        except Exception as exc:
            raise InsightGeneratorError('Failed to parse AI response.') from exc

        return self._parse_response(ai_text)

    def _build_prompt(self, phone_data: Dict[str, Any]) -> str:
        return (
            'Create a plain-English JSON object using only the keys: '
            'battery_summary, performance_summary, display_summary, camera_summary, '
            'software_summary, honest_verdict. Be concise, useful, and honest. '
            'Avoid marketing language. Base the output on these specs:\n\n'
            f'Battery: {phone_data.get("battery_mah")} mAh\n'
            f'Charging: {phone_data.get("charging_watts")}W\n'
            f'Processor: {phone_data.get("processor")}\n'
            f'RAM: {phone_data.get("ram_gb")} GB\n'
            f'Storage: {phone_data.get("storage_gb")} GB\n'
            f'Display: {phone_data.get("display_size")} {phone_data.get("display_type")}\n'
            f'Refresh rate: {phone_data.get("refresh_rate_hz")} Hz\n'
            f'Brightness: {phone_data.get("peak_brightness_nits")} nits\n'
            f'Camera: {phone_data.get("camera_main_mp")} MP\n'
            f'Software updates: {phone_data.get("os_updates_years")} years\n'
            f'Security updates: {phone_data.get("security_updates_years")} years\n'
            f'Launch price: {phone_data.get("launch_price")}\n'
            f'Current average price: {phone_data.get("current_avg_price")}\n\n'
            'Output valid JSON only. Do not wrap the JSON in markdown code fences.'
        )

    def _parse_response(self, raw: str) -> Dict[str, str]:
        cleaned = re.sub(r'```(?:json)?\n?', '', raw, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r'```$', '', cleaned, flags=re.IGNORECASE).strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            # Attempt to extract JSON object from the response if extra text is present.
            match = re.search(r'\{.*\}', cleaned, flags=re.DOTALL)
            if not match:
                raise InsightGeneratorError('AI returned invalid JSON.') from exc
            parsed = json.loads(match.group(0))

        required_keys = {
            'battery_summary',
            'performance_summary',
            'display_summary',
            'camera_summary',
            'software_summary',
            'honest_verdict',
        }
        if not required_keys.issubset(parsed.keys()):
            raise InsightGeneratorError('AI response is missing expected keys.')

        return {key: str(parsed[key]).strip() for key in required_keys}


class InsightGenerator:
    def __init__(self, provider: InsightProvider):
        self.provider = provider

    @classmethod
    def from_environment(cls) -> 'InsightGenerator':
        api_key = settings.openai_api_key or os.getenv('OPENAI_API_KEY', '')
        return cls(OpenAIInsightProvider(api_key=api_key))

    def generate(self, phone_data: Dict[str, Any]) -> Dict[str, str]:
        return self.provider.generate_insights(phone_data)
