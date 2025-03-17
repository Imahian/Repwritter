import os
import shutil
import subprocess
import readline
from datetime import datetime
import getpass
from dotenv import load_dotenv
import json
import sys

# Enable tab completion
readline.parse_and_bind('tab: complete')

# Constants
GITENV_PATH = os.path.expanduser("~/.Gitenv")
WRITEUPS_PATH = os.path.expanduser("~/writeups")
SAVED_WRITEUPS_PATH = os.path.expanduser("~/.repwritter/saved_writeups")

def setup_tab_completion():
    """Configure tab completion for paths"""
    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims(' \t\n;')
    readline.set_completer(path_completer)

def path_completer(text, state):
    """Enhanced path completer with better directory handling"""
    if "~" in text:
        text = os.path.expanduser(text)

    if os.path.isdir(text) and text.endswith('/'):
        directory = text
        prefix = ''
    else:
        directory = os.path.dirname(text) or '.'
        prefix = os.path.basename(text)

    try:
        names = os.listdir(directory)
        if prefix:
            names = [n for n in names if n.startswith(prefix)]
        dirs = sorted(n for n in names if os.path.isdir(os.path.join(directory, n)))
        files = sorted(n for n in names if os.path.isfile(os.path.join(directory, n)))
        names = dirs + files

        matches = []
        for name in names:
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                matches.append(os.path.join(directory, name) + '/')
            else:
                matches.append(path)

        if state < len(matches):
            return matches[state]
    except OSError:
        pass
    return None

def get_repo_path():
    """Ask for the repository path with tab completion."""
    setup_tab_completion()
    while True:
        try:
            repo_path = input("\nEnter the path to the repository (use Tab for completion): ").strip()
            repo_path = os.path.expanduser(repo_path)
            if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git")):
                return repo_path
            print("❌ Invalid repository path. Please provide a valid path containing a .git folder.")
        except KeyboardInterrupt:
            print("\nExiting program...")
            sys.exit(0)

def setup_gitenv():
    """Set up the GitHub token in ~/.Gitenv."""
    if os.path.exists(GITENV_PATH):
        print(f"Using existing GitHub token from {GITENV_PATH}.")
        return
    print("GitHub token not found. Let's set it up.")
    try:
        github_token = input("Enter your GitHub token: ").strip()
        with open(GITENV_PATH, "w") as f:
            f.write(f"GITHUB_TOKEN={github_token}")
        print(f"GitHub token saved to {GITENV_PATH}.")
    except KeyboardInterrupt:
        print("\nCancelling setup and exiting...")
        sys.exit(0)

def get_github_token():
    """Retrieve the GitHub token from ~/.Gitenv."""
    if not os.path.exists(GITENV_PATH):
        setup_gitenv()
    load_dotenv(GITENV_PATH)
    return os.getenv("GITHUB_TOKEN")

def ensure_writeups_folder():
    """Ensure the ~/writeups folder exists."""
    if not os.path.exists(WRITEUPS_PATH):
        os.makedirs(WRITEUPS_PATH)
        print(f"Created writeups folder at {WRITEUPS_PATH}.")
    return WRITEUPS_PATH

def ensure_saved_writeups_folder():
    """Ensure the saved writeups folder exists."""
    if not os.path.exists(SAVED_WRITEUPS_PATH):
        os.makedirs(SAVED_WRITEUPS_PATH)
        print(f"Created saved writeups folder at {SAVED_WRITEUPS_PATH}.")
    return SAVED_WRITEUPS_PATH

