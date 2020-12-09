#!/usr/bin/env python3

import os
import sys
import subprocess
from github import Github, GithubException
import configparser

# https://pypi.org/project/keyring/
import keyring

# To store github token on OS keystore
# keyring.set_password("system", "gitgudtoken", "YOUR GITHUB PERSONAL ACCESS TOKEN")

# Get TOKEN from OS keystore (the best option!)
_key = keyring.get_password("system", "gitgudtoken")

if _key is None:
    '''
    Try to get it from system environment variable (it is not good practice).
    You have to create GIT_GUD_TOKEN envvar inside of ~/.bashrc or ~/.zshrc, etc.
    '''
    _key = os.environ.get('GIT_GUD_TOKEN', None)
elif _key is None:
    '''
    If you are not using environment variable, then try to get GITHUB TOKEN KEY from config.ini file.
    (it is not a good idea as well, you should use keyring)

    On 'config.ini' file
    [DEFAULT]
    KEY = YOUR GITHUB PERSONAL ACCESS TOKEN
    '''
    _config_parser = configparser.ConfigParser()
    _config_parser.read('config.ini')
    _key = _config_parser['DEFAULT']['KEY']

GIT_GUD_CONFIG = {
    'key': _key,

    'owners': {
        "GitHub_User_Name1",
        "GitHub_User_Name2",
        "GitHub_User_Name3"
    },

    'grading_file': "GRADING.md",

    'passed': 'Result: PASS',

    'failed': 'Result: FAIL',

    'commit_msg': 'Graded project, see the {}-file in the root directory',

}

class ResultPrinter:
    def __init__(self, title='No title', header=[], dict={}):
        self.title = title
        self.header = header
        self.data = dict

    def __str__(self):

        line = '-' * (len(self.title) + 5)
        result = line + '\n' + self.title + ': ' + str(len(self.data)) + '\n' + line + '\n'

        if len(self.data) == 0:
            result += 'No data \n'
            return result

        if isinstance(self.data, dict):
            longer_key = 0
            for k in self.data.keys():
                if len(k) > longer_key:
                    longer_key = len(k)
            longer_key+=4

            if len(self.header) > 0:
                result += '{col1:<{width}} {col2:100}'.format(col1=self.header[0], width=longer_key, col2=self.header[1]) + '\n\n'

            for k,v in self.data.items():
                result += '{key:<{width}} {value:100}'.format(key=k, width=longer_key, value=v) + '\n'

        elif isinstance(self.data, list):
            self.data.sort()
            for r in self.data:
                result += "{}: {}".format(self.header[0], r) + '\n'

        return result



def print_help():
    '''
    Print help describing the syntax for how to use the program.

    Parameters:
        - None

    Returns:
        - None
    '''
    usage = f"{sys.argv[0]} <action> [--organization/-o=<org>] <search string>"
    print(f"Usage: {usage}")
    print("Available actions:")
    print("    clone")
    print("    ls")
    print("    push-checkpoint")
    print("    push-comment")
    print("    push-grade-sheet")
    print("    push-pass-fail")
    print("    set_readonly")


def is_matching(repo, project, organization):
    '''
    Check if a repo matches with a project and potential organization
    If an organization is provided, make sure the repo is owned by it,
    and that the project name is in the repo name. If an organization is
    not provided, simply make sure the project matches.

    Parameters:
        - Repo which is the repository queried from github
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo

    Returns:
        - True if repo matches project and organization provided
        - False if otherwise
    '''
    if organization:
        if project in repo.name and organization == repo.owner.login:
            return True
    else:
        if project in repo.name:
            return True

    return False


def git_add_commit_push(result, cwd):
    '''
    Adds, commits and pushes file to remote.

    Parameters:
        - Result of the file to be added to the repo and pushed
        - Cwd is the directory path of the repo where the file is located

    Returns:
        - None
    '''
    commit_msg = GIT_GUD_CONFIG['commit_msg'].format(result)
    subprocess.run(["git", "add", result], cwd=cwd)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=cwd)
    subprocess.run(["git", "push"], cwd=cwd)


def parse_markdown_grading_sheeet(filename):
    '''
    Parses a markdown file for names and matches them with comments.

    Parameters:
        - Filename of the markdown file to be parsed

    Returns:
        - Dictionary where keys are student names and values are comments
        - None if a non-markdown file was provided

    '''
    if ".md" not in filename:
        return None

    grading_sheet = dict()
    student_name = None
    student_content = ""

    with open(filename, "r") as markdown_file:
        for line in markdown_file:
            # New student, so add previous student to dict
            if line.startswith("### "):
                if student_name is not None:
                    grading_sheet[student_name] = student_content
                student_name = line.strip("# \n")
                student_content = line
            # Same student, concatenate content
            else:
                student_content = student_content + line

        grading_sheet[student_name] = student_content

    return grading_sheet


