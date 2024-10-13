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

import shlex
import subprocess
import transcription_utils


class Video:
  """Represents a video, storing its metadata and  AI-generated metadata.

  id (str): Unique identifier for the video.
  title (str, optional): The title of the video.
  uri (str): The URI where the video is located.
  description (str, optional): A description of the video (default: None).
  metadata (dict, optional): Additional metadata associated with the video
    (default: {}).
  transcript (str, optional): A transcription of the video's audio (default:
    None).
  summary (str, optional): A concise summary of the video's content (default:
    None).
  aiGeneratedMetadata (dict, optional): Metadata extracted or enhanced by AI
    (default: None).
  aiGeneratedMetadataWithCelebrity (dict, optional): AI-generated metadata
    focusing on celebrities mentioned in the video (default: None).
  duration (float): The duration of the video in seconds, determined by
    `detect_duration`.
  languages (list[str]): A list of detected languages in the video title,
    determined by `transcription_utils.detect_language`.
  """

  def __init__(
      self,
      id,
      uri,
      title=None,
      description=None,
      metadata=None,
      transcript=None,
      summary=None,
      ai_generated_metadata=None,
      ai_suggested_titles=None,
      ai_generated_metadata_with_celebrity=None,
      ai_suggested_external_summary=None,
  ):
    # From MRSS
    self.id = id
    self.title = title
    self.description = description
    self.uri = uri
    self.duration = self.detect_duration(self.uri)
    self.metadata = metadata if metadata else {}
    # AI Generated
    self.languages = transcription_utils.detect_language(title)
    self.transcript = transcript
    self.summary = summary
    self.ai_suggested_titles = ai_suggested_titles
    self.ai_suggested_external_summary = ai_suggested_external_summary
    # Metadata
    self.ai_generated_metadata = ai_generated_metadata
    self.ai_generated_metadata_with_celebrity = (
        ai_generated_metadata_with_celebrity
    )

  def detect_duration(self, video_uri: str) -> float:
    """Uses ffmpeg to retrieve the duration of a video from a given URI by executing a subprocess.

    Args:
      video_uri: The URI of the video file.

    Returns:
        The duration of the video in seconds as a float. Returns -1.0 if there
        is an error.
    """
    # Command to get video duration using ffprobe, which is part of the ffmpeg suite
    command = (
        "ffprobe -v error -show_entries format=duration -of"
        f" default=noprint_wrappers=1:nokey=1 {shlex.quote(video_uri)}"
    )
    try:
      # Execute the command
      result = subprocess.run(
          shlex.split(command),
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE,
          text=True,
      )
      # Check if the command was successful
      if result.returncode == 0:
        # Return the duration as a float
        return float(result.stdout.strip())
      else:
        print(f"Error fetching video duration: {result.stderr}")
    except Exception as e:
      print(f"Failed to run command: {e}")

    return -1.0
