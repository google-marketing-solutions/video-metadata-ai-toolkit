"""Unit tests for the file_io module."""

import time
import unittest
from unittest import mock

import file_io
import google
import google.api_core
import google.api_core.exceptions
import google.generativeai as google_genai


class FileTest(unittest.TestCase):

  def test_cleanup_calls_callbacks(self):
    file = file_io.File("name")
    mock_callback1 = mock.MagicMock()
    mock_callback2 = mock.MagicMock()
    file.add_cleanup_callback(mock_callback1)
    file.add_cleanup_callback(mock_callback2)

    file.cleanup()

    mock_callback1.assert_called_once()
    mock_callback2.assert_called_once()


class GeminiFileHandlerTest(unittest.TestCase):
  """Tests the GeminiFileHandler class."""

  def setUp(self):
    super().setUp()
    self.file_handler = file_io.GeminiFileHandler()

  @mock.patch.object(google_genai, "upload_file", autospec=True)
  def test_upload_calls_gemini_upload_with_valid_gemini_filename(
      self, mock_upload_file
  ):
    file = file_io.File("file/path/file_name.txt")

    self.file_handler.upload(file)

    mock_upload_file.assert_called_once_with(
        path="file/path/file_name.txt", name="filepathfilenametxt"
    )

  @mock.patch.object(google_genai, "get_file", autospec=True)
  def test_get_calls_gemini_get_file(self, mock_get_file):
    file = file_io.File("file/name.txt")

    self.file_handler.get(file)

    mock_get_file.assert_called_once_with("filenametxt")

  @mock.patch.object(google_genai, "get_file", autospec=True)
  def test_get_returns_none_if_file_not_found(self, mock_get_file):
    mock_get_file.side_effect = google.api_core.exceptions.PermissionDenied(
        "File not found"
    )
    file = file_io.File("file/name.txt")

    gemini_file = self.file_handler.get(file)

    self.assertIsNone(gemini_file)

  @mock.patch.object(time, "sleep", autospec=True)
  @mock.patch.object(google_genai, "get_file", autospec=True)
  def test_wait_for_processing(self, mock_get_file, _):
    file = mock.MagicMock(spec=google_genai.types.File)
    file.state.name = "PROCESSING"
    mock_get_file.return_value.state.name = "COMPLETED"

    gemini_file = self.file_handler.wait_for_processing(file)

    self.assertEqual(gemini_file.state.name, "COMPLETED")

  @mock.patch.object(time, "sleep", autospec=True)
  @mock.patch.object(google_genai, "upload_file", autospec=True)
  @mock.patch.object(google_genai, "get_file", autospec=True)
  def test_prepare_gets_file_if_exists(
      self, mock_get_file, mock_upload_file, _
  ):
    """Tests prepare retrieves the file if it exists in Gemini.

    Verifies that if the file is found in Gemini, it's retrieved directly
    and not uploaded again.

    Args:
      mock_get_file: Mock for Gemini's get_file method.
      mock_upload_file: Mock for Gemini's upload_file method.
      _: unused sleep function mock.
    """
    file = file_io.File("file/name.txt")
    mock_gemini_file = mock.MagicMock()
    mock_get_file.return_value = mock_gemini_file
    mock_gemini_file.state.name = "COMPLETED"

    prepared_file = self.file_handler.prepare(file)

    self.assertEqual(prepared_file, mock_gemini_file)
    mock_upload_file.assert_not_called()

  @mock.patch.object(time, "sleep", autospec=True)
  @mock.patch.object(google_genai, "upload_file", autospec=True)
  @mock.patch.object(google_genai, "get_file", autospec=True)
  def test_prepare_uploads_and_waits_if_file_doesnt_exist(
      self, mock_get_file, mock_upload_file, _
  ):
    """Tests prepare uploads the file if it doesn't exist in Gemini.

    Verifies that if the file is not found in Gemini, it's uploaded,
    the processing is waited for.

    Args:
      mock_get_file: Mock for Gemini's get_file method.
      mock_upload_file: Mock for Gemini's upload_file method.
      _: unused sleep function mock.
    """
    file = file_io.File("file/name.txt")
    mock_get_file.side_effect = google.api_core.exceptions.PermissionDenied(
        "File not found"
    )
    mock_gemini_file = mock.MagicMock()
    mock_upload_file.return_value = mock_gemini_file
    mock_gemini_file.state.name = "COMPLETED"

    prepared_file = self.file_handler.prepare(file)

    self.assertEqual(prepared_file, mock_gemini_file)
    mock_upload_file.assert_called_once()


if __name__ == "__main__":
  unittest.main()
