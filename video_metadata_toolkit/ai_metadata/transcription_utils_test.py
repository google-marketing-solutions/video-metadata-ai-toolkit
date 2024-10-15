# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test the transcription utils file."""
import os
import unittest
from unittest import mock
import google.api_core.exceptions as google_exceptions
import requests
import requests
import transcription_utils


class TestDownloadVideo(unittest.TestCase):

  @mock.patch("os.makedirs")
  @mock.patch("builtins.open", new_callable=unittest.mock.mock_open)
  @mock.patch("requests.get")
  def test_successful_download(self, mock_get, mock_file, mock_makedirs):
    """Test successful download of a video."""
    mock_response = mock.MagicMock()
    mock_response.headers = {"Content-Type": "video/mp4"}
    mock_response.iter_content = mock.MagicMock(return_value=[b"data"])
    mock_response.__enter__.return_value = mock_response
    mock_get.return_value = mock_response

    result = transcription_utils.download_video(
        "http://example.com/video.mp4", "./vids/video.mp4"
    )
    self.assertEqual(result, "./vids/video.mp4")
    mock_file.assert_called_once_with("./vids/video.mp4", "wb")
    mock_file().write.assert_called_with(b"data")

  @mock.patch("requests.get")
  def test_invalid_url_when_downloading(self, mock_get):
    """Test with a non-existent video URL (404 error)."""
    mock_get.side_effect = requests.HTTPError("404 Client Error")
    mock_get.raise_for_status.side_effect = requests.HTTPError(
        "404 Client Error"
    )
    local_path = "./vids/video.mp4"
    with self.assertRaises(requests.HTTPError):
      transcription_utils.download_video(
          "http://example.com/invalid_video.mp4", local_path
      )
    self.assertFalse(os.path.exists(local_path))

  @mock.patch("requests.get")
  def test_invalid_content_type(self, mock_get):
    """Test invalid content-type returned for a download."""
    mock_response = mock.MagicMock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.raise_for_status = mock.MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_get.return_value = mock_response
    local_path = "./vids/video.mp4"
    with self.assertRaises(ValueError):
      transcription_utils.download_video(
          "http://example.com/invalid_video.mp4", local_path
      )
    self.assertFalse(os.path.exists(local_path))

  @mock.patch("os.makedirs")
  @mock.patch("builtins.open", side_effect=IOError("Cannot write to file"))
  @mock.patch("requests.get")
  def test_file_write_error(self, mock_get, mock_file, mock_makedirs):
    """Test trying to write to folder without permission."""
    mock_response = mock.MagicMock()
    mock_response.headers = {"Content-Type": "video/mp4"}
    mock_response.iter_content = mock.MagicMock(return_value=[b"data"])
    mock_response.__enter__.return_value = mock_response
    mock_get.return_value = mock_response
    local_path_with_permission_error = "/path/with/permission/error/video.mp4"
    with self.assertRaises(IOError):
      transcription_utils.download_video(
          "http://example.com/video.mp4", local_path_with_permission_error
      )
    self.assertFalse(os.path.exists(local_path_with_permission_error))


