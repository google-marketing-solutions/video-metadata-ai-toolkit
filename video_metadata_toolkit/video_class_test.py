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

import unittest
from unittest.mock import MagicMock, patch
from video_class import Video  # Assuming this imports your Video class definition


class TestVideo(unittest.TestCase):

  def setUp(self):
    """Setup common patches for all tests."""
    # Mock subprocess.run to prevent actual execution
    self.subprocess_patch = patch("subprocess.run")
    self.mock_subprocess_run = self.subprocess_patch.start()

    # Mock the language detection to return a fixed language code
    self.language_patch = patch(
        "transcription_utils.detect_language", return_value="en"
    )
    self.mock_detect_language = self.language_patch.start()

  def tearDown(self):
    """Stop patches after each test."""
    self.subprocess_patch.stop()
    self.language_patch.stop()

  def test_video_creation_successful(self):
    """Tests successful creation of a video object with all attributes set correctly."""
    self.mock_subprocess_run.return_value = MagicMock(
        stdout="120", returncode=0
    )

    video = Video(
        id="video123",
        title="You Can't See Me But I'm Waving Video",
        uri="http://example.com/video.mp4",
        description="This is a sample video",
        metadata=["tag1", "tag2"],
    )

    self.assertEqual(video.id, "video123")
    self.assertEqual(video.title, "You Can't See Me But I'm Waving Video")
    self.assertEqual(video.description, "This is a sample video")
    self.assertEqual(video.uri, "http://example.com/video.mp4")
    self.assertEqual(video.languages, "en")
    self.assertEqual(video.duration, 120.0)
    self.assertEqual(video.metadata, ["tag1", "tag2"])

  def test_detect_duration_error(self):
    """Tests the behavior when there is an error fetching video duration."""
    self.mock_subprocess_run.return_value = MagicMock(
        stdout="", stderr="An error occurred", returncode=1
    )

    video = Video(
        id="video123", title="Error Video", uri="http://example.com/error.mp4"
    )

    self.assertEqual(video.duration, -1.0)

  def test_detect_duration_exception(self):
    """Tests the behavior when an exception occurs in the subprocess call."""
    self.mock_subprocess_run.side_effect = Exception("Mock exception")

    video = Video(
        id="video123",
        title="Exception Video",
        uri="http://example.com/exception.mp4",
    )

    self.assertEqual(video.duration, -1.0)


if __name__ == "__main__":
  unittest.main()
