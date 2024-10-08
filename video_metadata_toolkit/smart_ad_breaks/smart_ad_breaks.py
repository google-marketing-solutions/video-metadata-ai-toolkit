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

import video_analysis

from google.cloud import videointelligence


def _calculate_optimal_cue_points(
    potential_cue_points: list[float],
    minimum_time_for_first_cue_point: float = 0.0,
    minimum_time_between_cue_points: float = 30.0,
) -> list[float]:
  """Calculates optimal cue point times for a list of potential cue points.

  Args:
    potential_cue_points: A list of floats representing possible cue points.
    minimum_time_for_first_cue_point: A float, the earliest time, in seconds,
      that can be returned in the list of cue points. Defaults to 0.0, which
      will always be included in the output if provided.
    minimum_time_between_cue_points: A float, the shortest amount of time, in
      seconds,to allow between cue points. Defaults to 30 seconds.

  Returns
    A list of floats representing the optimal cue points, in seconds.
  """
  sorted_potential_cue_points = sorted(potential_cue_points)
  cue_points = []
  for cue_point in sorted_potential_cue_points:
    is_at_or_after_min_time = cue_point >= minimum_time_for_first_cue_point
    is_long_enough_after_prev_cue_point = (
        len(cue_points) == 0
        or (cue_point - minimum_time_between_cue_points) >= cue_points[-1]
    )
    if is_at_or_after_min_time and is_long_enough_after_prev_cue_point:
      cue_points.append(cue_point)
  return cue_points


def determine_video_cue_points(
    video_path_or_uri: str,
    video_analyzer: video_analysis.VideoAnalyzer,
    minimum_time_for_first_cue_point: float = 0.0,
    minimum_time_between_cue_points: float = 30.0,
    volume_threshold: float | None = None,
) -> list[float]:
  """Determines the best cue points for a video file based on shot changes.

  Args:
    video_path_or_uri: A string, the location of the video file
    minimum_time_for_first_cue_point: The earliest time, in seconds, that will
      be returned as a cue point. Defaults to 0.0, which corresponds to a
      pre-roll.
    minimum_time_between_cue_points: The smallest amount of time, in seconds,
      to allow between any two sequential cue points. Defaults to 30.0 seconds.
    volume_threshold: The maximum volume threshold for a cue point. Can be used
      to eliminate shot changes that may have dialogue or other important
      audio. This is currently a no-op for files hosted on GCP.

  Returns:
    A list of floats with the recommended cue points, in seconds.
  """
  video_segments = video_analyzer.detect_shot_changes(
      video_path_or_uri, volume_threshold=volume_threshold
  )
  potential_cue_points = [0.0]
  for i, segment in enumerate(video_segments):
    if i + 1 < len(video_segments):
      potential_cue_point = (
          segment.end_time
          + (video_segments[i + 1].start_time - segment.end_time) / 2
      )
    else:
      potential_cue_point = segment.end_time
    potential_cue_points.append(potential_cue_point)
  return _calculate_optimal_cue_points(
      potential_cue_points,
      minimum_time_for_first_cue_point=minimum_time_for_first_cue_point,
      minimum_time_between_cue_points=minimum_time_between_cue_points,
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
  argparser.add_argument(
      "--volume_threshold",
      "-v",
      type=float,
      default=None,
      help=(
          "If provided, the maximum in volume, in dB, for a cue point. This is"
          " always a no-op for files hosted on GCP."
      ),
  )
  return argparser.parse_args(args)


def main(args=sys.argv[1:]):
  args = _parse_args(args)
  if args.video.startswith("gs://"):
    video_intel_client = videointelligence.VideoIntelligenceServiceClient()
    video_analyzer = video_analysis.CloudVideoAnalyzer(video_intel_client)
  else:
    video_analyzer = video_analysis.FfmpegVideoAnalyzer()
  cue_points = determine_video_cue_points(
      args.video,
      video_analyzer,
      minimum_time_for_first_cue_point=args.first_cue,
      minimum_time_between_cue_points=args.between_cues,
      volume_threshold=args.volume_threshold,
  )
  print("Recommended cue points: ", cue_points)


if __name__ == "__main__":
  main()
