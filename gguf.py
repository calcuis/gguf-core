# !/usr/bin/env python3

__version__="0.0.24"

import argparse, json, os.path, urllib.request
from tkinter import *

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

            # from pypdf import PdfReader (pypdf dropped)
            # from llama_core.rpdf import PdfReader # generic module adopted
            from llama_core.pdf import PdfReader # lama_core 0.1.1 rpdf => pdf
            reader = PdfReader(selected_file)
            text=""
            number_of_pages = len(reader.pages)
            for i in range(number_of_pages):
                page = reader.pages[i]
                text += page.extract_text()
            # # print(text)
                
            # Join text
            output_text = join_text(text)
            inject = f"analyze the content below: "+output_text

            print(f"\nPDF cotent extracted as below:\n\n"+text)
            input("---Enter to analyze the PDF content above---")
            
            # print("Processing...")
            # ###########################################
            # # # output = llm("Q: "+inject, max_tokens=4096, echo=True)
            # ###########################################
            from llama_core.rich.progress import Progress
            with Progress(transient=True) as progress:
                task = progress.add_task("Processing", total=None)
                output = llm("Q: "+inject, max_tokens=32768, echo=True)
                answer = output['choices'][0]['text']
                print(answer+"\n")
            # ###########################################

        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No PDF files are available in the current directory.")
        input("--- Press ENTER To Exit ---")
# ###########################################################################
# from rich.progress import Progress (rich dropped)
from llama_core.rich.progress import Progress # generic module adopted (lama_core 0.1.2)

def get_file_size(url):
    with urllib.request.urlopen(url) as response:
        size = int(response.headers['Content-Length'])
    return size

def format_size(size_bytes):
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def clone_file(url):
    try:
        file_size = get_file_size(url)
        filename = os.path.basename(url)
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
# ###########################################################################

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

def __init__():
    parser = argparse.ArgumentParser(description="gguf will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    # Subparser session
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    # Subparser for 'clone [URL]' subcommand
    clone_parser = subparsers.add_parser('clone', help='download a GGUF file/model from URL')
    clone_parser.add_argument('url', type=str, help='URL to download from (i.e., gguf clone [url])')
    # Subparser for subcommands
    subparsers.add_parser('c', help='CLI connector')
    subparsers.add_parser('g', help='GUI connector')
    subparsers.add_parser('i', help='interface selector')
    subparsers.add_parser('p', help='PDF analyzor (beta)')
    subparsers.add_parser('r', help='GGUF metadata reader')
    subparsers.add_parser('s', help='sample GGUF list (download ready)')
    args = parser.parse_args()

    if args.subcommand == 'clone':
        clone_file(args.url)
    elif args.subcommand == 's':
        import os
        file_path = "https://raw.githubusercontent.com/calcuis/gguf-connector/main/src/gguf_connector/data.json"
        # file_path = os.path.join(os.path.dirname(__file__), 'data.json')
        json_data = read_json_file(file_path)
        print("Please select a GGUF file to download:")
        extract_names(json_data)
        handle_user_input(json_data)
    elif args.subcommand == 'r':
        from llama_core import read
    elif args.subcommand == 'i':
        from llama_core import menu
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
                    # if ask == "q" or ask == "Q":
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
        from llama_core import gui
    # elif args.subcommand == 'c':
    #     from llama_core import cli
    elif args.subcommand == 'c':
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
                # ##########################################################
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
                # ##########################################################
            except (ValueError, IndexError):
                print("Invalid choice. Please enter a valid number.")
        else:
            print("No GGUF files are available in the current directory.")
            input("--- Press ENTER To Exit ---")
        print("Goodbye!")
