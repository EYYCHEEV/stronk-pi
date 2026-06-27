Use only the stronk_subagent tool. Do not call the raw subagent tool.

1. Spawn role technical-researcher with this task exactly, preserving the dollar mention:
<child_task>
Do not modify files.
Do not run shell commands or inspect files.
Use $repos skill context only.
Report exactly these three lines:
STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK
REPOS_DIR=<copy the REPOS_DIR value from the repos skill>
QUICK_COMMAND=<copy the exact command under "List repo names only" from the repos skill>
</child_task>
2. Wait for that child to complete with timeoutMs 3600000.
3. Close the child after it is terminal.
4. Final answer must include the child status and terminal result.
