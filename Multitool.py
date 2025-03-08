import os
import shutil
from pathlib import Path
import hashlib
import datetime
import psutil
import platform
import subprocess
from cryptography.fernet import Fernet
import json
import time
from datetime import datetime
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import mimetypes
import humanize
import keyboard
import stat
import win32security
import win32api
import win32con
import win32file
from datetime import timedelta
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pyautogui
import re
import random
import sys
import fnmatch

init(autoreset=True)

PROGRAM_NAME = "Multitool v3.2"

def display_header():
    width = min(os.get_terminal_size().columns, 60)
    print(f"{Fore.CYAN}╔═{'═' * (width-4)}═╗")
    print(f"{Fore.CYAN}║ {Back.BLUE + Fore.WHITE + Style.BRIGHT}{PROGRAM_NAME.center(width-4)}{Style.RESET_ALL + Fore.CYAN} ║")
    print(f"{Fore.CYAN}║ {Fore.WHITE}Made by Darnix{' ' * (width-17)}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")

def display_menu_section(title, options, start_num):
    width = min(os.get_terminal_size().columns, 60)
    print(f"{Fore.CYAN}║ {Fore.CYAN + Style.BRIGHT}{title}{' ' * (width-3-len(title))}║")
    print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")
    
    for i, option in enumerate(options, start=start_num):
        option_text = option[:40] if len(option) > 40 else option
        remaining_space = width - 3 - len(str(i)) - len(option_text) - 1
        print(f"{Fore.CYAN}║{Fore.YELLOW} {i}{Fore.WHITE} {option_text}{' ' * remaining_space}{Fore.CYAN}║")

def preview_file(filepath):
    try:
        mime_type, _ = mimetypes.guess_type(filepath)
        size = os.path.getsize(filepath)
        modified = os.path.getmtime(filepath)
        
        print(f"\n{Fore.CYAN}File Preview: {Fore.WHITE}{filepath}")
        print(f"{Fore.YELLOW}Type: {Fore.WHITE}{mime_type}")
        print(f"{Fore.YELLOW}Size: {Fore.WHITE}{humanize.naturalsize(size)}")
        print(f"{Fore.YELLOW}Modified: {Fore.WHITE}{datetime.fromtimestamp(modified)}")
        
        if mime_type and mime_type.startswith('text'):
            print(f"\n{Fore.CYAN}Content Preview:{Fore.WHITE}")
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read(500) + "...")
    except Exception as e:
        print(f"{Fore.RED}Preview error: {e}")

def quick_actions():
    actions = [
        "Sort files by size (largest first)",
        "Sort files by date (newest first)",
        "Copy file list to clipboard",
        "Create Windows shortcut",
        "Back to main menu"
    ]
    
    while True:
        print(f"\n{Fore.CYAN}═══ Quick Actions Menu ═══")
        for i, action in enumerate(actions, 1):
            print(f"{Fore.YELLOW}{i}. {Fore.WHITE}{action}")
            
        print(f"\n{Fore.CYAN}What would you like to do?")
        choice = input(f"{Fore.GREEN}Enter your choice (1-5): {Fore.WHITE}")
        
        if choice == "1":
            files = [(f, os.path.getsize(f)) for f in os.listdir() if os.path.isfile(f)]
            files.sort(key=lambda x: x[1], reverse=True)
            print(f"\n{Fore.CYAN}Files in current directory, sorted by size:")
            for file, size in files:
                print(f"{Fore.WHITE}{humanize.naturalsize(size):>10} - {file}")
                
        elif choice == "2":
            files = [(f, os.path.getmtime(f)) for f in os.listdir() if os.path.isfile(f)]
            files.sort(key=lambda x: x[1], reverse=True)
            print(f"\n{Fore.CYAN}Files in current directory, sorted by date:")
            for file, mtime in files:
                print(f"{Fore.WHITE}{datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')} - {file}")

        elif choice == "3":
            file_list = "\n".join(os.listdir())
            import pyperclip
            pyperclip.copy(file_list)
            print(f"{Fore.GREEN}✓ List of {len(os.listdir())} files copied to clipboard!")
            
        elif choice == "4":
            if os.name == 'nt':
                target = input(f"{Fore.YELLOW}Enter name of file/folder to create shortcut for: {Fore.WHITE}")
                if os.path.exists(target):
                    import winshell
                    from win32com.client import Dispatch
                    shortcut = os.path.splitext(target)[0] + ".lnk"
                    shell = Dispatch('WScript.Shell')
                    link = shell.CreateShortCut(shortcut)
                    link.Targetpath = os.path.abspath(target)
                    link.save()
                    print(f"{Fore.GREEN}✓ Shortcut created: {shortcut}")
                else:
                    print(f"{Fore.RED}× Target not found in current directory!")
            else:
                print(f"{Fore.RED}× Shortcuts only supported on Windows!")
                
        elif choice == "5":
            break
        else:
            print(f"{Fore.RED}× Invalid choice!")
        
        if choice != "5":
            input(f"\n{Fore.CYAN}Press Enter to continue...")

def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def search_files(directory, pattern):
    found_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if pattern.lower() in file.lower():
                found_files.append(os.path.join(root, file))
    return found_files

def find_duplicates(directory):
    print("Scanning for duplicates (this might take a while)...")
    hash_dict = {}
    total_files = sum([len(files) for _, _, files in os.walk(directory)])
    processed = 0
    
    for root, _, files in os.walk(directory):
        for filename in files:
            try:
                filepath = os.path.join(root, filename)
                file_hash = get_file_hash(filepath)
                if file_hash in hash_dict:
                    hash_dict[file_hash].append(filepath)
                else:
                    hash_dict[file_hash] = [filepath]
                processed += 1
                print(f"Progress: {processed}/{total_files} files scanned\r", end="")
            except (PermissionError, OSError):
                continue
    
    return {k: v for k, v in hash_dict.items() if len(v) > 1}

def analyze_disk_space(directory):
    size_dict = {}
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                ext = os.path.splitext(file)[1].lower()
                size_dict[ext] = size_dict.get(ext, 0) + size
            except OSError:
                continue
    return size_dict

def create_folder(directory, folder_name):
    folder_path = os.path.join(directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def organize_files(directory):
    CATEGORIES = {
        'Images': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'description': 'Picture files and graphics'
        },
        'Documents': {
            'extensions': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.csv', '.rtf', '.odt'],
            'description': 'Text and document files'
        },
        'Audio': {
            'extensions': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'],
            'description': 'Music and sound files'
        },
        'Video': {
            'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'description': 'Movie and video files'
        },
        'Archives': {
            'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'description': 'Compressed files and archives'
        },
        'Code': {
            'extensions': ['.py', '.java', '.cpp', '.html', '.css', '.js', '.php'],
            'description': 'Programming and script files'
        }
    }
    
    try:
        moved_files = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_ext = os.path.splitext(filename)[1].lower()
                for category, info in CATEGORIES.items():
                    if file_ext in info['extensions']:
                        category_path = create_folder(directory, category)
                        shutil.move(filepath, os.path.join(category_path, filename))
                        moved_files += 1
                        print(f"Moved {filename} to {category} ({info['description']})")
                        break
        print(f"\nOrganization complete! Moved {moved_files} files.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def rename_files(directory, pattern, replacement):
    renamed = 0
    for filename in os.listdir(directory):
        if pattern in filename:
            new_name = filename.replace(pattern, replacement)
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            renamed += 1
    return renamed

def get_drives():
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):
        if bitmask & (1 << (letter - 65)):
            drives.append(chr(letter) + ":\\")
    return drives

