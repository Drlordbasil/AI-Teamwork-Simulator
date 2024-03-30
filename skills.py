import requests
import os
import re
import git
from pylint import lint
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_webpage(url):
    """
    Scrape the content of a webpage given a URL.
    
    Args:
        url (str): The URL of the webpage to scrape.
        
    Returns:
        str: The scraped webpage content if successful, otherwise an error message.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info(f"Webpage scraped successfully: {url}")
            return response.text
        else:
            logger.error(f"Failed to scrape webpage. Status code: {response.status_code}")
            return f"Failed to scrape webpage. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error occurred while scraping webpage: {url}")
        return f"Error occurred while scraping webpage: {str(e)}"

def save_file(file_path, content):
    """
    Save content to a file in the workspace.
    
    Args:
        file_path (str): The path where the file should be saved.
        content (str): The content to write to the file.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        with open(file_path, "w") as file:
            file.write(content)
        logger.info(f"File saved successfully: {file_path}")
        return f"File saved successfully: {file_path}"
    except IOError as e:
        logger.exception(f"Error occurred while saving file: {file_path}")
        return f"Error occurred while saving file: {str(e)}"

def edit_file(file_path, old_content, new_content):
    """
    Edit an existing file in the workspace by replacing old content with new content.
    
    Args:
        file_path (str): The path of the file to edit.
        old_content (str): The content to replace in the file.
        new_content (str): The new content to write in place of the old content.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
        content = content.replace(old_content, new_content)
        with open(file_path, "w") as file:
            file.write(content)
        logger.info(f"File edited successfully: {file_path}")
        return f"File edited successfully: {file_path}"
    except IOError as e:
        logger.exception(f"Error occurred while editing file: {file_path}")
        return f"Error occurred while editing file: {str(e)}"

def search_files(directory, keyword):
    """
    Search for files containing a specific keyword in the given directory.
    
    Args:
        directory (str): The directory to search in.
        keyword (str): The keyword to search for in file contents.
        
    Returns:
        str: The list of matching files if any, otherwise a message indicating no matches found.
    """
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
            logger.info(f"Search completed. {len(matching_files)} files found containing keyword: {keyword}")
        else:
            result = "No matching files found containing the keyword: {keyword}"
            logger.info(f"Search completed. No files found containing keyword: {keyword}")
        
        return result
    except Exception as e:
        logger.exception(f"Error occurred during file search in directory: {directory}")
        return f"Error occurred during file search: {str(e)}"

def git_clone(repository_url, target_directory):
    """
    Clone a Git repository to the specified target directory.
    
    Args:
        repository_url (str): The URL of the Git repository to clone.
        target_directory (str): The directory where the repository should be cloned to.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        git.Repo.clone_from(repository_url, target_directory)
        logger.info(f"Repository cloned successfully to {target_directory}")
        return f"Repository cloned successfully to {target_directory}"
    except git.GitCommandError as e:
        logger.exception(f"Error occurred during git clone of repository: {repository_url}")
        return f"Error occurred during git clone: {str(e)}"

def git_pull(repository_path):
    """
    Pull the latest changes from a Git repository.
    
    Args:
        repository_path (str): The path to the local Git repository.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        repo = git.Repo(repository_path)
        origin = repo.remotes.origin
        origin.pull()
        logger.info(f"Repository pulled successfully: {repository_path}")
        return "Repository pulled successfully"
    except git.GitCommandError as e:
        logger.exception(f"Error occurred during git pull in repository: {repository_path}")
        return f"Error occurred during git pull: {str(e)}"

def git_push(repository_path, commit_message):
    """
    Push local changes to a remote Git repository.
    
    Args:
        repository_path (str): The path to the local Git repository.
        commit_message (str): The commit message to use for the changes.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        repo = git.Repo(repository_path)
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        origin = repo.remotes.origin
        origin.push()
        logger.info(f"Changes pushed successfully to remote repository: {repository_path}")
        return "Changes pushed successfully"
    except git.GitCommandError as e:
        logger.exception(f"Error occurred during git push in repository: {repository_path}")
        return f"Error occurred during git push: {str(e)}"

