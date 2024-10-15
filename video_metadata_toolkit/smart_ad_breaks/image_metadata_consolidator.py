#!/usr/bin/env python

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

"""This module is responsible for consolidating labels from different iterations

of streaming labels output .tsv files.

This code is meant to be executed standalone and accepts three parameters, the
file type ('labels' supported), the beginning timestamp and end timestamp
in format: Y-m-d-H-M-S and the path of the files.
The output will be a .tsv file with the consolidated labels and their frequency.

Typical usage example:

   python3 ./image_metadata_consolidator.py labels
            2024-03-05-15-13-22 2024-03-05-15-20-23 "./"
"""

import argparse
import csv
import datetime
import operator
from os import listdir
from os.path import isfile, join

import image_metadata_utils as utils


FILE_INPUT_PREFIX = "stream_mdd_"
FILE_OUTPUT_PREFIX = "stream_mdd_CONS_"


def run_consolidation(
    dt_init: datetime.datetime, dt_end: datetime.datetime, file_path: str
) -> [str, dict[str, int]]:
  """Main code logic execution.

  Consolidates the labels and their frequency according to the input time range
  and writes a file as output.

   Args:
       dt_init: A timestamp. The beginning timestamp in format: Y-m-d-H-M-S.
       dt_end: A timestamp. The end timestamp in format: Y-m-d-H-M-S.
       file_path: A String file path to be processed.

   Returns:
       An array where the first element is a string timestamp of execution and
       the next is a dict mapping string labels related to the consolidated
       metadata of each file and their int frequency of appeareance in
       descending order. For example:

       ['2024-02-23 10:48:38.459056', [('Wood', 6), ('Audio equipment', 1),
       ('Handwriting', 1), ('Technology', 1)]]
  """

  applicable_files = _file_names_within_range(dt_init, dt_end, file_path)
  consolidated_dict = _consolidate_entries_to_dict(applicable_files)

  return_dict = sorted(
      consolidated_dict.items(), key=operator.itemgetter(1), reverse=True
  )
  time_stamp = str(datetime.datetime.now())
  return_dict_with_time = [time_stamp, return_dict]

  return return_dict_with_time


def _file_names_within_range(
    begin_time: datetime.datetime, end_time: datetime.datetime, path: str
) -> [str]:
  """Filters stream files containing labels for processing

  according to their timestamp.Only files which were generated within
  the start and end inputs will be considered.
  Returns the list of files as a list of strings.

  Args:
      begin_time: A timestamp. Beginning timestamp of interval.
      end_time: A timestamp. End timestamp of interval.
      path: A string. Path of directory to be processed.

  Returns:
      A list of strings containing the filenames which should be processed.
  """

  only_files = [f for f in listdir(path) if isfile(join(path, f))]
  return_list = []

  for f in only_files:
    if FILE_INPUT_PREFIX not in f or FILE_OUTPUT_PREFIX in f:
      continue

    file_time_stamp_str = f.partition(FILE_INPUT_PREFIX)[2]
    file_time_stamp_str = file_time_stamp_str.partition(".tsv")[0]
    file_time_stamp_dt = datetime.datetime.strptime(
        file_time_stamp_str, "%Y-%m-%d-%H-%M-%S"
    )
    if begin_time <= file_time_stamp_dt <= end_time:
      return_list.append(join(path, f))

  return return_list


def _consolidate_entries_to_dict(list_of_files: list[str]) -> dict[str, int]:
  """Consolidates the labels and frequencies from an input file to

  the new (if first iteration) or existing dictionary which will be outputed.

  Args:
      list_of_files: A list of strings. List of files to be processed.
      return_dict: A dic. Dictionary containing labels and their frequency.

  Returns:
      A dict which contains the consolidated labels and their frequency.
  """

  consolidated_dict = {}

  for file in list_of_files:
    with open(file, "r", encoding="utf-8") as labels_file:
      tsv_reader = csv.reader(labels_file, delimiter="\t")

      for row in tsv_reader:
        label, frequency = row
        if label in consolidated_dict:
          old_frequency = consolidated_dict[label]
          consolidated_dict[label] = old_frequency + int(frequency)
        else:
          consolidated_dict[label] = int(frequency)

    return consolidated_dict


def _dict_output_to_file(input_list: list[str]) -> str:
  """Persist list containing timestamp and metadata dictionary to local file.

  Args:
      input_list: A list containing the timestamp and the output metadata
        dictionary.

  Returns:
      A string of the file named saved.
  """

  file_timestamp = datetime.datetime.strptime(
      input_list[0], "%Y-%m-%d %H:%M:%S.%f"
  )
  dict_input = input_list[1]
  file_name = (
      FILE_OUTPUT_PREFIX
      + datetime.datetime.strftime(file_timestamp, "%Y-%m-%d-%H-%M-%S")
      + ".tsv"
  )

  with open(file_name, "w", encoding="utf-8") as f:
    for entry in dict_input:
      f.write(entry[0] + "\t" + str(entry[1]) + "\n")

  return file_name


def main(in_args):
  """main function. Generates and saves output to file."""

  begin_time = datetime.datetime.strptime(in_args.dt_init, "%Y-%m-%d-%H-%M-%S")
  end_time = datetime.datetime.strptime(in_args.dt_end, "%Y-%m-%d-%H-%M-%S")
  path = in_args.file_path

  return_dict_with_time = run_consolidation(begin_time, end_time, path)
  utils.dict_output_to_file(FILE_OUTPUT_PREFIX, return_dict_with_time)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
  )
  subparsers = parser.add_subparsers(dest="command")
  consolidator_parser = subparsers.add_parser("labels", help=main.__doc__)
  consolidator_parser.add_argument("dt_init")
  consolidator_parser.add_argument("dt_end")
  consolidator_parser.add_argument("file_path")
  args = parser.parse_args()
  main(args)
