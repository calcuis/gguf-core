# !/usr/bin/env python3

__version__="0.0.59"

import argparse, json, os.path, urllib.request

def read_gguf_file(gguf_file_path):
    from llama_core.reader import GGUFReader
    reader = GGUFReader(gguf_file_path)
    print("Key-Value Pairs:")
    max_key_length = max(len(key) for key in reader.fields.keys())
    for key, field in reader.fields.items():
        value = field.parts[field.data[0]]
        print(f"{key:{max_key_length}} : {value}")
    print("\n")
    print("Tensors:")
    tensor_info_format = "{:<30} | Shape: {:<15} | Size: {:<12} | Quantization: {}"
    print(tensor_info_format.format("Tensor Name", "Shape", "Size", "Quantization"))
    print("-" * 80)
    for tensor in reader.tensors:
        shape_str = "x".join(map(str, tensor.shape))
        size_str = str(tensor.n_elements)
        quantization_str = tensor.tensor_type.name
        print(tensor_info_format.format(tensor.name, shape_str, size_str, quantization_str))

def wav_handler_online(llm):
    import os
    wav_files = [file for file in os.listdir() if file.endswith('.wav')]
    if wav_files:
        print("WAV file(s) available. Select which one to use:")
        for index, file_name in enumerate(wav_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(wav_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=wav_files[choice_index]
            print(f"WAV file: {selected_file} is selected!")
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(selected_file) as source:
                audio = r.record(source)
            try:
                text = r.recognize_google(audio)
                # text = r.recognize_sphinx(audio)
                from llama_core.rich.console import Console
                console = Console()
                console.print(f"\n[green]Speech/voice content recognized as: [yellow]"+text)
                from llama_core.rich.progress import Progress
                with Progress(transient=True) as progress:
                    task = progress.add_task("Processing", total=None)
                    output = llm("\nQ: "+text, max_tokens=16384, echo=True)
                    answer = output['choices'][0]['text']
                    print(answer+"\n")
            except sr.UnknownValueError:
                print("Could not understand audio content")
            except sr.RequestError as e:
                print("Error; {0}".format(e))
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No WAV files are available in the current directory.")
        input("--- Press ENTER To Exit ---")

def pdf_handler(llm):
    import os
    pdf_files = [file for file in os.listdir() if file.endswith('.pdf')]
    def join_text(input_text):
        joined_text = ' '.join(input_text.splitlines())
        return joined_text
    if pdf_files:
        print("PDF file(s) available. Select which one to use:")
        for index, file_name in enumerate(pdf_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(pdf_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=pdf_files[choice_index]
            print(f"PDF file: {selected_file} is selected!")
            from llama_core.pdf import PdfReader # rpdf => pdf (lama_core >=0.1.1)
            reader = PdfReader(selected_file)
            text=""
            number_of_pages = len(reader.pages)
            for i in range(number_of_pages):
                page = reader.pages[i]
                text += page.extract_text()
            output_text = join_text(text)
            inject = f"analyze the content below: "+output_text
            from llama_core.rich.console import Console
            console = Console()
            console.print(f"\n[green]PDF content extracted as below:\n\n[yellow]"+text)
            input("---Enter to analyze the PDF content above---")
            from llama_core.rich.progress import Progress
            with Progress(transient=True) as progress:
                task = progress.add_task("Processing", total=None)
                # output = llm("Q: "+inject, max_tokens=32768, echo=True)
                output = llm("Q: "+inject, max_tokens=32768, echo=False)
                answer = output['choices'][0]['text']
                token_info = output["usage"]["total_tokens"]
                print("\n>>>"+answer+"...<<< (token spent: "+str(token_info)+")\n")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No PDF files are available in the current directory.")
        input("--- Press ENTER To Exit ---")

def wav_handler(llm):
    import os
    wav_files = [file for file in os.listdir() if file.endswith('.wav')]
    if wav_files:
        print("WAV file(s) available. Select which one to use:")
        for index, file_name in enumerate(wav_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(wav_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=wav_files[choice_index]
            print(f"WAV file: {selected_file} is selected!")
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(selected_file) as source:
                audio = r.record(source)
            try:
                text = r.recognize_sphinx(audio)
                from llama_core.rich.console import Console
                console = Console()
                console.print(f"\n[green]Speech/voice content recognized as: [yellow]"+text)
                from llama_core.rich.progress import Progress
                with Progress(transient=True) as progress:
                    task = progress.add_task("Processing", total=None)
                    output = llm("\nQ: "+text, max_tokens=16384, echo=True)
                    answer = output['choices'][0]['text']
                    print(answer+"\n")
            except sr.UnknownValueError:
                print("Could not understand audio content")
            except sr.RequestError as e:
                print("Error; {0}".format(e))
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No WAV files are available in the current directory.")
        input("--- Press ENTER To Exit ---")

def get_file_size(url):
    with urllib.request.urlopen(url) as response:
        size = int(response.headers['Content-Length'])
    return size

def format_size(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def clone_file(url): # no more invalid certificate issues; certifi required (llama_core >=0.1.9)
    try:
        file_size = get_file_size(url)
        filename = os.path.basename(url)
        from llama_core.rich.progress import Progress # generic module adopted (lama_core >=0.1.2)
        with Progress(transient=True) as progress:
            task = progress.add_task(f"Downloading {filename}", total=file_size)
            with urllib.request.urlopen(url) as response, open(filename, 'wb') as file:
                chunk_size = 1024
                downloaded = 0
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded += len(chunk)
                    progress.update(task, completed=downloaded, description=f"Downloading {filename} [green][{format_size(downloaded)} / {format_size(file_size)}]")
        print(f"File cloned successfully and saved as '{filename}'({format_size(file_size)}) in the current directory.")
    except Exception as e:
        print(f"Error: {e}")

def read_json_file(file_path):
    response = urllib.request.urlopen(file_path)
    data = json.loads(response.read())
    # with open(file_path, 'r') as file:
    #     data = json.load(file)
    return data

def extract_names(data):
    for idx, entry in enumerate(data, start=1):
        print(f'{idx}. {entry["name"]}')

def handle_user_input(data):
    while True:
        user_choice = input(f"Enter your choice (1 to {len(data)}) or 'q' to quit: ")
        if user_choice.lower() == 'q':
            break
        try:
            index = int(user_choice)
            if 1 <= index <= len(data):
                source_url = data[index - 1]["url"]
                clone_file(source_url)
                break
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

from tkinter import *

def __init__():
    parser = argparse.ArgumentParser(description="gguf will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # Subparser session
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    # Subparser for 'get [URL]' subcommand
    clone_parser = subparsers.add_parser('get', help='download a GGUF file/model from URL')
    clone_parser.add_argument('url', type=str, help='URL to download/clone from (i.e., gguf get [url])')
    # Subparser for subcommands
    subparsers.add_parser('c', help='CLI connector')
    subparsers.add_parser('g', help='GUI connector')
    subparsers.add_parser('v', help='vision connector')
    subparsers.add_parser('i', help='interface selector')
    subparsers.add_parser('p', help='PDF analyzor (beta)')
    subparsers.add_parser('a', help='model analyzor (beta)')
    subparsers.add_parser('r', help='GGUF metadata reader')
    subparsers.add_parser('s', help='sample GGUF list (download ready)')
    subparsers.add_parser('comfy', help='download comfy pack (beta)')
    args = parser.parse_args()
    if args.subcommand == 'get':
        clone_file(args.url)
    elif args.subcommand == 's':
        import os
        file_path = "https://raw.githubusercontent.com/calcuis/gguf-connector/main/src/gguf_connector/data.json"
        # file_path = os.path.join(os.path.dirname(__file__), 'data.json')
        json_data = read_json_file(file_path)
        print("Please select a GGUF file to download:")
        extract_names(json_data)
        handle_user_input(json_data)
    elif args.subcommand == 'comfy':
        version = "https://raw.githubusercontent.com/calcuis/gguf-comfy/main/version.json"
        jdata = read_json_file(version)
        url = f"https://github.com/calcuis/gguf-comfy/releases/download/{jdata[0]['version']}/ComfyUI_GGUF_windows_portable.7z"
        clone_file(url)
    elif args.subcommand == 'us':
        print("activating browser...")
        import webbrowser
        webbrowser.open("https://gguf.us")
    elif args.subcommand == 'io':
        print("activating browser...")
        import webbrowser
        webbrowser.open("https://gguf.io")
    elif args.subcommand == 'r':
        import os
        gguf_files = [file for file in os.listdir() if file.endswith('.gguf')]
        if gguf_files:
            print("GGUF file(s) available. Select which one to read:")   
            for index, file_name in enumerate(gguf_files, start=1):
                print(f"{index}. {file_name}")
            choice = input(f"Enter your choice (1 to {len(gguf_files)}): ")
            try:
                choice_index=int(choice)-1
                selected_file=gguf_files[choice_index]
                print(f"Model file: {selected_file} is selected!")
                ModelPath=selected_file
                from rich.progress import Progress
                with Progress(transient=True) as progress:
                    task = progress.add_task("Processing", total=None)
                    read_gguf_file(ModelPath)
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
    elif args.subcommand == 'a':
        from llama_core import parse
    elif args.subcommand == 'i':
        from llama_core import menu
    elif args.subcommand == 'v':
        import os
        def clear():
            if os.name == 'nt':
                _ = os.system('cls')
            else:
                _ = os.system('clear')
        gguf_files = [file for file in os.listdir() if file.endswith('.gguf')]
        if gguf_files:
            print("GGUF file(s) available. Select which one to use as Clip Handler:")
            for index, file_name in enumerate(gguf_files, start=1):
                print(f"{index}. {file_name}")
            choice1 = input(f"Enter your choice (1 to {len(gguf_files)}): ")
            try:
                choice_index=int(choice1)-1
                selected_file=gguf_files[choice_index]
                print(f"Model file: {selected_file} is selected!")
                clip_model_path=selected_file
                from llama_core.llama_chat_format import Llava15ChatHandler
                chat_handler = Llava15ChatHandler(clip_model_path)
                clear()
                print("Clip Handler: "+clip_model_path+" has been activated!\n")
                print("GGUF file(s) available. Select which one to use as Vision Model:")
                for index, file_name in enumerate(gguf_files, start=1):
                    print(f"{index}. {file_name}")
                choice2 = input(f"Enter your choice (1 to {len(gguf_files)}): ")
                try:
                    choice_index=int(choice2)-1
                    selected_file=gguf_files[choice_index]
                    print(f"Model file: {selected_file} is selected!")
                    model_path=selected_file
                    from llama_core import Llama
                    llm = Llama(
                        model_path=model_path,
                        chat_handler=chat_handler,
                        n_ctx=2048,
                        )
                    clear()
                    while True:
                        ask = input("Provide a picture URL (Q for quit): ")
                        if ask.lower() == 'q':
                            break
                        from llama_core.rich.progress import Progress
                        with Progress(transient=True) as progress:
                            task = progress.add_task("Processing", total=None)
                            response = llm.create_chat_completion(
                                messages = [
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type" : "text", "text": "What's in this image?"},
                                            {"type": "image_url", "image_url": {"url": ask } }
                                        ]
                                    }
                                ]
                            )
                            clear()
                            print("Picture URL: "+ask+"\n")
                            print(">>>"+response["choices"][0]["message"]["content"])
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
            except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
    elif args.subcommand == 'p':
        import os
        gguf_files = [file for file in os.listdir() if file.endswith('.gguf')]
        if gguf_files:
            print("GGUF file(s) available. Select which one to use:")
            for index, file_name in enumerate(gguf_files, start=1):
                print(f"{index}. {file_name}")
            choice = input(f"Enter your choice (1 to {len(gguf_files)}): ")
            try:
                choice_index=int(choice)-1
                selected_file=gguf_files[choice_index]
                print(f"Model file: {selected_file} is selected!")
                ModelPath=selected_file
                print("Processing...")
                from llama_core import Llama
                llm = Llama(model_path=ModelPath)
                while True:
                    ask = input("---Enter to select a PDF file (Q for quit)---")
                    if ask.lower() == 'q':
                        break
                    pdf_handler(llm)
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
    elif args.subcommand == 'c':
        import os
        def clear():
            if os.name == 'nt':
                _ = os.system('cls')
            else:
                _ = os.system('clear')
        gguf_files = [file for file in os.listdir() if file.endswith('.gguf')]
        if gguf_files:
            print("GGUF file(s) available. Select which one to use:")
            for index, file_name in enumerate(gguf_files, start=1):
                print(f"{index}. {file_name}")
            choice = input(f"Enter your choice (1 to {len(gguf_files)}): ") 
            try:
                choice_index=int(choice)-1
                selected_file=gguf_files[choice_index]
                print(f"Model file: {selected_file} is selected!")
                ModelPath=selected_file
                from llama_core import Llama
                llm = Llama(model_path=ModelPath)
                clear()
                while True:
                    ask = input("Enter a Question (Q for quit): ")
                    if ask.lower() == 'q':
                        break
                    clear()
                    from llama_core.rich.progress import Progress
                    with Progress(transient=True) as progress:
                        task = progress.add_task("Processing", total=None)
                        output = llm("Q: "+ask, max_tokens=2048, echo=True)
                        answer = output['choices'][0]['text']
                        token_info = output["usage"]["total_tokens"]
                        clear()
                        print("Raw input: "+ask+" (token used: "+str(token_info)+")\n")
                        print(answer+"\n")
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
    elif args.subcommand == 'g':
        import os
        def clear():
            # for windows
            if os.name == 'nt':
                _ = os.system('cls')
            # for mac and linux(here, os.name is 'posix')
            else:
                _ = os.system('clear')
        gguf_files = [file for file in os.listdir() if file.endswith('.gguf')]
        if gguf_files:
            print("GGUF file(s) available. Select which one to use:")
            for index, file_name in enumerate(gguf_files, start=1):
                print(f"{index}. {file_name}")
            choice = input(f"Enter your choice (1 to {len(gguf_files)}): ")
            try:
                choice_index=int(choice)-1
                selected_file=gguf_files[choice_index]
                print(f"Model file: {selected_file} is selected!")
                ModelPath=selected_file
                from llama_core import Llama
                llm = Llama(model_path=ModelPath)
                # from tkinter import *
                import tkinter.scrolledtext as st
                root = Tk()
                root.title("chatGPT")
                root.columnconfigure([0, 1, 2], minsize=150)
                root.rowconfigure(0, weight=2)
                root.rowconfigure(1, weight=1)
                # icon = PhotoImage(file = os.path.join(os.path.dirname(__file__), "logo.png"))
                # root.iconphoto(False, icon)
                i = Entry()
                o = st.ScrolledText()
                def submit(i):
                    root.title("Processing...")
                    clear()
                    from llama_core.rich.console import Console
                    console = Console()
                    console.print("*note: [green]it might show: (Not Responding) and/or keep spinning; but running in background still; please be patient.")
                    from llama_core.rich.progress import Progress
                    with Progress(transient=True) as progress:
                        task = progress.add_task("Processing", total=None)
                        output = llm("Q: "+str(i.get()), max_tokens=2048, echo=True)
                        answer = output['choices'][0]['text']
                        token_info = output["usage"]["total_tokens"]
                        print("Raw input: "+str(i.get())+" (token used: "+str(token_info)+")\n")
                        print(answer)
                    o.insert(INSERT, answer+"\n\n")
                    i.delete(0, END)
                    root.title("chatGPT")
                btn = Button(text = "Submit", command = lambda: submit(i))
                i.grid(row=1, columnspan=2, sticky="nsew")
                btn.grid(row=1, column=2, sticky="nsew")
                o.grid(row=0, columnspan=3, sticky="nsew")
                root.mainloop()
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
