## Video Metadata Toolkit

### Development

#### Setup

1. Create a Python virual environment.
1. From inside the environment run `pip install -r requirements.txt`.
1. If you plan to run anything locally, setup your Application Default Credentials and project ID for GCP.

Application Default Credentials:
```
gcloud auth application-default login
```
Set project ID:
```
gcloud config set project [PROJECT_ID]
```
#### Run tests

From the top level project directory:
```
python -m unittest discover video_metadata_toolkit  -p "*_test.py"
```

#### Code format

Submitted code should conform to Google's Python style guide. To format code automatically, run `pyink --pyink-indentation=2 [FILENAME]`.

For VS Code users, you can configure the formatter to run automatically by adding the following to your `settings.json`:

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

To manually run the linter:
```
pylint
