#!/data/data/com.termux/files/usr/bin/python

import os
import re
import requests
import gdown
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def show_banner():
    print(r"""
   ____                    _       _      
  |  _ \ _ __ _   _ _ __ | | ___ | |__   
  | | | | '__| | | | '_ \| |/ _ \| '_ \  
  | |_| | |  | |_| | |_) | | (_) | |_) | 
  |____/|_|   \__, | .__/|_|\___/|_.__/  
              |___/|_|                   
""")

def get_folder_id(url):
    """Extract folder ID from Google Drive URL"""
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
    """Get list of files from public Google Drive folder"""
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.98 Mobile Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Modern parsing method
        files = []
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all script tags containing file data
        scripts = soup.find_all('script')
        for script in scripts:
            if 'window._DRIVE_ivd' in script.text:
                data = script.text.split('window._DRIVE_ivd = ')[1].split(';')[0]
                matches = re.findall(r'\["([^"]+)",null,null,\d+,\d+,\[\["([^"]+)"\]', data)
                for name, file_id in matches:
                    if name and file_id:
                        file_url = f"https://drive.google.com/uc?id={file_id}"
                        files.append((name, file_url))
        
        return files
    except Exception as e:
        print(f"\033[1;31m[!] Error accessing folder: {str(e)}\033[0m")
        return []

def download_file(file_url, destination):
    """Download file using gdown"""
    try:
        output = gdown.download(file_url, destination, fuzzy=True, quiet=False)
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
        print("\033[1;31m[!] No files found. Possible reasons:\033[0m")
        print("    1. Folder is not public (check sharing settings)")
        print("    2. Google changed their page structure (report to developer)")
        print("    3. No internet connection")

if __name__ == "__main__":
    main()
