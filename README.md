### GGUF core

[<img src="https://raw.githubusercontent.com/calcuis/gguf-connector/master/gguf.gif" width="128" height="128">](https://github.com/calcuis/gguf-connector)

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
#### gui connector
```
gguf g
```

GGUF file(s) in the same directory will automatically be detected by the caller, hence, a selection menu will be shown in the console as below.

[<img src="https://raw.githubusercontent.com/calcuis/chatgpt-model-selector/master/demo.gif" width="350" height="280">](https://github.com/calcuis/chatgpt-model-selector/blob/main/demo.gif)
[<img src="https://raw.githubusercontent.com/calcuis/chatgpt-model-selector/master/demo1.gif" width="350" height="280">](https://github.com/calcuis/chatgpt-model-selector/blob/main/demo1.gif)

### clone feature
```
gguf clone [url]
```
With this fast clone feature, you can clone any (GGUF model) file from URL, save it automatically in the current directory, and get it ready to connect locally (run it with your own machine offline); depends on the file size, as well as the network connectivity, it may take a while to complete the clone process; and you can see a dynamic progress bar showing the downloading status in this latest version. (an universal issue was detected for mac users: ssl cert. verify failed; possible solution: click Install Certificates.command under your Python version folder)

#### sample model(s) available to download (try out)
For general purpose
[chat.gguf] (size: around 2GB or less)
```
gguf clone https://huggingface.co/calcuis/chat/resolve/main/chat.gguf
```
For coding
[code.gguf] (size: around 3GB or more)
```
gguf clone https://huggingface.co/calcuis/chat/resolve/main/code.gguf
```
For health/medical advice
[medi.gguf] (size: around 3GB or more)
```
gguf clone https://huggingface.co/calcuis/chat/resolve/main/medi.gguf
```
***those are all experimental models; no guarantee on quality

#### sample model list
You can either use the clone feature above or opt a sample GGUF straight from the sample list by:
```
gguf s
```
