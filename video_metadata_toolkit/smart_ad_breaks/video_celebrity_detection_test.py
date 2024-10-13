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
"""Tests for the video_celebrity_detection module."""

import unittest
from unittest.mock import patch, MagicMock
import video_celebrity_detection as vcd


class TestVideoCelebrityDetection(unittest.TestCase):
  """Tests for the video_celebrity_detection module."""

  @patch("video_celebrity_detection.requests.post")
  @patch("video_celebrity_detection.get_access_token")
  def test_execute_celebrity_detection(self, mock_get_token, mock_post):
    mock_get_token.return_value = "mock_access_token"

    mock_response = MagicMock()
    mock_response.text = '{"name": "test_operation_name"}'
    mock_post.return_value = mock_response

    result = vcd.execute_celebrity_detection(
        "gs://input_video.mp4", "gs://output_json.json", "123456789"
    )

    mock_post.assert_called_once_with(
        url="https://videointelligence.googleapis.com/v1p3beta1/videos:annotate",
        json={
            "inputUri": "gs://input_video.mp4",
            "outputUri": "gs://output_json.json",
            "features": ["CELEBRITY_RECOGNITION"],
        },
        headers={
            "Authorization": "Bearer mock_access_token",
            "x-goog-user-project": "123456789",
            "Content-Type": "application/json; charset=utf-8",
        },
        timeout=20,
    )
    self.assertEqual(result, '{"name": "test_operation_name"}')

  @patch("requests.get")
  @patch("google.auth.default")
  def test_result_celebrity_detection(self, mock_auth, mock_get):
    mock_auth.return_value = (MagicMock(), "test_project")
    mock_get.return_value.text = '{"annotationResults": []}'

    result = vcd.result_celebrity_detection(
        "projects/test_project/locations/us-east1/operations/test_operation"
    )
    self.assertEqual(result, '{"annotationResults": []}')

  def test_get_project_num(self):
    result_name = "projects/12345/locations/us-central1/operations/98765"
    project_num = vcd.get_project_num(result_name)
    self.assertEqual(project_num, "12345")

  def test_get_project_num_invalid(self):
    invalid_result_name = "invalid_format"
    with self.assertRaises(ValueError):
      vcd.get_project_num(invalid_result_name)

  @patch("requests.post")
  def test_valid_uris(self, mock_post):
    mock_post.return_value.text = "{}"

    valid_cases = [
        ("gs://my-bucket/input.mp4", "gs://another-bucket/output.json"),
        (
            "gs://long-bucket-name/path/to/video.mov",
            "gs://my-project/results.json",
        ),
    ]

    for input_uri, output_uri in valid_cases:
      vcd.execute_celebrity_detection(input_uri, output_uri, "1234567890")
      mock_post.assert_called_once()
      mock_post.reset_mock()

  @patch("requests.post")
  def test_invalid_uris(self, mock_post):
    invalid_cases = [
        ("", "gs://output.json"),
        ("gs://input", ""),
        ("invalid-uri", "gs://output.json"),
        ("gs://input", "http://not-gs.com"),
    ]

    for input_uri, output_uri in invalid_cases:
      with self.assertRaises(ValueError):
        vcd.execute_celebrity_detection(input_uri, output_uri, "1234567890")
      mock_post.assert_not_called()


if __name__ == "__main__":
  unittest.main()