class WriteupGenerator:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo_name = os.path.basename(os.path.normpath(repo_path))
        self.markdown = ""
        self.sections = {
            'title': False,
            'image': False,
            'description': False
        }
        self.images = []  # Standalone images
        self.title = ""
        self.steps = []  # Descriptions with their own images
        self.flags = []
        self.files = []  # Additional files to upload
        self.writeup_name = None
        self.input_order = []
        self.saved = False

    def show_menu(self):
        print("\n" + "=" * 40)
        print("WRITEUP GENERATOR")
        print("=" * 40)

        # Display current inputs in order
        if self.input_order:
            print("\nCurrent Writeup:")
            for input_type, index in self.input_order:
                if input_type == 'title':
                    print(f"Title: {self.title}")
                elif input_type == 'image':
                    image_name, _ = self.images[index]
                    print(f"Image: {image_name}")
                elif input_type == 'step':
                    subtitle, _, _, _ = self.steps[index]
                    print(f"Description: {subtitle}")
                elif input_type == 'flag':
                    flag = self.flags[index]
                    print(f"Flag: {flag[:4]}****")
                elif input_type == 'file':
                    file_name, _ = self.files[index]
                    print(f"File: {file_name}")

        options = [
            ("1", "Add Title"),
            ("2", "Add Image"),  # Changed from "Add Machine Image" for brevity
            ("3", "Add Description with Subtitle, One-liner, and/or Image"),
            ("4", "Add Flag"),
            ("5", "Add File"),
            ("6", "Edit Steps"),
            ("S", "Save Current Writeup"),
            ("L", "Load Writeup"),
            ("F", "Finish and Generate Writeup"),
            ("Q", "Quit without Saving")
        ]
        print("\nOptions:")
        for opt, label in options:
            print(f"  {opt}. {label}")
        return input("\nSelect an option: ")

    def add_title(self):
        try:
            new_title = input("\nEnter the machine title: ").strip()
            if new_title:
                if not any(item[0] == 'title' for item in self.input_order):
                    self.input_order.append(('title', None))
                self.title = new_title
                self.markdown = f"# {self.title}\n\n"
                self.sections['title'] = True
                self.saved = False
                print("✅ Title updated.")
            else:
                print("❌ Title cannot be empty.")
        except KeyboardInterrupt:
            print("\nCancelled title input, returning to menu...")
            return

    def add_machine_image(self):
        try:
            image_name = input("\nEnter a unique name for the image: ").strip()
            while not image_name or any(name == image_name for name, _ in self.images):
                print("Image name already exists or is invalid. Choose another.")
                image_name = input("Enter a unique name for the image: ").strip()

            setup_tab_completion()
            image_path = input(f"Enter the path to the image '{image_name}' (use Tab for completion): ").strip()
            image_path = os.path.expanduser(image_path)
            if os.path.isfile(image_path):
                self.images.append((image_name, image_path))
                self.input_order.append(('image', len(self.images) - 1))
                self.markdown += f"<div align='center'>\n  <img src='img/{image_name}.png' width='400' alt='Machine Image'>\n</div>\n\n"
                self.sections['image'] = True
                self.saved = False
                print(f"✅ Image '{image_name}' added.")
            else:
                print("❌ File not found.")
        except KeyboardInterrupt:
            print("\nCancelled image input, returning to menu...")
            return

    def process_references(self, text):
        words_to_process = []
        current_text = text
        while '[' in current_text and ']' in current_text:
            start = current_text.find('[')
            end = current_text.find(']')
            word = current_text[start + 1:end]
            if word not in [w for w, _ in words_to_process]:
                words_to_process.append((word, None))
            current_text = current_text[end + 1:]

        if words_to_process:
            print("\nEnter URLs for references:")
            for i, (word, _) in enumerate(words_to_process):
                try:
                    url = input(f"URL for '{word}': ")
                    words_to_process[i] = (word, url)
                except KeyboardInterrupt:
                    print("\nCancelled URL input, using empty URLs for remaining...")
                    break

        result = text
        for word, url in words_to_process:
            result = result.replace(f"[{word}]", f"[{word}]({url})")
        return result

    def add_description(self):
        try:
            subtitle = input("\nEnter the subtitle for this section: ").strip()
            print("\nEnter the description (type 'END' on a new line to finish):")
            description = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'END':
                        break
                    line = self.process_references(line)
                    description.append(line)
                except KeyboardInterrupt:
                    print("\nCancelled description input, saving current content...")
                    break

            self.markdown += f"## {subtitle}\n\n"
            self.markdown += "\n".join(description) + "\n\n"

            add_oneliner = input("Add a one-liner? (y/n): ").lower()
            oneliner = None
            if add_oneliner == 'y':
                try:
                    oneliner = input("Enter the one-liner (terminal style): ")
                    self.markdown += f"```bash\n {oneliner}\n```\n\n"
                except KeyboardInterrupt:
                    print("\nCancelled one-liner input, proceeding without...")
                    oneliner = None

            add_image = input("Add an image? (y/n): ").lower()
            image_name = None
            image_path = None
            if add_image == 'y':
                setup_tab_completion()
                while True:
                    try:
                        image_path = input("Enter the path to the image (use Tab for completion): ").strip()
                        image_path = os.path.expanduser(image_path)
                        if os.path.isfile(image_path):
                            image_name = input("Enter a name for the image (e.g., 'scan_results'): ")
                            self.markdown += f"<div align='center'>\n  <img src='img/{image_name}.png' width='600' alt='{subtitle}'>\n</div>\n\n"
                            break
                        else:
                            print("❌ File not found. Please check the path.")
                    except KeyboardInterrupt:
                        print("\nCancelled image input, proceeding without...")
                        break

            self.steps.append((subtitle, description, oneliner, (image_name, image_path) if image_name else None))
            self.input_order.append(('step', len(self.steps) - 1))
            self.sections['description'] = True
            self.saved = False
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            return

    def add_flag(self):
        try:
            real_flag = input("\nEnter the flag: ").strip()
            if not real_flag:
                print("❌ Flag cannot be empty.")
                return

            flag_length = len(real_flag)
            blurred = real_flag[:flag_length // 2] + "*" * (flag_length - flag_length // 2)
            self.markdown += f"\n## Flag\n\n```bash\n{blurred}\n```\n"
            self.flags.append(real_flag)
            self.input_order.append(('flag', len(self.flags) - 1))
            self.saved = False
            print("✅ Flag added successfully.")
        except KeyboardInterrupt:
            print("\nCancelled flag input, returning to menu...")
            return

    def add_file(self):
        try:
            file_name = input("\nEnter a unique name for the file: ").strip()
            while not file_name or any(name == file_name for name, _ in self.files):
                print("File name already exists or is invalid. Choose another.")
                file_name = input("Enter a unique name for the file: ").strip()

            setup_tab_completion()
            file_path = input(f"Enter the path to the file '{file_name}' (use Tab for completion): ").strip()
            file_path = os.path.expanduser(file_path)
            if os.path.isfile(file_path):
                self.files.append((file_name, file_path))
                self.input_order.append(('file', len(self.files) - 1))
                self.saved = False
                print(f"✅ File '{file_name}' added.")
            else:
                print("❌ File not found.")
        except KeyboardInterrupt:
            print("\nCancelled file input, returning to menu...")
            return

    def edit_steps(self):
        if not self.input_order:
            print("No steps to edit.")
            return

        while True:
            try:
                print("\nEdit Steps:")
                print("=" * 40)
                options = []
                for i, (input_type, index) in enumerate(self.input_order, 1):
                    if input_type == 'title':
                        label = f"Edit Title: {self.title}"
                    elif input_type == 'image':
                        image_name, image_path = self.images[index]
                        label = f"Edit Image: {image_name} ({image_path})"
                    elif input_type == 'step':
                        subtitle, _, _, _ = self.steps[index]
                        label = f"Edit Description: {subtitle}"
                    elif input_type == 'flag':
                        flag = self.flags[index]
                        label = f"Edit Flag: {flag[:4]}****"
                    elif input_type == 'file':
                        file_name, file_path = self.files[index]
                        label = f"Edit File: {file_name} ({file_path})"
                    options.append((str(i), label))

                options.append(("b", "Go back"))

                print("\nAvailable Options:")
                for opt, label in options:
                    print(f"{opt:>3}. {label}")

                choice = input("\nSelect an option: ").lower()
                if choice == 'b':
                    break

                if choice.isdigit():
                    choice = int(choice) - 1
                    if 0 <= choice < len(self.input_order):
                        input_type, index = self.input_order[choice]
                        if input_type == 'title':
                            self.add_title()
                        elif input_type == 'image':
                            self.edit_image(index)
                        elif input_type == 'step':
                            self.edit_description(index)
                        elif input_type == 'flag':
                            self.edit_flag(index)
                        elif input_type == 'file':
                            self.edit_file(index)
                    else:
                        print("❌ Invalid option. Try again.")
                else:
                    print("❌ Invalid option. Try again.")
            except KeyboardInterrupt:
                print("\nReturning to main menu...")
                break

    def edit_image(self, index):
        image_name, image_path = self.images[index]
        print(f"\nEditing Image: {image_name} ({image_path})")
        try:
            new_path = input("Enter new image path (or press Enter to keep current): ").strip()
            if new_path and os.path.isfile(os.path.expanduser(new_path)):
                self.images[index] = (image_name, os.path.expanduser(new_path))
                self.saved = False
                print("✅ Image updated.")
            elif new_path:
                print("❌ File not found.")
        except KeyboardInterrupt:
            print("\nCancelled image edit, returning...")
            return

    def edit_flag(self, index):
        current_flag = self.flags[index]
        print(f"\nEditing Flag: {current_flag}")
        try:
            new_flag = input("Enter new flag (or press Enter to keep current): ").strip()
            if new_flag:
                self.flags[index] = new_flag
                self.saved = False
                print("✅ Flag updated.")
        except KeyboardInterrupt:
            print("\nCancelled flag edit, returning...")
            return

    def edit_file(self, index):
        file_name, file_path = self.files[index]
        print(f"\nEditing File: {file_name} ({file_path})")
        try:
            new_name = input("Enter new file name (or press Enter to keep current): ").strip()
            new_path = input("Enter new file path (or press Enter to keep current): ").strip()
            if new_path and not os.path.isfile(os.path.expanduser(new_path)):
                print("❌ File not found.")
                return
            if new_name or new_path:
                self.files[index] = (
                    new_name if new_name else file_name,
                    os.path.expanduser(new_path) if new_path else file_path
                )
                self.saved = False
                print("✅ File updated.")
        except KeyboardInterrupt:
            print("\nCancelled file edit, returning...")
            return

    def edit_description(self, index):
        subtitle, description, oneliner, image_info = self.steps[index]
        image_name, image_path = image_info if image_info else (None, None)
        while True:
            try:
                print(f"\nEdit Description: {subtitle}")
                print("=" * 40)
                print(f"1. Edit Subtitle: {subtitle}")
                print(f"2. Edit Description: {' '.join(description[:1])}...")
                print(f"3. Edit Oneliner: {oneliner if oneliner else 'None'}")
                print(f"4. Edit Image: {image_name if image_name else 'None'} ({image_path if image_path else 'No path'})")
                print("b. Go back")

                choice = input("\nSelect what to edit: ").lower()
                if choice == 'b':
                    break

                if choice == '1':
                    new_subtitle = input(f"New subtitle (current: '{subtitle}'): ").strip()
                    if new_subtitle:
                        self.steps[index] = (new_subtitle, description, oneliner, image_info)
                        subtitle = new_subtitle
                        self.saved = False
                        print("✅ Subtitle updated.")

                elif choice == '2':
                    print(f"\nCurrent description:\n{' '.join(description)}")
                    print("\nEnter new description (type 'END' on a new line to finish):")
                    new_description = []
                    while True:
                        try:
                            line = input()
                            if line.strip().upper() == 'END':
                                break
                            new_description.append(line)
                        except KeyboardInterrupt:
                            print("\nCancelled description edit, saving current...")
                            break
                    if new_description:
                        self.steps[index] = (subtitle, new_description, oneliner, image_info)
                        self.saved = False
                        print("✅ Description updated.")

                elif choice == '3':
                    new_oneliner = input(f"New one-liner (current: '{oneliner if oneliner else 'None'}'): ").strip()
                    if new_oneliner:
                        self.steps[index] = (subtitle, description, new_oneliner, image_info)
                        self.saved = False
                        print("✅ Oneliner updated.")
                    elif new_oneliner == "":
                        self.steps[index] = (subtitle, description, None, image_info)
                        self.saved = False
                        print("✅ Oneliner removed.")

                elif choice == '4':
                    current_image_path = image_path if image_path else "None"
                    print(f"Current image: {current_image_path}")
                    new_image_path = input("Enter new image path (Tab for completion, Enter to keep current): ").strip()
                    if new_image_path and os.path.isfile(os.path.expanduser(new_image_path)):
                        new_image_name = input("Enter new image name (or press Enter to keep current): ").strip() or image_name or "default_image"
                        self.steps[index] = (subtitle, description, oneliner, (new_image_name, os.path.expanduser(new_image_path)))
                        self.saved = False
                        print("✅ Image updated.")
                    elif new_image_path:
                        print("❌ Invalid image path")
            except KeyboardInterrupt:
                print("\nReturning to edit menu...")
                break

    def load_readme(self):
        while True:
            try:
                print("\nLoad Writeup Options:")
                print("=" * 40)
                print("1. Load from ~/writeups/")
                print("2. Load from any system path")
                print("b. Go back")
                choice = input("\nSelect an option: ").lower()

                if choice == 'b':
                    return False

                if choice not in ['1', '2']:
                    print("❌ Invalid option. Try again.")
                    continue

                setup_tab_completion()
                if choice == '1':
                    subfolders = [f for f in os.listdir(WRITEUPS_PATH) if os.path.isdir(os.path.join(WRITEUPS_PATH, f))]
                    if subfolders:
                        print("\nAvailable folders in ~/writeups/:")
                        for i, folder in enumerate(subfolders, 1):
                            print(f"{i}. {folder}")
                        selection = input("\nSelect a folder by number: ")
                        try:
                            index = int(selection) - 1
                            if 0 <= index < len(subfolders):
                                full_path = os.path.join(WRITEUPS_PATH, subfolders[index])
                            else:
                                print("❌ Invalid selection. Try again.")
                                continue
                        except ValueError:
                            print("❌ Invalid input. Please enter a number.")
                            continue
                    else:
                        full_path = WRITEUPS_PATH
                        print(f"❌ No subfolders found in {WRITEUPS_PATH}")
                        create = input(f"Would you like to create a new writeup in {WRITEUPS_PATH}? (y/n): ").lower()
                        if create == 'y':
                            self.title = os.path.basename(os.path.normpath(full_path))
                            self.markdown = f"# {self.title}\n\n"
                            self.sections['title'] = True
                            self.input_order = [('title', None)]
                            readme_path = os.path.join(full_path, "README.md")
                            with open(readme_path, 'w') as f:
                                f.write(self.markdown)
                            self.saved = True
                            print(f"✅ Created README.md in {full_path}. Returning to main menu.")
                            return True
                        else:
                            print("Returning to load menu...")
                            continue
                else:
                    full_path = input("Enter the full folder path (use Tab for completion): ").strip()
                    full_path = os.path.expanduser(full_path)

                if not os.path.isdir(full_path):
                    print("❌ Folder does not exist.")
                    continue

                readme_path = os.path.join(full_path, "README.md")
                if os.path.isfile(readme_path):
                    with open(readme_path, 'r') as f:
                        self.markdown = f.read()
                    self.title = os.path.basename(os.path.normpath(full_path))
                    self.sections['title'] = True
                    self.input_order = [('title', None)]
                    self.saved = True
                    print(f"✅ Loaded README.md from {full_path}")
                    return True
                else:
                    print(f"❌ No README.md found in {full_path}")
                    create = input("Would you like to create a new README.md in this folder? (y/n): ").lower()
                    if create == 'y':
                        self.title = os.path.basename(os.path.normpath(full_path))
                        self.markdown = f"# {self.title}\n\n"
                        self.sections['title'] = True
                        self.input_order = [('title', None)]
                        with open(readme_path, 'w') as f:
                            f.write(self.markdown)
                        self.saved = True
                        print(f"✅ Created README.md in {full_path}. Returning to main menu.")
                        return True
                    else:
                        print("Returning to load menu...")
            except KeyboardInterrupt:
                print("\nReturning to main menu...")
                return False

    def load_state(self, file_path):
        """Load the state from a saved .json file."""
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)

            self.repo_path = state.get('repo_path', self.repo_path)
            self.markdown = state.get('markdown', "")
            self.sections = state.get('sections', {'title': False, 'image': False, 'description': False})
            self.images = [(img[0], img[1]) for img in state.get('images', [])]
            self.title = state.get('title', "")
            self.steps = [(s, d, o, tuple(i) if i else None) for s, d, o, i in state.get('steps', [])]
            self.flags = state.get('flags', [])
            self.files = [(f[0], f[1]) for f in state.get('files', [])]
            self.input_order = state.get('input_order', [])
            self.writeup_name = state.get('writeup_name', os.path.splitext(os.path.basename(file_path))[0])
            self.saved = True

            print(f"✅ Loaded writeup '{self.writeup_name}' from {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading writeup from {file_path}: {e}")
            return False

    def generate_writeup(self):
        required_missing = [k for k, v in self.sections.items() if not v]
        if required_missing:
            print(f"\n⚠️ Missing required sections: {', '.join(required_missing)}")
            return None

        self.markdown += "<div align='center'>\n"
        self.markdown += "  <p>Thanks for reading! Follow me on my socials:</p>\n"
        self.markdown += "  <a href='https://x.com/@imahian'><img src='https://www.vectorlogo.zone/logos/x/x-icon.svg' alt='X' width='40'></a>\n"
        self.markdown += "  <a href='https://discord.gg/dbesG8EX'><img src='https://www.vectorlogo.zone/logos/discord/discord-icon.svg' alt='Discord' width='40'></a>\n"
        self.markdown += "  <a href='https://youtube.com/@imahian'><img src='https://www.vectorlogo.zone/logos/youtube/youtube-icon.svg' alt='YouTube' width='40'></a>\n"
        self.markdown += "  <a href='https://twitch.tv/imahian'><img src='https://www.vectorlogo.zone/logos/twitch/twitch-icon.svg' alt='Twitch' width='40'></a>\n"
        self.markdown += "</div>\n\n"
        self.markdown += "---\n"

        # Save locally in title folder structure
        writeups_folder = ensure_writeups_folder()
        title_folder = os.path.join(writeups_folder, self.title)
        os.makedirs(title_folder, exist_ok=True)
        file_path = os.path.join(title_folder, "README.md")
        with open(file_path, 'w') as f:
            f.write(self.markdown)

        # Copy all images (standalone and from steps) to img/ folder
        img_folder = os.path.join(title_folder, "img")
        os.makedirs(img_folder, exist_ok=True)
        # Standalone images
        for image_name, image_path in self.images:
            shutil.copy(image_path, os.path.join(img_folder, f"{image_name}.png"))
        # Images from descriptions
        for _, _, _, image_info in self.steps:
            if image_info:
                image_name, image_path = image_info
                shutil.copy(image_path, os.path.join(img_folder, f"{image_name}.png"))

        # Copy additional files to title folder
        for file_name, file_path in self.files:
            shutil.copy(file_path, os.path.join(title_folder, file_name))

        self.saved = True
        print(f"\n✅ Writeup generated successfully: {file_path}")
        return file_path

    def upload_to_github(self, file_path, target_folder):
        # Use self.title for the folder name, save as README.md
        machine_folder = os.path.join(target_folder, self.title)
        os.makedirs(machine_folder, exist_ok=True)
        shutil.copy(file_path, os.path.join(machine_folder, "README.md"))
        img_folder = os.path.join(machine_folder, "img")
        os.makedirs(img_folder, exist_ok=True)
        # Copy all images (standalone and from steps) to img/
        for image_name, image_path in self.images:
            shutil.copy(image_path, os.path.join(img_folder, f"{image_name}.png"))
        for _, _, _, image_info in self.steps:
            if image_info:
                image_name, image_path = image_info
                shutil.copy(image_path, os.path.join(img_folder, f"{image_name}.png"))
        # Copy additional files to the root of the machine folder
        for file_name, file_path in self.files:
            shutil.copy(file_path, os.path.join(machine_folder, file_name))
        os.chdir(target_folder)
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Add writeup: {self.title}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"\n✅ Writeup, images, and files uploaded to GitHub in folder: {self.title}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing Git commands: {e}")

    def save_state(self):
        if not self.writeup_name:
            self.writeup_name = input("Enter a name for this writeup: ").strip()
            while not self.writeup_name or os.path.exists(os.path.join(SAVED_WRITEUPS_PATH, f"{self.writeup_name}.json")):
                print("Name already exists or is invalid. Choose another.")
                self.writeup_name = input("Enter a name for this writeup: ").strip()
        state = {
            'repo_path': self.repo_path,
            'markdown': self.markdown,
            'sections': self.sections,
            'images': self.images,
            'title': self.title,
            'steps': self.steps,
            'flags': self.flags,
            'files': self.files,
            'input_order': self.input_order,
            'writeup_name': self.writeup_name
        }
        save_file = os.path.join(SAVED_WRITEUPS_PATH, f"{self.writeup_name}.json")
        with open(save_file, 'w') as f:
            json.dump(state, f)
        self.saved = True
        print(f"Writeup saved to {save_file}")

