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

"""Utility functions to transcribe videos."""

import os
import subprocess
import project_configs
import google.api_core.exceptions as google_exceptions
import google.cloud.speech as speech
import google.cloud.storage as storage
import google.cloud.translate_v3 as translate
import requests


def download_video(video_url: str, local_video_path: str) -> str:
  """Downloads a video from a specified URL to a local file.

  Uses a browser-like User-Agent to potentially bypass web server
  restrictions on non-browser agents.

  Args:
      video_url (str): URL of the video to download.
      local_video_path (str): Local path to save the downloaded video.

  Returns:
      str: Full local path of the downloaded video file, or an empty string if
      the download fails.

  Raises:
      requests.HTTPError: If the HTTP request resulted in an unsuccessful status
      code.
      ValueError: If the content type of the response is not a video.
  """
  # Define headers to mimic a browser request
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/58.0.3029.110 Safari/537.36"
      )
  }

  try:
    os.makedirs(os.path.dirname(local_video_path), exist_ok=True)

    with requests.get(video_url, headers=headers, stream=True) as response:
      response.raise_for_status()  # Raises HTTPError for bad responses

      # Check if the response is indeed a video
      if "video" not in response.headers.get("Content-Type", ""):
        print(
            "Expected video content, but received"
            f" {response.headers['Content-Type']}"
        )
        raise ValueError(f"URL did not point to a video file: {video_url}")

      with open(local_video_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
          file.write(chunk)

    print(f"Video downloaded successfully to {local_video_path}")
    return local_video_path
  except requests.RequestException as e:
    print(f"Failed to download video due to network error: {e}")
    raise requests.HTTPError(f"Failed to download video: {video_url}") from e
  except IOError as e:
    print(f"Failed to save video to {local_video_path}: {e}")
    raise IOError(f"Error saving file at {local_video_path}") from e


def download_file_from_gcs(gcs_uri: str, local_destination: str):
  """Downloads a file from Google Cloud Storage to a local destination.

  Args:
      gcs_uri (str): The GfCS URI of the file to download (e.g.,
        'gs://my-bucket/file.txt').
      local_destination (str): The path where to save the downloaded file.

  Raises:
      ValueError: If the GCS URI is invalid or if the file does not exist.
      PermissionError: If there are insufficient permissions to access the file.
      IOError: If there are issues writing the file to the local destination.
      Exception: For other Google Cloud Storage related errors.
  """
  try:
    client = storage.Client()
    bucket_name = gcs_uri.split("/")[2]  # Extract bucket name
    object_path = "/".join(gcs_uri.split("/")[3:])  # Extract object path

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_path)
    blob.download_to_filename(local_destination)
  except OSError as e:
    raise OSError(f"Failed to write the file to {local_destination}: {e}")
  except google_exceptions.NotFound:
    raise ValueError(f"The file at {gcs_uri} does not exist.")
  except google_exceptions.Forbidden:
    raise PermissionError(
        f"Insufficient permissions to access the file at {gcs_uri}."
    )
  except Exception as e:
    raise Exception(f"An error occurred with Google Cloud Storage: {e}")


def map_language_code(generic_code: str) -> str:
  """Map generic language codes to locales supported by Speech-to-Text API.

  Args:
    generic_code (str): The two-letter ISO 639-1 language code.

  Returns:
    str: A list containing a single, specific locale code. Defaults to British
      English.
  """
  language_mapping = {
      "pt": "pt-BR",
      "es": "es-ES",
      "en": "en-GB",
      "it": "it-IT",
      "nl": "nl-NL",
      "ar": "ar-SA",
      "zu": "zu-ZA",
      "de": "de-DE",
      "id": "id-ID",
  }
  return language_mapping.get(
      generic_code, "en-GB"
  )  # Return British English as default if no mapping found


def detect_language(text: str) -> list[str]:
  """Detects the languages of the text given to it.

  Args:
      text (str): The string input to detect the language of.

  Returns:
    list[str]: Either a list of just the top most likely language (1), or a
      list of all
      the languages used. Defaults to British English.
  """
  if text is None or text == "":
    return ["en-GB"]
  translate_client = translate.TranslationServiceClient()

  request = translate.DetectLanguageRequest(
      content=text,
      parent=f"projects/{project_configs.PROJECT_ID}/locations/global",
      mime_type="text/plain",
  )

  response = translate_client.detect_language(request=request)

  # Extract the most likely language
  most_likely_language = response.languages[0]

  if len(response.languages) > 1:
    languages_used = []
    for language in response.languages:
      languages_used.append(map_language_code(language.language_code))
    print(f"The languages used...={languages_used}")
    return languages_used
  else:
    return [map_language_code(most_likely_language.language_code)]


