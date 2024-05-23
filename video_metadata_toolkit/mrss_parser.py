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

"""Module for parsing MRSS Feeds."""

import subprocess
from typing import List
import feedparser as fp
import transcription_utils
from video_class import Video


def parse_mrss(mrss_url: str) -> List[Video]:
  """Parses a specific publisher's MRSS feed to extract video information.

  This function is designed to handle the unique structure of a particular
  publisher's MRSS feed. It extracts video IDs, titles, descriptions, metadata,
  and URLs to create  a list of `Video` objects. May need to change for another
  publisher's MRSS feed.

  Args:
      mrss_url: The URL of the MRSS feed to parse.

  Returns:
      A list of `Video` objects if the feed is parsed successfully.

  Raises:
       Exception: If any issue arises during the parsing process.
  """
  try:
    feed = fp.parse(mrss_url)
    videos = []
    for entry in feed.entries:
      try:
        video_id = entry.get("dfpvideo:contentID") or entry.get("guid")
        media_content = entry.get("media_content", [{}])
        media_url = media_content[0].get("url") if media_content else None
        title = entry.get("title")
        description = entry.get("media:description")
        metadata = entry.get("media_tags")
        if video_id and media_url:
          video = Video(
              id=video_id,
              title=title,
              url=media_url,
              metadata=metadata,
              description=description,
          )
          videos.append(video)
      except Exception as video_error:
        print(f"Error processing video entry: {video_error} for entry: {entry}")
    return videos
  except Exception as mrs_parsing_exception:
    print(f"Error parsing MRSS feed: {mrs_parsing_exception}")
    return []