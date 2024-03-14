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
"""This module calculates shot changes for a given video file."""

import dataclasses
from google.cloud import videointelligence


@dataclasses.dataclass()
class VideoSegment:
  start_time: float
  end_time: float


def detect_shot_changes_gcp(
    video_uri: str,
    video_intelligence_client: videointelligence.VideoIntelligenceServiceClient,
) -> list[VideoSegment]:
  """Identifies segments of a video based on shot changes.

  Shot change detection is handled by the Video Intelligence API.

  Args:
    video_uri: A URI, as a string, pointing to the video.
    video_client: The VideoIntelligenceServiceClient to use for shot detection.

  Returns:
    A list of VideoSegment objects for the video.
  """
  features = [videointelligence.Feature.SHOT_CHANGE_DETECTION]
  operation = video_intelligence_client.annotate_video(
      request={"features": features, "input_uri": video_uri}
  )
  result = operation.result(timeout=1000)
  shot_annotations = result.annotation_results[0].shot_annotations
  video_segments = []
  for shot_annotation in shot_annotations:
    start_time = shot_annotation.start_time_offset.seconds + (
        shot_annotation.start_time_offset.microseconds / 1e6
    )
    end_time = shot_annotation.end_time_offset.seconds + (
        shot_annotation.end_time_offset.microseconds / 1e6
    )
    video_segments.append(VideoSegment(start_time, end_time))
  return video_segments
