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

from dataclasses import dataclass
import unittest
from unittest.mock import MagicMock, patch

import feedparser
import mrss_parser
from video_class import Video


@dataclass
class MockEntry:

  def get(self, key, default=None):
    mock_data = {
        "dfpvideo:contentID": "video123",
        "guid": "guid456",  # Used if contentID is not present
        "media_content": [{"uri": "http://example.com/video.mp4"}],
        "title": "You Can't See Me But I'm Waving Video",
        "media:description": (
            "Description of a video where this person waving could not be seen."
        ),
        "media_tags": ["tag1", "tag2"],
    }
    return mock_data.get(key, default)

  def __iter__(self):
    yield self  # Yield the MockEntry object itself when iterated


class TestMRSSParser(unittest.TestCase):

  def setUp(self):
    """Setup common patches for all tests."""
    # Start the patch for detect_duration method in the Video class
    self.patcher = patch.object(Video, "detect_duration", return_value=120)
    self.mock_duration = self.patcher.start()

  def tearDown(self):
    """Stop patches after each test."""
    self.patcher.stop()

  @patch("feedparser.parse")
  def test_parse_mrss_success(self, mock_parse):
    """Tests successful parsing of a valid MRSS feed."""
    mock_entry = MagicMock()
    mock_entry.get.side_effect = lambda key, default=None: {
        "dfpvideo:contentID": "video123",
        "guid": "guid456",
        "media_content": [{"url": "http://example.com/video.mp4"}],
        "title": "You Can't See Me But I'm Waving Video",
        "media:description": (
            "Description of a video where this person waving could not be seen."
        ),
        "media_tags": ["tag1", "tag2"],
    }.get(key, default)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed

    videos = mrss_parser.parse_mrss("http://example.com/mrss.xml")

    self.assertIsNotNone(videos)
    self.assertIsInstance(videos, list)
    self.assertEqual(len(videos), 1)
    self.assertEqual(videos[0].id, "video123")
    self.assertEqual(videos[0].uri, "http://example.com/video.mp4")
    self.assertEqual(videos[0].title, "You Can't See Me But I'm Waving Video")
    self.assertEqual(
        videos[0].description,
        "Description of a video where this person waving could not be seen.",
    )
    self.assertEqual(videos[0].metadata, ["tag1", "tag2"])

  @patch("feedparser.parse")
  def test_video_attributes(self, mock_parse):
    """Tests the attributes of the videos parsed from the MRSS feed."""
    mock_entry = MagicMock()
    mock_entry.get.side_effect = lambda key, default=None: {
        "dfpvideo:contentID": "video123",
        "guid": "guid456",
        "media_content": [{"url": "http://example.com/video.mp4"}],
        "title": "You Can't See Me But I'm Waving Video",
        "media:description": (
            "Description of a video where this person waving could not be seen."
        ),
        "media_tags": ["tag1", "tag2"],
    }.get(key, default)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed

    videos = mrss_parser.parse_mrss("http://example.com/mrss.xml")

    video = videos[0]
    self.assertEqual(video.id, "video123")
    self.assertEqual(video.uri, "http://example.com/video.mp4")
    self.assertEqual(video.title, "You Can't See Me But I'm Waving Video")
    self.assertEqual(
        video.description,
        "Description of a video where this person waving could not be seen.",
    )
    self.assertEqual(video.metadata, ["tag1", "tag2"])

  @patch("feedparser.parse")
  def test_parse_mrss_empty_feed(self, mock_parse):
    """Tests the behavior when the MRSS feed has no entries."""
    mock_feed = MagicMock()
    mock_feed.entries = []
    mock_parse.return_value = mock_feed

    videos = mrss_parser.parse_mrss("http://example.com/mrss.xml")
    self.assertIsInstance(videos, list)
    self.assertEqual(len(videos), 0)

  @patch("feedparser.parse")
  def test_parse_mrss_missing_attributes(self, mock_parse):
    """Tests parsing entries with missing attributes."""
    mock_entry = MagicMock()
    mock_entry.get.side_effect = lambda key, default=None: {
        "dfpvideo:contentID": "video123",
        "media_content": [{"url": "http://example.com/video.mp4"}],
        "title": "You Can't See Me But I'm Waving Video",
    }.get(key, default)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed

    videos = mrss_parser.parse_mrss("http://example.com/mrss.xml")

    self.assertIsNotNone(videos)
    self.assertIsInstance(videos, list)
    self.assertEqual(len(videos), 1)
    self.assertEqual(videos[0].metadata, {})
    self.assertIsNone(videos[0].description)

  @patch("feedparser.parse", side_effect=Exception("Failed to fetch"))
  def test_parse_mrss_error_handling(self, mock_parse):
    """Tests the function's error handling."""
    videos = mrss_parser.parse_mrss("http://example.com/mrss.xml")
    self.assertEqual(len(videos), 0)

  @patch("feedparser.parse")
  def test_parse_mrss_invalid_media_uri(self, mock_parse):
    """Tests entries with missing or invalid media URIs."""
    mock_entry = MagicMock()
    mock_entry.get.side_effect = lambda key, default=None: {
        "dfpvideo:contentID": "video123",
        "media_content": [{}],  # Missing URL
        "title": "You Can't See Me But I'm Waving Video",
        "media:description": (
            "Description of a video where this person waving could not be seen."
        ),
    }.get(key, default)

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_parse.return_value = mock_feed

    videos = mrss_parser.parse_mrss("http://example.com/mrss.xml")

    self.assertIsNotNone(videos)
    self.assertIsInstance(videos, list)
    self.assertEqual(len(videos), 0)  # No video added due to missing URL


if __name__ == "__main__":
  unittest.main()
