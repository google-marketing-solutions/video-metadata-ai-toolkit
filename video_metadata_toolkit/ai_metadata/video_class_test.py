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

import shlex
import subprocess
import unittest
from unittest import mock

import video_class


class TestVideo(unittest.TestCase):

  def test_video_creation_successful(self):
    """Tests successful creation of a video object."""

    video = video_class.Video(
        video_id="video123",
        title="You Can't See Me But I'm Waving Video",
        uri="http://example.com/video.mp4",
        description="This is a sample video",
        metadata=["tag1", "tag2"],
    )

    self.assertEqual(video.video_id, "video123")
    self.assertEqual(video.title, "You Can't See Me But I'm Waving Video")
    self.assertEqual(video.description, "This is a sample video")
    self.assertEqual(video.uri, "http://example.com/video.mp4")
    self.assertEqual(video.metadata, ["tag1", "tag2"])

  @mock.patch.object(subprocess, "run")
  def test_detect_duration_returns_subprocess_result(self, mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        "command", returncode=0, stdout="120.0"
    )

    video = video_class.Video(
        video_id="video123",
        uri="any.mp4",
    )

    self.assertEqual(video.detect_duration(), 120.0)

  @mock.patch.object(subprocess, "run")
  def test_detect_duration_uses_subprocess(self, mock_run):
    video = video_class.Video(
        video_id="video123",
        uri="any.mp4",
    )

    video.detect_duration()
    command = (
        "ffprobe -v error -show_entries format=duration -of"
        " default=noprint_wrappers=1:nokey=1 any.mp4"
    )
    mock_run.assert_called_once_with(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

  @mock.patch.object(subprocess, "run")
  def test_detect_duration_error(self, mock_run):
    """Tests the behavior when there is an error fetching video duration."""
    mock_run.return_value = subprocess.CompletedProcess(
        "command", returncode=1, stdout="any"
    )

    video = video_class.Video(
        video_id="video123",
        title="Error Video",
        uri="http://example.com/error.mp4",
    )

    self.assertEqual(video.detect_duration(), -1.0)

  @mock.patch.object(subprocess, "run")
  def test_detect_duration_exception(self, mock_run):
    """Tests the behavior when an exception occurs in the subprocess call."""
    mock_run.side_effect = Exception("Mock exception")

    video = video_class.Video(
        video_id="video123",
        title="Exception Video",
        uri="http://example.com/exception.mp4",
    )

    self.assertEqual(video.detect_duration(), -1.0)


if __name__ == "__main__":
  unittest.main()
