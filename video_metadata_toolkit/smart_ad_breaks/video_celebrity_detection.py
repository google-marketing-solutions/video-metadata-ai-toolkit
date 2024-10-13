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
"""
This script allows you to execute and get the results of celebrity detection
using the cloud video intelligence API.

There are two operations and each can be executed as follows:

execute: To initiate a processing request of a video:
  python3 ./video_celebrity_detection.py execute
  -i "gs://inputuri.mp4" -o "gs://outputuri.json" -p 755258082165

result: To fetch the processing results after an execute step. The ri argument
is the output of the execute step:
  python3 ./video_celebrity_detection.py result
  -ri "projects/123/locations/us-east1/operations/456" 
"""

import argparse
import logging
import re
import requests
import sys

import google.auth
import google.auth.transport.requests


def execute_celebrity_detection(
    input_uri: str, output_uri: str, project_number: str
) -> str:
  """Executes celebrity detection.

  Args:
    input_uri: The URI of the input video.
    output_uri: The URI of the output JSON file.
    project_number: The project number.

  Returns:
    The name response from the API which is used to get the result.
  """
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
  )

  gs_uri_pattern = re.compile("^gs://")

  if not gs_uri_pattern.match(input_uri):
    raise ValueError(f"Invalid input URI: {input_uri}")
  if not gs_uri_pattern.match(output_uri):
    raise ValueError(f"Invalid output URI: {output_uri}")

  token = "Bearer " + get_access_token()
  url = "https://videointelligence.googleapis.com/v1p3beta1/videos:annotate"
  data = {
      "inputUri": input_uri,
      "outputUri": output_uri,
      "features": ["CELEBRITY_RECOGNITION"],
  }
  headers = {
      "Authorization": token,
      "x-goog-user-project": project_number,
      "Content-Type": "application/json; charset=utf-8",
  }

  r = requests.post(url=url, json=data, headers=headers, timeout=20)
  response = r.text
  logging.info(response)
  return response


def result_celebrity_detection(result_input: str) -> str:
  """Gets the celebrity detection result.

  Args:
    result_input: The result name obtained from the execution operation
    response.

  Returns:
    The JSON response from the API.
  """
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
  )

  token = "Bearer " + get_access_token()
  url = "https://videointelligence.googleapis.com/v1/" + result_input
  project_number = get_project_num(result_input)

  headers = {
      "Authorization": token,
      "x-goog-user-project": project_number,
  }

  r = requests.get(url=url, headers=headers, timeout=20)
  response = r.text
  logging.info(response)
  return response


def get_access_token() -> str:
  """Gets an access token for the Video Intelligence API.

  Returns:
    The access token.
  """
  creds, _ = google.auth.default()
  auth_req = google.auth.transport.requests.Request()
  creds.refresh(auth_req)
  return str(creds.token)


def get_project_num(result_input: str) -> str:
  """Gets the project number from an execute operation output string, which
  then can be used as an input for the result operation.

  Args:
    result_input: The result name obtained from the execution operation
    response.

  Returns:
    The project number.
  """
  segments = result_input.split("/")
  if len(segments) != 6 or not all(segments):
    raise ValueError(
        "Invalid string format. Should be"
        "e.g., projects/123/locations/us-central1/operations/456"
    )
  project_num = segments[1]
  return project_num


def _parse_args(args) -> argparse.Namespace:
  argparser = argparse.ArgumentParser(
      description=(
          "Executes the celebrity detection feature of the cloud video "
          "intelligence API."
      )
  )
  subparsers = argparser.add_subparsers(dest="operation")
  execute_parser = subparsers.add_parser(
      "execute",
      help=("To execute the detection of a video."),
  )
  result_parser = subparsers.add_parser(
      "result",
      help=("Gets the celebrity detection result."),
  )
  execute_parser.add_argument(
      "--input-uri",
      "-i",
      type=str,
      help=("Input URI of video to be processed."),
  )
  execute_parser.add_argument(
      "--output-uri",
      "-o",
      type=str,
      help=("Output URI of where results will be saved."),
  )
  execute_parser.add_argument(
      "--project-number",
      "-p",
      type=str,
      help=("The numeric identifier for your Google Cloud project."),
  )
  result_parser.add_argument(
      "--result-input",
      "-ri",
      type=str,
      help=(
          "The input to be used for the result operation. Obtained from the"
          "execute operation."
      ),
  )

  return argparser.parse_args(args)


def main(args=sys.argv[1:]):
  args = _parse_args(args)
  if args.operation == "execute":
    execute_celebrity_detection(
        args.input_uri, args.output_uri, args.project_number
    )

  elif args.operation == "result":
    result_celebrity_detection(args.result_input)

  else:
    print("Invalid operation: ", args.operation)


if __name__ == "__main__":
  main()
