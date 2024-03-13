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

"""Tests for mrss_parser."""

import unittest
import feedparser as fp
from unittest import mock
import mrss_parser
class TestMrssParser(unittest.TestCase):

    @mock.patch.object(fp, 'parse', autospec=True)
    def test_fetch_video_file_urls_success(self, mock_parse):
        """Tests successful parsing of a sample MRSS feed."""

        # Mock MRSS feed data
        mock_feed = fp.FeedParserDict()
        mock_feed.entries = [
            {'guid': 'video_123', 'media_content': [{'url': 'http://test.com/video1.mp4'}]},
            {'guid': 'video_456', 'media_content': [{'url': 'http://test.com/video2.mp4'}]}
        ]
        mock_parse.return_value = mock_feed

        # Expected output
        expected_videos = {
            'video_123': 'http://test.com/video1.mp4',
            'video_456': 'http://test.com/video2.mp4'
        }

        # Call the function
        result = mrss_parser.fetch_video_file_urls('test_mrss_url')
        # Assert the result
        self.assertEqual(result, expected_videos)
        mock_parse.assert_called_with('test_mrss_url')

if __name__ == '__main__':
    unittest.main()