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
"""VideoAnalyzer handles video analysis operations."""

import abc
import dataclasses
import re

import ffmpeg
from google.cloud import videointelligence


@dataclasses.dataclass()
class VideoSegment:
  start_time: float
  end_time: float


class VideoAnalyzer(abc.ABC):

  @abc.abstractmethod
  def detect_shot_changes(
      self,
      video: str,
      volume_threshold: float | None = None,
  ) -> list[VideoSegment]:
    raise NotImplementedError()


class FakeVideoAnalyzer(VideoAnalyzer):
  """Fake implementation of VideoAnalyzer for use in tests."""

  def __init__(self, detect_shot_responses: list[list[VideoSegment]]) -> None:
    self._detect_shot_responses = iter(detect_shot_responses)
    super().__init__()

  # pylint: disable=unused-argument
  def detect_shot_changes(
      self, video: str, volume_threshold: float | None = None
  ):
    return next(self._detect_shot_responses)

  # pylint: enable=unused-argument


class CloudVideoAnalyzer(VideoAnalyzer):
  """Analyzes video content using Cloud's Video Intelligence API's."""

  def __init__(
      self,
      client: videointelligence.VideoIntelligenceServiceClient,
  ) -> None:
    """Initializes the analyzer with a VideoIntelligenceServiceClient.

    Args:
      client: The VideoIntelligenceServiceClient instance to use for video
        analysis.
    """
    self._video_intelligence_client = client
    super().__init__()

  def detect_shot_changes(
      self, video: str, volume_threshold: float | None = None
  ) -> list[VideoSegment]:
    """Determines the distinct segments of a video using shot changes.

    Args:
      video: The uri of the video. Should be in the format gs://path/to/video
      volume_threshold: Currently a no-op. GCP's shot detection does not
        support a volume threshold.

    Returns:
      A list of VideoSegments for the video.
    """
    features = [videointelligence.Feature.SHOT_CHANGE_DETECTION]
    operation = self._video_intelligence_client.annotate_video(
        request={"features": features, "input_uri": video}
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


class FfmpegVideoAnalyzer(VideoAnalyzer):
  """Analyzes video content using FFMPEG."""

  def __init__(self, ffmpeg_python: ffmpeg = ffmpeg) -> None:
    """Initializes the analyzer with an instance of FFMPEG Python.

    Args:
      ffmpeg_python: The FFMPEG Python instance to use for video analysis.
    """
    self._ffmpeg = ffmpeg_python
    super().__init__()

  def detect_shot_changes(
      self,
      video: str,
      volume_threshold: float | None = None,
  ) -> list[VideoSegment]:
    """Determines the distinct segments of a video using shot changes.

    Shot change detection is handled by FFMPEG's scene filter. If a
    volume_threshold is specified, the silencedetect filter will also be used
    to further filter the shot changes by volume. This function
    supports both local videos and videos hosted online.

    Streaming formats like HLS are not currently supported. Convert to a
    non-streaming format first.

    Args:
      video: The path for the video. Should be in the format gs://path/to/video
      volume_threshold: If provided, shot changes must be below this volume, in
        dB to be included in the results.

    Returns:
      A list of VideoSegments for the video.
    """
    probe_results = self._ffmpeg.probe(video)
    video_info = next(
        stream
        for stream in probe_results["streams"]
        if stream["codec_type"] == "video"
    )
    video_start_time = float(video_info["start_time"])
    video_duration = float(video_info["duration"])
    video_total_frames = int(video_info["nb_frames"])
    seconds_per_frame = video_duration / video_total_frames

    input_stream = self._ffmpeg.input(video)
    video_stream = input_stream.video.filter("select", "gt(scene,0.3)").filter(
        "showinfo"
    )
    # if no volume threshold is specified, use a large enough value to
    # ensure that all of the shot changes are eligible
    volume_threshold = volume_threshold or 1_000.0
    audio_stream = input_stream.audio.filter(
        "silencedetect", n=f"{volume_threshold}dB", d=0.25
    )
    _, message = self._ffmpeg.output(
        video_stream,
        audio_stream,
        "pipe:",
        format="null",
    ).run(quiet=True)
    ffmpeg_ouput = message.decode()
    # filter output to only include entries within the volume threshold (between
    # "silent_start:" and "silent_end:")
    silent_output_sections = [
        silent_section
        for silent_section in re.findall(
            r"silence_start:([\s\S]*?)silence_end", ffmpeg_ouput
        )
    ]
    silent_output = "\n".join(silent_output_sections)
    # parse out timestamps from the scene detect filter
    shot_change_timestamps = [
        float(pts_string)
        for pts_string in re.findall(
            r"Parsed_showinfo.+pts_time:([^\s]+)", silent_output
        )
    ]
    if not shot_change_timestamps:
      return [VideoSegment(0.0, video_duration)]
    video_segments = []
    shot_change_timestamps = [video_start_time] + shot_change_timestamps
    for i, shot_start_time in enumerate(shot_change_timestamps):
      end_pts = (
          shot_change_timestamps[i + 1] - seconds_per_frame
          if i + 1 < len(shot_change_timestamps)
          else video_duration
      )
      video_segments.append(VideoSegment(shot_start_time, end_pts))
    return video_segments
