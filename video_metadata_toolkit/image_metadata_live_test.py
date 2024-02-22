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
import urllib

import ffmpeg
import image_metadata_live


class TestImageMetadataLive(unittest.TestCase):

  def test_run_live_bad_input_params(self):
    "Tests for valid input params before processing."

    with self.assertRaises(TypeError):
      parser = argparse.ArgumentParser(
          description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
      )
      subparsers = parser.add_subparsers(dest="command")
      run_live_parser = subparsers.add_parser(
          "labels", help=image_metadata_live.run_live.__doc__
      )
      run_live_parser.add_argument("url")
      run_live_parser.add_argument("conf_threshold")
      run_live_parser.add_argument("persist_files")
      image_metadata_live.run_live()

  def test_run_live_bad_url(self):
    "Tests for valid URL to exist before processing."

    with self.assertRaises(IndexError):
      parser = argparse.ArgumentParser(
          description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
      )
      subparsers = parser.add_subparsers(dest="command")
      run_live_parser = subparsers.add_parser(
          "labels", help=image_metadata_live.run_live.__doc__
      )
      run_live_parser.add_argument("url")
      run_live_parser.add_argument("conf_threshold")
      run_live_parser.add_argument("persist_files")
      args = parser.parse_args(
          ["labels", "http://BAD_NON_EXISTING_URL.xyzz123", "0.70", "y"]
      )
      image_metadata_live.run_live(args)

  def test_get_frames_bad_url(self):
    "Tests for valid URL to exist before processing."

    url = "http://BAD_NON_EXISTING_URL.XYZ123"
    with self.assertRaises(IndexError):
      image_metadata_live.get_frames(url)

  def test_get_base_bad_url(self):
    "Tests for valid URL to exist before processing."

    url = "http://BAD_NON_EXISTING_URL.XYZ123"
    with self.assertRaises(IndexError):
      image_metadata_live.get_base(url)

  def test_get_manifest_bad_url(self):
    "Tests for valid URL to exist before processing."

    url = "http://BAD_NON_EXISTING_URL.XYZ123"
    with self.assertRaises(urllib.error.URLError):
      image_metadata_live.get_manifest(url)

  def test_get_ts_segments_bad_url(self):
    "Tests for valid URL to exist before processing."

    url = "http://BAD_NON_EXISTING_URL.XYZ123"
    with self.assertRaises(urllib.error.URLError):
      image_metadata_live.get_ts_segments(url)

  def test_convert_ts_to_mp4(self):
    "Tests for valid video file to exist before processing."

    input_file = "BAD_FILE"
    output_file = "test.jpg"

    with self.assertRaises(ffmpeg.Error):
      image_metadata_live.convert_ts_to_mp4(input_file, output_file)

  def test_download_file_bad_url(self):
    "Tests for valid URL to exist before processing."

    url = "http://BAD_NON_EXISTING_URL.XYZ123"
    filename = "test.ts"

    with self.assertRaises(urllib.error.URLError):
      image_metadata_live.download_file(url, filename)


if __name__ == "__main__":
  unittest.main()
