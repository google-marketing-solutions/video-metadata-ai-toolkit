## **Video Metadata AI Toolkit**

### **Disclaimer**

This is not an officially supported Google product. The code samples shared here
are not formally supported by Google and are provided only as a reference.

### **Introduction**

This is a Python solution which takes a media content (video, images, articles, etc.) and uses a language model to describe and generate metadata for the content. The project supports generating detailed content descriptions, user-friendly summaries, metadata tags, key values, and title suggestions.


### **AI Metadata Development**

#### Setup

1.  Create a Python virual environment.

2.  From inside the environment run `pip install -r requirements.txt`.

3.  Export your Gemini API Key as an environment variable:

```
export GEMINI_API_KEY=[YOUR API KEY]
```

4. (Optional) To use ```add_ai_attributes_to_video``` you must also setup your application default credentials for Google Cloud and populate the values in ```project_configs.py```.

##### **Run AI Metadata Code**

###### From the command line:
```
usage: ai_metadata_generator.py [-h] [--keys KEYS [KEYS ...]] {describe,summarize,tag,title} content_file

Analyzes content using AI.

positional arguments:
  {describe,summarize,tag,title}
                        The action to perform for the provided content.
  content_file          The URI of the content to be processed (local files only).

options:
  -h, --help            show this help message and exit
  --keys KEYS [KEYS ...]
                        Use with "tag" to create key/values instead of free-form metadata values. No-op otherwise.
```

describe: Generates a content description with as much detail as possible.
```
python ai_metadata_generator.py describe my/video/uri.mp4
```

summarize: Generates a user-friendly summary of the content
```
python ai_metadata_generator.py summarize my/video/uri.mp4
```

tag: Generates metadata tags for the content (use with --keys to create key values)
```
python ai_metadata_generator.py tag my/video/uri.mp4
```
```
python ai_metadata_generator.py tag my/video/uri.mp4 --keys key1 key2 key3
```

title: Suggests possible titles for the content
```
python ai_metadata_generator.py title my/video/uri.mp4
```


###### From a python project:

And of these functions can be called from a python project by importing the [ai_metadata_generator.py](https://github.com/google-marketing-solutions/video-metadata-ai-toolkit/video-metadata-ai-toolkit/ai_metadata_generator.py) and [file_io.py](https://github.com/google-marketing-solutions/video-metadata-ai-toolkit/video-metadata-ai-toolkit/file_io.py) modules into your code:

```py
from video_metadata_toolkit.ai_metadata import ai_metadata_generator, file_io


content_file = file_io.File("my/video/uri.mp4")
content_description = ai_metadata_generator.describe(content_file)

# to remove the file from Gemini's storage
content_file.cleanup()
```
