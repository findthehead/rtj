#!/usr/bin/env python3


import os
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from jsbeautifier import beautify

# ASCII art greeting
ASCII_ART = r"""

$$$$$$$\                      $$\                      $$$$$$$$\ $$\   $$\ $$$$$$$$\               
$$  __$$\                     \__|                     \__$$  __|$$ |  $$ |$$  _____|              
$$ |  $$ | $$$$$$\ $$\    $$\ $$\  $$$$$$\  $$\  $$\  $$\ $$ |   $$ |  $$ |$$ |      $$\  $$$$$$$\ 
$$$$$$$  |$$  __$$\\$$\  $$  |$$ |$$  __$$\ $$ | $$ | $$ |$$ |   $$$$$$$$ |$$$$$\    \__|$$  _____|
$$  __$$< $$$$$$$$ |\$$\$$  / $$ |$$$$$$$$ |$$ | $$ | $$ |$$ |   $$  __$$ |$$  __|   $$\ \$$$$$$\  
$$ |  $$ |$$   ____| \$$$  /  $$ |$$   ____|$$ | $$ | $$ |$$ |   $$ |  $$ |$$ |      $$ | \____$$\ 
$$ |  $$ |\$$$$$$$\   \$  /   $$ |\$$$$$$$\ \$$$$$\$$$$  |$$ |   $$ |  $$ |$$$$$$$$\ $$ |$$$$$$$  |
\__|  \__| \_______|   \_/    \__| \_______| \_____\____/ \__|   \__|  \__|\________|$$ |\_______/ 
                                                                               $$\   $$ |          
                                                                               \$$$$$$  |          
                                                                                \______/           
"""

def check_url_format(url):
    if not (url.startswith('https://') or url.startswith('http://')):
        raise argparse.ArgumentTypeError("Invalid URL format. Use 'http://example.com/page' or 'https://example.com/page' format.")

    return url

def check_page_existence(url):
    response = requests.head(url)

    if response.status_code != 200:
        raise ValueError(f"No page found by the URL: {url}")

    return url

def download_js_files(url, output_dir):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    script_tags = soup.find_all('script', src=True)

    for script_tag in script_tags:
        js_url = script_tag['src']

        # Check if the URL is relative and combine it with the base URL if needed
        if not js_url.startswith('http://') and not js_url.startswith('https://'):
            js_url = urljoin(url, js_url)

        js_filename = os.path.basename(js_url)
        js_content = requests.get(js_url).text

        # Skip files that are not valid JS files (e.g., compressed code)
        if not js_content.strip().startswith("function"):
            print(f"Skipped (not a valid JS file): {js_url}")
            continue

        with open(os.path.join(output_dir, js_filename), 'w', encoding='utf-8') as f:
            f.write(js_content)

        print(f"Downloaded: {js_url}")

def beautify_js_files(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.js'):
            input_file_path = os.path.join(input_dir, filename)

            with open(input_file_path, 'r', encoding='utf-8') as f:
                js_content = f.read()

            beautified_code = beautify(js_content)

            with open(input_file_path, 'w', encoding='utf-8') as f:
                f.write(beautified_code)

            print(f"Beautified: {input_file_path}")

if __name__ == "__main__":
    # Print the ASCII art greeting
    print(ASCII_ART)

    parser = argparse.ArgumentParser(description='Scrape and download JS files from a website.')
    parser.add_argument('url', type=check_url_format, help='The URL of the website with the specified page (e.g., http://example.com/page)')
    
    args = parser.parse_args()

    output_directory = os.path.join(os.getcwd(), 'js_files')
    os.makedirs(output_directory, exist_ok=True)

    # Step 1: Download JS files from the specific page on the website
    download_js_files(args.url, output_directory)

    # Step 2: Beautify the downloaded JS files (overwrite the original files)
    beautify_js_files(output_directory)

    print(f"Your JS files are downloaded to: {output_directory}")
