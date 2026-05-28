"""Auto-summarizer engine for compressing conversation history.

This module provides a rule-based extractive summarization approach that does
not require any LLM. It analyzes message keyword frequency and generates a
structured summary of conversation highlights.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional

from agentmemory.core.message import Message


class AutoSummarizer:
    """Rule-based extractive summarizer for conversation messages.

    Analyzes message content to extract high-frequency keywords and generates
    a structured summary. Designed to compress older messages when a session
    exceeds a configurable message threshold.

    Attributes:
        threshold: Number of messages before summarization is triggered.
        max_keywords: Maximum number of keywords to extract.
        min_keyword_length: Minimum character length for a keyword.
    """

    # Common stop words to exclude from keyword analysis
    STOP_WORDS: frozenset[str] = frozenset({
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "because", "but", "and", "or", "if", "while", "that", "this", "it",
        "its", "i", "me", "my", "we", "our", "you", "your", "he", "him",
        "his", "she", "her", "they", "them", "their", "what", "which", "who",
        "whom", "these", "those", "am",
        # Common Chinese stop words
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
        "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
        "着", "没有", "看", "好", "自己", "这", "他", "她", "它", "们",
        "那", "些", "什么", "吗", "吧", "啊", "呢", "嗯", "哦", "哈",
    })

    def __init__(
        self,
        threshold: int = 20,
        max_keywords: int = 10,
        min_keyword_length: int = 2,
    ) -> None:
        """Initialize the AutoSummarizer.

        Args:
            threshold: Number of messages before summarization triggers.
            max_keywords: Maximum keywords to extract from messages.
            min_keyword_length: Minimum length for a word to be considered
                as a keyword.
        """
        self.threshold = threshold
        self.max_keywords = max_keywords
        self.min_keyword_length = min_keyword_length

    def should_summarize(self, message_count: int) -> bool:
        """Check if summarization should be triggered.

        Args:
            message_count: Current number of messages in the session.

        Returns:
            True if the message count exceeds the threshold.
        """
        return message_count >= self.threshold

    def summarize(self, messages: List[Message]) -> Dict[str, Any]:
        """Generate a structured summary from a list of messages.

        Args:
            messages: The list of messages to summarize.

        Returns:
            A dictionary containing:
                - summary: A human-readable summary text.
                - keywords: List of extracted high-frequency keywords.
                - message_count: Number of messages summarized.
                - role_distribution: Count of messages per role.
                - time_range: Dict with 'start' and 'end' timestamps.
        """
        if not messages:
            return {
                "summary": "No messages to summarize.",
                "keywords": [],
                "message_count": 0,
                "role_distribution": {},
                "time_range": {"start": "", "end": ""},
            }

        # Extract keywords from all message content
        all_text = " ".join(msg.content for msg in messages)
        keywords = self._extract_keywords(all_text)

        # Compute role distribution
        role_counts: Dict[str, int] = {}
        for msg in messages:
            role_counts[msg.role] = role_counts.get(msg.role, 0) + 1

        # Determine time range
        timestamps = [msg.timestamp for msg in messages]
        time_range = {
            "start": min(timestamps),
            "end": max(timestamps),
        }

        # Extract key user messages (first and last user messages)
        user_messages = [msg for msg in messages if msg.role == Role.USER.value]
        key_user_msgs: List[str] = []
        if user_messages:
            key_user_msgs.append(f"First topic: {user_messages[0].content[:100]}")
            if len(user_messages) > 1:
                key_user_msgs.append(
                    f"Last topic: {user_messages[-1].content[:100]}"
                )

        # Build summary text
        summary_lines: List[str] = []
        summary_lines.append(
            f"Summary of {len(messages)} messages "
            f"(from {time_range['start'][:19]} to {time_range['end'][:19]})"
        )
        summary_lines.append("")

        if keywords:
            summary_lines.append(f"Key topics: {', '.join(keywords)}")
            summary_lines.append("")

        summary_lines.append("Role distribution:")
        for role, count in sorted(role_counts.items()):
            summary_lines.append(f"  - {role}: {count} messages")
        summary_lines.append("")

        if key_user_msgs:
            summary_lines.append("Conversation highlights:")
            for line in key_user_msgs:
                summary_lines.append(f"  - {line}")

        summary_text = "\n".join(summary_lines)

        return {
            "summary": summary_text,
            "keywords": keywords,
            "message_count": len(messages),
            "role_distribution": role_counts,
            "time_range": time_range,
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract high-frequency keywords from text.

        Tokenizes the text, filters stop words and short tokens, then
        returns the most frequent words.

        Args:
            text: The text to analyze.

        Returns:
            A list of keywords sorted by frequency (descending).
        """
        # Tokenize: split on non-alphanumeric/non-CJK characters
        tokens = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())

        # Filter stop words and short tokens
        filtered = [
            token
            for token in tokens
            if token not in self.STOP_WORDS
            and len(token) >= self.min_keyword_length
        ]

        if not filtered:
            return []

        # Count and sort by frequency
        counter = Counter(filtered)
        return [
            word
            for word, _count in counter.most_common(self.max_keywords)
        ]

    def get_summary_text(self, summary: Dict[str, Any]) -> str:
        """Get the plain-text summary from a summary dict.

        Args:
            summary: A summary dictionary returned by summarize().

        Returns:
            The summary text string.
        """
        return summary.get("summary", "No summary available.")


# Avoid circular import by importing Role here (used in summarize method)
from agentmemory.core.message import Role  # noqa: E402
