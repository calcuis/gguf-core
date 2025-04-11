# !/usr/bin/env python3

__version__="0.0.66"

import argparse, json, random, os.path, urllib.request, subprocess
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
def generate_prompt(descriptors):
    subject = random.choice(descriptors.get("subject", []))
    hair_color = random.choice(descriptors.get("hair_color", []))
    eye_color = random.choice(descriptors.get("eye_color", []))
    scene = random.choice(descriptors.get("scene", []))
    return f"A {hair_color} haired {subject} with {eye_color} eyes, {scene}."
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
                input("\n---Enter to prompt the WAV content recognized above into GGUF model---")
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
        input("--- Press ENTER to Skip ---")
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
                # print("Content recognized: "+r.recognize_sphinx(audio))
                # print("Content recognized: "+text)
                # input("---Enter to analyze the WAV content above---")
                input("\n---Enter to prompt the WAV content recognized above into GGUF model---")
                # print("Processing...")
                from llama_core.rich.progress import Progress
                with Progress(transient=True) as progress:
                    task = progress.add_task("Processing", total=None)
                    # output = llm("Q: "+r.recognize_sphinx(audio), max_tokens=4096, echo=True)
                    output = llm("\nQ: "+text, max_tokens=16384, echo=True)
                    answer = output['choices'][0]['text']
                    print(answer+"\n")
                    # token_info = output["usage"]["total_tokens"]
                    # print("\n>>>"+answer+"...<<< (token spent: "+str(token_info)+")\n")
                    # print(answer+" (token spent: "+str(token_info)+")\n")
            except sr.UnknownValueError:
                print("Could not understand audio content")
            except sr.RequestError as e:
                print("Error; {0}".format(e))
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No WAV files are available in the current directory.")
        input("--- Press ENTER to Skip ---")
def pdf_handler(llm):
    import os
    pdf_files = [file for file in os.listdir() if file.endswith('.pdf')]
    def join_text(input_text):
        # Remove newline characters and join lines into one
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
            # print(f"\nPDF cotent extracted as below:\n\n"+text)
            input("---Enter to analyze the PDF content above---")
            # print("Processing...")
            from llama_core.rich.progress import Progress
            with Progress(transient=True) as progress:
                task = progress.add_task("Processing", total=None)
                # output = llm("Q: "+inject, max_tokens=32768, echo=True)
                output = llm("Q: "+inject, max_tokens=32768, echo=False)
                answer = output['choices'][0]['text']
                # print(inject+"\n")
                token_info = output["usage"]["total_tokens"]
                # print(answer+"\n")
                print("\n>>>"+answer+"...<<< (token spent: "+str(token_info)+")\n")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No PDF files are available in the current directory.")
        input("--- Press ENTER to Skip ---")
def get_file_size(url):
    with urllib.request.urlopen(url) as response:
        size = int(response.headers['Content-Length'])
    return size
