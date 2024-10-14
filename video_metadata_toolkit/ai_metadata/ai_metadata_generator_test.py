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
"""Test the ai metadata genertator file."""

import unittest
from unittest import mock

import ai_metadata_generator
import llm_utils
import transcription_utils
import video_class


@mock.patch.object(transcription_utils, "get_transcript_from_video")
@mock.patch.object(llm_utils, "call_llm")
class TestVideoMetadataGenerator(unittest.TestCase):

  def test_add_ai_attributes_to_video(
      self,
      mock_call_llm,
      mock_get_transcript_from_video,
  ):
    """Tests adding ai attributes to a video (e.g. metadata/summary/titles)."""
    transcript = (
        "This is a long transcript with more than 100 characters. This ensures"
        " the transcription length condition is satisfied."
    )
    mock_get_transcript_from_video.return_value = transcript
    video = video_class.Video(
        video_id="1234", uri="https://example.com/video.mp4", duration=1200
    )
    audio_bucket_name = "audio_bucket"
    mock_call_llm.side_effect = [
        "Generated summary",
        "Generated metadata",
        ["Title 1", "Title 2"],
        "Generated external summary",
    ]

    video = ai_metadata_generator.add_ai_attributes_to_video(
        video, audio_bucket_name
    )

    self.assertEqual(
        video.transcript,
        transcript,
    )
    self.assertEqual(video.summary, "Generated summary")
    self.assertEqual(video.ai_generated_metadata, "Generated metadata")
    self.assertEqual(video.ai_suggested_titles, ["Title 1", "Title 2"])
    self.assertEqual(
        video.ai_suggested_external_summary, "Generated external summary"
    )

  def test_add_ai_attributes_to_video_short_transcript(
      self,
      mock_call_llm,
      mock_get_transcript_from_video,
  ):
    """Tests for when the transcript is too short to generate attributes."""
    mock_get_transcript_from_video.return_value = "Short transcript"
    video = video_class.Video(
        video_id="1234", uri="https://example.com/video.mp4", duration=1200
    )
    audio_bucket_name = "audio_bucket"

    video = ai_metadata_generator.add_ai_attributes_to_video(
        video, audio_bucket_name
    )

    self.assertEqual(video.transcript, "Short transcript")
    self.assertIsNone(video.summary)
    self.assertIsNone(video.ai_generated_metadata)
    self.assertIsNone(video.ai_suggested_titles)
    self.assertIsNone(video.ai_suggested_external_summary)
    mock_call_llm.assert_not_called()

  def test_add_ai_attributes_to_video_longer_than_40_minutes(
      self,
      mock_call_llm,
      mock_get_transcript_from_video,
  ):
    """Tests for when the video is too long to generate attributes."""
    mock_get_transcript_from_video.return_value = (
        "This is a video longer than 40 minutes."
    )
    video = video_class.Video(
        video_id="1234", uri="https://example.com/video.mp4", duration=3400
    )
    audio_bucket_name = "audio_bucket"

    video = ai_metadata_generator.add_ai_attributes_to_video(
        video, audio_bucket_name
    )

    self.assertEqual(
        video.transcript, "This is a video longer than 40 minutes."
    )
    self.assertIsNone(video.summary)
    self.assertIsNone(video.ai_generated_metadata)
    self.assertIsNone(video.ai_suggested_titles)
    self.assertIsNone(video.ai_suggested_external_summary)
    mock_call_llm.assert_not_called()

  @mock.patch.object(ai_metadata_generator, "add_ai_attributes_to_video")
  def test_main(self, mock_add_ai_attributes_to_video, *_):
    """Tests the main function which takes in a video and adds ai attributes."""
    video_url = "https://example.mp4"
    metadata = "test metadata"
    video_title = "test title"

    ai_metadata_generator.main([
        video_url,
        "--title",
        video_title,
        "--metadata",
        metadata,
    ])

    mock_add_ai_attributes_to_video.assert_called_once()

  def test_main_no_video_url(self, *_):
    """Tests the main function throws error when no video URL is provided."""
    with self.assertRaises(ValueError):
      ai_metadata_generator.main([""])


if __name__ == "__main__":
  unittest.main()