def _extract_audio_from_local_file(
    local_file_path: str, output_audio_file_directory: str
) -> str:
  """Extracts audio from a local video file using FFmpeg.

  Args:
    local_file_path (str): The path to the local video file.
    output_audio_file_directory (str): The directory to save the extracted
      audio file.

  Returns:
    str: Full path of the extracted audio file.

  Raises:
    subprocess.CalledProcessError: If FFmpeg fails to extract audio.
  """
  video_file_name_with_extension = os.path.basename(local_file_path)
  audio_file_name = (
      os.path.splitext(video_file_name_with_extension)[0] + "_audio_only.wav"
  )
  output_audio_file_full_path = os.path.join(
      output_audio_file_directory, audio_file_name
  )
  command = [
      "ffmpeg",
      "-i",
      local_file_path,
      "-vn",  # Discards video stream
      "-acodec",
      "pcm_s16le",  # Specifies WAV encoding (signed 16-bit little-endian)
      output_audio_file_full_path,
  ]
  subprocess.run(command, check=True)
  print(
      "Audio extracted successfully to this directory:"
      f" {output_audio_file_directory}"
  )
  print(f"Audio saved in this file: {output_audio_file_full_path}")
  return output_audio_file_full_path


def _extract_audio_from_gcs(
    gcs_uri: str, output_audio_file_directory: str
) -> str:
  """Downloads a video from GCS and extracts the audio using FFmpeg.

  Args:
    gcs_uri (str): The GCS URI of the video file (e.g.,
      'gs://my-bucket/video.mp4').
    output_audio_file_directory (str): The directory to save the extracted
      audio file.

  Returns:
    str: Full path of the extracted audio file.

  Raises:
    ValueError: If the download from GCS fails.
      subprocess.CalledProcessError: If FFmpeg fails to extract audio.
  """
  # Download the video from GCS and save locally, to then use local audio
  # extraction function.
  video_file_name_with_extension = os.path.basename(gcs_uri)
  local_video_path_to_download_to = (
      f"{os.path.splitext(video_file_name_with_extension)[0]}_video.mp4"
  )
  print(f"Local_video_path_to_download_to = {local_video_path_to_download_to}")
  local_video_path = download_video(
      gcs_uri,
      f"./videos/{local_video_path_to_download_to}",
  )
  print(f"Local_video_path = {local_video_path}")
  output_audio_file_full_path = _extract_audio_from_local_file(
      local_video_path, output_audio_file_directory
  )
  return output_audio_file_full_path


def extract_audio_from_video(
    gcs_uri_or_local_file_path: str, output_audio_file_directory: str
) -> str:
  """Extracts audio from a GCS URI or a local file path using ffmpeg.

  Args:
    gcs_uri_or_local_file_path (str): GCS URI (e.g.,
      'gs://my-bucket/video.mp4') or local file path.
    output_audio_file_directory (str): The name of the directory in which to
      save the audio file.

  Returns:
    str: Full path of the extracted audio file.

  Raises:
    FileNotFoundError: If the specified file does not exist in GCS or locally.
      subprocess.CalledProcessError: If FFmpeg fails to extract audio.
  """
  local_output_audio_file_full_path = None

  if gcs_uri_or_local_file_path.startswith("gs://"):
    try:
      local_output_audio_file_full_path = _extract_audio_from_gcs(
          gcs_uri_or_local_file_path, output_audio_file_directory
      )
    except FileNotFoundError:
      print(f"GCS object not found: {gcs_uri_or_local_file_path}")
      raise
  else:
    try:
      local_output_audio_file_full_path = _extract_audio_from_local_file(
          gcs_uri_or_local_file_path, output_audio_file_directory
      )
    except FileNotFoundError:
      print(f"Local file not found: {gcs_uri_or_local_file_path}")
  if local_output_audio_file_full_path is None:
    raise FileNotFoundError("The audio file could not be processed.")
  return local_output_audio_file_full_path


def upload_local_file_to_google_cloud(
    bucket_name: str, source_file: str, destination_blob: str
) -> str:
  """Uploads a file to the Google Cloud Storage bucket.

  Args:
    bucket_name (str): The name of the GCS bucket to upload to.
    source_file (str): The local path of the file to upload.
    destination_blob (str): The name to give the uploaded file in GCS.

  Returns:
    str: The GCS URI of the uploaded file if successful.

  Raises:
    FileNotFoundError: If the local file does not exist.
    NotFound: If the GCS bucket does not exist.
    Forbidden: If there's a permission issue accessing the GCS bucket.
    Exception: For general errors during the upload process.
  """
  print(
      f"Uploading to GCP - bucket_name = {bucket_name}, source_file ="
      f" {source_file}, destination_blob = {destination_blob}"
  )
  try:
    client = storage.Client()
    # Check if the local file exists before trying to upload
    if not os.path.isfile(source_file):
      raise FileNotFoundError(f"File not found: {source_file}")

    blob = client.bucket(bucket_name).blob(destination_blob)
    blob.upload_from_filename(source_file)
    print(
        f"Uploading to GCP - bucket_name = {bucket_name}, source_file ="
        f" {source_file}, destination_blob = {destination_blob}"
    )
    gcs_uri = f"gs://{bucket_name}/{destination_blob}"
    print(f"File uploaded successfully to {gcs_uri}")
    return gcs_uri
  except FileNotFoundError as e:
    print(f"Local file not found: {source_file}. Error: {e}")
    raise
  except google_exceptions.NotFound as e:
    print(f"GCS bucket not found: {bucket_name}. Error: {e}")
    raise
  except google_exceptions.Forbidden as e:
    print(f"Permission denied accessing GCS bucket: {bucket_name}. Error: {e}")
    raise
  except Exception as e:
    print(f"Error while trying to upload to GCP: {e}")
    raise


