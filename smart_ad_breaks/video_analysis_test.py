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
"""This module contains tests for the video_analysis module."""

import math
import unittest
from unittest import mock

import ffmpeg
from google.cloud import videointelligence
import video_analysis


class FakeVideoAnalyzerTest(unittest.TestCase):

  def test_detect_shot_changes(self):
    shot_detect_responses = [
        [video_analysis.VideoSegment(0.0, 1.0)],
        [video_analysis.VideoSegment(0.0, 2.0)],
    ]
    fake_video_analyzer = video_analysis.FakeVideoAnalyzer(
        detect_shot_responses=shot_detect_responses
    )

    self.assertEqual(
        fake_video_analyzer.detect_shot_changes("video_path"),
        shot_detect_responses[0],
    )

  def test_detect_shot_changes_mulitple_responses(self):
    shot_detect_responses = [
        [video_analysis.VideoSegment(0.0, 1.0)],
        [video_analysis.VideoSegment(0.0, 2.0)],
    ]
    fake_video_analyzer = video_analysis.FakeVideoAnalyzer(
        detect_shot_responses=shot_detect_responses
    )

    fake_video_analyzer.detect_shot_changes("video_path")
    self.assertEqual(
        fake_video_analyzer.detect_shot_changes("video_path"),
        shot_detect_responses[1],
    )


def _create_gcp_video_segment(
    start_offset: float, end_offset: float
) -> videointelligence.VideoSegment:
  start_seconds = int(math.floor(start_offset))
  start_nanos = int((start_offset - start_seconds) * 1e9)
  end_seconds = int(math.floor(end_offset))
  end_nanos = int((end_offset - end_seconds) * 1e9)
  return videointelligence.VideoSegment({
      "start_time_offset": {
          "seconds": start_seconds,
          "nanos": start_nanos,
      },
      "end_time_offset": {
          "seconds": end_seconds,
          "nanos": end_nanos,
      },
  })


@mock.patch.object(
    videointelligence, "VideoIntelligenceServiceClient", autospec=True
)
class CloudVideoAnalyzerTest(unittest.TestCase):

  def test_detect_shot_changes_gcp_calls_annotate_video(
      self, mock_video_intelligence_client
  ):
    cloud_video_analyzer = video_analysis.CloudVideoAnalyzer(
        mock_video_intelligence_client
    )
    cloud_video_analyzer.detect_shot_changes("video_uri")

    mock_video_intelligence_client.annotate_video.assert_called_once_with(
        request={
            "features": [videointelligence.Feature.SHOT_CHANGE_DETECTION],
            "input_uri": "video_uri",
        }
    )

  def test_detect_shot_changes(self, mock_video_intelligence_client):
    mock_operation = mock_video_intelligence_client.annotate_video.return_value
    mock_operation.result.return_value = (
        videointelligence.AnnotateVideoResponse(
            annotation_results=[
                videointelligence.VideoAnnotationResults(
                    shot_annotations=[
                        _create_gcp_video_segment(0.0, 15.3),
                        _create_gcp_video_segment(15.9, 30.1),
                        _create_gcp_video_segment(30.3, 34.5),
                    ]
                )
            ]
        )
    )

    cloud_video_analyzer = video_analysis.CloudVideoAnalyzer(
        mock_video_intelligence_client
    )
    video_segments = cloud_video_analyzer.detect_shot_changes("video_uri")

    self.assertEqual(
        video_segments,
        [
            video_analysis.VideoSegment(0.0, 15.3),
            video_analysis.VideoSegment(15.9, 30.1),
            video_analysis.VideoSegment(30.3, 34.5),
        ],
    )


# This is a partial version of the ffprobe response. Add more fields as
# necessary for testing.
_TEST_FFMPEG_PROBE_RESULTS = {
    "streams": [
        {
            "codec_type": "video",
            "start_time": "0.000",
            "duration": "100.0",
            "nb_frames": "400",
        },
        {"codec_type": "audio", "duration": "100.1"},
    ]
}


