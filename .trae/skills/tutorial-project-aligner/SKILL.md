---
name: "tutorial-project-aligner"
description: "Aligns tutorials with projects, generates corresponding tutorial docs and README files, synchronizes naming conventions, and updates the overall project README. Invoke when user asks to sync documentation or generate tutorials for new projects."
---

# Tutorial-Project Aligner

## Overview

This skill aligns tutorial documents with engineering projects, ensuring consistency between documentation and code.

## Functionality

1. **Generate Tutorials**: Creates corresponding tutorial documents in `docs/02-教程/` for new projects
2. **Generate READMEs**: Creates README files in each project directory
3. **Align Naming**: Synchronizes naming conventions between tutorials and projects
4. **Update Main README**: Updates the overall project README with new content

## When to Invoke

- When user asks to sync documentation
- When user completes a new project and requests tutorial generation
- When tutorials need to be aligned with project code
- When README files need to be updated across the project

## Usage

1. User creates a new project in `projects/` directory
2. User invokes this skill
3. The skill:
   - Generates a corresponding tutorial in `docs/02-教程/`
   - Creates README.md in the project directory
   - Updates the main README.md with new entries
   - Ensures consistent naming between tutorials and projects

## Output

- New tutorial file in `docs/02-教程/` (e.g., `06-new-project-tutorial.md`)
- README.md in the project directory
- Updated main README.md with project information

## Example

If user creates `projects/06-langchain-workflow/`, this skill will:
1. Generate `docs/02-教程/06-工作流教程.md`
2. Create `projects/06-langchain-workflow/README.md`
3. Update `README.md` with the new project entry