def _transcribe_from_local_file(local_path: str, languages=["en-GB"]) -> str:
  """Transcribes a local audio file and returns the text.

  Args:
    local_path (str): The local path of the audio file to transcribe.
    languages (list): The languages to use for transcription. Defaults to
      British English.

  Returns:
    str: The transcribed text.
  """
  speech_client = speech.SpeechClient()
  print(f"In transcribe_from_local_file - local_path={local_path}")
  with open(local_path, "rb") as audio_file:
    content = audio_file.read()

  audio = speech.RecognitionAudio(content=content)
  config = speech.RecognitionConfig(
      language_codes=languages,
      audio_channel_count=2,
      use_enhanced=True,
      model="latest_long",
  )

  operation = speech_client.long_running_recognize(config=config, audio=audio)
  response = operation.result()

  transcript = ""
  for result in response.results:
    for alternative in result.alternatives:
      transcript += (
          f"{alternative.confidence:.2f} => {alternative.transcript}\n"
      )

  print(f"In transcribe_from_local_file - transcript= {transcript}")
  return transcript


def _transcribe_from_gcs(gcs_uri: str, languages=["en-GB"]) -> str:
  """Transcribes an audio file located on Google Cloud Storage.

  Args:
    gcs_uri: The GCS URI of the audio file to transcribe (e.g.,
      'gs://my-bucket/audio.wav').
    languages: The languages to use for transcription. Defaults to British
      English.

  Returns:
    str: The transcribed text from the audio file.
  """
  audio = speech.RecognitionAudio(uri=gcs_uri)

  config = speech.RecognitionConfig(
      language_code=languages[0],  # Just get the first language
      alternative_language_codes=languages[1:],  # Give any other languages
      audio_channel_count=2,
      use_enhanced=True,
      model="latest_long",
  )

  speech_client = speech.SpeechClient()
  operation = speech_client.long_running_recognize(config=config, audio=audio)
  response = operation.result()

  transcript = ""
  for result in response.results:
    for alternative in result.alternatives:
      transcript += (
          f"{alternative.confidence:.2f} => {alternative.transcript}\n"
      )

  print(f"Transcript from GCS: {transcript}")
  return transcript


def transcribe_audio(
    gcs_uri_or_local_file_path: str, languages=["en-GB"], output_filename=None
) -> str:
  """Transcribes audio from a GCS URI or a local file path.

  Args:
    gcs_uri_or_local_file_path (str): GCS URI (e.g.,
      'gs://my-bucket/audio.wav') or local file path.
    languages (list): The languages to use for transcription. Defaults to
      British English.
    output_filename (str, optional): The name of the file to save the
      transcription. Defaults to None.

  Returns:
    str: The path where the transcript is stored locally.

  Raises:
    FileNotFoundError: If the specified file does not exist in GCS or locally.
  """
  if gcs_uri_or_local_file_path.startswith("gs://"):
    try:
      transcript = _transcribe_from_gcs(gcs_uri_or_local_file_path, languages)
      base_name = os.path.basename(gcs_uri_or_local_file_path)
      local_transcript_file_path = os.path.join(
          "./transcriptions/",
          f"{os.path.splitext(base_name)[0]}_transcription.txt",
      )
      with open(local_transcript_file_path, "w") as file:
        file.write(transcript)
        print(f"Text content saved to {local_transcript_file_path}")
    except FileNotFoundError:
      print(f"GCS object not found: {gcs_uri_or_local_file_path}")
      raise
  else:
    try:
      transcript = _transcribe_from_local_file(
          gcs_uri_or_local_file_path, languages
      )
      if output_filename is None:
        output_filename = f"{os.path.splitext(os.path.basename(gcs_uri_or_local_file_path))[0]}_transcription.txt"
      local_transcript_file_path = os.path.join(
          "./transcriptions/", output_filename
      )
      with open(local_transcript_file_path, "w") as file:
        file.write(transcript)
        print(f"Text content saved to {local_transcript_file_path}")
    except FileNotFoundError as e:
      print(f"Local file not found: {gcs_uri_or_local_file_path}")
      raise e

  return local_transcript_file_path
