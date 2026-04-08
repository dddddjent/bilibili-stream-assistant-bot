---
applyTo: "**"
---

# Agent Instructions

Be simple. Don't add fallback codes unless you have to.

1. Run all python files as modules. Run them from the root directory
2. New python related folders should have an `__init__.py` file
3. Check the file current state before making changes. I may have already made some changes
4. Write type hints for all functions and methods possible (no need to write redundant types, like for most variables)
6. all the files with bpy can be run with python directly. This module is already in my venv.
7. Don't write any try except unless it's very important or I tell you to.
8. For checking whether something exists, especially for files/dirs, try to use assert firstly. Try to avoid using if statement for checking none.
9. Avoid running python commands. Only do it when you have to, or ask me.
10. Avoid writing to __init__.py, as you need to change two places if you want to change one function.
11. Before using a python package, search on the internet to use it properly.
12. Don't do any backward compatibility thing. Old things should be removed to only support the new things.
13. Always put a template command to call this script. Include all args.
14. Never change the status of git, like unstage, stage, rm files. You are only allowed to do readonly operations on git.
