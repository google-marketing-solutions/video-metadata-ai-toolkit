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
"""Determines optimal cue points based on shot changes and audio."""

import sys
import argparse
import shot_detection

from google.cloud import videointelligence


class _ShotChange(shot_detection.VideoSegment):
  volume: float | None = None


def _calculate_optimal_cue_points(
    shot_changes: list[_ShotChange],
    minimum_time_for_first_cue_point: float = 0.0,
    minimum_time_between_cue_points: float = 30.0,
    maximum_volume: float = -25.0,
) -> list[float]:
  """Calculates optimal cue point times for a list of shot changes.

  Args:
    shot_changes: A list of ShotChange objects
    minimum_time_for_first_cue_point: A float, the earliest time, in seconds,
      that can be returned in the list of cue points. Defaults to 0.0, which
      will always be included in the output if provided.
    minimum_time_between_cue_points: A float, the shortest amount of time, in
      seconds,to allow between cue points. Defaults to 30 seconds.
    maximum_volume: A float, the maximum volume, in db, for the shot change to
      be included as a cue point. Defaults to -25.0, and will be a no-op if
      the shot changes don't have volume values.

  Returns
    A list of floats representing the optimal cue points, in seconds.
  """
  shot_changes = sorted(shot_changes, key=lambda s: s.start_time)
  cue_points = []
  for shot_change in shot_changes:
    cue_point = (
        shot_change.start_time
        + (shot_change.end_time - shot_change.start_time) / 2
    )
    is_at_or_after_min_time = cue_point >= minimum_time_for_first_cue_point
    is_quiet_enough = (
        not shot_change.volume or shot_change.volume <= maximum_volume
    )
    is_long_enough_after_prev_cue_point = (
        len(cue_points) == 0
        or (cue_point - minimum_time_between_cue_points) >= cue_points[-1]
    )
    if (
        is_at_or_after_min_time
        and is_quiet_enough
        and is_long_enough_after_prev_cue_point
    ):
      cue_points.append(cue_point)
  return cue_points


def determine_video_cue_points_gcp(
    video_uri: str,
    video_intelligence_client: videointelligence.VideoIntelligenceServiceClient,
    minimum_time_for_first_cue_point: float = 0.0,
    minimum_time_between_cue_points: float = 30.0,
) -> list[float]:
  """Determines the best cue points for a video hosted on GCS.

  Args:
    video_uri: A string, the URI for the video in the format gs://path/to/video
    video_intelligence_client: The VideoIntelligenceServiceClient to use for
      shot detection.
    minimum_time_for_first_cue_point: The earliest time, in seconds, that will
      be returned as a cue point. Defaults to 0.0, which corresponds to a
      pre-roll.
    minimum_time_between_cue_points: The smallest amount of time, in seconds,
      to allow between any two sequential cue points. Defaults to 30.0 seconds.

  Returns:
    A list of floats with the recommended cue points, in seconds.
  """
  video_segments = shot_detection.detect_shot_changes_gcp(
      video_uri, video_intelligence_client
  )
  shot_changes = []
  shot_changes.append(_ShotChange(start_time=0.0, end_time=0.0))
  for i, video_segment in enumerate(video_segments):
    shot_change_start = video_segment.end_time
    if i + 1 < len(video_segments):
      shot_change_end = video_segments[i + 1].start_time
    else:
      shot_change_end = video_segment.end_time
    shot_changes.append(
        _ShotChange(start_time=shot_change_start, end_time=shot_change_end)
    )
  return _calculate_optimal_cue_points(
      shot_changes,
      minimum_time_for_first_cue_point,
      minimum_time_between_cue_points,
  )


def _parse_args(args) -> argparse.Namespace:
  argparser = argparse.ArgumentParser(
      description=(
          "Determines the optimal cue points for a given video file based on"
          "shot changes."
      )
  )
  argparser.add_argument(
      "video",
      type=str,
      help=(
          "The location of the video. For videos on GCS, this is the URI in "
          "the format: gs://path/to/video. Local video files are not currently"
          " supported."
      ),
  )
  argparser.add_argument(
      "--first_cue",
      "-f",
      type=float,
      default=0.0,
      help=(
          "The earliest time that a cue point should be created. Defaults to "
          "0.0."
      ),
  )
  argparser.add_argument(
      "--between_cues",
      "-b",
      type=float,
      default=30.0,
      help=(
          "The minimum amount of time that should be between two cue points. "
          "Defaults to 30.0."
      ),
  )
  return argparser.parse_args(args)


def main(args=sys.argv[1:]):
  args = _parse_args(args)
  if args.video.startswith("gs://"):
    cue_points = determine_video_cue_points_gcp(
        args.video,
        videointelligence.VideoIntelligenceServiceClient(),
        minimum_time_for_first_cue_point=args.first_cue,
        minimum_time_between_cue_points=args.between_cues,
    )
    print("Recommended cue points: ", cue_points)
  else:
    print("Local shot detection not yet implemented.")


if __name__ == "__main__":
  main()
