#!/usr/bin/env python

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module is responsible for generating metadata from live/streaming files.

This code is meant to be executed standalone and accepts a URL of a
live-streaming .m3u8 file such that it captures three pairs of screenshots,
beginning, middle and end, from the latest .TS file from the stream considering
the medium quality bitrate and submits each individual screenshot to Google's
Cloud Vision API for metadata generation. A dictionary is returned with the
label and the frequency of each in descending order.

Typical usage example:

  python3 image_metadata_live.py labels \
    https://example-live-stream.com/master.m3u8 0.70 --persist

PLEASE NOTE: REGEX is still not Generic! Will have to adapt depending on
the stream/.TS File format.
"""

import argparse
import datetime
import operator
import os
import re
import urllib.request as urllib

import ffmpeg
import image_metadata_utils as utils

LOCAL_MP4_FILE = "local_mp4_file.mp4"
LOCAL_TS_FILE = "local_ts_file.ts"
OUTPUT_FILE_PREFIX = "stream_mdd_"
SCREENSHOT_1_FILE = "./begin1.jpg"
SCREENSHOT_2_FILE = "./begin2.jpg"
SCREENSHOT_3_FILE = "./middle1.jpg"
SCREENSHOT_4_FILE = "./middle2.jpg"
SCREENSHOT_5_FILE = "./end1.jpg"
SCREENSHOT_6_FILE = "./end2.jpg"
SCREENSHOT_WIDTH_PX = 500


def generate_metadata(url: str, confidence: int) -> list[str, dict[str, int]]:
  """Main code logic execution.

  Saves screenshot files locally, fetches metadata for each image and outputs
   dictionary with labels, frequency of each and the timestamp.

  Args: in_args.command: A string. Currently only "labels" supported
  in_args.url: A string. URL of stream .m3u8 file to be processed.
  in_args.conf_threshold: A float between 0 and 1. Represents confidence
  threshold to consider when detecting labels.

  Returns:
      An array where the first element is a string timestamp of execution and
      the next is a dict mapping string labels related to metadata of each print
      and their int frequency of appeareance in descending order. For
      example:

      ['2024-02-23 10:48:38.459056', [('Wood', 6), ('Audio equipment', 1),
      ('Handwriting', 1), ('Technology', 1)]]
  """

  time_stamp = str(datetime.datetime.now())
  _get_frames(url)

  return_dict = {}
  utils.detect_labels_dict(SCREENSHOT_1_FILE, return_dict, confidence)
  utils.detect_labels_dict(SCREENSHOT_2_FILE, return_dict, confidence)
  utils.detect_labels_dict(SCREENSHOT_3_FILE, return_dict, confidence)
  utils.detect_labels_dict(SCREENSHOT_4_FILE, return_dict, confidence)
  utils.detect_labels_dict(SCREENSHOT_5_FILE, return_dict, confidence)
  utils.detect_labels_dict(SCREENSHOT_6_FILE, return_dict, confidence)

  return_dict = sorted(
      return_dict.items(), key=operator.itemgetter(1), reverse=True
  )
  return_dict_with_time = [time_stamp, return_dict]

  return return_dict_with_time


def _get_frames(url: str) -> list[str]:
  """Get frames from video and calls method to generate sceenshoot from frames.

  Initially fetches base url from stream, followed by the manifest, followed
  by the medium quality bitrate stream, followed by the .TS segment files. Then
  fetches the most recent .TS file, calculates its duration and corresponding
  seconds of where each pair of frames will be collected, beginning, middle
  and end. Downloads .TS file locally and converts to .mp4 such that it can be
  processed by ffmpeg. Then three pairs of frames are saved locally respecting
  the seconds previously calculated. The frames are begin1.jpg (at the
  beginning), begin2.jpg (1 second later), middle1.jpg (at the middle),
  middle2.jpg (1 second later), end1.jpg (0.5 seconds before end), end2.jpg
  (-0.5 seconds prior).

  Args:
      url: A string. URL of stream .m3u8 file to be processed.

  Returns:
      Output screenshot names saved locally: begin1.jpg, begin2,jpg,
      middle1.jpg, middle2.jpg, end1.jpg, end2.jpg.
  """

  base = _get_base(url)
  streams = _get_manifest(url)
  manif_selected = base + "/" + streams[round(len(streams) / 2)]
  segments = _get_ts_segments(manif_selected)
  seg_selected = base + "/" + segments[round(len(segments) - 1)]

  duration = float(utils.get_video_duration(seg_selected))
  duration_tenth = duration / 10
  begin_seconds = duration_tenth
  middle_seconds = duration / 2
  end_seconds = duration

  _download_file(seg_selected, LOCAL_TS_FILE)

  _convert_ts_to_mp4(LOCAL_TS_FILE, LOCAL_MP4_FILE)
  utils.generate_screenshot(
      LOCAL_MP4_FILE, SCREENSHOT_1_FILE, begin_seconds, SCREENSHOT_WIDTH_PX
  )
  utils.generate_screenshot(
      LOCAL_MP4_FILE,
      SCREENSHOT_2_FILE,
      begin_seconds + duration_tenth,
      SCREENSHOT_WIDTH_PX,
  )
  utils.generate_screenshot(
      LOCAL_MP4_FILE, SCREENSHOT_3_FILE, middle_seconds, SCREENSHOT_WIDTH_PX
  )
  utils.generate_screenshot(
      LOCAL_MP4_FILE,
      SCREENSHOT_4_FILE,
      middle_seconds + duration_tenth,
      SCREENSHOT_WIDTH_PX,
  )
  utils.generate_screenshot(
      LOCAL_MP4_FILE,
      SCREENSHOT_5_FILE,
      end_seconds - duration_tenth * 2,
      SCREENSHOT_WIDTH_PX,
  )
  utils.generate_screenshot(
      LOCAL_MP4_FILE,
      SCREENSHOT_6_FILE,
      end_seconds - duration_tenth,
      SCREENSHOT_WIDTH_PX,
  )

  return [
      SCREENSHOT_1_FILE,
      SCREENSHOT_2_FILE,
      SCREENSHOT_3_FILE,
      SCREENSHOT_4_FILE,
      SCREENSHOT_5_FILE,
      SCREENSHOT_6_FILE,
  ]


def _get_base(url: str) -> str:
  """Gets the base URL from stream .m3u8 file.

  Args:
      url: A string. URL of stream .m3u8 file to be processed.

  Returns:
      A string pertaining to the base url, such as:
      www.streamdomain.com
  """
  # TODO: Genericize regex to support various m3u8/ts formats.
  sequence0 = re.compile(r"(https?\:\/\/.*)(/.*?\.m3u8)", re.MULTILINE)
  base = re.findall(sequence0, str(url))[0][0]
  return base


def _get_manifest(url: str) -> list[str]:
  """Get manifest entries from base URL.

  Args:
      url: A string. URL of stream .m3u8 file to be processed.

  Returns:
      An array of strings pertaining to the manifest file of stream.
  """
  # TODO: Genericize regex to support various m3u8/ts formats.
  with urllib.urlopen(url) as response:
    content = response.read()

  sequence1 = re.compile(r"([^\\n]+\.m3u8)", re.MULTILINE)
  streams = re.findall(sequence1, str(content))
  return streams


def _get_ts_segments(url: str) -> list[str]:
  """Gets .ts file names from selected manifest URL.

  Args:
      url: A string. URL of stream .m3u8 file to be processed.

  Returns:
      An array of strings pertaining to the .ts file names of the stream.
  """
  # TODO: Genericize regex to support various m3u8/ts formats.
  with urllib.urlopen(url) as response:
    content = response.read()

  sequence2 = re.compile(r"segment_.*?\.ts(?=\W)", re.MULTILINE)
  segments = re.findall(sequence2, str(content))
  return segments


def _convert_ts_to_mp4(input_file: str, output_file: str) -> str:
  """Converts ts file to .mp4 file for processing.

  Args:
      input_file: A string ot the .ts file path and name to be converted.
      output_file: A string of .mp4 file path and name to be generated.

  Returns:
      A string of the generated screenshot file name.

  Raises:
      ffmpeg.Error: An error during conversion.
  """

  try:
    (
        ffmpeg.input(input_file)
        .output(output_file, vcodec="libx264", acodec="aac")
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
  except ffmpeg.Error as e:
    print(f"Error converting file: {e.stderr.decode()}")
    raise e from None

  return output_file


def _download_file(url: str, filename: str = None) -> str:
  """Downloads latest .ts file from stream locally

  Args:
      url: A string. URL of the file to be downloaded locally.
      filename: A string of the filename to be saved as.

  Returns:
      A string of the saved file name.
  """

  if filename is None:
    filename = os.path.basename(url)
  urllib.urlretrieve(url, filename)

  return filename


def _clean_up() -> list[str]:
  """Cleans local files used for processing.

  Returns:
      An array of strings of the removed files.
  """
  utils.remove_local_file(SCREENSHOT_1_FILE)
  utils.remove_local_file(SCREENSHOT_2_FILE)
  utils.remove_local_file(SCREENSHOT_3_FILE)
  utils.remove_local_file(SCREENSHOT_4_FILE)
  utils.remove_local_file(SCREENSHOT_5_FILE)
  utils.remove_local_file(SCREENSHOT_6_FILE)
  utils.remove_local_file(LOCAL_MP4_FILE)
  utils.remove_local_file(LOCAL_TS_FILE)

  return [
      SCREENSHOT_1_FILE,
      SCREENSHOT_2_FILE,
      SCREENSHOT_3_FILE,
      SCREENSHOT_4_FILE,
      SCREENSHOT_5_FILE,
      SCREENSHOT_6_FILE,
      LOCAL_MP4_FILE,
      LOCAL_TS_FILE,
  ]


def main(in_args: object):
  """main function. Generates and saves output to file and cleans if neeeded."""

  url = in_args.url
  confidence = in_args.conf_threshold
  return_dict_with_time = generate_metadata(url, confidence)
  utils.dict_output_to_file(OUTPUT_FILE_PREFIX, return_dict_with_time)

  if not in_args.persist_files:
    _clean_up()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
  )
  subparsers = parser.add_subparsers(dest="command")
  main_parser = subparsers.add_parser("labels", help=main.__doc__)
  main_parser.add_argument("url")
  main_parser.add_argument("conf_threshold")
  main_parser.add_argument(
      "--persist", dest="persist_files", action="store_true"
  )
  main_parser.add_argument(
      "--no-persist", dest="persist_files", action="store_false"
  )
  args = parser.parse_args()
  main(args)
