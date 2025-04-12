import requests
import argparse
import csv
import os

# GitHub API URL
GITHUB_API_URL = "https://api.github.com/repos/"

# Function to get repository information using GitHub API
def get_repo_info(owner, repo):
    try:
        repo_url = f"{GITHUB_API_URL}{owner}/{repo}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(repo_url, headers=headers)
        repo_data = response.json()

        if response.status_code != 200:
            print(f"Error fetching repository {owner}/{repo}: {repo_data.get('message')}")
            return None

        # Get repository statistics
        last_commit_url = f"{repo_url}/commits"
        last_commit_response = requests.get(last_commit_url, headers=headers)
        commits_data = last_commit_response.json()
        last_commit_date = commits_data[0]['commit']['committer']['date'] if commits_data else "No commits found"

        # Fetch README.md file content
        readme_url = f"{repo_url}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            readme_content_url = readme_data['download_url']
            readme_content = requests.get(readme_content_url).text
            first_sentence = readme_content.split('.')[0] + '.' if readme_content else "README not available"
        else:
            first_sentence = "README not available"

        # Return repository details
        return {
            "url": f"https://github.com/{owner}/{repo}",
            "owner": owner,
            "repo": repo,
            "first_sentence_of_readme": first_sentence,
            "last_commit_date": last_commit_date,
            "stars": repo_data.get('stargazers_count', 'N/A'),
            "watchers": repo_data.get('watchers_count', 'N/A'),
            "forks": repo_data.get('forks_count', 'N/A')
        }
    
    except Exception as e:
        print(f"Error fetching information for {owner}/{repo}: {e}")
        return None

# Function to process a single GitHub URL
def process_single_url(url):
    try:
        url = url.strip()
        parts = url.split("/")
        if len(parts) < 2:
            raise ValueError("URL does not have enough parts.")
        owner, repo = parts[-2], parts[-1]
        return get_repo_info(owner, repo)
    except Exception as e:
        print(f"Invalid GitHub URL '{url}': {e}")
        return None

# Function to process multiple GitHub URLs from a file
def process_multiple_urls(file_path):
    results = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            urls = file.readlines()
            for url in urls:
                cleaned_url = url.strip()
                if not cleaned_url:
                    continue  # Skip empty lines
                result = process_single_url(cleaned_url)
                if result:
                    results.append(result)
    else:
        print(f"File '{file_path}' not found.")
    return results

# Function to write output to CSV file
def write_to_csv(output_file, data):
    if not data:
        print("No data to write.")
        return

    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['url', 'owner', 'repo', 'first_sentence_of_readme', 'last_commit_date', 'stars', 'watchers', 'forks']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Results written to {output_file}")

# Main function to handle arguments and run the tool
def main():
    parser = argparse.ArgumentParser(
        description="GitHub Metadata Lookup Tool",
        usage="%(prog)s [-u URL | -f FILE] [-o OUTPUT] [-h]"
    )

    parser.add_argument("-u", "--url", type=str, help="GitHub repository URL (for a single repository)")
    parser.add_argument("-f", "--file", type=str, help="File containing multiple GitHub repository URLs (one per line)")
    parser.add_argument("-o", "--output", type=str, help="Output CSV file to store results")

    args = parser.parse_args()

    results = []

    if args.url:
        # Process a single URL
        result = process_single_url(args.url)
        if result:
            results.append(result)
    elif args.file:
        # Process multiple URLs from a file
        results = process_multiple_urls(args.file)
    else:
        print("Please specify either a GitHub URL using -u or a file containing URLs using -f.")
        return

    if args.output:
        write_to_csv(args.output, results)
    else:
        # Print results to console if no output file is specified
        for result in results:
            print(f"\nRepository: {result['owner']}/{result['repo']}")
            print(f"URL: {result['url']}")
            print(f"First sentence of README: {result['first_sentence_of_readme']}")
            print(f"Last commit date: {result['last_commit_date']}")
            print(f"Stars: {result['stars']}")
            print(f"Watchers: {result['watchers']}")
            print(f"Forks: {result['forks']}")

if __name__ == "__main__":
    main()
