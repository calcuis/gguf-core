### GGUF core
[<img src="https://raw.githubusercontent.com/calcuis/chatgpt-model-selector/master/callgg.gif" width="128" height="128">](https://github.com/calcuis/gguf-core)
[![Static Badge](https://img.shields.io/badge/core-0.0.3-orange?logo=github)](https://github.com/calcuis/gguf-core/releases)

This package is a GGUF (GPT-Generated Unified Format) file caller.
#### install the caller via pip/pip3 (once only):
```
pip install gguf-core
```
#### update the caller (if not in the latest version) by:
```
pip install gguf-core --upgrade
```
### user manual
This is a cmd-based (command line) package, you can find the user manual by adding the flag -h or --help.
```
gguf -h
```
#### check current version
```
gguf -v
```
#### cli connector
```
gguf c
```
#### gui connector
```
gguf g
```
GGUF file(s) in the same directory will automatically be detected by the caller.
#### clone feature
```
gguf clone [url]
```
#### sample model list
You can either use the clone feature above or opt a sample GGUF straight from the sample list by:
```
gguf s
```
