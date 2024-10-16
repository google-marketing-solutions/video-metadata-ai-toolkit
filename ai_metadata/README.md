## **Video Metadata AI Toolkit**

### **Disclaimer**

This is not an officially supported Google product. The code samples shared here
are not formally supported by Google and are provided only as a reference.

### **Introduction**

This is a Python solution which takes a publisher-provided video and generates metadata to tag the video, allowing publishers to better target ads and improve monetization. It does this by downloading the video, stripping out the audio, using Speech-to-Text to get the transcript, and sending that to Gemini to generate the metadata. Publishers can run this solution on their videos as they get uploaded to their CMS, so the metadata can be automatically added.

### **AI Metadata Development**

#### Setup

1.  Create a Python virual environment.

2.  From inside the environment run `pip install -r requirements.txt`.

3.  If you plan to run anything locally, setup your Application Default
    Credentials and project ID for GCP.


Application Default Credentials:

```

gcloud auth application-default login

```

Set project ID:

```

gcloud config set project [PROJECT_ID]

```

Input your GCP project ID into the project_configs.py file.


4.  Make sure to run the code from within the ai_tags directory.


### **Google Cloud**

You need a Google Cloud Project to each of these use cases.

These are the APIs you need to enable for the AI-generated metadata tags.

*   Cloud Storage

*   Cloud Translation

*   Cloud Speech-to-Text

*   Vertex AI

##### **Run AI Metadata Code**

###### From the command line:
```
usage: ai_metadata_generator.py [-h] [--video_id VIDEO_ID] [--title TITLE]
  [--metadata METADATA] video_uri

positional arguments:
  video_uri            The URI of the video to be processed.

options:
  -h, --help           show this help message and exit
  --video_id VIDEO_ID  The unique identifier of the video. If not provided,
                        it will be extracted from the video URI.
  --title TITLE        User provided title for the video. Defaults to an
                        empty string
  --metadata METADATA  User provided metadata associated with the video.
                        Defaults to anempty string.
```

For example:
```
python ai_metadata_generator.py my/video/uri.mp4
```



###### From a python project:

[ai_metadata_generator.py](https://github.com/google-marketing-solutions/video-metadata-ai-toolkit/video-metadata-ai-toolkit/ai_metadata_generator.py) has the function which is the main entry point for
running the code:

```py
from video_metadata_toolkit.ai_metadata import ai_metadata_generator, video_class

video = video_class.Video(
    "my_video_id",
    uri="https://example_video.mp4" # Also supports local files.
)
video_with_ai_attributes = ai_metadata_generator.add_ai_attributes_to_video(
    video,
    project_configs.AUDIO_BUCKET_NAME,
)

```

#### **Run tests**

From the top level project directory:

```

python -m unittest discover video_metadata_toolkit -p "*_test.py"

```

## **Code format**

Submitted code should conform to Google's Python style guide. To format code
automatically, run `pyink --pyink-indentation=2 -l 80 [FILENAME]`.

For VS Code users, you can configure the formatter to run automatically by
adding the following to your `settings.json`:

```

"[python]": {

"editor.defaultFormatter": "ms-python.black-formatter",

"editor.formatOnSave": true,

"editor.formatOnPaste": true,

"editor.formatOnType": true

},

"black-formatter.args": [

"--pyink-indentation=2"

],

"black-formatter.path": [

"pyink"

],

```

#### **Scripts**

To manually run tests and the linter:

```

sh test_and_lint.sh

```