def change_directory():
    while True:
        current_dir = os.getcwd()
        print(f"\nCurrent directory: {current_dir}")
        print("\nOptions:")
        print("1. Go to parent directory")
        print("2. Select subdirectory")
        print("3. Go to specific drive")
        print("4. Enter custom path")
        print("5. Return to main menu")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '1':
            parent = os.path.dirname(current_dir)
            if os.path.exists(parent):
                os.chdir(parent)
        
        elif choice == '2':
            try:
                subdirs = [d for d in os.listdir(current_dir) 
                          if os.path.isdir(os.path.join(current_dir, d))]
                if not subdirs:
                    print("No subdirectories found!")
                    continue
                    
                print("\nAvailable subdirectories:")
                for i, d in enumerate(subdirs, 1):
                    print(f"{i}. {d}")
                    
                idx = int(input("\nSelect directory number: ")) - 1
                if 0 <= idx < len(subdirs):
                    new_dir = os.path.join(current_dir, subdirs[idx])
                    os.chdir(new_dir)
            except (ValueError, IndexError):
                print("Invalid selection!")
        
        elif choice == '3':
            drives = get_drives()
            print("\nAvailable drives:")
            for i, drive in enumerate(drives, 1):
                print(f"{i}. {drive}")
            try:
                idx = int(input("\nSelect drive number: ")) - 1
                if 0 <= idx < len(drives):
                    os.chdir(drives[idx])
            except (ValueError, IndexError):
                print("Invalid selection!")
        
        elif choice == '4':
            custom_path = input("Enter full path: ")
            if os.path.exists(custom_path):
                os.chdir(custom_path)
            else:
                print("Invalid path!")
        
        elif choice == '5':
            break

def get_system_info():
    try:
        info = {
            "OS": f"{platform.system()} {platform.release()}",
            "CPU": platform.processor(),
            "RAM Total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "RAM Available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "Disk Usage": {}
        }
        
        for partition in psutil.disk_partitions():
            if 'fixed' in partition.opts:
                usage = psutil.disk_usage(partition.mountpoint)
                info["Disk Usage"][partition.mountpoint] = (
                    f"{usage.used / (1024**3):.1f}GB used / "
                    f"{usage.total / (1024**3):.1f}GB total "
                    f"({usage.percent}% full)"
                )
        return info
    except Exception as e:
        return f"Error getting system info: {str(e)}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_categories():
    CATEGORIES = {
        'Images': {
            'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'description': 'Picture files and graphics'
        },
        'Documents': {
            'extensions': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.csv', '.rtf', '.odt'],
            'description': 'Text and document files'
        },
        'Audio': {
            'extensions': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'],
            'description': 'Music and sound files'
        },
        'Video': {
            'extensions': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'description': 'Movie and video files'
        },
        'Archives': {
            'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'description': 'Compressed files and archives'
        },
        'Code': {
            'extensions': ['.py', '.java', '.cpp', '.html', '.css', '.js', '.php'],
            'description': 'Programming and script files'
        }
    }
    
    try:
        print("\nFile Categories and Extensions:")
        for category, info in CATEGORIES.items():
            print(f"\n{category}:")
            print(f"Description: {info['description']}")
            print(f"Extensions: {', '.join(info['extensions'])}")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"Error displaying categories: {str(e)}")

def encrypt_file(filepath, key=None):
    if not key:
        key = Fernet.generate_key()
        with open('encryption_key.key', 'wb') as key_file:
            key_file.write(key)
    
    f = Fernet(key)
    with open(filepath, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    with open(filepath + '.encrypted', 'wb') as file:
        file.write(encrypted_data)
    return key

def decrypt_file(filepath, key):
    f = Fernet(key)
    with open(filepath, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    output_file = filepath.replace('.encrypted', '.decrypted')
    with open(output_file, 'wb') as file:
        file.write(decrypted_data)

def verify_file_integrity(filepath):
    try:
        MAGIC_NUMBERS = {
            '.jpg': (b'\xFF\xD8\xFF', 2),
            '.jpeg': (b'\xFF\xD8\xFF', 2),
            '.png': (b'\x89PNG\r\n\x1A\n', 8),
            '.gif': (b'GIF8', 4),
            '.pdf': (b'%PDF', 4),
            '.zip': (b'PK\x03\x04', 4),
            '.rar': (b'Rar!\x1A\x07', 6),
            '.7z': (b'7z\xBC\xAF\x27\x1C', 6),
            '.mp3': (b'ID3', 3),
            '.mp4': (b'ftyp', 4),
            '.docx': (b'PK\x03\x04', 4),
            '.xlsx': (b'PK\x03\x04', 4),
        }

        if not os.path.exists(filepath):
            return False, "File not found"

        filesize = os.path.getsize(filepath)
        if filesize == 0:
            return False, "File is empty"

        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        try:
            with open(filepath, 'rb') as f:
                if ext in MAGIC_NUMBERS:
                    magic, length = MAGIC_NUMBERS[ext]
                    header = f.read(length)
                    if not header.startswith(magic):
                        return False, f"Invalid {ext} file header - file is corrupted"

                if ext in ['.txt', '.log', '.ini', '.csv', '.md', '.py', '.json', '.xml', '.html']:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as text_f:
                            content = text_f.read(1024)
                            
                            if '\0' in content:
                                return False, "File contains null bytes - likely corrupted"
                            
                            non_print = sum(1 for c in content if ord(c) < 32 and c not in '\n\r\t')
                            if non_print / len(content) > 0.25:
                                return False, "File contains too many non-printable characters"
                    except UnicodeDecodeError:
                        return False, "File contains invalid text encoding"

                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    try:
                        from PIL import Image
                        with Image.open(filepath) as img:
                            img.verify()
                    except Exception as e:
                        return False, f"Image file structure is corrupted: {str(e)}"

                chunk_size = 65536
                corrupted_chunks = 0
                total_chunks = 0
                
                f.seek(0)
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    total_chunks += 1
                    if chunk.count(b'\0' * 16) > len(chunk) / 32:
                        corrupted_chunks += 1
                
                if corrupted_chunks > 0 and corrupted_chunks / total_chunks > 0.1:
                    return False, "File contains suspicious data patterns"

            return True, "File integrity check passed"

        except IOError as e:
            return False, f"Error reading file: {str(e)}"

    except Exception as e:
        return False, f"Error checking file: {str(e)}"

def disk_health_check():
    results = {
        "space_usage": {},
        "warnings": [],
        "errors": [],
        "performance": {}
    }
    
    print(f"{Fore.YELLOW}Checking disk space usage...")
    for drive in get_drives():
        try:
            total, used, free = shutil.disk_usage(drive)
            percent_used = (used / total) * 100
            results["space_usage"][drive] = {
                "total": total,
                "used": used,
                "free": free,
                "percent_used": percent_used
            }
            
            if percent_used > 90:
                results["warnings"].append(f"Critical: Drive {drive} is {percent_used:.1f}% full")
            elif percent_used > 80:
                results["warnings"].append(f"Warning: Drive {drive} is {percent_used:.1f}% full")
        except Exception as e:
            results["errors"].append(f"Error checking drive {drive}: {str(e)}")
    
    try:
        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'multitool_temp')
        os.makedirs(temp_dir, exist_ok=True)
        test_file = os.path.join(temp_dir, 'disk_speed_test.tmp')
        
        print(f"{Fore.YELLOW}Testing disk performance...")
        size_mb = 50
        block_size = 1024 * 1024
        
        start_time = time.time()
        with open(test_file, 'wb') as f:
            for _ in range(size_mb):
                f.write(os.urandom(block_size))
        write_time = time.time() - start_time
        write_speed = size_mb / write_time
        
        start_time = time.time()
        with open(test_file, 'rb') as f:
            while f.read(block_size):
                pass
        read_time = time.time() - start_time
        read_speed = size_mb / read_time
        
        try:
            os.remove(test_file)
            os.rmdir(temp_dir)
        except:
            pass
        
        results["performance"]["write_speed"] = f"{write_speed:.1f} MB/s"
        results["performance"]["read_speed"] = f"{read_speed:.1f} MB/s"
        
        if write_speed < 10:
            results["warnings"].append(f"Slow write speed: {write_speed:.1f} MB/s")
        if read_speed < 20:
            results["warnings"].append(f"Slow read speed: {read_speed:.1f} MB/s")
            
    except Exception as e:
        results["errors"].append(f"Could not perform disk speed test. Try running as administrator.")
        results["errors"].append(f"Error details: {str(e)}")
    
    if os.name == 'nt':
        try:
            pass
        except Exception as e:
            results["errors"].append("Some checks require administrator privileges")
    
    return results

def check_permissions(path):
    try:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return {"error": "Path not found"}
            
        results = {
            "basic": {},
            "owner": "",
            "acl": [],
            "attributes": []
        }
        
        results["basic"] = {
            "readable": os.access(path, os.R_OK),
            "writable": os.access(path, os.W_OK),
            "executable": os.access(path, os.X_OK)
        }
        
        if os.name == 'nt':
            try:
        if os.name == 'nt':
            try:
                sd = win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION)
                owner_sid = sd.GetSecurityDescriptorOwner()
                name, domain, type = win32security.LookupAccountSid(None, owner_sid)
                results["owner"] = f"{domain}\\{name}"
                
                attrs = win32file.GetFileAttributes(path)
                if attrs & win32con.FILE_ATTRIBUTE_HIDDEN:
                    results["attributes"].append("Hidden")
                if attrs & win32con.FILE_ATTRIBUTE_SYSTEM:
                    results["attributes"].append("System")
                if attrs & win32con.FILE_ATTRIBUTE_READONLY:
                    results["attributes"].append("Read-only")
                if attrs & win32con.FILE_ATTRIBUTE_ARCHIVE:
                    results["attributes"].append("Archive")
            except Exception as e:
                results["error"] = f"Error getting Windows permissions: {str(e)}"
        else:
            try:
                stat_info = os.stat(path)
                mode = stat_info.st_mode
                results["owner"] = stat.filemode(mode)
            except Exception as e:
                results["error"] = f"Error getting Unix permissions: {str(e)}"
                
        return results
    except Exception as e:
        return {"error": str(e)}