class TestDownloadFileFromGCS(unittest.TestCase):

  @mock.patch("transcription_utils.storage.Client")
  def test_successful_download_from_gcs(self, mock_client):
    """Test successful download from GCS."""
    mock_bucket = mock.MagicMock()
    mock_blob = mock.MagicMock()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    local_file_path = "download_from_gcs_file.mp4"
    transcription_utils.download_file_from_gcs(
        "gs://my-bucket/file.mp4", local_file_path
    )
    mock_blob.download_to_filename.assert_called_once_with(local_file_path)

  @mock.patch("transcription_utils.storage.Client")
  def test_file_from_gcs_not_found_error(self, mock_client):
    """Test error raised when file does not exist in GCS."""
    mock_bucket = mock.MagicMock()
    mock_blob = mock.MagicMock()
    mock_blob.download_to_filename.side_effect = google_exceptions.NotFound(
        "File not found"
    )
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with self.assertRaises(ValueError) as context:
      transcription_utils.download_file_from_gcs(
          "gs://my-bucket/nonexistent.txt", "/local/path/nonexistent.mp4"
      )
    self.assertIn("does not exist", str(context.exception))

  @mock.patch("transcription_utils.storage.Client")
  def test_insufficient_permissions_error(self, mock_client):
    """Test error raised when permissions are insufficient."""
    mock_bucket = mock.MagicMock()
    mock_blob = mock.MagicMock()
    mock_blob.download_to_filename.side_effect = google_exceptions.Forbidden(
        "Access Denied"
    )
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with self.assertRaises(PermissionError) as context:
      transcription_utils.download_file_from_gcs(
          "gs://my-bucket/privatefile.txt", "/local/path/privatefile.txt"
      )
    self.assertIn("Insufficient permissions", str(context.exception))

  @mock.patch("transcription_utils.storage.Client")
  def test_google_cloud_error(self, mock_client):
    """Test general GCS error."""
    mock_bucket = mock.MagicMock()
    mock_blob = mock.MagicMock()
    mock_blob.download_to_filename.side_effect = Exception()
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with self.assertRaises(Exception) as context:
      transcription_utils.download_file_from_gcs(
          "gs://my-bucket/problemfile.txt", "/local/path/problemfile.txt"
      )
    self.assertIn("Google Cloud Storage", str(context.exception))

  @mock.patch("transcription_utils.storage.Client")
  def test_local_io_error(self, mock_client):
    """Test error during local file write."""
    mock_bucket = mock.MagicMock()
    mock_blob = mock.MagicMock()
    mock_blob.download_to_filename.side_effect = OSError(
        "Simulated write error"
    )
    mock_client.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with self.assertRaises(OSError) as context:
      transcription_utils.download_file_from_gcs(
          "gs://my-bucket/validfile.txt", "/invalid/path/file.txt"
      )
    self.assertIn("Failed to write the file", str(context.exception))


class TestExtractAudioFromVideo(unittest.TestCase):

  @mock.patch("transcription_utils._extract_audio_from_gcs")
  def test_extract_audio_from_gcs(self, mock_extract_audio_from_gcs):
    """Test extracting audio from a GCS URI."""
    mock_extract_audio_from_gcs.return_value = "/output/dir/audio_file.wav"
    result = transcription_utils.extract_audio_from_video(
        "gs://my-bucket/video.mp4", "/output/dir"
    )
    mock_extract_audio_from_gcs.assert_called_once_with(
        "gs://my-bucket/video.mp4", "/output/dir"
    )
    self.assertEqual(result, "/output/dir/audio_file.wav")

  @mock.patch("transcription_utils._extract_audio_from_local_file")
  def test_extract_audio_from_local_file(
      self, mock_extract_audio_from_local_file
  ):
    """Test extracting audio from a local file path."""
    mock_extract_audio_from_local_file.return_value = (
        "/output/dir/local_audio_file.wav"
    )
    result = transcription_utils.extract_audio_from_video(
        "/local/path/video.mp4", "/output/dir"
    )
    mock_extract_audio_from_local_file.assert_called_once_with(
        "/local/path/video.mp4", "/output/dir"
    )
    self.assertEqual(result, "/output/dir/local_audio_file.wav")

  @mock.patch("transcription_utils._extract_audio_from_gcs")
  def test_gcs_file_not_found_error(self, mock_extract_audio_from_gcs):
    """Test GCS file not found error."""
    mock_extract_audio_from_gcs.side_effect = FileNotFoundError(
        "GCS object not found"
    )
    with self.assertRaises(FileNotFoundError):
      transcription_utils.extract_audio_from_video(
          "gs://my-bucket/nonexistent.mp4", "/output/dir"
      )

  @mock.patch("transcription_utils._extract_audio_from_local_file")
  def test_local_file_not_found_error(self, mock_extract_audio_from_local_file):
    """Test local file not found error."""
    mock_extract_audio_from_local_file.side_effect = FileNotFoundError(
        "Local file not found"
    )
    with self.assertRaises(FileNotFoundError):
      transcription_utils.extract_audio_from_video(
          "/local/path/nonexistent.mp4", "/output/dir"
      )


