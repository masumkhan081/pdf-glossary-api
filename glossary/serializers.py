from rest_framework import serializers

from glossary.services.text_processing import count_words


class StrictCharField(serializers.CharField):
    """
    A CharField that strictly requires an actual string.
    Rejects numbers, booleans, null, lists, and objects rather than coercing them.
    Also validates original string length before whitespace trimming.
    """

    default_error_messages = {
        "invalid": "Not a valid string.",
        "blank": "This field may not be blank.",
        "max_length": "Ensure this field has no more than {max_length} characters.",
    }

    def to_internal_value(self, data):
        # Explicitly check for actual string type (reject bool, int, float, list, dict, etc.)
        if not isinstance(data, str) or isinstance(data, bool):
            self.fail("invalid")

        # Check the original untrimmed string length
        if len(data) > self.max_length:
            self.fail("max_length", max_length=self.max_length)

        # Check for empty or whitespace-only
        stripped = data.strip()
        if not stripped:
            self.fail("blank")

        return stripped


class TextAnalysisInputSerializer(serializers.Serializer):
    """Input serializer for the text analysis endpoint."""

    text = StrictCharField(max_length=20000)

    def validate_text(self, value: str) -> str:
        counts = count_words(value)
        if not counts:
            raise serializers.ValidationError("No valid words found in the submitted text.")
        return value
