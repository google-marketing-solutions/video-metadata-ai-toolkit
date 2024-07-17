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
"""Tests for image_metadata_consolidator."""

import argparse
import unittest

import image_metadata_consolidator as consolidator


class ImageMetadataConsolidatorTest(unittest.TestCase):

  def test_consolidator_input_bad_date_format(self):
    "Tests valid input argument format."

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")
    consolidator_parser = subparsers.add_parser(
        "labels", help=consolidator.main.__doc__
    )
    consolidator_parser.add_argument("dt_init")
    consolidator_parser.add_argument("dt_end")
    consolidator_parser.add_argument("file_path")
    args = parser.parse_args(
        ["labels", "not-a-valid-date", "not-a-valid-date", "./"]
    )

    with self.assertRaises(ValueError):
      consolidator.main(args)


if __name__ == "__main__":
  unittest.main()
