import unittest
from unittest import mock
import file_io
import google.generativeai as google_genai
import models


class MultiModalLLMTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_adapter = mock.MagicMock(spec=models.MultiModalLLMAdapater)
    self.mock_adapter.generate.return_value = "response_text"
    self.model = models.MultiModalLLM(self.mock_adapter)

  def test_generate_calls_adapter_correctly(self):
    self.model.generate(["prompt_part"], dict[str, str], 1.0)

    self.mock_adapter.generate.assert_called_once_with(
        ["prompt_part"], dict[str, str], 1.0
    )

  def test_generate_returns_response_text(self):
    self.mock_adapter.generate.return_value = "response_text"

    response_text = self.model.generate(["prompt_part"], dict[str, str], 1.0)

    self.assertEqual(response_text, "response_text")


class GeminiLLMAdapterTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_gemini = mock.MagicMock(spec=google_genai.GenerativeModel)
    self.mock_file_handler = mock.MagicMock(spec=file_io.GeminiFileHandler)
    self.gemini_adapter = models.GeminiLLMAdapter(
        self.mock_gemini, self.mock_file_handler
    )

  def test_generate_creates_correct_prompt(self):
    file = file_io.File("file/path")
    self.gemini_adapter.generate(["prompt_part", file], dict[str, str], 1.0)

    self.mock_file_handler.prepare.assert_called_once_with(file)
    self.mock_gemini.generate_content.assert_called_once_with(
        ["prompt_part", self.mock_file_handler.prepare.return_value],
        generation_config=mock.ANY,
    )

  def test_generate_sets_custom_response_schema(self):
    self.gemini_adapter.generate(["prompt_part"], dict[str, str], 1.0)

    self.mock_gemini.generate_content.assert_called_once_with(
        mock.ANY,
        generation_config=google_genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=dict[str, str],
            temperature=mock.ANY,
        ),
    )

  def test_generate_no_response_schema_for_str(self):
    self.gemini_adapter.generate(["prompt_part"], str, 1.0)

    self.mock_gemini.generate_content.assert_called_once_with(
        mock.ANY,
        generation_config=google_genai.GenerationConfig(
            response_mime_type=None,
            response_schema=None,
            temperature=mock.ANY,
        ),
    )

  def test_generate_sets_temperature(self):
    self.gemini_adapter.generate(["prompt_part"], str, 1.4)

    self.mock_gemini.generate_content.assert_called_once_with(
        mock.ANY,
        generation_config=google_genai.GenerationConfig(
            response_mime_type=mock.ANY,
            response_schema=mock.ANY,
            temperature=1.4,
        ),
    )

  def test_generate_returns_gemini_response_text(self):
    response_text = self.gemini_adapter.generate(
        ["prompt_part"], dict[str, str], 1.0
    )

    self.assertEqual(
        response_text, self.mock_gemini.generate_content.return_value.text
    )


if __name__ == "__main__":
  unittest.main()