def recursive_folder_selection(base_path):
    while True:
        try:
            print("\nAvailable folders:")
            folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
            for i, folder in enumerate(folders, 1):
                print(f"{i}. {folder}")
            print(f"{len(folders) + 1}. Select this folder")
            print(f"{len(folders) + 2}. Go back")

            choice = input("Enter the number of the folder to navigate (or 's' to select this folder, 'b' to go back): ").lower()
            if choice == 's':
                return base_path
            if choice == 'b':
                return None

            choice = int(choice) - 1
            if choice < 0 or choice >= len(folders) + 2:
                print("❌ Invalid choice.")
                continue
            if choice == len(folders):
                return base_path
            if choice == len(folders) + 1:
                return None
            selected_folder = folders[choice]
            new_path = os.path.join(base_path, selected_folder)
            result = recursive_folder_selection(new_path)
            if result:
                return result
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nReturning to previous menu...")
            return None

def get_target_folder(repo_path):
    print("\nSelect the folder to save the writeup:")
    try:
        target_folder = recursive_folder_selection(repo_path)
        if not target_folder:
            print("❌ No folder selected.")
            return None
        return target_folder
    except KeyboardInterrupt:
        print("\nReturning to main menu...")
        return None

def main():
    print("""
    .------------------------------------------------------------------------------.
    |                             .mmMMMMMMMMMMMMMmm.                              |
    |                         .mMMMMMMMMMMMMMMMMMMMMMMMm.                          |
    |                      .mMMMMMMMMMMMMMMMMMMMMMMMMMMMMMm.                       |
    |                    .MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.                     |
    |                  .MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.                   |
    |                 MMMMMMMM'  `"MMMMM~~~~~~~MMMM""`  'MMMMMMMM                  |
    |                MMMMMMMMM                           MMMMMMMMM                 |
    |               MMMMMMMMMM:                         :MMMMMMMMMM                |
    |              .MMMMMMMMMM                           MMMMMMMMMM.               |
    |              MMMMMMMMM"                             "MMMMMMMMM               |
    |              MMMMMMMMM                               MMMMMMMMM               |
    |              MMMMMMMMM           REPWRITER           MMMMMMMMM               |
    |              MMMMMMMMMM                             MMMMMMMMMM               |
    |              `MMMMMMMMMM                           MMMMMMMMMM`               |
    |               MMMMMMMMMMMM.                     .MMMMMMMMMMMM                |
    |                MMMMMM  MMMMMMMMMM         MMMMMMMMMMMMMMMMMM                 |
    |                 MMMMMM  'MMMMMMM           MMMMMMMMMMMMMMMM                  |
    |                  `MMMMMM  "MMMMM           MMMMMMMMMMMMMM`                   |
    |                    `MMMMMm                 MMMMMMMMMMMM`                     |
    |                      `"MMMMMMMMM           MMMMMMMMM"`                       |
    |                         `"MMMMMM           MMMMMM"`                          |
    |                             `""M           M""`                              |
    '------------------------------------------------------------------------------'
    """)

    try:
        github_token = get_github_token()
        repo_path = get_repo_path()
        ensure_saved_writeups_folder()

        generator = WriteupGenerator(repo_path)

        while True:
            try:
                choice = generator.show_menu().lower()

                if choice == '1':
                    generator.add_title()
                elif choice == '2':
                    generator.add_machine_image()
                elif choice == '3':
                    generator.add_description()
                elif choice == '4':
                    generator.add_flag()
                elif choice == '5':
                    generator.add_file()
                elif choice == '6':
                    generator.edit_steps()
                elif choice == 's':
                    generator.save_state()
                elif choice == 'l':
                    saved_files = [f for f in os.listdir(SAVED_WRITEUPS_PATH) if f.endswith('.json')]
                    if not saved_files:
                        print("\nNo saved writeups found.")
                        generator.load_readme()
                        continue
                    print("\nAvailable Saved Writeups:")
                    for i, file in enumerate(saved_files, 1):
                        print(f"{i}. {file}")
                    print("b. Go back or load from README")
                    selection = input("\nSelect a writeup to load (number) or 'b' to go back: ").lower()
                    if selection == 'b':
                        generator.load_readme()
                        continue
                    try:
                        index = int(selection) - 1
                        if 0 <= index < len(saved_files):
                            file_path = os.path.join(SAVED_WRITEUPS_PATH, saved_files[index])
                            if generator.load_state(file_path):
                                print("Writeup loaded successfully. You can now edit it.")
                            else:
                                print("Failed to load writeup.")
                        else:
                            print("❌ Invalid selection.")
                    except ValueError:
                        print("❌ Invalid input. Please enter a number or 'b'.")
                elif choice == 'f':
                    md_file = generator.generate_writeup()
                    if md_file:
                        target_folder = get_target_folder(repo_path)
                        if not target_folder:
                            continue
                        if not os.path.exists(target_folder):
                            print(f"❌ Target folder not found: {target_folder}")
                            continue
                        generator.upload_to_github(md_file, target_folder)
                        if generator.writeup_name and input("Delete saved writeup state? (y/n): ").lower() == 'y':
                            save_file = os.path.join(SAVED_WRITEUPS_PATH, f"{generator.writeup_name}.json")
                            if os.path.exists(save_file):
                                os.remove(save_file)
                                print("Saved state deleted.")
                    break
                elif choice == 'q':
                    if not generator.saved and (generator.title or generator.images or generator.steps or generator.flags or generator.files):
                        print("\nYou have unsaved changes. Do you want to exit without saving?")
                        print("S/s: Save and exit")
                        print("Q/q: Quit without saving")
                        exit_choice = input("Select an option: ").lower()
                        if exit_choice == 's':
                            generator.save_state()
                            print("Exiting program...")
                            sys.exit(0)
                        elif exit_choice == 'q':
                            print("\nExiting without saving...")
                            sys.exit(0)
                        else:
                            print("Invalid choice, returning to menu...")
                            continue
                    print("\n❌ Operation canceled")
                    break
                else:
                    print("\n⚠️ Invalid option, try again")
            except KeyboardInterrupt:
                if not generator.saved and (generator.title or generator.images or generator.steps or generator.flags or generator.files):
                    print("\nYou have unsaved changes. Do you want to exit without saving?")
                    print("S/s: Save and exit")
                    print("Q/q: Quit without saving")
                    try:
                        exit_choice = input("Select an option: ").lower()
                        if exit_choice == 's':
                            generator.save_state()
                            print("Exiting program...")
                            sys.exit(0)
                        elif exit_choice == 'q':
                            print("\nExiting without saving...")
                            sys.exit(0)
                        else:
                            print("Invalid choice, returning to menu...")
                            continue
                    except KeyboardInterrupt:
                        print("\nForcing exit without saving...")
                        sys.exit(0)
                else:
                    print("\nExiting program...")
                    sys.exit(0)

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
