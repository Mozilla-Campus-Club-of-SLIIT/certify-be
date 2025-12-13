#!/usr/bin/env python3
import re
import sys

if len(sys.argv) < 2:
    print("Error: No commit message provided")
    sys.exit(1)

message = " ".join(sys.argv[1:]).strip()

pattern = r"^(feat|bug|fix|docs|style|refactor|test|chore)(\([a-zA-Z0-9_/]+\))?: .+"

if not re.match(pattern, message):
    print("Error: Commit message must follow conventional commit format.")
    print("Examples: 'feat: add feature', 'fix(login): correct bug', 'feat(api/v2): new endpoint'")
    sys.exit(1)

print("Commit message is valid ✅")