def add_commit_push_grading_sheet():
    '''
    Parses a markdown file for names, matches them to the specific students,
    writes the comment to a file, adds and commits it to the repo before
    pushing it to remote.

    Promts the user for the filename of the grading sheet.
    Can only be used to parse a markdown file where the comments are on the
    following format:

    ### student-github-name
    - comments
    - more comments

    ### new-student-name

    The important thing is not the format of the comments, though they should
    be markdown as well, but that each student name, and only student names
    start with ### and that no comments contain ###.

    Parameters:
        - None

    Returns:
        - None
    '''
    filename = input("Enter path to sheet filename: ")
    grading_sheet = parse_markdown_grading_sheeet(filename)
    if grading_sheet is None:
        print(f"{filename} is not a markdown file: it must end in .md")

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    result = GIT_GUD_CONFIG['grading_file']

    graded_students = ResultPrinter('Grading comment pushed to students bellow',['Student', 'Repository'], {})
    no_repo_for_student = ResultPrinter('No repository was found to students bellow', ['Student'], [])
    no_student_for_repo = ResultPrinter('No student was found on grading file to repositories bellow',['Repository'], [])


    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        no_student_for_repo.data.append(repo)
        if os.path.isdir(repo_dir):
            # Try and find a student name matching the repo name
            found_student = False
            for student_name in grading_sheet.keys():
                if repo.endswith(student_name):
                    no_student_for_repo.data.remove(repo)
                    found_student = True
                    graded_students.data[student_name] = repo

                    with open(f"{repo_dir}/{result}", "w+") as f:
                        f.write(grading_sheet[student_name])
                    break

            if found_student:
                git_add_commit_push(result, repo_dir)
                print("Grading comment pushed to github: {}".format(repo))
            else:
                no_repo_for_student.data.append(student_name)

    print(graded_students)
    print(no_student_for_repo)
    print(no_repo_for_student)



def add_commit_push(project, comment):
    '''
    Adds a file, commits it and pushed to the git repos
    which are present in a project directory.

    Can be used to specify if a student has passed or failed, or to provide
    a comment interactively.

    Parameters:
        - Project which should match the name of the sub-directory containing
          the git repositories which should be added, committed and pushed to.
        - Comment parameter determines if the commit should be a comment or not

    Returns:
        - None
    '''
    if not comment:
        passed = GIT_GUD_CONFIG['passed']
        failed = GIT_GUD_CONFIG['failed']

    project_dir = "{}/{}".format(os.getcwd(), project)
    repos = os.listdir(project_dir)
    for repo in repos:
        repo_dir = "{}/{}".format(project_dir, repo)
        if os.path.isdir(repo_dir):
            if not comment:
                inp = input(f"Did {repo} 'pass' or 'fail'? [Default: pass]: ")
                if inp == "fail":
                    result = failed
                elif inp == "skip":
                    continue
                else:
                    result = passed
                text = ""
            else:
                result = GIT_GUD_CONFIG['grading_file']
                print(f"\nGrading {repo} - enter grading comment:")
                text = sys.stdin.read()

            with open(f"{repo_dir}/{result}", "w+") as f:
                f.write(text)

            git_add_commit_push(result, repo_dir)
            print("Pushed changes to github")
        else:
            print(f"\n{repo} is not a directory, and can't be a repo")


def list_matching(project, organization):
    '''
    Lists the repositories matching the provided project and organization.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    g = Github(GIT_GUD_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print(repo.name)


def set_matching_readonly(project, organization):
    '''
    Sets the matching repositories to read-only for all non-owners.
    Can be used to revoke students' write permissions.

    PS: Will ONLY work if the github library is modified.
        See github.com/NikolaiMagnussen/pygithub.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    g = Github(GIT_GUD_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            print("Changing permissions for {}".format(repo.name))
            for collab in repo.get_collaborators():
                if collab.login not in GIT_GUD_CONFIG['owners']:
                    # Student found. change permissions from push to pull
                    repo.remove_from_collaborators(collab)
                    try:
                        repo.add_to_collaborators(collab, "pull")
                        print("    {} can only read".format(collab.login))
                    except GithubException as e:
                        print(e)
                        repo.add_to_collaborators(collab)
                        print("    {} can still write because readonly is only"
                              " possible in orgs".format(collab.login))
                else:
                    print("    Owner: {}".format(collab.login))


def clone_matching(project, organization):
    '''
    Clone the matching repositories to a project directory.

    Parameters:
        - Project name to be queried (repo name should contain this)
        - Organization name which should own the repo (if any)

    Returns:
        - None
    '''
    project_dir = "{}/{}".format(os.getcwd(), project)
    g = Github(GIT_GUD_CONFIG['key'])
    for repo in g.get_user().get_repos():
        if is_matching(repo, project, organization):
            if not os.path.isdir(project_dir):
                os.mkdir(project_dir)
            split_idx = repo.clone_url.find("github.com")
            repo_url = "{}{}@{}".format(repo.clone_url[:split_idx],
                                        GIT_GUD_CONFIG['key'],
                                        repo.clone_url[split_idx:])
            subprocess.run(["git", "clone", repo_url], cwd=project_dir)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    action = sys.argv[1]
    if "--organization=" in sys.argv[2] or "-o=" in sys.argv[2]:
        organization = sys.argv[2].split("=")[1]
        project = sys.argv[3]
    else:
        if len(sys.argv) > 3:
            print_help()
            sys.exit(1)
        project = sys.argv[2]
        organization = None

    if action == "ls":
        list_matching(project, organization)
    elif action == "clone":
        clone_matching(project, organization)
    elif action == "set_readonly":
        print("Are you sure you want to set all non-owners of the matching "
              "repos to read-only?")
        print("Type 'YES' to confirm")
        ans = input()
        if ans == "YES":
            set_matching_readonly(project, organization)
    elif action == "push-pass-fail":
        if organization is not None:
            print("Organization does not affect pushing")
        add_commit_push(project, comment=False)
    elif action == "push-comment":
        if organization is not None:
            print("Organization does not affect pushing")
        add_commit_push(project, comment=True)
    elif action == "push-grade-sheet":
        if organization is not None:
            print("Organization does not affect pushing")
        add_commit_push_grading_sheet()
    else:
        print_help()