class TestTranscribeAudio(unittest.TestCase):

  @mock.patch("transcription_utils._transcribe_from_gcs")
  @mock.patch("builtins.open", new_callable=unittest.mock.mock_open)
  @mock.patch("os.path.join")
  @mock.patch("os.path.basename")
  @mock.patch("os.path.splitext")
  def test_transcribe_audio_from_gcs(
      self,
      mock_splitext,
      mock_basename,
      mock_join,
      mock_open,
      mock_transcribe_gcs,
  ):
    """Test transcription from a GCS URI."""
    mock_transcribe_gcs.return_value = "Transcribed text"
    mock_basename.return_value = "audio.wav"
    mock_splitext.return_value = ("audio", ".wav")
    mock_join.return_value = "./transcriptions/audio_transcription.txt"
    mock_file_handle = mock.MagicMock()
    mock_open.return_value = mock_file_handle
    result = transcription_utils.transcribe_audio("gs://my-bucket/audio.wav")
    mock_transcribe_gcs.assert_called_once_with(
        "gs://my-bucket/audio.wav", ["en-GB"]
    )
    mock_open.assert_called_once_with(
        "./transcriptions/audio_transcription.txt", "w"
    )
    handle = mock_open()
    handle.__enter__().write.assert_called_once_with("Transcribed text")
    self.assertEqual(result, "./transcriptions/audio_transcription.txt")

  @mock.patch("transcription_utils._transcribe_from_local_file")
  @mock.patch("builtins.open")
  @mock.patch("os.path.join")
  def test_transcribe_audio_from_local_file(
      self, mock_join, mock_open, mock_transcribe_local
  ):
    """Test transcription from a local file."""
    mock_transcribe_local.return_value = "Local transcribed text"
    mock_join.return_value = "./transcriptions/local_audio_transcription.txt"
    mock_file_handle = mock.MagicMock()
    mock_open.return_value = mock_file_handle
    result = transcription_utils.transcribe_audio("/local/path/video.wav")
    mock_transcribe_local.assert_called_once_with(
        "/local/path/video.wav", ["en-GB"]
    )
    mock_open.assert_called_once_with(
        "./transcriptions/local_audio_transcription.txt", "w"
    )
    handle = mock_open()
    handle.__enter__().write.assert_called_once_with("Local transcribed text")
    self.assertEqual(result, "./transcriptions/local_audio_transcription.txt")

  @mock.patch("transcription_utils._transcribe_from_gcs")
  def test_gcs_file_not_found_error(self, mock_transcribe_gcs):
    """Test handling GCS file not found error."""
    mock_transcribe_gcs.side_effect = FileNotFoundError("GCS object not found")
    with self.assertRaises(FileNotFoundError):
      transcription_utils.transcribe_audio("gs://my-bucket/nonexistent.mp4")

  @mock.patch("transcription_utils._transcribe_from_local_file")
  def test_local_file_not_found_error(self, mock_transcribe_local):
    """Test handling local file not found error."""
    mock_transcribe_local.side_effect = FileNotFoundError(
        "Local file not found"
    )
    with self.assertRaises(FileNotFoundError):
      transcription_utils.transcribe_audio("/local/path/nonexistent.mp4")


