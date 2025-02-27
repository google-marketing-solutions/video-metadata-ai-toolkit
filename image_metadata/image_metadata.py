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

"""This module is responsible for generating metadata from .mp4 files.

This code is meant to be executed standalone and accepts a local .mp4 file
such that it captures three pairs of screenshots, beginning, middle and end.
Each individual screenshot is sent to Google's Cloud Vision API for
metadata generation. A dictionary is returned with the label and the frequency
of each in descending order.

Typical usage example:

  python3 image_metadata.py labels ./local_file.mp4 0.90 --persist
"""

import argparse
import datetime
import operator

import image_metadata_utils as utils

OUTPUT_FILE_PREFIX = "vod_mdd_"
SCREENSHOT_1_FILE = "./begin1.jpg"
SCREENSHOT_2_FILE = "./begin2.jpg"
SCREENSHOT_3_FILE = "./middle1.jpg"
SCREENSHOT_4_FILE = "./middle2.jpg"
SCREENSHOT_5_FILE = "./end1.jpg"
SCREENSHOT_6_FILE = "./end2.jpg"
SCREENSHOT_WIDTH_PX = 500


def generate_metadata(path: str, confidence: float) -> [str, dict[str, int]]:
  """Main code logic execution.

  Saves screenshot files locally, fetches metadata for each image and outputs
   dictionary with labels, frequency of each and the timestamp.

  Args:
      path: A string. Path of the .mp4 file to be processed.
      conf_threshold: A float between 0 and 1. Represents confidence threshold
        to consider when detecting labels.

  Returns:
      An array where the first element is a string timestamp of execution and
      the next is a dict mapping string labels related to metadata of each print
      and their int frequency of appeareance in descending order. For
      example:

      ['2024-02-23 10:48:38.459056', [('Wood', 6), ('Audio equipment', 1),
      ('Handwriting', 1), ('Technology', 1)]]
  """

  time_stamp = str(datetime.datetime.now())

  duration = float(utils.get_video_duration(path))
  duration_tenth = duration / 10
  begin_seconds = duration_tenth
  middle_seconds = duration / 2
  end_seconds = duration

  utils.generate_screenshot(
      path, SCREENSHOT_1_FILE, begin_seconds, SCREENSHOT_WIDTH_PX
  )
  utils.generate_screenshot(
      path,
      SCREENSHOT_2_FILE,
      begin_seconds + duration_tenth,
      SCREENSHOT_WIDTH_PX,
  )
  utils.generate_screenshot(
      path, SCREENSHOT_3_FILE, middle_seconds, SCREENSHOT_WIDTH_PX
  )
  utils.generate_screenshot(
      path,
      SCREENSHOT_4_FILE,
      middle_seconds + duration_tenth,
      SCREENSHOT_WIDTH_PX,
  )
  utils.generate_screenshot(
      path,
      SCREENSHOT_5_FILE,
      end_seconds - duration_tenth * 2,
      SCREENSHOT_WIDTH_PX,
  )
  utils.generate_screenshot(
      path, SCREENSHOT_6_FILE, end_seconds - duration_tenth, SCREENSHOT_WIDTH_PX
  )

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


def _clean_up() -> [str]:
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
  return [
      SCREENSHOT_1_FILE,
      SCREENSHOT_2_FILE,
      SCREENSHOT_3_FILE,
      SCREENSHOT_4_FILE,
      SCREENSHOT_5_FILE,
      SCREENSHOT_6_FILE,
  ]


def main(in_args: object):
  """main function. Generates and saves output to file and cleans if neeeded."""

  path = in_args.path
  confidence = in_args.conf_threshold
  return_dict_with_time = generate_metadata(path, confidence)
  utils.dict_output_to_file(OUTPUT_FILE_PREFIX, return_dict_with_time)

  if not in_args.persist_files:
    _clean_up()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
  )
  subparsers = parser.add_subparsers(dest="command")

  main_parser = subparsers.add_parser("labels", help=main.__doc__)
  main_parser.add_argument("path")
  main_parser.add_argument("conf_threshold")
  main_parser.add_argument(
      "--persist", dest="persist_files", action="store_true"
  )
  main_parser.add_argument(
      "--no-persist", dest="persist_files", action="store_false"
  )
  args = parser.parse_args()
  main(args)
