"""Emotion profile data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EmotionProfile:
    emotion: str = "neutral"
    description: str = "No clear emotion detected."
    food_preferences: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmotionProfile":
        return cls(
            emotion=data.get("emotion", "neutral"),
            description=data.get("description", "No clear emotion detected."),
            food_preferences=list(data.get("food_preferences", [])),
        )


@dataclass(slots=True)
class EmotionInference:
    primary_emotion: str = "neutral"
    secondary_emotion: str = ""
    confidence: float = 0.0
    matched_emotions: list[str] = field(default_factory=list)

