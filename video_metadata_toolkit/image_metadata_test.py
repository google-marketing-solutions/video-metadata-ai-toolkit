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

import argparse
import unittest

import ffmpeg
import image_metadata


class TestImageMetadata(unittest.TestCase):

  def test_nonexistent_path(self):
    "Tests for valid video file to exist before processing."
    with self.assertRaises(ffmpeg.Error):
      parser = argparse.ArgumentParser(
          description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
      )
      subparsers = parser.add_subparsers(dest="command")
      run_local_parser = subparsers.add_parser(
          "labels", help=image_metadata.run_local.__doc__
      )
      run_local_parser.add_argument("path")
      run_local_parser.add_argument("conf_threshold")
      run_local_parser.add_argument("persist_files")
      args = parser.parse_args(["labels", "BAD_PATH.mp4", "0.90", "y"])
      image_metadata.run_local(args)

  def test_run_pair_frames_local_bad_input_params(self):
    "Tests for valid input params before processing."

    with self.assertRaises(TypeError):
      parser = argparse.ArgumentParser(
          description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
      )
      subparsers = parser.add_subparsers(dest="command")
      run_local_parser = subparsers.add_parser(
          "labels", help=image_metadata.run_local.__doc__
      )
      run_local_parser.add_argument("path")
      run_local_parser.add_argument("conf_threshold")
      run_local_parser.add_argument("persist_files")
      image_metadata.run_local()


if __name__ == "__main__":
  unittest.main()
