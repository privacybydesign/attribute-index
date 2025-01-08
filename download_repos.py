import os
import json
import subprocess

def clone_or_update_repo(source, github_url, base_dir="."):
    """
    Clones or updates a GitHub repository based on the source and GitHub URL.
    
    Args:
        source (str): Name of the source directory to store the repo.
        github_url (str): URL of the GitHub repository.
        base_dir (str): Base directory where the repos are stored.
    """
    os.makedirs(base_dir, exist_ok=True)
    
    repo_dir = os.path.join(base_dir, source)
    
    if github_url.endswith("/blob/master"):
        github_url = github_url.replace("/blob/master", ".git")
    elif github_url.endswith("/blob/main"):
        github_url = github_url.replace("/blob/main", ".git")
    elif github_url.endswith("/master"):
        github_url = github_url.replace("/master", ".git")
    elif github_url.endswith("/main"):
        github_url = github_url.replace("/main", ".git")
    
    if os.path.exists(repo_dir):
        print(f"Updating repository: {source}")
        subprocess.run(["git", "-C", repo_dir, "pull"], check=True)
    else:
        print(f"Cloning repository: {source}")
        subprocess.run(["git", "clone", github_url, repo_dir], check=True)

def main():
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found.")
        return
    
    with open(config_file, "r") as file:
        config = json.load(file)
    
    for repo in config:
        source = repo.get("source")
        github_url = repo.get("github")
        if source and github_url:
            try:
                clone_or_update_repo(source, github_url)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {source}: {e}")
        else:
            print(f"Invalid configuration entry: {repo}")

if __name__ == "__main__":
    main()
