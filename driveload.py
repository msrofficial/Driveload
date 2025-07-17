#!/data/data/com.termux/files/usr/bin/python

import os
import re
import requests
from bs4 import BeautifulSoup
import gdown
import argparse
from urllib.parse import urlparse, parse_qs

def show_banner():
    print("\033[1;34m")
    print("   ____                    _       _      ")
    print("  |  _ \ _ __ _   _ _ __ | | ___ | |__   ")
    print("  | | | | '__| | | | '_ \| |/ _ \| '_ \  ")
    print("  | |_| | |  | |_| | |_) | | (_) | |_) | ")
    print("  |____/|_|   \__, | .__/|_|\___/|_.__/  ")
    print("              |___/|_|                   ")
    print("\033[0m")

def get_folder_id(url):
    patterns = [
        r'https://drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)',
        r'https://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return qs.get('id', [None])[0]

def get_files_from_folder(folder_id):
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return [
            (a.text, "https://drive.google.com" + a['href'])
            for a in soup.find_all('a', {'class': 'Q5txwe'})
        ]
    except Exception as e:
        print(f"\033[1;31m[!] Error accessing folder: {str(e)}\033[0m")
        return []

def download_file(file_url, destination):
    try:
        output = gdown.download(file_url, destination, fuzzy=True)
        return bool(output)
    except Exception as e:
        print(f"\033[1;31m[!] Download error: {str(e)}\033[0m")
        return False

def main():
    show_banner()
    parser = argparse.ArgumentParser(description='Driveload - Google Drive Downloader')
    parser.add_argument('url', help='Google Drive folder URL')
    parser.add_argument('-d', '--destination', 
                      help='Custom download directory',
                      default=os.path.join(os.path.expanduser('~'), 'storage', 'downloads', 'Driveload'))
    args = parser.parse_args()
    
    if not (folder_id := get_folder_id(args.url)):
        print("\033[1;31m[!] Invalid Google Drive folder URL\033[0m")
        return
    
    print(f"\n\033[1;34m[•] Fetching files from folder ID: {folder_id}\033[0m")
    
    if not os.path.exists(args.destination):
        os.makedirs(args.destination)
    
    if files := get_files_from_folder(folder_id):
        print(f"\033[1;32m[+] Found {len(files)} files in the folder\033[0m\n")
        for file_name, file_url in files:
            clean_name = re.sub(r'[\\/*?:"<>|]', "_", file_name)
            destination = os.path.join(args.destination, clean_name)
            print(f"\033[1;33m[•] Downloading: {clean_name}\033[0m")
            if download_file(file_url, destination):
                print(f"\033[1;32m[✓] Success: {clean_name}\033[0m")
            else:
                print(f"\033[1;31m[✗] Failed: {clean_name}\033[0m")
        print("\n\033[1;32m[+] Download completed!\033[0m")
    else:
        print("\033[1;31m[!] No files found or folder is not public\033[0m")

if __name__ == "__main__":
    main()
