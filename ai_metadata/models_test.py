import hashlib
import os
import tempfile
import unittest
from unittest import mock
import file_io
from google import genai
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
    self.mock_client = mock.MagicMock(spec=genai.Client)

    mock_generate_content_response = mock.MagicMock()
    mock_generate_content_response.text = "gemini_response_text"
    self.mock_client.models.generate_content.return_value = (
        mock_generate_content_response
    )

    # Mock file operations
    self.mock_uploaded_file_object = mock.MagicMock(spec=genai.types.File)
    self.mock_uploaded_file_object.state = genai.types.FileState.PROCESSING
    self.mock_client.files.upload.return_value = self.mock_uploaded_file_object
    self.mock_client.files.get.return_value = None  # Default to file not found
    self.mock_client.files.delete.return_value = None

    self.gemini_adapter = models.GeminiLLMAdapter(
        client=self.mock_client, model="gemini-test-model"
    )

    self.mock_time_sleep_patcher = mock.patch("time.sleep")
    self.mock_time_sleep = self.mock_time_sleep_patcher.start()
    self.addCleanup(self.mock_time_sleep_patcher.stop)

    self.temp_dir = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp_dir.cleanup)

  def test_generate_with_new_file_uploads_and_waits(self):
    # Setup: File does not exist initially, then gets uploaded and processed
    mock_file_processing = mock.MagicMock(spec=genai.types.File)
    mock_file_processing.state = genai.types.FileState.PROCESSING
    mock_file_active = mock.MagicMock(spec=genai.types.File)
    mock_file_active.state = genai.types.FileState.ACTIVE

    # Create a temporary file with unique content
    temp_file_path = os.path.join(self.temp_dir.name, "new_file.mp4")
    file_content = b"unique_content_for_new_file_upload_test"
    with open(temp_file_path, "wb") as f:
      f.write(file_content)

    # Calculate expected Gemini filename (first 40 chars of content hash)
    hasher = hashlib.sha256()
    hasher.update(file_content)
    expected_gemini_filename = hasher.hexdigest()[:40]

    self.mock_client.files.get.side_effect = [
        None,  # 1st: file not found
        mock_file_active,  # 2nd: file is active
    ]
    self.mock_client.files.upload.return_value = mock_file_processing

    file_to_upload = file_io.File(temp_file_path)
    file_to_upload.add_cleanup_callback = mock.MagicMock()

    prompt_text_part = "prompt_text"
    self.gemini_adapter.generate(
        [prompt_text_part, file_to_upload], dict[str, str], 1.0
    )

    self.mock_client.files.upload.assert_called_once_with(
        file=temp_file_path, config={"name": expected_gemini_filename}
    )
    file_to_upload.add_cleanup_callback.assert_called_once()
    self.mock_time_sleep.assert_called_once_with(10)
    self.mock_client.models.generate_content.assert_called_once_with(
        model="gemini-test-model",
        contents=[prompt_text_part, mock_file_active],
        config=mock.ANY,
    )

  def test_generate_with_existing_file_uses_it(self):
    # Setup: File exists
    temp_file_path = os.path.join(self.temp_dir.name, "existing_file.jpg")
    file_content = b"unique_content_for_existing_file_test"
    with open(temp_file_path, "wb") as f:
      f.write(file_content)

    hasher = hashlib.sha256()
    hasher.update(file_content)
    expected_gemini_filename = hasher.hexdigest()[:40]

    mock_existing_file = mock.MagicMock(spec=genai.types.File)
    mock_existing_file.state = genai.types.FileState.ACTIVE
    self.mock_client.files.get.return_value = mock_existing_file

    file_to_use = file_io.File(temp_file_path)
    file_to_use.add_cleanup_callback = mock.MagicMock()

    prompt_text_part = "prompt_text_existing"
    self.gemini_adapter.generate(
        [prompt_text_part, file_to_use], dict[str, str], 1.0
    )

    self.mock_client.files.get.assert_called_once_with(
        name=expected_gemini_filename
    )
    self.mock_client.files.upload.assert_not_called()
    file_to_use.add_cleanup_callback.assert_not_called()
    self.mock_time_sleep.assert_not_called()

    self.mock_client.models.generate_content.assert_called_once_with(
        model="gemini-test-model",
        contents=[prompt_text_part, mock_existing_file],
        config=mock.ANY,
    )

  def test_generate_sets_custom_response_schema(self):
    self.gemini_adapter.generate(["prompt_part"], dict[str, str], 1.0)

    self.mock_client.models.generate_content.assert_called_once_with(
        model="gemini-test-model",
        contents=mock.ANY,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=dict[str, str],
            temperature=1.0,
        ),
    )

  def test_generate_no_response_schema_and_mime_type_for_str_response(self):
    self.gemini_adapter.generate(["prompt_part"], str, 1.0)

    self.mock_client.models.generate_content.assert_called_once_with(
        model="gemini-test-model",
        contents=mock.ANY,
        config=genai.types.GenerateContentConfig(
            response_mime_type=None,
            response_schema=None,
            temperature=1.0,
        ),
    )

  def test_generate_sets_temperature(self):
    self.gemini_adapter.generate(["prompt_part"], str, 1.4)

    self.mock_client.models.generate_content.assert_called_once_with(
        model="gemini-test-model",
        contents=mock.ANY,
        config=genai.types.GenerateContentConfig(
            response_mime_type=None,
            response_schema=None,
            temperature=1.4,
        ),
    )

  def test_generate_returns_gemini_response_text(self):
    actual_response_text = self.gemini_adapter.generate(
        ["prompt_part"], dict[str, str], 1.0
    )
    self.assertEqual(actual_response_text, "gemini_response_text")


if __name__ == "__main__":
  unittest.main()