class TestUploadLocalFileToGoogleCloud(unittest.TestCase):

  @mock.patch("transcription_utils.storage.Client")
  def test_file_not_found_error(self, mock_client):
    """Test handling of FileNotFoundError if the source file does not exist."""
    mock_client.return_value.bucket.return_value.blob.return_value = (
        mock.MagicMock()
    )

    with self.assertRaises(FileNotFoundError):
      transcription_utils.upload_local_file_to_google_cloud(
          "test-bucket", "/path/nonexistent_file.txt", "destination_blob.txt"
      )

  @mock.patch("transcription_utils.storage.Client")
  def test_bucket_not_found_error(self, mock_client):
    """Test handling of NotFound error if the bucket does not exist."""
    mock_client.return_value.bucket.side_effect = google_exceptions.NotFound(
        "Bucket not found"
    )

    with self.assertRaises(google_exceptions.NotFound):
      transcription_utils.upload_local_file_to_google_cloud(
          "nonexistent-bucket", "./smart_ad_breaks.py", "destination_blob.txt"
      )

  @mock.patch("transcription_utils.storage.Client")
  def test_permission_denied_error(self, mock_client):
    """Test handling of Forbidden error due to permission issues."""
    mock_client.return_value.bucket.return_value.blob.return_value.upload_from_filename.side_effect = google_exceptions.Forbidden(
        "Permission denied"
    )

    with self.assertRaises(google_exceptions.Forbidden):
      transcription_utils.upload_local_file_to_google_cloud(
          "test-bucket", "./smart_ad_breaks.py", "destination_blob.txt"
      )

  @mock.patch("transcription_utils.storage.Client")
  def test_generic_api_error(self, mock_client):
    """Test handling of generic Google API errors during upload."""
    mock_client.return_value.bucket.return_value.blob.return_value.upload_from_filename.side_effect = Exception(
        "API error"
    )

    with self.assertRaises(Exception):
      transcription_utils.upload_local_file_to_google_cloud(
          "test-bucket", "/path/existent_file.txt", "destination_blob.txt"
      )


class TestDetectLanguage(unittest.TestCase):

  @mock.patch("transcription_utils.translate.TranslationServiceClient")
  def test_detect_single_language(self, mock_translate_client):
    mock_client_instance = mock.MagicMock()
    mock_translate_client.return_value = mock_client_instance
    mock_response = mock.MagicMock()
    mock_response.languages = [
        mock.MagicMock(language_code="en", confidence=0.99)
    ]
    mock_client_instance.detect_language.return_value = mock_response

    result = transcription_utils.detect_language(
        "Imagine waving and no one saw you."
    )
    self.assertEqual(result, ["en-GB"])
    mock_client_instance.detect_language.assert_called_once()

    @mock.patch("transcription_utils.translate.TranslationServiceClient")
    def test_detect_language_none_input(self, mock_translate_client):
      mock_client_instance = mock.MagicMock()
      mock_translate_client.return_value = mock_client_instance

      result = transcription_utils.detect_language(None)
      self.assertEqual(result, ["en-GB"])
      mock_client_instance.detect_language.assert_not_called()

  @mock.patch("transcription_utils.translate.TranslationServiceClient")
  def test_detect_multiple_languages(self, mock_translate_client):
    mock_client_instance = mock.MagicMock()
    mock_translate_client.return_value = mock_client_instance
    mock_response = mock.MagicMock()
    mock_response.languages = [
        mock.MagicMock(language_code="en", confidence=0.75),
        mock.MagicMock(language_code="es", confidence=0.25),
    ]
    mock_client_instance.detect_language.return_value = mock_response

    result = transcription_utils.detect_language(
        "This test tiene English y Español."
    )

    self.assertIn("en-GB", result)
    self.assertIn("es-ES", result)
    self.assertEqual(len(result), 2)
    mock_client_instance.detect_language.assert_called_once()


class TestMapLanguageCode(unittest.TestCase):

  def test_map_language_code_valid(self):
    """Test when the language code is valid."""
    self.assertEqual(transcription_utils.map_language_code("zu"), "zu-ZA")

  def test_map_language_code_invalid(self):
    """Test when the language code is not valid."""
    self.assertEqual(transcription_utils.map_language_code("xx"), "en-GB")


if __name__ == "__main__":
  unittest.main()