def analyze_code(code_file):
    """
    Perform static code analysis on a given code file using Pylint.
    
    Args:
        code_file (str): The path to the code file to analyze.
        
    Returns:
        str: A summary of the code analysis results, including the Pylint score and any major issues found.
    """
    try:
        results = lint.Run([code_file], do_exit=False)
        score = results.linter.stats['global_note']
        
        issues = []
        for message in results.linter.reporter.messages:
            if message.category in ['error', 'warning']:
                issues.append(f"{message.category.upper()}: {message.msg} (Line: {message.line})")
        
        summary = f"Code Analysis Results for {code_file}:\n"
        summary += f"Pylint Score: {score:.2f}/10\n"
        if issues:
            summary += "Major Issues Found:\n" + "\n".join(issues)
        else:
            summary += "No major issues found."
        
        logger.info(f"Code analysis completed for {code_file}. Pylint Score: {score:.2f}/10")
        return summary
    except Exception as e:
        logger.exception(f"Error occurred during code analysis for file: {code_file}")
        return f"Error occurred during code analysis: {str(e)}"

def check_code_quality(file_path):
    """
    Check the quality of a Python file using Pylint.
    
    Args:
        file_path (str): The path to the Python file to check.
        
    Returns:
        str: The Pylint score and a summary of the issues found, if any.
    """
    try:
        results = lint.Run([file_path], do_exit=False)
        score = results.linter.stats['global_note']
        
        issues = []
        for message in results.linter.reporter.messages:
            if message.category in ['error', 'warning']:
                issues.append(f"{message.category.upper()}: {message.msg} (Line: {message.line})")
        
        summary = f"Code Quality Results for {file_path}:\n"
        summary += f"Pylint Score: {score:.2f}/10\n"
        if issues:
            summary += "Issues Found:\n" + "\n".join(issues)
        else:
            summary += "No major issues found."
        
        logger.info(f"Code quality check completed for {file_path}. Pylint Score: {score:.2f}/10")
        return summary
    except Exception as e:
        logger.exception(f"Error occurred during code quality check for file: {file_path}")
        return f"Error occurred during code quality check: {str(e)}"

def install_dependencies(requirements_file):
    """
    Install dependencies from a requirements file using pip.
    
    Args:
        requirements_file (str): The path to the requirements file listing the dependencies.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        subprocess.check_call(["pip", "install", "-r", requirements_file])
        logger.info(f"Dependencies installed successfully from {requirements_file}")
        return "Dependencies installed successfully"
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error occurred during dependency installation from file: {requirements_file}")
        return f"Error occurred during dependency installation: {str(e)}"

def generate_documentation(code_directory, output_file):
    """
    Generate documentation for Python code in the specified directory using pydoc.
    
    Args:
        code_directory (str): The directory containing the Python code to generate documentation for.
        output_file (str): The file path where the generated documentation should be written.
        
    Returns:
        str: A message indicating success or an error message.
    """
    try:
        command = f"pydoc -w {code_directory} > {output_file}"
        subprocess.check_call(command, shell=True)
        logger.info(f"Documentation generated successfully for {code_directory}. Output file: {output_file}")
        return f"Documentation generated successfully: {output_file}"
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error occurred during documentation generation for directory: {code_directory}")
        return f"Error occurred during documentation generation: {str(e)}"

def run_unit_tests(test_directory):
    """
    Run unit tests for Python code in the specified directory using unittest.
    
    Args:
        test_directory (str): The directory containing the unit test files.
        
    Returns:
        str: A summary of the unit test results, including the number of tests run, passed, and failed.
    """
    try:
        command = f"python -m unittest discover {test_directory}"
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for line in output.split('\n'):
            if line.startswith('Ran'):
                total_tests = int(line.split()[1])
            elif line.startswith('OK'):
                passed_tests = total_tests
            elif line.startswith('FAILED'):
                failed_tests = total_tests - passed_tests
        
        summary = f"Unit Test Results for {test_directory}:\n"
        summary += f"Total Tests: {total_tests}\n"
        summary += f"Passed Tests: {passed_tests}\n"
        summary += f"Failed Tests: {failed_tests}\n"
        
        if failed_tests > 0:
            summary += "Some unit tests failed. Please check the test output for more details."
        else:
            summary += "All unit tests passed successfully!"
        
        logger.info(f"Unit tests executed for {test_directory}. Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}")
        return summary
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error occurred during unit test execution for directory: {test_directory}")
        return f"Error occurred during unit test execution: {str(e)}"
