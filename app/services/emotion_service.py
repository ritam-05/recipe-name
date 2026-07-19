"""Emotion profile lookup backed by app/data/emotions.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.models.emotion import EmotionInference, EmotionProfile
from app.utils.helpers import normalize_text


class EmotionService:
    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or Path(__file__).resolve().parents[1] / "data" / "emotions.json"
        self._profiles = self._load_profiles()
        self._emotion_keywords = {
            "happy": ["happy", "joyful", "celebrat", "excited", "thrilled", "good news"],
            "sad": ["sad", "down", "low", "unhappy", "depressed", "blue"],
            "stressed": ["stress", "stressed", "pressure", "overwhelmed", "deadline", "exam", "burned out"],
            "anxious": ["anxious", "nervous", "worried", "worry", "uneasy", "panic"],
            "angry": ["angry", "mad", "irritated", "frustrated", "annoyed", "upset"],
            "bored": ["bored", "boring", "nothing to do", "stuck"],
            "romantic": ["romantic", "date", "love", "affection", "intimate"],
            "tired": ["tired", "exhausted", "drained", "sleepy", "worn out"],
            "sick": ["sick", "ill", "flu", "cold", "nausea", "recover"],
            "nostalgic": ["nostalgic", "miss my", "mom's food", "childhood", "memories", "home food"],
            "lonely": ["lonely", "alone", "isolated", "by myself"],
            "celebratory": ["promoted", "promotion", "celebrate", "celebratory", "milestone", "achievement"],
            "adventurous": ["adventurous", "explore", "try new", "curious", "different cuisine"],
            "focused": ["focused", "study", "study for", "work hard", "exam", "productivity", "concentrate"],
            "lazy": ["lazy", "don't feel like cooking", "no energy to cook", "can't be bothered", "effortless"],
            "energetic": ["energetic", "workout", "gym", "active", "motivated", "just finished a workout"],
            "guilty": ["guilty", "balance", "after indulgence", "healthy again"],
            "curious": ["curious", "interested", "want to try", "experiment"],
            "cozy": ["cozy", "warm", "snug", "comforting", "relaxing"],
            "heartbroken": ["breakup", "heartbroken", "broken heart", "split up", "lost my partner"],
        }

    def _load_profiles(self) -> list[EmotionProfile]:
        if not self.data_path.exists():
            return []

        with self.data_path.open("r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)

        return [EmotionProfile.from_dict(item) for item in payload.get("emotions", [])]

    def get_profile_by_emotion(self, emotion: str) -> EmotionProfile:
        normalized_emotion = normalize_text(emotion)
        for profile in self._profiles:
            if profile.emotion == normalized_emotion:
                return profile
        return EmotionProfile(emotion=normalized_emotion or "neutral")

    def infer_emotions(self, query_text: str) -> EmotionInference:
        normalized_query = normalize_text(query_text)
        if not normalized_query:
            return EmotionInference()

        scores: dict[str, float] = {}

        for profile in self._profiles:
            score = 0.0
            emotion_name = profile.emotion.lower()
            if re.search(rf"\b{re.escape(emotion_name)}\b", normalized_query):
                score += 5.0

            for keyword in self._emotion_keywords.get(emotion_name, []):
                if keyword in normalized_query:
                    score += 2.0 if " " in keyword else 1.0

            for preference in profile.food_preferences:
                if preference.lower() in normalized_query:
                    score += 0.5

            if score:
                scores[emotion_name] = score

        if not scores:
            return EmotionInference()

        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        primary_emotion, primary_score = sorted_scores[0]
        secondary_emotion = ""
        secondary_score = 0.0
        if len(sorted_scores) > 1 and sorted_scores[1][1] >= primary_score * 0.55:
            secondary_emotion, secondary_score = sorted_scores[1]

        confidence = min(0.99, 0.45 + (primary_score * 0.09) + (secondary_score * 0.04))
        matched_emotions = [primary_emotion]
        if secondary_emotion:
            matched_emotions.append(secondary_emotion)

        return EmotionInference(
            primary_emotion=primary_emotion,
            secondary_emotion=secondary_emotion,
            confidence=round(confidence, 2),
            matched_emotions=matched_emotions,
        )

    def match_emotion(self, query_text: str) -> EmotionProfile:
        inference = self.infer_emotions(query_text)
        return self.get_profile_by_emotion(inference.primary_emotion)
