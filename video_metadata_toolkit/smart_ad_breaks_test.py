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
import smart_ad_breaks
import shot_detection


@mock.patch.object(shot_detection, "detect_shot_changes_gcp", autospec=True)
class SmartAdBreaksTest(unittest.TestCase):

  def test_determine_video_cue_points_gcp_uses_shot_detection(
      self, mock_detect_shots_gcp
  ):
    mock_video_client = mock.MagicMock()
    smart_ad_breaks.determine_video_cue_points_gcp(
        "video_uri", video_intelligence_client=mock_video_client
    )

    mock_detect_shots_gcp.assert_called_once_with(
        "video_uri", video_intelligence_client=mock_video_client
    )

  def test_determine_video_cue_points_gcp(self, mock_detect_shots_gcp):
    mock_detect_shots_gcp.return_value = [
        shot_detection.VideoSegment(0.0, 12.1),
        shot_detection.VideoSegment(12.3, 12.5),
        shot_detection.VideoSegment(12.7, 60.1),
        shot_detection.VideoSegment(60.3, 60.8),
        shot_detection.VideoSegment(65.3, 65.8),
    ]

    cue_points = smart_ad_breaks.determine_video_cue_points_gcp(
        "video_uri", video_intelligence_client=mock.MagicMock()
    )

    self.assertEqual(cue_points, [0, 60.2])

  def test_determine_video_cue_points_gcp_first_cue(
      self, mock_detect_shots_gcp
  ):
    mock_detect_shots_gcp.return_value = [
        shot_detection.VideoSegment(0.0, 12.1),
        shot_detection.VideoSegment(12.3, 12.5),
    ]

    cue_points = smart_ad_breaks.determine_video_cue_points_gcp(
        "video_uri",
        video_intelligence_client=mock.MagicMock(),
        minimum_time_for_first_cue_point=10.0,
    )

    self.assertEqual(cue_points, [12.2])

  def test_determine_video_cue_points_gcp_between_cues(
      self, mock_detect_shots_gcp
  ):
    mock_detect_shots_gcp.return_value = [
        shot_detection.VideoSegment(0.0, 12.1),
        shot_detection.VideoSegment(12.3, 12.5),
    ]

    cue_points = smart_ad_breaks.determine_video_cue_points_gcp(
        "video_uri",
        video_intelligence_client=mock.MagicMock(),
        minimum_time_between_cue_points=10.0,
    )

    self.assertEqual(cue_points, [0, 12.2])


if __name__ == "__main__":
  unittest.main()
