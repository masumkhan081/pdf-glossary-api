from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from glossary.services.text_processing import count_words


class CountWordsTests(SimpleTestCase):
    """Tests for the word-counting service function."""

    def test_counts_repeated_words_case_insensitively(self):
        result = count_words("Freedom, freedom!")
        self.assertEqual(result["freedom"], 2)

    def test_ignores_punctuation(self):
        result = count_words("Books teach; books inspire!")
        self.assertEqual(result, {"books": 2, "teach": 1, "inspire": 1})

    def test_empty_string_returns_empty_dict(self):
        self.assertEqual(count_words(""), {})

    def test_preserves_apostrophes_in_contractions(self):
        result = count_words("Isn't isn't")
        self.assertEqual(result, {"isn't": 2})


class HealthEndpointTests(SimpleTestCase):
    """Tests for GET /api/v1/health/."""

    def test_get_returns_200_and_ok_json(self):
        response = self.client.get(reverse("glossary:health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), {"status": "ok"})

    def test_post_returns_405(self):
        response = self.client.post(reverse("glossary:health"))
        self.assertEqual(response.status_code, 405)
