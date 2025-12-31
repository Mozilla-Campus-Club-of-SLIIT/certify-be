#!/usr/bin/env python3
import re
import sys

if len(sys.argv) < 2:
    print("Error: No commit message file provided")
    sys.exit(1)

commit_file = sys.argv[1]

with open(commit_file, "r", encoding="utf-8") as f:
    message = f.read().strip()

pattern = r"^(feat|bug|fix|docs|style|refactor|test|chore)(\([a-zA-Z0-9/_\-]+\))?: .+\s*$"

if not re.match(pattern, message):
    print("Error: Commit message must follow conventional commit format.\n")
    print("Examples:")
    print("  feat: add new feature")
    print("  fix(login): correct authentication bug")
    print("  feat(api/v2): add new endpoint")
    sys.exit(1)

print("Commit message is valid")