class FfmpegVideoAnalyzerTest(unittest.TestCase):

  def test_detect_shot_changes_uses_scene_filter_and_silece_detect(self):
    wrapped_ffmpeg = mock.MagicMock(wraps=ffmpeg)
    wrapped_ffmpeg.probe.return_value = _TEST_FFMPEG_PROBE_RESULTS
    wrapped_ffmpeg.run.return_value = (
        "unused",
        str.encode("ffmpeg output string"),
    )
    ffmpeg_video_analyzer = video_analysis.FfmpegVideoAnalyzer(wrapped_ffmpeg)

    ffmpeg_video_analyzer.detect_shot_changes("video_path", -25.0)

    expected_input_stream = wrapped_ffmpeg.input("video_path")
    video_stream = expected_input_stream.video.filter(
        "select", "gt(scene,0.3)"
    ).filter("showinfo")
    audio_stream = expected_input_stream.audio.filter(
        "silencedetect", n="-25.0dB", d=0.25
    )
    wrapped_ffmpeg.output.assert_called_once_with(
        video_stream, audio_stream, "pipe:", format="null"
    )

  def test_detect_shot_changes_volume_thresh_1000_if_none(self):
    wrapped_ffmpeg = mock.MagicMock(wraps=ffmpeg)
    wrapped_ffmpeg.probe.return_value = _TEST_FFMPEG_PROBE_RESULTS
    wrapped_ffmpeg.run.return_value = (
        "unused",
        str.encode("ffmpeg output string"),
    )
    ffmpeg_video_analyzer = video_analysis.FfmpegVideoAnalyzer(wrapped_ffmpeg)

    ffmpeg_video_analyzer.detect_shot_changes("video_path", None)

    audio_stream = wrapped_ffmpeg.input("video_path").audio.filter(
        "silencedetect", n="1000.0dB", d=0.25
    )
    wrapped_ffmpeg.output.assert_called_once_with(
        mock.ANY, audio_stream, "pipe:", format="null"
    )

  def test_detect_shot_changes_no_shots_returns_one_segment(self):
    wrapped_ffmpeg = mock.MagicMock(wraps=ffmpeg)
    wrapped_ffmpeg.probe.return_value = _TEST_FFMPEG_PROBE_RESULTS
    wrapped_ffmpeg.run.return_value = (
        "unused",
        str.encode("ffmpeg output string with no shots detected"),
    )
    ffmpeg_video_analyzer = video_analysis.FfmpegVideoAnalyzer(wrapped_ffmpeg)

    video_segments = ffmpeg_video_analyzer.detect_shot_changes("video_path")

    self.assertEqual(video_segments, [video_analysis.VideoSegment(0.0, 100.0)])

  def test_detect_shot_changes(self):
    wrapped_ffmpeg = mock.MagicMock(wraps=ffmpeg)
    wrapped_ffmpeg.probe.return_value = _TEST_FFMPEG_PROBE_RESULTS
    ffmpeg_output_string = (
        "[silencedetect @ 0x55d381c9e340] silence_start: 65.2051trate=N/A"
        " speed=40.5x\n[Parsed_showinfo_1 @ 0x55d381c9e100] n:  21 pts:   1969"
        " pts_time:65.6333 duration:      1 duration_time:0.0333333 fmt:yuv420p"
        " cl:left sar:1/1 s:1280x720 i:P iskey:1 type:I checksum:06EF2934"
        " plane_checksum:[46DED666 A0342EB7 9A392408] mean:[73 127 130]"
        " stdev:[60.1 9.5 10.1]\n[Parsed_showinfo_1 @ 0x55d381c9e100]"
        " color_range:unknown color_space:unknown color_primaries:unknown"
        " color_trc:unknown[silencedetect @ 0x55d381c9e340] silence_end:"
        " 65.7935 | silence_duration: 0.588417\n"
    )
    wrapped_ffmpeg.run.return_value = (
        "unused",
        str.encode(ffmpeg_output_string),
    )
    ffmpeg_video_analyzer = video_analysis.FfmpegVideoAnalyzer(wrapped_ffmpeg)

    video_segments = ffmpeg_video_analyzer.detect_shot_changes("video_path")

    self.assertEqual(
        video_segments,
        [
            video_analysis.VideoSegment(0.0, 65.3833),
            video_analysis.VideoSegment(65.6333, 100.0),
        ],
    )


if __name__ == "__main__":
  unittest.main()
