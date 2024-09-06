import requests
import os
import base64
from dotenv import load_dotenv

# DESCRIPTION:
# This program is made to scrape files and code from GitHub using the GitHub api. To authenticate accessing these
# repos, the users GitHub token is needed. The program then reads the contents of the "githubRepos.txt" file,
# which contains a link to a file in a GitHub repo on each line (ex. https://github.com/cshafizadeh/cshafizadeh/blob/main/README.md).
# The scraper grabs the code from the file, and the contents of the page are sent to a .md file.

# Load environment variables from .env
load_dotenv()

# GitHub personal access token from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

# Headers for authentication
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Function to extract details from the GitHub URL
def extract_repo_details(github_url: str):
    # Example URL format:
    # https://github.com/{owner}/{repo}/blob/{branch}/{file_path}
    parts = github_url.replace("https://github.com/", "").split("/")
    owner = parts[0]
    repo = parts[1]
    branch = parts[3]  # assuming 'blob' comes before the branch name
    file_path = "/".join(parts[4:])
    
    return owner, repo, branch, file_path


# Function to retrieve the file content from a repository
def get_file_content(owner, repo, file_path, branch="main"):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        file_content = file_info["content"]
        file_content_decoded = base64.b64decode(file_content).decode("utf-8")
        return file_content_decoded
    else:
        print(f"Error retrieving file: {response.status_code} - {response.text}")
        return None


# Function to save file content to .md file
def save_to_md_file(file_content, file_name: str):
    # Ensure the file_name has no illegal characters
    file_name = file_name.replace("/", "_")
    # Create the 'data' folder if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(f"data/{file_name}.md", "w", encoding="utf-8") as f:
        f.write(file_content)
    print(f"File saved: {file_name}.md")


# Function to process each URL
def process_github_url(github_url):
    owner, repo, branch, file_path = extract_repo_details(github_url)    
    # Get the file content from GitHub
    file_content = get_file_content(owner, repo, file_path, branch)
    if file_content:
        # Extract the filename from the file path
        filename = file_path.split("/")[-1].replace(".js", "")  # Change this based on the file extension
        # Save the file content to a .md file
        save_to_md_file(file_content, filename)


# Main function to read URLs from a .txt file and download files
def process_urls_from_file(file_path):
    # Open the .txt file containing the list of URLs
    with open(file_path, "r") as file:
        urls = file.readlines()
    # Iterate through each URL and process it
    for url in urls:
        url = url.strip()  # Remove any leading/trailing whitespace or newlines
        if url:  # Check if the URL is not empty
            process_github_url(url)


if __name__ == "__main__":
    # Path to the .txt file containing the URLs (one per line)
    url_file_path = "gitHubRepos.txt"
    # Process all URLs in the file and download them
    process_urls_from_file(url_file_path)
