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
"""This module contains tests for the shot_detection module."""

import unittest
from unittest import mock
import math

from google.cloud import videointelligence
import shot_detection


def create_gcp_video_segment(
    start_offset: float, end_offset: float
) -> videointelligence.VideoSegment:
  start_seconds = int(math.floor(start_offset))
  start_nanos = int((start_offset - start_seconds) * 1e9)
  end_seconds = int(math.floor(end_offset))
  end_nanos = int((end_offset - end_seconds) * 1e9)
  return videointelligence.VideoSegment(
      {
          "start_time_offset": {
              "seconds": start_seconds,
              "nanos": start_nanos,
          },
          "end_time_offset": {
              "seconds": end_seconds,
              "nanos": end_nanos,
          },
      }
  )


class ShotDetectionTest(unittest.TestCase):

  def test_detect_shot_changes_gcp_calls_annotate_video(self):
    mock_video_intelligence_client = mock.MagicMock(
        spec=videointelligence.VideoIntelligenceServiceClient
    )

    shot_detection.detect_shot_changes_gcp(
        "video_uri", mock_video_intelligence_client
    )

    mock_video_intelligence_client.annotate_video.assert_called_once_with(
        request={
            "features": [videointelligence.Feature.SHOT_CHANGE_DETECTION],
            "input_uri": "video_uri",
        }
    )

  def test_detect_shot_changes_gcp(self):
    mock_video_intelligence_client = mock.MagicMock(
        spec=videointelligence.VideoIntelligenceServiceClient
    )
    mock_operation = mock_video_intelligence_client.annotate_video.return_value
    mock_operation.result.return_value = (
        videointelligence.AnnotateVideoResponse(
            annotation_results=[
                videointelligence.VideoAnnotationResults(
                    shot_annotations=[
                        create_gcp_video_segment(0.0, 15.3),
                        create_gcp_video_segment(15.9, 30.1),
                        create_gcp_video_segment(30.3, 34.5),
                    ]
                )
            ]
        )
    )

    video_segments = shot_detection.detect_shot_changes_gcp(
        "video_uri", mock_video_intelligence_client
    )

    self.assertEqual(
        video_segments,
        [
            shot_detection.VideoSegment(0.0, 15.3),
            shot_detection.VideoSegment(15.9, 30.1),
            shot_detection.VideoSegment(30.3, 34.5),
        ],
    )


if __name__ == "__main__":
  unittest.main()
