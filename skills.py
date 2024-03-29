import requests
import os
import re
import git
from pylint import lint
import subprocess

def scrape_webpage(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to scrape webpage. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Error occurred while scraping webpage: {str(e)}"

def save_file(file_path, content):
    try:
        with open(file_path, "w") as file:
            file.write(content)
        return f"File saved successfully: {file_path}"
    except IOError as e:
        return f"Error occurred while saving file: {str(e)}"

def edit_file(file_path, old_content, new_content):
    try:
        with open(file_path, "r") as file:
            content = file.read()
        content = content.replace(old_content, new_content)
        with open(file_path, "w") as file:
            file.write(content)
        return f"File edited successfully: {file_path}"
    except IOError as e:
        return f"Error occurred while editing file: {str(e)}"

def analyze_code(code):
    try:
        # Perform static code analysis using pylint
        results = lint.Run([code], do_exit=False)
        
        # Extract relevant metrics from the analysis results
        errors = results.linter.stats['error']
        warnings = results.linter.stats['warning']
        metrics = {
            'errors': errors,
            'warnings': warnings,
            'lines_of_code': results.linter.stats['statement'],
            'score': results.linter.stats['global_note']
        }
        
        return metrics
    except Exception as e:
        return f"Error occurred during code analysis: {str(e)}"

def search_files(directory, keyword):
    try:
        matching_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    if keyword in content:
                        matching_files.append(file_path)

        if matching_files:
            result = "Matching files:\n" + "\n".join(matching_files)
        else:
            result = "No matching files found."
        
        return result
    except Exception as e:
        return f"Error occurred during file search: {str(e)}"

def git_clone(repository_url, target_directory):
    try:
        git.Repo.clone_from(repository_url, target_directory)
        return f"Repository cloned successfully to {target_directory}"
    except git.GitCommandError as e:
        return f"Error occurred during git clone: {str(e)}"

def git_pull(repository_path):
    try:
        repo = git.Repo(repository_path)
        origin = repo.remotes.origin
        origin.pull()
        return "Repository pulled successfully"
    except git.GitCommandError as e:
        return f"Error occurred during git pull: {str(e)}"

def git_push(repository_path, commit_message):
    try:
        repo = git.Repo(repository_path)
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        origin = repo.remotes.origin
        origin.push()
        return "Changes pushed successfully"
    except git.GitCommandError as e:
        return f"Error occurred during git push: {str(e)}"

def check_code_quality(file_path):
    try:
        results = lint.Run([file_path], do_exit=False)
        return results.linter.stats['global_note']
    except Exception as e:
        return f"Error occurred during code quality check: {str(e)}"

def install_dependencies(requirements_file):
    try:
        subprocess.check_call(["pip", "install", "-r", requirements_file])
        return "Dependencies installed successfully"
    except subprocess.CalledProcessError as e:
        return f"Error occurred during dependency installation: {str(e)}"

def generate_documentation(code_directory, output_file):
    try:
        command = f"pydoc -w {code_directory} > {output_file}"
        subprocess.check_call(command, shell=True)
        return f"Documentation generated successfully: {output_file}"
    except subprocess.CalledProcessError as e:
        return f"Error occurred during documentation generation: {str(e)}"

def run_unit_tests(test_directory):
    try:
        command = f"python -m unittest discover {test_directory}"
        subprocess.check_call(command, shell=True)
        return "Unit tests executed successfully"
    except subprocess.CalledProcessError as e:
        return f"Error occurred during unit test execution: {str(e)}"