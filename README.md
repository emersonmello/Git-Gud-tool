# GIT GUD CLI Tool

## Usage

- Create a [GitHub personal access token](https://docs.github.com/en/enterprise-server@2.22/github/authenticating-to-github/creating-a-personal-access-token) and store it on the OS keystore (See [How to store GitHub Person Access Token](#how-to-store-github-person-access-token))
- Edit [git_gud.py](git_gud.py) and update `GIT_GUD_CONFIG` dictionary (if you want)  
- [Notes](#notes)

## Author
Nikolai Magnussen


This is a tool I made to make my life as a teacher using GitHub Classroom easier and simpler, and at the
current moment it has all the features I need to maintain an effective workflow as I grade projects after submission.

## Requirements
* A GitHub Personal Access Token
* Python3
* Python3 packages
  - [pygithub](https://pypi.org/project/PyGithub/)
  - [keyring](https://pypi.org/project/keyring/)
## Features
- [GIT GUD CLI Tool](#git-gud-cli-tool)
  - [Usage](#usage)
  - [Author](#author)
  - [Requirements](#requirements)
  - [Features](#features)
    - [Repository Search](#repository-search)
    - [Mass Clone](#mass-clone)
    - [Set Student Access Read Only](#set-student-access-read-only)
    - [Interactive PASS/FAIL grading without comment](#interactive-passfail-grading-without-comment)
    - [Interactive grading with comment](#interactive-grading-with-comment)
    - [Automatic grading using a Markdown document](#automatic-grading-using-a-markdown-document)
  - [Notes:](#notes)
  - [How to store API Key](#how-to-store-api-key)
### Repository Search
* Fuzzy matching on repository names
* Ability to specify a GitHub organization if you have multiple assignments that are named the same, but in different organizations and you don’t want both
* Is very practical to use before cloning to make sure you do not clone repositories that should not be cloned
### Mass Clone
* Fuzzy matching on repository names
* Ability to specify a GitHub organization if you have multiple assignments that are named the same, but in different organizations and you don’t want both
* Clones all matching repositories into a directory matching the search string used when specifying which repositories to clone
### Set Student Access Read Only
* This feature is from before the GitHub Classroom deadline feature
* Fuzzy matching on repository names
* Ability to specify a GitHub organization, which is required because it is only possible in those types of repositories
### Interactive PASS/FAIL grading without comment
* Uses the local directory of previously mass cloned repositories
* It will go through all student repositories and prompt you for PASS or FAIL, with PASS being default
* After specifying whether the submission is PASSED or FAILED, it will automatically add, commit and push the grading file to remote (probably GitHub Classroom)
### Interactive grading with comment
* Uses the local directory of previously mass cloned repositories
* It will go through all student repositories and prompt you for the feedback that should be provided, writing to the grading file until EOF is intered, allowing for multi-line feedback.
* After providing feedback to the student, it will automatically add, commit and push the grading file to remote (probably GitHub Classroom)
### Automatic grading using a Markdown document
* Uses the local directory of previously mass cloned repositories as well as your feedback to all students in a Markdown document
* It will parse the markdown file, matching students with their feedback, and then match it with the repositories in the directory.
* The matched feedback is added to the student repository, committed and pushed to remote (probably GitHub Classroom)
## Notes:
* If a student has not been graded in the Markdown document, you will simply be notified that the student has not been provided any feedback in the Markdown document, and if you have graded students that are not cloned, their feedback will simply be ignored.
* The only rule for writing the feedback document is that heading the feedback for student “John Doe”, you must write the username of the student like so: “### JohnDoe” (assuming John Doe uses JohnDoe as is GitHub username).

## How to store GitHub Person Access Token

From [keyring](https://pypi.org/project/keyring/) documentation:

> The Python keyring library provides an easy way to access the system keyring service from python. It can be used in any application that needs safe password storage.
> These recommended keyring backends are supported:
> - macOS Keychain
> - Freedesktop Secret Service supports many DE including GNOME (requires [secretstorage](https://pypi.org/project/SecretStorage/))
> - KDE4 & KDE5 KWallet (requires dbus)
> - Windows Credential Locker

1. Execute the follow lines on a python3 shell 
    ```python
    import keyring
    keyring.set_password("system", "gitgudtoken", "YOUR GITHUB PERSONAL ACCESS TOKEN")
    ```