def format_size(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"
def clone_file(url): # no more invalid certificate issues; llama_core >=0.1.9 required
    try:
        file_size = get_file_size(url)
        filename = os.path.basename(url)
        from llama_core.rich.progress import Progress
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
def clone_github_repo(repo_url):
    try:
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        if os.path.exists(repo_name):
            print(f"Error: A folder named '{repo_name}' already exists in the current directory.")
            return
        print(f"Cloning repository '{repo_url}'...")
        subprocess.run(["git", "clone", repo_url], check=True)
        print(f"Repository '{repo_name}' cloned successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to clone the repository. {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
def list_gguf_files():
    import os
    files = [f for f in os.listdir() if f.endswith(".gguf")]
    if not files:
        print("No .gguf files found in the current directory.")
        return None
    print("Available .gguf files:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")
    while True:
        try:
            choice = int(input("Select a file by number: "))
            return files[choice - 1]
        except (ValueError, IndexError):
            print("Invalid selection. Try again.")
def get_cutoff_size():
    while True:
        try:
            mb = float(input("Enter cutoff size for each part (in MB): "))
            return int(mb * 1024 * 1024)
        except ValueError:
            print("Please enter a valid number.")
def get_tensor_count():
    while True:
        try:
            count = int(input("Enter the total tensor count (split.tensors.count): "))
            return count
        except ValueError:
            print("Please enter a valid integer.")
def get_cutoff_size():
    while True:
        try:
            mb = float(input("Enter cutoff size for each part (in MB): "))
            return int(mb * 1024 * 1024)
        except ValueError:
            print("Please enter a valid number.")
def split_gguf_file(filename, cutoff_size):
    with open(filename, "rb") as f:
        data = f.read()
    total_size = len(data)
    parts = []
    offset = 0
    part_id = 1
    while offset < total_size:
        end = min(offset + cutoff_size, total_size)
        part_data = data[offset:end]
        part_name = f"model-{part_id:05d}-of-XXXX.gguf"
        with open(part_name, "wb") as pf:
            pf.write(part_data)
        parts.append(part_name)
        offset = end
        part_id += 1
    num_parts = len(parts)
    final_files = []
    for i, old_name in enumerate(parts):
        new_name = f"model-{i+1:05d}-of-{num_parts:05d}.gguf"
        os.rename(old_name, new_name)
        final_files.append(new_name)
    index = {
        "metadata": {
            "total_size": total_size
        },
        "file_map": {
            f"part_{i+1}": name for i, name in enumerate(final_files)
        }
    }
    with open("model.gguf.index.json", "w") as f:
        json.dump(index, f, indent=2)
    print(f"\nSplit complete! {num_parts} parts created.")
    print("Index file: model.gguf.index.json")
def merge_gguf_files():
    import os
    gguf_files = [f for f in os.listdir('.') if f.endswith('.gguf')]
    if not gguf_files:
        print("No .gguf files found in the current directory.")
        return
    filename = input("Enter the output file name (without .gguf): ").strip()
    if not filename:
        filename = "model"
    output_file = f"{filename}.gguf"
    with open(output_file, 'wb') as outfile:
        for fname in gguf_files:
            print(f"Merging: {fname}")
            with open(fname, 'rb') as infile:
                outfile.write(infile.read())
    print(f"\nAll files merged into: {output_file}")
from tkinter import *
def __init__():
    parser = argparse.ArgumentParser(description="gguf will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # Subparser session
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    # Subparser 'get [URL]' subcommand
    clone_parser = subparsers.add_parser('get', help='get a GGUF file/model from URL')
    clone_parser.add_argument('url', type=str, help='URL to download/clone from (i.e., gguf get [url])')
    # Subparser subcommands
    subparsers.add_parser('org', help='launch to page/container (gguf.org)')
    subparsers.add_parser('io', help='launch to page/container (gguf.io)')
    subparsers.add_parser('us', help='launch to page/container (gguf.us)')
    subparsers.add_parser('c', help='CLI connector')
    subparsers.add_parser('g', help='GUI connector')
    subparsers.add_parser('v', help='vision connector')
    subparsers.add_parser('i', help='interface selector')
    subparsers.add_parser('p', help='PDF analyzor (beta)')
    subparsers.add_parser('f', help='WAV analyzor (offline)')
    subparsers.add_parser('o', help='WAV analyzor (online)')
    subparsers.add_parser('a', help='model analyzor (beta)')
    subparsers.add_parser('r', help='GGUF metadata reader')
    subparsers.add_parser('s', help='sample GGUF list (download ready)')
    subparsers.add_parser('split', help='split GGUF')
    subparsers.add_parser('merge', help='merge GGUF')
    subparsers.add_parser('prompt', help='generate random prompt (beta)')
    subparsers.add_parser('comfy', help='download comfy pack with gguf-node')
    subparsers.add_parser('node', help='download gguf-node only')
    subparsers.add_parser('pack', help='download gguf pack')
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
    elif args.subcommand == 'node':
        repo_url = "https://github.com/calcuis/gguf"
        clone_github_repo(repo_url)
    elif args.subcommand == 'comfy':
        # clone_file("https://github.com/calcuis/gguf-comfy/releases/download/0.0.5/ComfyUI_GGUF_windows_portable.7z")
        # version = "https://raw.githubusercontent.com/calcuis/gguf-comfy/main/version.json"
        version = "https://raw.githubusercontent.com/calcuis/gguf/main/version.json"
        jdata = read_json_file(version)
        url = f"https://github.com/calcuis/gguf/releases/download/{jdata[0]['version']}/ComfyUI_GGUF_windows_portable.7z"
        clone_file(url)
    elif args.subcommand == 'pack':
        version = "https://raw.githubusercontent.com/calcuis/gguf-pack/main/version.json"
        jdata = read_json_file(version)
        url = f"https://github.com/calcuis/gguf/releases/download/{jdata[0]['version']}/GGUF_windows_portable.7z"
        clone_file(url)
    elif args.subcommand == 'prompt':
        file_path = "https://raw.githubusercontent.com/calcuis/rjj/main/descriptor.json"
        descriptors = read_json_file(file_path)
        if not descriptors:
            return
        try:
            num_descriptors = int(input("Enter the number of prompt(s) to generate: "))
            if num_descriptors <= 0:
                print("Please enter a positive number.")
                return
            for i in range(1, num_descriptors + 1):
                descriptor = generate_prompt(descriptors)
                filename = f"{i}.txt"
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(descriptor)
            print(f"{num_descriptors} prompt(s) generated and saved in separate text file(s).")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    elif args.subcommand == 'split':
        file = list_gguf_files()
        if file:
            cutoff = get_cutoff_size()
            split_gguf_file(file, cutoff)
    elif args.subcommand == 'merge':
        merge_gguf_files()
    elif args.subcommand == 'us':
        print("activating browser...")
        import webbrowser
        webbrowser.open("https://gguf.us")
    elif args.subcommand == 'io':
        print("activating browser...")
        import webbrowser
        webbrowser.open("https://gguf.io")
    elif args.subcommand == 'org':
        print("activating browser...")
        import webbrowser
        webbrowser.open("https://gguf.org")
    elif args.subcommand == 'a':
        from llama_core import parse
    elif args.subcommand == 'r':
        # from llama_core import read
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
                from llama_core.rich.progress import Progress
                with Progress(transient=True) as progress:
                    task = progress.add_task("Processing", total=None)
                    read_gguf_file(ModelPath)
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
    elif args.subcommand == 'i':
        from llama_core import menu
    elif args.subcommand == 'v':
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
                            print("👀 >>>"+response["choices"][0]["message"]["content"]+"\n")
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
            except (ValueError, IndexError):
                    print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
    elif args.subcommand == 'o':
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
                print("Processing...")
                from llama_core import Llama
                llm = Llama(model_path=ModelPath)
                clear()
                while True:
                    ask = input("---Enter to select a WAV file (Q for quit)---")
                    if ask.lower() == 'q':
                        break
                    wav_handler_online(llm)
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
    elif args.subcommand == 'f':
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
                print("Processing...")
                from llama_core import Llama
                llm = Llama(model_path=ModelPath)
                clear()
                while True:
                    ask = input("---Enter to select a WAV file (Q for quit)---")
                    if ask.lower() == 'q':
                        break
                    wav_handler(llm)
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
    elif args.subcommand == 'p':
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
                print("Processing...")
                from llama_core import Llama
                llm = Llama(model_path=ModelPath)
                clear()
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
    elif args.subcommand == 'g':
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
                print("Model Activated! Switch to chatPIG pop-up; Enter a Question then click Submit")
                # from tkinter import * # move it to the top
                import tkinter.scrolledtext as st
                root = Tk()
                root.title("chatPIG")
                root.columnconfigure([0, 1, 2], minsize=150)
                root.rowconfigure(0, weight=2)
                root.rowconfigure(1, weight=1)
                icon = PhotoImage(file = os.path.join(os.path.dirname(__file__), "logo.png"))
                root.iconphoto(False, icon)
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
                    root.title("chatPIG")
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
