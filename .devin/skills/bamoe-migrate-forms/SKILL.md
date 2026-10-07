# BAMOE Migrate Forms

Regenerates legacy v8 .frm forms using BAMOE Developer Tools form code generation.

## When to Use

Use this skill to:
- Replace v8 .frm form files with v9-compatible forms
- Generate form code for User Tasks
- Test forms in Dev UI

## Prerequisites

- v9 project structure created (Sub-Task 2)
- BPMN files migrated (Sub-Task 3)
- BAMOE Developer Tools for VS Code installed
- Project must be compiled (`mvn clean package`)
- bamoe-quarkus-devui dependency in POM

## What This Skill Does

1. Instructs user to run BAMOE Developer Tools command:
   - Command palette: `CMD + SHIFT + P` (macOS) or `CTRL + SHIFT + P` (Windows/Linux)
   - Command: "BAMOE Developer Tools: Generate form code for User Tasks"
2. Guides user through:
   - Selecting project path (auto-filled with current workspace)
   - Choosing UI library (PatternFly for React, Bootstrap 4 for HTML)
   - Selecting User Tasks (all or specific)
3. Forms are generated in `src/main/resources/custom-forms-dev/`
4. Instructs user to verify forms in Dev UI:
   - Run `mvn clean -Pdevelopment quarkus:dev`
   - Navigate to `http://localhost:8080/q/dev-ui/extensions`
   - Click "Forms" card
   - Test each form

## Expected Output

- Forms generated in `src/main/resources/custom-forms-dev/`
- For each User Task: form file (.tsx for PatternFly, .html for Bootstrap 4) + .config file
- Forms accessible and testable in Dev UI
- v8 .frm files can be deleted after verification

## Notes

- v8 .frm files are completely incompatible with v9 and cannot be migrated directly
- PatternFly generates React/TypeScript forms (recommended for modern apps)
- Bootstrap 4 generates plain HTML forms (simpler, no React)
- The custom-forms-dev folder is where generated forms are stored
- Forms can be customized in Dev UI by editing the source and clicking Save
