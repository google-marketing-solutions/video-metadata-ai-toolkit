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
"""Tests for image_metadata."""

import argparse
import unittest

import ffmpeg
import image_metadata


class ImageMetadataTest(unittest.TestCase):

  def test_nonexistent_path(self):
    "Tests for valid video file to exist before processing."
    with self.assertRaises(ffmpeg.Error):
      parser = argparse.ArgumentParser(
          description=__doc__,
          formatter_class=argparse.RawDescriptionHelpFormatter,
      )
      subparsers = parser.add_subparsers(dest="command")
      main_parser = subparsers.add_parser(
          "labels", help=image_metadata.main.__doc__
      )
      main_parser.add_argument("path")
      main_parser.add_argument("conf_threshold")
      main_parser.add_argument(
          "--persist", dest="persist_files", action="store_true"
      )
      main_parser.add_argument(
          "--no-persist", dest="persist_files", action="store_false"
      )
      args = parser.parse_args(["labels", "BAD_PATH.mp4", "0.90", "--persist"])
      image_metadata.main(args)

  def test_run_pair_frames_local_bad_input_params(self):
    "Tests for valid input params before processing."

    with self.assertRaises(TypeError):
      parser = argparse.ArgumentParser(
          description=__doc__,
          formatter_class=argparse.RawDescriptionHelpFormatter,
      )
      subparsers = parser.add_subparsers(dest="command")
      main_parser = subparsers.add_parser(
          "labels", help=image_metadata.main.__doc__
      )
      main_parser.add_argument("path")
      main_parser.add_argument("conf_threshold")
      main_parser.add_argument(
          "--persist", dest="persist_files", action="store_true"
      )
      main_parser.add_argument(
          "--no-persist", dest="persist_files", action="store_false"
      )
      image_metadata.main()


if __name__ == "__main__":
  unittest.main()
