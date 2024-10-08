## **Video Metadata AI Toolkit**

### **Disclaimer**

This is not an officially supported Google product. The code samples shared here
are not formally supported by Google and are provided only as a reference.

### **Introduction**

This repo currently houses two different use cases: AI Metadata (generate metadata
for your videos using AI) and Smart Ad Breaks (generate cue points for your VOD
and live video content to insert ads at the right moments). Navigate to their respective
folders to find more info on each of them.

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
