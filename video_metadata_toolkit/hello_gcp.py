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

"""Basic module for connecting to GCP and setting up testing infrastructure.

Note: Creating this module so there is a test to run when configuring
presubmit/ci and as a means of testing the GCP application default credentials.
It can be removed once real code (+tests) are checked in for the project.
"""

from google.cloud import storage


def list_storage_buckets(storage_client: storage.Client = storage.Client()):
  """Returns an iterator with the buckets."""
  return storage_client.list_buckets()


def main():
  print("Buckets:")
  for bucket in list_storage_buckets():
    print(bucket.name)


if __name__ == "__main__":
  main()
