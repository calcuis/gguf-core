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
with command-line interface
```
gguf c
```
#### gui connector
with graphical user interface
```
gguf g
```
#### vision connector (beta)
with vision model supported
```
gguf v
```
#### interface selector
selection menu for connector interface(s) above
```
gguf i
```
#### metadata reader
read model metadata for detail(s)
```
gguf r
```
or try model analyzor (beta)
```
gguf a
```
GGUF file(s) in the current directory will automatically be detected by the caller.
#### get feature
get GGUF from URL; clone/download it to the current directory
```
gguf get [url]
```
#### sample model list
You can either use the get feature above or opt a sample GGUF straight from the sample list by:
```
gguf s
```
#### prompt generator (beta)
Generate bulk prompt/descriptor(s) by:
```
gguf prompt
```
#### comfy pack with gguf node (beta)
Download ComfyUI GGUF portable package with gguf node by:
```
gguf node
```
#### pdf analyzor (beta)
You can now load your PDF file(s) straight into the model for generating digested summary; try it out by:
```
gguf p
```
#### wav analyzor (offline)
You can speak/talk straight to GGUF right away; prompt WAV(s) into the model for feedback; try it out by:
```
gguf f
```
#### wav analyzor (online)
more accurate (via google Open api); Internet access needed; try it out by:
```
gguf o
```
#### launch to page/container (gguf.org)
```
gguf org
```
#### launch to page/container (gguf.io)
```
gguf io
```
#### launch to page/container (gguf.us)
```
gguf us
```
