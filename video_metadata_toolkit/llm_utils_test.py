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
"""Test the LLM utils file."""

import unittest
from unittest import mock
import llm_utils
from video_class import Video


class TestCallLLM(unittest.TestCase):

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_generate_metadata(self, mock_generate_content, mock_vertexai_init):
    mock_generate_content.return_value.text = "metadata_response"

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_metadata")

    self.assertEqual(response, "metadata_response")
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_generate_summary(self, mock_generate_content, mock_vertexai_init):
    mock_generate_content.return_value.text = "summary_response"

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_summary")

    self.assertEqual(response, "summary_response")
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_generate_title_options(
      self, mock_generate_content, mock_vertexai_init
  ):
    mock_generate_content.return_value.text = '["Title 1", "Title 2"]'

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_title_options")

    self.assertEqual(response, ["Title 1", "Title 2"])
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_generate_external_summary(
      self, mock_generate_content, mock_vertexai_init
  ):
    mock_generate_content.return_value.text = "external_summary_response"

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )
    video.ai_suggested_titles = ["Title 1", "Title 2"]
    response = llm_utils.call_llm(video, "generate_external_summary")

    self.assertEqual(response, "external_summary_response")
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  def test_invalid_attribute(self):
    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )

    with self.assertRaises(ValueError):
      llm_utils.call_llm(video, "invalid_attribute")

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_empty_transcript(self, mock_generate_content, mock_vertexai_init):
    mock_generate_content.return_value.text = "metadata_response"

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="",
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_metadata")

    self.assertEqual(response, "metadata_response")
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_long_transcript(self, mock_generate_content, mock_vertexai_init):
    long_transcript = "word " * 10000  # Simulating a long transcript
    mock_generate_content.return_value.text = "metadata_response"

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript=long_transcript,
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_metadata")

    self.assertEqual(response, "metadata_response")
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_handle_connection_error(
      self, mock_generate_content, mock_vertexai_init
  ):
    mock_generate_content.side_effect = Exception("Connection error")

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_metadata")

    self.assertEqual(response, "")
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()

  @mock.patch("vertexai.init")
  @mock.patch("vertexai.generative_models.GenerativeModel.generate_content")
  def test_response_parsing_error(
      self, mock_generate_content, mock_vertexai_init
  ):
    mock_generate_content.return_value.text = '["Title 1", "Title 2'

    video = Video(
        id="123",
        uri="http://example.com/video.mp4",
        title="Test Title",
        transcript="Test Transcript",
        summary="Test Summary",
    )
    response = llm_utils.call_llm(video, "generate_title_options")

    self.assertEqual(response, '["Title 1", "Title 2')
    mock_vertexai_init.assert_called_once()
    mock_generate_content.assert_called_once()


if __name__ == "__main__":
  unittest.main()
