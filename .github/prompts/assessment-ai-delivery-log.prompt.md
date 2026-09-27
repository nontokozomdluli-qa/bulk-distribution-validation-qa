---
name: assessment-ai-delivery-log
description: Generate and maintain AI-assisted delivery documentation for multi-task assessment projects.
argument-hint: Optional: task names, required folder name, and log depth (brief|detailed)
---
Create or update AI-assisted documentation for this assessment workspace.

## Inputs
Use these inputs when provided by the user:
- Task folders to include (default: task 1, task 2, task 3)
- Documentation folder name (default: AI-Assisted Delivery)
- Log depth: brief or detailed (default: detailed)
- Whether to move root SOLUTION.md into the documentation folder (default: yes)

If an input is missing, apply defaults and continue.

## Required workflow
1. Validate structure:
- Confirm task folders and resources folder exist.
- Identify missing required artifacts per task (README, SOLUTION, core implementation files).

2. Create or update central documentation folder:
- Ensure folder exists: AI-Assisted Delivery (or user-provided name).
- Ensure these files exist and are updated:
  - TASK1.md
  - TASK2.md
  - TASK3.md
  - SOLUTION.md

3. Task prompt logs:
For each TASK*.md, include:
- Goal
- Useful prompts used
- What AI accelerated
- What was manually validated
- Output artifacts

4. Root summary:
In SOLUTION.md include:
- Overview of human-in-the-loop approach
- How AI was used strategically across tasks
- Quality controls to avoid blind trust
- Manual vs AI-generated work split
- Traceability from prompts to outputs

5. File placement:
- If root SOLUTION.md exists and move is enabled, place it in the documentation folder.
- Avoid duplicate SOLUTION.md files unless user asks for both.

## Style rules
- Keep content practical, reviewer-friendly, and evidence-based.
- Prefer concrete file names and executed validation steps over generic claims.
- Use concise headings and numbered lists where helpful.

## Output behavior
- Make the file edits directly.
- Summarize exactly what was created, moved, or updated.
- Call out any missing files or assumptions made.
