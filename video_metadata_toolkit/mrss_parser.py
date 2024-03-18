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

import feedparser as fp

def fetch_video_file_urls(mrss_url: str) -> dict[str, str]:
  """
  Parses the given MRSS Feed to get the individual videos.

  Args:
    mrss_url: The link to the MRSS feed.

  Returns:
    A dictionary of videos like {video id: media file URLs}.
  """
  feed = fp.parse(mrss_url)
  videos = {}
  for entry in feed.entries:
    # Key - If it exists, video ID = <dfpvideo:contentID>, otherwise = <guid>
    if 'dfpvideo:contentId' in entry:
      video_id = entry['dfpvideo:contentID']
    elif 'guid' in entry:
      video_id = entry['guid']
    # Value - If it exists, media_content = <media:content url>
    if 'media_content' in entry:
      media_url = entry['media_content'][0]['url']
    if video_id and media_url:
      videos[video_id] = media_url
  return videos