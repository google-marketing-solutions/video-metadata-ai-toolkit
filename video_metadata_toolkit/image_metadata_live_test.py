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

import image_metadata_live


class TestImageMetadataLive(unittest.TestCase):

  def test_run_live_bad_input_params(self):
    "Tests for valid input params before processing."

    with self.assertRaises(TypeError):
      parser = argparse.ArgumentParser(
          description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
      )
      subparsers = parser.add_subparsers(dest="command")
      main_parser = subparsers.add_parser(
          "labels", help=image_metadata_live.main.__doc__
      )
      main_parser.add_argument("url")
      main_parser.add_argument("conf_threshold")
      main_parser.add_argument("--persist", dest="persist_files", action="store_true")
      main_parser.add_argument(
          "--no-persist", dest="persist_files", action="store_false"
      )
      image_metadata_live.main()

  def test_run_live_bad_url(self):
    "Tests for valid URL to exist before processing."

    with self.assertRaises(IndexError):
      parser = argparse.ArgumentParser(
          description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
      )
      subparsers = parser.add_subparsers(dest="command")
      main_parser = subparsers.add_parser(
          "labels", help=image_metadata_live.main.__doc__
      )
      main_parser.add_argument("url")
      main_parser.add_argument("conf_threshold")
      main_parser.add_argument("--persist", dest="persist_files", action="store_true")
      main_parser.add_argument(
          "--no-persist", dest="persist_files", action="store_false"
      )
      args = parser.parse_args(
          ["labels", "http://BAD_NON_EXISTING_URL.xyzz123", "0.70", "--persist"]
      )
      image_metadata_live.main(args)


if __name__ == "__main__":
  unittest.main()
