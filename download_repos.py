import os
import json
import requests
import zipfile
import io

# (connect, read) timeout in seconds for the GitHub download. Keeps the build
# from hanging indefinitely when a remote is unresponsive (see issue #28).
REQUEST_TIMEOUT = (10, 60)

def download_and_extract_zip(url, base_dir="."):
    repo_dir = os.path.join(base_dir, "repos")
    os.makedirs(repo_dir, exist_ok=True)

    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(repo_dir)
        except zipfile.BadZipFile as e:
            print(f"Failed to extract zip from {url}: {e}")
            return

        # Rename directories if they end with -master or -main
        for root, dirs, files in os.walk(repo_dir):
            for dir_name in dirs:
                if dir_name.endswith("-master") or dir_name.endswith("-main"):
                    new_name = dir_name.rsplit("-", 1)[0]
                    os.rename(os.path.join(root, dir_name), os.path.join(root, new_name))
        
        print(f"Downloaded and extracted zip file to: {repo_dir}")
    else:
        print(f"Failed to download zip from {url}. Status code: {response.status_code}")

def main():
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found.")
        return
    
    with open(config_file, "r") as file:
        config = json.load(file)
    
    for scheme in config:
        zip_url = scheme.get("url")
        if zip_url:
            try:
                download_and_extract_zip(zip_url)
            except requests.Timeout as e:
                print(f"Timed out downloading {zip_url}: {e}")
            except requests.RequestException as e:
                print(f"Error processing {zip_url}: {e}")
        else:
            print(f"Invalid configuration entry: {scheme}")

if __name__ == "__main__":
    main()
