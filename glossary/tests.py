import json
from django.test import SimpleTestCase
from django.urls import reverse

from glossary.services.text_processing import analyse_text, count_words, tokenize


class TokenizerTests(SimpleTestCase):
    """Unit tests for the English tokenizer and word-counting service."""

    def test_counts_repeated_words_case_insensitively(self):
        result = count_words("Freedom, FREEDOM!")
        self.assertEqual(result, {"freedom": 2})

    def test_normalises_curly_apostrophes(self):
        result = count_words("Isn't isn’t")
        self.assertEqual(result, {"isn't": 2})

    def test_excludes_digits_and_underscores(self):
        result = count_words("123 ___ abc123 some_variable")
        self.assertEqual(result, {})

    def test_hyphen_and_dash_separators(self):
        result_hyphen = count_words("well-being")
        self.assertEqual(result_hyphen, {"well": 1, "being": 1})

        result_em_dash = count_words("well—being")
        self.assertEqual(result_em_dash, {"well": 1, "being": 1})

        result_en_dash = count_words("well–being")
        self.assertEqual(result_en_dash, {"well": 1, "being": 1})

    def test_empty_string_returns_empty_dict(self):
        self.assertEqual(count_words(""), {})

    def test_punctuation_only_returns_empty_dict(self):
        self.assertEqual(count_words(".,:;!?\"'()[]{}"), {})

    def test_strips_surrounding_apostrophes(self):
        result = count_words("'hello' 'world'")
        self.assertEqual(result, {"hello": 1, "world": 1})

    def test_internal_apostrophes_preserved(self):
        result = count_words("o'clock rock'n'roll")
        self.assertEqual(result, {"o'clock": 1, "rock'n'roll": 1})


class AnalyseTextServiceTests(SimpleTestCase):
    """Unit tests for the analyse_text service function."""

    def test_exact_structure_and_sorting(self):
        result = analyse_text("Freedom, freedom! Books inspire.")
        self.assertEqual(
            result,
            {
                "total_words": 4,
                "unique_words": 3,
                "words": [
                    {"word": "freedom", "count": 2},
                    {"word": "books", "count": 1},
                    {"word": "inspire", "count": 1},
                ],
            },
        )

    def test_alphabetical_tie_breaking(self):
        result = analyse_text("zebra apple banana")
        self.assertEqual(
            result["words"],
            [
                {"word": "apple", "count": 1},
                {"word": "banana", "count": 1},
                {"word": "zebra", "count": 1},
            ],
        )


class AnalyseTextAPITests(SimpleTestCase):
    """Integration tests for POST /api/v1/analyse-text/."""

    def setUp(self):
        self.url = reverse("glossary:analyse_text")

    def test_exact_success_response(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "Freedom, freedom! Books inspire."}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(
            response.json(),
            {
                "total_words": 4,
                "unique_words": 3,
                "words": [
                    {"word": "freedom", "count": 2},
                    {"word": "books", "count": 1},
                    {"word": "inspire", "count": 1},
                ],
            },
        )

    def test_deterministic_sorting(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "cat dog bird dog cat dog"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["words"],
            [
                {"word": "dog", "count": 3},
                {"word": "cat", "count": 2},
                {"word": "bird", "count": 1},
            ],
        )

    def test_missing_text_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_empty_text_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_whitespace_only_text_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "   \n\t  "}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_wrong_type_number_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": 123}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_wrong_type_boolean_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": True}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_wrong_type_null_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": None}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_wrong_type_list_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": ["Freedom"]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_wrong_type_object_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": {"nested": "Freedom"}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_non_dictionary_root_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps(["Freedom"]),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_exact_20000_character_boundary_accepted(self):
        # 4000 repetitions of "word " (5 chars each) = 20,000 characters
        exact_text = "word " * 3999 + "word"  # 3999 * 5 + 4 = 19999. Let's make exact 20,000:
        exact_text = "a " * 9999 + "aa"  # 9999 * 2 + 2 = 20,000
        self.assertEqual(len(exact_text), 20000)

        response = self.client.post(
            self.url,
            data=json.dumps({"text": exact_text}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_20001_characters_rejected(self):
        oversized = "a" * 20001
        response = self.client.post(
            self.url,
            data=json.dumps({"text": oversized}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())
        self.assertIn("20000", str(response.json()["text"]))

    def test_20001_characters_with_trailing_whitespace_rejected_before_trimming(self):
        # 20,000 chars of text + 1 trailing space = 20,001 chars
        exact_20000 = "a " * 9999 + "aa"
        text_with_space = exact_20000 + " "
        self.assertEqual(len(text_with_space), 20001)

        response = self.client.post(
            self.url,
            data=json.dumps({"text": text_with_space}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())
        self.assertIn("20000", str(response.json()["text"]))

    def test_numbers_only_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "12345 67890"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_punctuation_only_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "!@#$%^&*()_+"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_no_valid_words_rejected(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"text": "123 ___ abc123 some_variable"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("text", response.json())

    def test_malformed_json_rejected(self):
        response = self.client.post(
            self.url,
            data='{"text": "broken json',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_unsupported_content_type_rejected(self):
        response = self.client.post(
            self.url,
            data="text=Freedom",
            content_type="text/plain",
        )
        self.assertEqual(response.status_code, 415)

    def test_get_method_rejected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class HealthEndpointTests(SimpleTestCase):
    """Tests for GET /api/v1/health/ to verify existing behaviour is preserved."""

    def test_get_returns_200_and_ok_json(self):
        response = self.client.get(reverse("glossary:health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), {"status": "ok"})

    def test_post_returns_405(self):
        response = self.client.post(reverse("glossary:health"))
        self.assertEqual(response.status_code, 405)
