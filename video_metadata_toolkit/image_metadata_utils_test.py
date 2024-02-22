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

import unittest

import ffmpeg
import image_metadata_utils as utils


class TestImageMetadataUtils(unittest.TestCase):

  def test_detect_labels_dict_bad_path(self):
    "Tests for valid screenshots to exist before processing."

    path = "BAD_PATH"
    threshold = 0.70
    in_dict = {}
    with self.assertRaises(FileNotFoundError):
      utils.detect_labels_dict(path, in_dict, threshold)

  def test_generate_screenhot_bad_path(self):
    "Tests for valid video file to exist before processing."

    in_filename = "BAD_PATH"
    out_filename = "test.jpg"
    time = 10
    width = 500

    with self.assertRaises(ffmpeg.Error):
      utils.generate_screenshot(in_filename, out_filename, time, width)

  def test_gen_video_duration_bad_path(self):
    "Tests for valid video file to exist before processing."

    in_filename = "BAD_PATH"
    with self.assertRaises(ffmpeg.Error):
      utils.get_video_duration(in_filename)