def scan_directory(directory):
    issues = {
        "security": [],
        "storage": [],
        "suspicious": [],
        "recommendations": []
    }
    
    print(f"{Fore.YELLOW}Scanning directory: {directory}")
    total_size = 0
    large_files = []
    
    for root, dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            try:
                size = os.path.getsize(path)
                total_size += size
                if size > 100 * 1024 * 1024:
                    large_files.append((path, size))
                
                if size == 0:
                    issues["storage"].append(f"Empty file found: {name}")
                
                if any(name.lower().endswith(ext) for ext in ['.exe', '.dll', '.bat', '.ps1']):
                    issues["suspicious"].append(
                        f"Potentially sensitive file found: {name} "
                        f"(in {os.path.basename(root)})"
                    )
                
                if not os.access(path, os.R_OK):
                    issues["security"].append(f"No read access to: {name}")
                
            except Exception as e:
                continue
    
    if total_size > 1024**3:
        issues["recommendations"].append(
            f"Large directory ({humanize.naturalsize(total_size)}). "
            "Consider archiving old files."
        )
    
    if large_files:
        issues["recommendations"].append("Large files found:")
        for path, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
            issues["recommendations"].append(
                f"  • {os.path.basename(path)}: {humanize.naturalsize(size)}"
            )
    
    return issues

def get_permission_string(access_mask):
    perms = []
    if access_mask & win32con.FILE_READ_DATA: perms.append("Read")
    if access_mask & win32con.FILE_WRITE_DATA: perms.append("Write")
    if access_mask & win32con.FILE_EXECUTE: perms.append("Execute")
    if access_mask & win32con.DELETE: perms.append("Delete")
    if access_mask & win32con.WRITE_DAC: perms.append("Change Permissions")
    if access_mask & win32con.WRITE_OWNER: perms.append("Take Ownership")
    return ", ".join(perms) if perms else "No Access"

def clean_cache():
    cleaned = 0
    errors = []
    paths_to_clean = list(set([
        os.environ.get('TEMP'),
        os.environ.get('TMP'),
        os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp'),
        os.path.join(os.environ.get('WINDIR'), 'Temp')
    ]))
    
    for path in paths_to_clean:
        if not path or not os.path.exists(path):
            continue
            
        print(f"{Fore.YELLOW}Cleaning {path}...")
        for root, dirs, files in os.walk(path, topdown=False):
            if any(skip in root for skip in ['_MEI', 'pywin32_system32']):
                continue
                
            for name in files:
                try:
                    filepath = os.path.join(root, name)
                    if not any(skip in filepath for skip in ['.dll', '.pyd', '.exe']):
                        os.unlink(filepath)
                        cleaned += 1
                except Exception as e:
                    pass
            
            for name in dirs:
                try:
                    dirpath = os.path.join(root, name)
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                        cleaned += 1
                except Exception:
                    pass
    
    return cleaned, []

