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
"""Tests for the smart_ad_breaks module."""

import unittest
from unittest import mock

from smart_ad_breaks import cue_point_generator
from smart_ad_breaks import video_analysis

_TEST_SHOT_DETECT_RESPONSE = [
    video_analysis.VideoSegment(0.0, 12.1),
    video_analysis.VideoSegment(12.3, 12.5),
    video_analysis.VideoSegment(12.7, 60.1),
    video_analysis.VideoSegment(60.3, 60.8),
    video_analysis.VideoSegment(65.3, 65.8),
]


class SmartAdBreaksTest(unittest.TestCase):

  def test_determine_video_cue_points_video_analyzer_args(self):
    mock_analyzer = mock.MagicMock(spec=video_analysis.VideoAnalyzer)

    cue_point_generator.determine_video_cue_points(
        "video", mock_analyzer, volume_threshold=-10.0
    )

    mock_analyzer.detect_shot_changes.assert_called_once_with(
        "video", volume_threshold=-10.0
    )

  def test_determine_video_cue_points(self):
    fake_video_analyzer = video_analysis.FakeVideoAnalyzer(
        detect_shot_responses=[_TEST_SHOT_DETECT_RESPONSE]
    )

    cue_points = cue_point_generator.determine_video_cue_points(
        "video_uri", fake_video_analyzer
    )

    self.assertEqual(cue_points, [0, 60.2])

  def test_determine_video_cue_points_first_cue(self):
    fake_video_analyzer = video_analysis.FakeVideoAnalyzer(
        detect_shot_responses=[_TEST_SHOT_DETECT_RESPONSE]
    )

    cue_points = cue_point_generator.determine_video_cue_points(
        "video_uri", fake_video_analyzer, minimum_time_for_first_cue_point=10.0
    )

    self.assertEqual(cue_points, [12.2, 60.2])

  def test_determine_video_cue_points_between_cues(self):
    fake_video_analyzer = video_analysis.FakeVideoAnalyzer(
        detect_shot_responses=[_TEST_SHOT_DETECT_RESPONSE]
    )

    cue_points = cue_point_generator.determine_video_cue_points(
        "video_uri", fake_video_analyzer, minimum_time_between_cue_points=5.0
    )

    self.assertEqual(cue_points, [0.0, 12.2, 60.2, 65.8])


if __name__ == "__main__":
  unittest.main()
