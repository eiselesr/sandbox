Tool for monkey patching riaps app device functions.
To preserve default operation
1. Put app into `app` folder and add to (dot)riaps file.
2. Create wrapper that inherits from `app.\<your app\>` that matches name used in (dot)riaps file. It can be the same as the base implementation.
To use monkey patch
3. Create copy of (dot)riaps file, and change component name to `\<your component name>_test`
4. Create copy of `\<your component name>.py` called `\<your component name>_test.py`
5. See example app for contents


* Next steps
    * Some additional work is needed to patch non-device components since they cannot start an external thread to run the injection server.