def monitor_directory(directory):
    class FileHandler(FileSystemEventHandler):
        def __init__(self):
            self.last_modified = {}
            
        def on_created(self, event):
            if not event.is_directory:
                path = event.src_path
                size = os.path.getsize(path) if os.path.exists(path) else 0
                print(f"{Fore.GREEN}+ File created: {path} ({humanize.naturalsize(size)})")

        def on_modified(self, event):
            if not event.is_directory:
                path = event.src_path
                now = time.time()
                
                if path in self.last_modified:
                    if now - self.last_modified[path] < 1:
                        return
                
                self.last_modified[path] = now
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"{Fore.YELLOW}~ File modified: {path} ({humanize.naturalsize(size)})")

        def on_deleted(self, event):
            if not event.is_directory:
                print(f"{Fore.RED}- File deleted: {event.src_path}")

        def on_moved(self, event):
            if not event.is_directory:
                print(f"{Fore.BLUE}→ File moved/renamed:")
                print(f"  From: {event.src_path}")
                print(f"  To: {event.dest_path}")

    print(f"{Fore.CYAN}Starting directory monitor for: {directory}")
    print(f"{Fore.YELLOW}Events that will be detected:")
    print(f"{Fore.GREEN}• File creation")
    print(f"{Fore.YELLOW}• File modification")
    print(f"{Fore.RED}• File deletion")
    print(f"{Fore.BLUE}• File moving/renaming")
    print(f"\n{Fore.WHITE}Press Ctrl+C to stop monitoring...")

    observer = Observer()
    handler = FileHandler()
    observer.schedule(handler, directory, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{Fore.YELLOW}Monitoring stopped.")
    observer.join()

def file_stats():
    stats = {
        "types": {},
        "sizes": {"small": 0, "medium": 0, "large": 0},
        "ages": {"today": 0, "week": 0, "month": 0, "older": 0},
        "total_size": 0,
        "count": 0
    }
    
    now = time.time()
    for f in os.listdir():
        if os.path.isfile(f):
            stats["count"] += 1
            ext = os.path.splitext(f)[1].lower() or "no_extension"
            stats["types"][ext] = stats["types"].get(ext, 0) + 1
            
            size = os.path.getsize(f)
            stats["total_size"] += size
            if size < 1024*1024:
                stats["sizes"]["small"] += 1
            elif size < 100*1024*1024:
                stats["sizes"]["medium"] += 1
            else:
                stats["sizes"]["large"] += 1
            
            age = now - os.path.getmtime(f)
            if age < 86400:
                stats["ages"]["today"] += 1
            elif age < 604800:
                stats["ages"]["week"] += 1
            elif age < 2592000:
                stats["ages"]["month"] += 1
            else:
                stats["ages"]["older"] += 1
    
    return stats

def screen_capture():
    try:
        pictures_dir = os.path.join(os.path.expanduser('~'), 'Pictures', 'Multitool Screenshots')
        os.makedirs(pictures_dir, exist_ok=True)
        
        print(f"{Fore.CYAN}Screen Capture Options:")
        print(f"{Fore.YELLOW}1. Full screen")
        print(f"{Fore.YELLOW}2. Active window")
        print(f"{Fore.YELLOW}3. Cancel")
        
        choice = input(f"\n{Fore.GREEN}Choose option (1-3): {Fore.WHITE}")
        
        if choice == '3':
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(pictures_dir, f'screenshot_{timestamp}.png')
        
        if choice == '1':
            print(f"{Fore.YELLOW}Taking full screen screenshot in 3 seconds...")
            print(f"{Fore.YELLOW}Switch to the window you want to capture...")
            time.sleep(3)
            screenshot = pyautogui.screenshot()
            
        elif choice == '2':
            try:
                print(f"{Fore.YELLOW}Capturing active window in 3 seconds...")
                print(f"{Fore.YELLOW}Make sure your target window is active...")
                time.sleep(3)
                
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                rect = win32gui.GetWindowRect(hwnd)
                region = (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
                screenshot = pyautogui.screenshot(region=region)
            except Exception as e:
                print(f"{Fore.RED}Error capturing active window: {e}")
                print(f"{Fore.YELLOW}Falling back to full screen...")
                screenshot = pyautogui.screenshot()
        else:
            print(f"{Fore.RED}Invalid choice!")
            return
        
        screenshot.save(filename)
        
        size = os.path.getsize(filename)
        
        print(f"\n{Fore.GREEN}Screenshot saved successfully!")
        print(f"{Fore.CYAN}Location: {Fore.WHITE}{filename}")
        print(f"{Fore.CYAN}Size: {Fore.WHITE}{humanize.naturalsize(size)}")
        print(f"{Fore.CYAN}Dimensions: {Fore.WHITE}{screenshot.size[0]}x{screenshot.size[1]} pixels")
        
        if input(f"\n{Fore.YELLOW}Open screenshots folder? (y/n): {Fore.WHITE}").lower() == 'y':
            os.startfile(pictures_dir)
            
    except Exception as e:
        print(f"{Fore.RED}Error taking screenshot: {str(e)}")
        print(f"{Fore.YELLOW}Tips:")
        print(f"{Fore.WHITE}- Make sure you have permission to save files")
        print(f"{Fore.WHITE}- Try running the program as administrator")

def clean_filenames():
    pattern = re.compile(r'[^\w\-_\. ]')
    renamed = 0
    
    for filename in os.listdir():
        if os.path.isfile(filename):
            name, ext = os.path.splitext(filename)
            new_name = pattern.sub('', name)
            new_name = ' '.join(new_name.split())
            new_name = f"{new_name}{ext}"
            
            if new_name != filename:
                try:
                    os.rename(filename, new_name)
                    renamed += 1
                    print(f"{Fore.GREEN}Cleaned: {filename} → {new_name}")
                except Exception as e:
                    print(f"{Fore.RED}Error renaming {filename}: {e}")
    
    return renamed

def corrupt_file(filepath):
    """Deliberately corrupts a file by randomly modifying bytes"""
    try:
        if not os.path.exists(filepath):
            print(f"{Fore.RED}File not found!")
            return False
            
        print(f"{Fore.RED}!!! WARNING !!!")
        print(f"{Fore.RED}This will PERMANENTLY corrupt the file with NO WAY to recover it!")
        print(f"{Fore.RED}File: {Fore.WHITE}{filepath}")
        print(f"{Fore.RED}There will be NO backup created. The file will be permanently damaged.")
        confirm = input(f"{Fore.RED}Type 'DESTROY' to confirm permanent file corruption: {Fore.CYAN}")
        
        if confirm != 'DESTROY':
            print(f"{Fore.GREEN}Operation cancelled.")
            return False
        
        filesize = os.path.getsize(filepath)
        with open(filepath, 'rb+') as f:
            corrupt_bytes = max(int(filesize * 0.5), 1)
            for _ in range(corrupt_bytes):
                pos = random.randint(0, filesize-1)
                f.seek(pos)
                f.write(os.urandom(1))
                
        print(f"{Fore.GREEN}File has been corrupted successfully.")
        print(f"{Fore.RED}The file is now permanently damaged.")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error corrupting file: {str(e)}")
        return False

def monitor_network():
    """Enhanced network traffic monitoring with detailed stats"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}Enhanced Network Monitor (Press Ctrl+C to exit)")
        print(f"{Fore.CYAN}{'=' * 60}")
        
        old_stats = psutil.net_io_counters()
        start_time = time.time()
        
        while True:
            new_stats = psutil.net_io_counters()
            current_time = time.time()
            elapsed = current_time - start_time
            
            bytes_sent = new_stats.bytes_sent - old_stats.bytes_sent
            bytes_recv = new_stats.bytes_recv - old_stats.bytes_recv
            packets_sent = new_stats.packets_sent - old_stats.packets_sent
            packets_recv = new_stats.packets_recv - old_stats.packets_recv
            
            connections = psutil.net_connections(kind='inet')
            active_conns = len([c for c in connections if c.status == 'ESTABLISHED'])
            listening_ports = len([c for c in connections if c.status == 'LISTEN'])
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}Network Monitor (Press Ctrl+C to exit)")
            print(f"{Fore.CYAN}{'=' * 60}")
            
            print(f"\n{Fore.YELLOW}Current Speeds:")
            print(f"{Fore.WHITE}Upload:   {humanize.naturalsize(bytes_sent)}/s")
            print(f"{Fore.WHITE}Download: {humanize.naturalsize(bytes_recv)}/s")
            
            print(f"\n{Fore.YELLOW}Packet Statistics:")
            print(f"{Fore.WHITE}Packets Sent:     {packets_sent:,} packets")
            print(f"{Fore.WHITE}Packets Received: {packets_recv:,} packets")
            
            print(f"\n{Fore.YELLOW}Total Transfer:")
            print(f"{Fore.WHITE}Total Upload:   {humanize.naturalsize(new_stats.bytes_sent)}")
            print(f"{Fore.WHITE}Total Download: {humanize.naturalsize(new_stats.bytes_recv)}")
            
            print(f"\n{Fore.YELLOW}Network Status:")
            print(f"{Fore.WHITE}Active Connections: {active_conns}")
            print(f"{Fore.WHITE}Listening Ports:    {listening_ports}")
            
            interfaces = psutil.net_if_stats()
            print(f"\n{Fore.YELLOW}Network Interfaces:")
            for iface, stats in interfaces.items():
                status = f"{Fore.GREEN}Up" if stats.isup else f"{Fore.RED}Down"
                print(f"{Fore.WHITE}{iface}: {status}{Fore.WHITE} (Speed: {stats.speed}Mb/s)")
            
            print(f"\n{Fore.CYAN}Monitor running for: {timedelta(seconds=int(elapsed))}")
            
            old_stats = new_stats
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Monitoring stopped.")

def system_resources():
    """Enhanced system resource overview"""
    try:
        print(f"{Fore.CYAN}System Resource Overview (Static Snapshot)")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        print(f"{Fore.YELLOW}CPU Information:")
        print(f"{Fore.WHITE}Cores/Threads: {cpu_count} logical processors")
        print(f"{Fore.WHITE}Current Usage: {cpu_percent}%")
        if cpu_freq:
            print(f"{Fore.WHITE}Frequency: {cpu_freq.current/1000:.1f}GHz (Max: {cpu_freq.max/1000:.1f}GHz)")
        
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        print(f"\n{Fore.YELLOW}Memory Usage:")
        print(f"{Fore.WHITE}RAM: {humanize.naturalsize(mem.used)} used of {humanize.naturalsize(mem.total)} ({mem.percent}%)")
        print(f"{Fore.WHITE}Swap: {humanize.naturalsize(swap.used)} used of {humanize.naturalsize(swap.total)} ({swap.percent}%)")
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                print(f"\n{Fore.YELLOW}Temperature Sensors:")
                for name, entries in temps.items():
                    for entry in entries:
                        print(f"{Fore.WHITE}{name}: {entry.current}°C")
        except:
            pass
            
        processes = len(list(psutil.process_iter()))
        threads = sum(p.num_threads() for p in psutil.process_iter())
        print(f"\n{Fore.YELLOW}Process Information:")
        print(f"{Fore.WHITE}Active Processes: {processes}")
        print(f"{Fore.WHITE}Total Threads: {threads}")
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        print(f"\n{Fore.YELLOW}System Uptime:")
        print(f"{Fore.WHITE}Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.WHITE}Up for: {str(uptime).split('.')[0]}")
        
        print(f"\n{Fore.YELLOW}Note: This is a static snapshot. Press any key to exit.")
        keyboard.read_event()
        
    except Exception as e:
        print(f"{Fore.RED}Error getting system resources: {str(e)}")

def monitor_services():
    try:
        import win32serviceutil
        import win32service
        
        print(f"{Fore.CYAN}Windows Services Monitor")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        services = []
        accessSCM = win32con.GENERIC_READ
        sc_handle = win32service.OpenSCManager(None, None, accessSCM)
        
        try:
            type_filter = win32service.SERVICE_WIN32
            state_filter = win32service.SERVICE_STATE_ALL
            
            serv_status = win32service.EnumServicesStatus(sc_handle, type_filter, state_filter)
            
            for service in serv_status:
                services.append({
                    'name': service[0],
                    'display_name': service[1],
                    'status': service[2],
                    'status_code': service[2][1]
                })
                
            running = []
            stopped = []
            
            for service in services:
                if service['status_code'] == win32service.SERVICE_RUNNING:
                    running.append(service)
                elif service['status_code'] == win32service.SERVICE_STOPPED:
                    stopped.append(service)
            
            print(f"{Fore.GREEN}Running Services: {len(running)}")
            for svc in sorted(running, key=lambda x: x['display_name'])[:10]:
                print(f"{Fore.WHITE}• {svc['display_name']}")
            
            print(f"\n{Fore.RED}Stopped Services: {len(stopped)}")
            for svc in sorted(stopped, key=lambda x: x['display_name'])[:5]:
                print(f"{Fore.WHITE}• {svc['display_name']}")
                
            print(f"\n{Fore.YELLOW}Service Statistics:")
            print(f"{Fore.WHITE}Total Services: {len(services)}")
            print(f"{Fore.WHITE}Running: {len(running)}")
            print(f"{Fore.WHITE}Stopped: {len(stopped)}")
            print(f"{Fore.WHITE}Other States: {len(services) - len(running) - len(stopped)}")
            
        finally:
            win32service.CloseServiceHandle(sc_handle)
            
    except Exception as e:
        print(f"{Fore.RED}Error accessing services: {str(e)}")
        print(f"{Fore.YELLOW}Note: This feature requires administrator privileges")
    
    input(f"\n{Fore.CYAN}Press Enter to continue...")

def monitor_processes():
    """Monitor system processes with CPU and memory usage"""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[?25l")
        print(f"{Fore.CYAN}Process Monitor (Press Ctrl+C to exit)")
        print(f"{Fore.CYAN}{'Process':<30} {'CPU %':>8} {'Memory MB':>12} {'Status':>8}")
        print(f"{Fore.CYAN}{'=' * 60}")
        
        while True:
            print("\033[H\033[4B", end='')
            
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    processes.append({
                        'name': proc.info['name'],
                        'cpu': proc.info['cpu_percent'],
                        'memory': proc.info['memory_info'].rss / 1024 / 1024,
                        'status': proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            
            print("\033[J", end='')
            
            for proc in processes[:15]:
                name = proc['name'][:30]
                print(f"{Fore.WHITE}{name:<30} {Fore.YELLOW}{proc['cpu']:>7.1f}% "
                      f"{Fore.GREEN}{proc['memory']:>10.1f}MB {Fore.CYAN}{proc['status']:>8}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\033[?25h")
        print(f"\n{Fore.YELLOW}Monitoring stopped.")

def force_admin():
    """Check and request admin privileges"""
    import ctypes, sys
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            if sys.argv[-1] != 'asadmin':
                script = os.path.abspath(sys.argv[0])
                params = ' '.join([script] + sys.argv[1:] + ['asadmin'])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                sys.exit()
            return False
        return True
    except:
        return False

def manage_startup():
    """Manage Windows startup programs"""
    try:
        import winreg
        print(f"{Fore.CYAN}Startup Programs Manager")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        startup_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
            r"Software\Microsoft\Windows\CurrentVersion\Run", 0, 
            winreg.KEY_ALL_ACCESS)
        
        programs = []
        try:
            i = 0
            while True:
                name, _, _ = winreg.EnumValue(startup_key, i)
                programs.append(name)
                i += 1
        except WindowsError:
            pass
        
        print(f"{Fore.YELLOW}Current Startup Programs:")
        if programs:
            for i, name in enumerate(programs, 1):
                print(f"{Fore.WHITE}{i}. {name}")
        else:
            print(f"{Fore.WHITE}No startup programs found")
            
        print(f"\n{Fore.YELLOW}Options:")
        print(f"{Fore.WHITE}1. Add program")
        print(f"{Fore.WHITE}2. Remove program")
        print(f"{Fore.WHITE}3. Exit")
        
        choice = input(f"\n{Fore.GREEN}Choose option (1-3): {Fore.WHITE}")
        
        if choice == "1":
            name = input(f"{Fore.YELLOW}Enter program name: {Fore.WHITE}")
            path = input(f"{Fore.YELLOW}Enter full program path: {Fore.WHITE}")
            winreg.SetValueEx(startup_key, name, 0, winreg.REG_SZ, path)
            print(f"{Fore.GREEN}Program added to startup!")
            
        elif choice == "2":
            if programs:
                idx = int(input(f"{Fore.YELLOW}Enter program number to remove: {Fore.WHITE}")) - 1
                if 0 <= idx < len(programs):
                    winreg.DeleteValue(startup_key, programs[idx])
                    print(f"{Fore.GREEN}Program removed from startup!")
            else:
                print(f"{Fore.RED}No programs to remove")
                
        winreg.CloseKey(startup_key)
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")
        print(f"{Fore.YELLOW}This feature requires administrator privileges")

def system_restore():
    """Create and manage system restore points"""
    try:
        import win32com.client
        print(f"{Fore.CYAN}System Restore Manager")
        print(f"{Fore.CYAN}{'=' * 60}\n")

        shell = win32com.client.Dispatch("WScript.Shell")
        system = win32com.client.Dispatch("Microsoft.Update.SystemInfo")
        
        print(f"{Fore.YELLOW}System Restore Options:")
        print(f"{Fore.WHITE}1. Create restore point")
        print(f"{Fore.WHITE}2. Open System Restore")
        print(f"{Fore.WHITE}3. Exit")
        
        choice = input(f"\n{Fore.GREEN}Choose option (1-3): {Fore.WHITE}")
        
        if choice == "1":
            desc = input(f"{Fore.YELLOW}Enter description for restore point: {Fore.WHITE}")
            os.system(f'wmic.exe /Namespace:\\\\root\\default Path SystemRestore Call CreateRestorePoint "{desc}", 100, 7')
            print(f"{Fore.GREEN}Restore point created successfully!")
            
        elif choice == "2":
            os.system('rstrui.exe')
            print(f"{Fore.GREEN}System Restore window opened.")
            
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")
        print(f"{Fore.YELLOW}This feature requires administrator privileges")

def process_explorer():
    """Interactive process explorer with detailed info"""
    try:
        while True:
            clear_screen()
            print(f"{Fore.CYAN}Process Explorer")
            print(f"{Fore.CYAN}{'=' * 60}\n")
            
            # Create a dict to store parent process information
            parent_processes = {}
            
            # First collect all processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'create_time', 'status', 'ppid']):
                try:
                    if proc.pid == 0 or proc.name().lower() == "system idle process":
                        continue
                        
                    # Get parent PID
                    ppid = proc.info['ppid']
                    
                    # If it's a parent process (no parent or parent not found)
                    if ppid == 0 or ppid not in parent_processes:
                        cpu = proc.cpu_percent() / psutil.cpu_count()
                        parent_processes[proc.pid] = {
                            'pid': proc.pid,
                            'name': proc.name(),
                            'cpu': cpu,
                            'memory': proc.memory_info().rss / 1024 / 1024,
                            'time': datetime.fromtimestamp(proc.create_time()).strftime('%H:%M:%S'),
                            'status': proc.status(),
                            'children_cpu': 0,
                            'children_memory': 0
                        }
                    else:
                        # Add child process resources to parent
                        cpu = proc.cpu_percent() / psutil.cpu_count()
                        parent_processes[ppid]['children_cpu'] += cpu
                        parent_processes[ppid]['children_memory'] += proc.memory_info().rss / 1024 / 1024
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Create final process list with combined resources
            process_list = []
            for proc in parent_processes.values():
                total_cpu = min(proc['cpu'] + proc['children_cpu'], 100.0)
                total_memory = proc['memory'] + proc['children_memory']
                
                process_list.append({
                    'pid': proc['pid'],
                    'name': proc['name'],
                    'cpu': total_cpu,
                    'memory': total_memory,
                    'time': proc['time'],
                    'status': proc['status']
                })
            
            # Sort by total CPU usage
            process_list.sort(key=lambda x: x['cpu'], reverse=True)
            
            print(f"\n{Fore.YELLOW}Top Processes by CPU Usage (including subprocesses):")
            print(f"{Fore.CYAN}{'PID':>6} {'Name':<20} {'CPU%':>6} {'Memory':>10} {'Started':>10} {'Status':<8}")
            print(f"{Fore.CYAN}{'-' * 65}")
            
            for proc in process_list[:10]:
                print(f"{Fore.WHITE}{proc['pid']:>6} {proc['name'][:20]:<20} {proc['cpu']:>6.1f} "
                      f"{proc['memory']:>9.1f}M {proc['time']:>10} {proc['status']:<8}")
            
            print(f"\n{Fore.YELLOW}Options:")
            print(f"{Fore.WHITE}1. Refresh")
            print(f"{Fore.WHITE}2. Kill process (and children)")
            print(f"{Fore.WHITE}3. Process details")
            print(f"{Fore.WHITE}4. Exit")
            
            choice = input(f"\n{Fore.GREEN}Choose option (1-4): {Fore.WHITE}")
            
            if choice == "1":
                continue
                    
            elif choice == "2":
                pid = input(f"{Fore.YELLOW}Enter PID to terminate: {Fore.WHITE}")
                try:
                    parent = psutil.Process(int(pid))
                    # Get all child processes
                    children = parent.children(recursive=True)
                    # Terminate children first
                    for child in children:
                        try:
                            child.terminate()
                        except:
                            try:
                                child.kill()
                            except:
                                pass
                    # Terminate parent
                    parent.terminate()
                    print(f"{Fore.GREEN}Process and all subprocesses terminated successfully!")
                except:
                    print(f"{Fore.RED}Failed to terminate process")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
                    
            elif choice == "3":
                pid = input(f"{Fore.YELLOW}Enter PID for details: {Fore.WHITE}")
                try:
                    proc = psutil.Process(int(pid))
                    children = proc.children(recursive=True)
                    
                    print(f"\n{Fore.CYAN}Process Details:")
                    print(f"{Fore.WHITE}Name: {proc.name()}")
                    print(f"Path: {proc.exe()}")
                    print(f"Status: {proc.status()}")
                    print(f"Created: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"CPU Usage: {proc.cpu_percent()}%")
                    print(f"Memory: {proc.memory_info().rss / 1024 / 1024:.1f}MB")
                    print(f"Threads: {proc.num_threads()}")
                    if children:
                        print(f"\nChild Processes: {len(children)}")
                        for child in children:
                            try:
                                print(f"  • {child.name()} (PID: {child.pid})")
                            except:
                                continue
                    print("\nConnections:")
                    for conn in proc.connections():
                        print(f"  {conn.laddr} -> {conn.raddr if conn.raddr else '*'} ({conn.status})")
                except:
                    print(f"{Fore.RED}Could not get process details")
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            
            elif choice == "4":
                break

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")
        input(f"\n{Fore.CYAN}Press Enter to continue...")

def advanced_search():
    try:
        current_dir = os.getcwd()
        clear_screen()
        print(f"{Fore.CYAN}Advanced File Search")
        print(f"{Fore.CYAN}{'=' * 60}\n")
        
        print(f"{Fore.YELLOW}Current search directory: {Fore.WHITE}{current_dir}")
        print(f"{Fore.YELLOW}Tip: {Fore.WHITE}You can change directory using option 1 in the main menu\n")
        
        print(f"{Fore.YELLOW}Search Options:")
        print(f"{Fore.WHITE}1. Search by pattern/name")
        print(f"{Fore.WHITE}2. Search by size range")
        print(f"{Fore.WHITE}3. Search by date modified")
        print(f"{Fore.WHITE}4. Search by content (text files)")
        print(f"{Fore.WHITE}5. Exit")
        
        choice = input(f"\n{Fore.GREEN}Choose option (1-5): {Fore.WHITE}")
        
        results = []
        if choice == "1":
            print(f"\n{Fore.CYAN}Pattern Search Tips:")
            print(f"{Fore.WHITE}* = matches any characters")
            print(f"{Fore.WHITE}? = matches single character")
            print(f"{Fore.WHITE}Examples:")
            print(f"  *.txt       = all text files")
            print(f"  test*.doc   = all Word docs starting with 'test'")
            print(f"  backup_???  = files like 'backup_001', 'backup_v2', etc")
            pattern = input(f"\n{Fore.YELLOW}Enter search pattern: {Fore.WHITE}")
            
            print(f"\n{Fore.CYAN}Searching...")
            for root, _, files in os.walk(current_dir):
                for file in fnmatch.filter(files, pattern):
                    results.append(os.path.join(root, file))
                    
        elif choice == "2":
            min_size = float(input(f"{Fore.YELLOW}Enter minimum size in MB (0 for no limit): {Fore.WHITE}"))
            max_size = float(input(f"{Fore.YELLOW}Enter maximum size in MB (0 for no limit): {Fore.WHITE}"))
            
            print(f"\n{Fore.CYAN}Searching...")
            for root, _, files in os.walk(current_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    if (min_size == 0 or size_mb >= min_size) and (max_size == 0 or size_mb <= max_size):
                        results.append(filepath)
                        
        elif choice == "3":
            days = int(input(f"{Fore.YELLOW}Find files modified in the last X days: {Fore.WHITE}"))
            
            print(f"\n{Fore.CYAN}Searching...")
            now = time.time()
            for root, _, files in os.walk(current_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    if (now - os.path.getmtime(filepath)) <= (days * 86400):
                        results.append(filepath)
                        
        elif choice == "4":
            text = input(f"{Fore.YELLOW}Enter text to search for: {Fore.WHITE}")
            print(f"\n{Fore.CYAN}Searching text files (txt, log, ini, csv, md, py, json)...")
            
            for root, _, files in os.walk(current_dir):
                for file in files:
                    if file.endswith(('.txt', '.log', '.ini', '.csv', '.md', '.py', '.json')):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                if text.lower() in f.read().lower():
                                    results.append(filepath)
                        except:
                            continue
        
        if choice in ["1", "2", "3", "4"]:
            if results:
                print(f"\n{Fore.GREEN}Found {len(results)} matches:\n")
                for i, result in enumerate(results, 1):
                    size = humanize.naturalsize(os.path.getsize(result))
                    modified = datetime.fromtimestamp(os.path.getmtime(result)).strftime('%Y-%m-%d %H:%M:%S')
                    rel_path = os.path.relpath(result, current_dir)
                    
                    print(f"{Fore.YELLOW}{i:>3}. {Fore.WHITE}{rel_path}")
                    print(f"     {Fore.CYAN}Size: {Fore.WHITE}{size:<10} {Fore.CYAN}Modified: {Fore.WHITE}{modified}")
            else:
                print(f"\n{Fore.YELLOW}No matching files found.")
                
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

def display_exit_screen():
    clear_screen()
    terminal_width = os.get_terminal_size().columns
    terminal_height = os.get_terminal_size().lines
    
    # Calculate center position
    message = f"Thanks for using {PROGRAM_NAME}!"
    box_width = len(message) + 4
    padding_left = (terminal_width - box_width) // 2
    padding_top = (terminal_height - 5) // 2
    
    # Print empty lines to center vertically
    for _ in range(padding_top):
        print()
    
    # Print centered box with message
    print(" " * padding_left + f"{Fore.CYAN}╔{'═' * (box_width-2)}╗")
    print(" " * padding_left + f"{Fore.CYAN}║{Fore.GREEN + Style.BRIGHT} {message} {Fore.CYAN}║")
    print(" " * padding_left + f"{Fore.CYAN}╚{'═' * (box_width-2)}╝")
    
    time.sleep(1.5)

def main_menu():
    while True:
        clear_screen()
        display_header()
        width = min(os.get_terminal_size().columns, 60)  # Back to 60

        current_dir = os.getcwd()
        display_dir = os.path.basename(current_dir)
        if not display_dir:
            display_dir = current_dir

        dir_space = width - 8 - len(display_dir)
        print(f"{Fore.CYAN}║{Fore.BLUE} Dir: {Fore.WHITE}{display_dir}{' ' * dir_space}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")

        file_options = [
            "Change Directory",
            "Search Files",
            "Find Duplicates",
            "Quick Actions",
            "Preview File",
            "Bulk Rename",
            "Clean Names"
        ]
        
        organize_options = [
            "Organize Files",
            "Categories",
            "Monitor Directory",
            "Space Analysis",
            "File Statistics"
        ]
        
        system_options = [
            "System Info",
            "Clean Cache",
            "Disk Health",
            "Screen Capture"
        ]
        
        security_options = [
            "Encrypt",
            "Decrypt",
            "Permissions",
            "Scan",
            "File Integrity",
            "Corrupt File"
        ]
        
        system_monitoring_options = [
            "Network Usage",
            "System Resources",
            "Running Services"
        ]

        advanced_options = [
            "Startup Manager",
            "System Restore",
            "Advanced Search",
            "Process Explorer"
        ]

        menu_sections = [
            ("File Management", file_options, 1),         
            ("Organization", organize_options, 8),    
            ("System Tools", system_options, 13),   
            ("Security", security_options, 17),    
            ("System Monitoring", system_monitoring_options, 23),
            ("Advanced Tools", advanced_options, 26) 
        ]
        
        for title, options, start_num in menu_sections:
            display_menu_section(title, options, start_num)
            print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")
        
        print(f"{Fore.CYAN}║{Fore.RED} 30 {Fore.WHITE}Exit Program{' ' * (width-18)}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╚═{'═' * (width-4)}═╝")

        try:
            choice = input(f"\n{Fore.GREEN}Enter your choice (1-30): {Fore.WHITE}")
            clear_screen()
            
            if choice == '1':
                change_directory()
                
            elif choice == '2':
                directory = os.getcwd()
                pattern = input(f"{Fore.YELLOW}Enter search pattern: {Fore.WHITE}")
                results = search_files(directory, pattern)
                print(f"\n{Fore.GREEN}Found {len(results)} files:")
                for i, file in enumerate(results, 1):
                    print(f"{i}. {file}")
                
            elif choice == '3':
                directory = os.getcwd()
                duplicates = find_duplicates(directory)
                print(f"\n{Fore.GREEN}Found {len(duplicates)} duplicate sets:")
                for i, (hash_val, files) in enumerate(duplicates.items(), 1):
                    print(f"\n{Fore.YELLOW}Duplicate set {i}:")
                    for file in files:
                        print(f"  {file}")
                
            elif choice == '4':
                quick_actions()
                
            elif choice == '5':
                filepath = input(f"{Fore.YELLOW}Enter file path: {Fore.WHITE}")
                preview_file(filepath)
                
            elif choice == '6':
                renamed = auto_rename()
                print(f"\n{Fore.GREEN}Renamed {renamed} files.")
                
            elif choice == '7':
                cleaned = clean_filenames()
                print(f"\n{Fore.GREEN}Cleaned {cleaned} filenames.")
                
            elif choice == '8':
                directory = os.getcwd()
                organize_files(directory)
                
            elif choice == '9':
                show_categories()
                
            elif choice == '10':
                directory = os.getcwd()
                monitor_directory(directory)
                
            elif choice == '11':
                directory = os.getcwd()
                space_usage = analyze_disk_space(directory)
                print(f"\n{Fore.GREEN}Space usage by file type:")
                for ext, size in sorted(space_usage.items(), key=lambda x: x[1], reverse=True):
                    print(f"{ext or 'No extension'}: {humanize.naturalsize(size)}")
                
            elif choice == '12':
                stats = file_stats()
                print(f"\n{Fore.CYAN}File Statistics for: {os.getcwd()}")
                print(f"\n{Fore.YELLOW}Total Files: {stats['count']}")
                print(f"Total Size: {humanize.naturalsize(stats['total_size'])}")
                
                print(f"\n{Fore.CYAN}File Types:")
                for ext, count in sorted(stats['types'].items()):
                    print(f"{ext}: {count} files")
                
                print(f"\n{Fore.CYAN}Size Distribution:")
                for category, count in stats['sizes'].items():
                    print(f"{category.title()}: {count} files")
                
                print(f"\n{Fore.CYAN}Age Distribution:")
                for category, count in stats['ages'].items():
                    print(f"{category.title()}: {count} files")
                
            elif choice == '13':
                info = get_system_info()
                print(f"\n{Fore.CYAN}System Information:")
                if isinstance(info, dict):
                    for key, value in info.items():
                        if key == "Disk Usage":
                            print(f"\n{Fore.YELLOW}Disk Usage:")
                            for disk, usage in value.items():
                                print(f"  {disk}: {usage}")
                        else:
                            print(f"{key}: {value}")
                else:
                    print(info)
                
            elif choice == '14':
                print(f"{Fore.YELLOW}Cleaning temporary files...")
                cleaned, errors = clean_cache()
                print(f"{Fore.GREEN}Cleaned {cleaned} items.")
                if errors:
                    print(f"\n{Fore.RED}Errors encountered:")
                    for error in errors[:5]:
                        print(f"• {error}")
                    if len(errors) > 5:
                        print(f"...and {len(errors) - 5} more errors")
                
            elif choice == '15':
                print(f"{Fore.YELLOW}Performing comprehensive disk health check...")
                results = disk_health_check()
                
                print(f"\n{Fore.CYAN}━━━ DISK HEALTH REPORT ━━━")
                
                print(f"\n{Fore.CYAN}Disk Space:")
                for drive, info in results["space_usage"].items():
                    total_gb = info["total"] / (1024**3)
                    used_gb = info["used"] / (1024**3)
                    free_gb = info["free"] / (1024**3)
                    print(f"{Fore.WHITE}Drive {drive}")
                    print(f"  Total: {total_gb:.1f} GB")
                    print(f"  Used:  {used_gb:.1f} GB ({info['percent_used']:.1f}%)")
                    print(f"  Free:  {free_gb:.1f} GB")
                
                print(f"\n{Fore.CYAN}Disk Performance:")
                if "disk_status" in results["performance"]:
                    print(f"Disk Status: {Fore.WHITE}{results["performance"]["disk_status"]}")
                if "fragmentation" in results["performance"]:
                    print(f"Fragmentation: {Fore.WHITE}{results["performance"]["fragmentation"]}")
                if "write_speed" in results["performance"]:
                    print(f"Write Speed: {Fore.WHITE}{results["performance"]["write_speed"]}")
                if "read_speed" in results["performance"]:
                    print(f"Read Speed: {Fore.WHITE}{results["performance"]["read_speed"]}")
                
                if results["warnings"]:
                    print(f"\n{Fore.YELLOW}Warnings:")
                    for warning in results["warnings"]:
                        print(f"• {warning}")
                
                if results["errors"]:
                    print(f"\n{Fore.RED}Errors:")
                    for error in results["errors"]:
                        print(f"• {error}")
                
                if not results["warnings"] and not results["errors"]:
                    print(f"\n{Fore.GREEN}No issues detected. Your disk appears to be healthy!")
                elif results["errors"]:
                    print(f"\n{Fore.RED}Disk health issues detected! Consider running a full disk check.")
                else:
                    print(f"\n{Fore.YELLOW}Minor issues found. Consider disk maintenance soon.")
                
            elif choice == '16':
                screen_capture()
                
            elif choice == '17':
                filepath = input(f"{Fore.YELLOW}Enter file to encrypt: {Fore.WHITE}")
                if os.path.exists(filepath):
                    key = encrypt_file(filepath)
                    print(f"{Fore.GREEN}File encrypted successfully.")
                    print(f"{Fore.YELLOW}Keep this key safe: {key.decode()}")
                else:
                    print(f"{Fore.RED}File not found!")
                    
            elif choice == '18':
                filepath = input(f"{Fore.YELLOW}Enter encrypted file: {Fore.WHITE}")
                key_path = input(f"{Fore.YELLOW}Enter key file path (or paste key): {Fore.WHITE}")
                try:
                    if os.path.exists(key_path):
                        with open(key_path, 'rb') as f:
                            key = f.read()
                    else:
                        key = key_path.encode()
                    decrypt_file(filepath, key)
                    print(f"{Fore.GREEN}File decrypted successfully.")
                except Exception as e:
                    print(f"{Fore.RED}Decryption failed: {str(e)}")

            elif choice == '19':
                path = input(f"{Fore.YELLOW}Enter file/folder name or path: {Fore.WHITE}")
                abs_path = os.path.abspath(path)
                perms = check_permissions(abs_path)
                
                if "error" in perms:
                    print(f"{Fore.RED}× Error: {perms['error']}")
                else:
                    print(f"\n{Fore.CYAN}Permission Details for: {path}")
                    print(f"\n{Fore.CYAN}Basic Access:")
                    for perm, value in perms["basic"].items():
                        icon = "✓" if value else "×"
                        color = Fore.GREEN if value else Fore.RED
                        print(f"{color}{icon} {perm.capitalize()}")
                    
                    if perms["owner"]:
                        print(f"\n{Fore.CYAN}Owner: {Fore.WHITE}{perms['owner']}")
                    
                    if perms["attributes"]:
                        print(f"\n{Fore.CYAN}File Attributes:")
                        for attr in perms["attributes"]:
                            print(f"{Fore.WHITE}• {attr}")

            elif choice == '20':
                directory = os.getcwd()
                print(f"{Fore.YELLOW}Scanning directory for potential issues...")
                issues = scan_directory(directory)
                if issues["security"]:
                    print(f"\n{Fore.RED}Security Issues:")
                    for issue in issues["security"]:
                        print(f"• {issue}")
                if issues["storage"]:
                    print(f"\n{Fore.YELLOW}Storage Issues:")
                    for issue in issues["storage"]:
                        print(f"• {issue}")
                if issues["suspicious"]:
                    print(f"\n{Fore.RED}Suspicious Files:")
                    for issue in issues["suspicious"]:
                        print(f"• {issue}")
                if issues["recommendations"]:
                    print(f"\n{Fore.CYAN}Recommendations:")
                    for issue in issues["recommendations"]:
                        print(f"• {issue}")
                if not any(issues.values()):
                    print(f"\n{Fore.GREEN}No issues found in the directory.")
                    
            elif choice == '21':
                filepath = input(f"{Fore.YELLOW}Enter file to check for corruption: {Fore.WHITE}")
                if os.path.exists(filepath):
                    print(f"{Fore.YELLOW}Checking file integrity...")
                    is_valid, message = verify_file_integrity(filepath)
                    if is_valid:
                        print(f"{Fore.GREEN}✓ File check passed!")
                        print(f"{Fore.WHITE}The file can be read completely without errors")
                    else:
                        print(f"{Fore.RED}× File appears to be corrupted!")
                        print(f"{Fore.WHITE}Error: {message}")
                else:
                    print(f"{Fore.RED}× File not found!")
                    
            elif choice == '22':
                filepath = input(f"{Fore.YELLOW}Enter file to corrupt: {Fore.WHITE}")
                corrupt_file(filepath)
                
            elif choice == '23':
                monitor_network()
            elif choice == '24':
                system_resources()
            elif choice == '25':
                monitor_services()
            elif choice == '26':           
                manage_startup()
            elif choice == '27':           
                system_restore()
            elif choice == '28':      
                advanced_search()
            elif choice == '29':         
                process_explorer()
            elif choice == '30':  
                display_exit_screen()
                break

            if choice != '1':
                input(f"\n{Fore.CYAN}Press Enter to continue...{Fore.WHITE}")
                
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {str(e)}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Fore.WHITE}")

if __name__ == "__main__":
    if not any(arg.lower() == 'asadmin' for arg in sys.argv):
        force_admin()
    main_menu()
