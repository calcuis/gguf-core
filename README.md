### GGUF core
[<img src="https://raw.githubusercontent.com/calcuis/gguf-core/master/gguf.gif" width="128" height="128">](https://github.com/calcuis/gguf-core)
[![Static Badge](https://img.shields.io/badge/core-release-orange?logo=github)](https://github.com/calcuis/gguf-core/releases)

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
#### pdf analyzor (beta)
You can now load your PDF file(s) straight into the model for generating digested summary; try it out by:
```
gguf p
```
#### webpage (alpha)
```
https://gguf.us
```
Paste it (gguf.us) to browser instead of cmd console.
