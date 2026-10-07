# BAMOE Migrate BPMN Workflow Assets

Migrates BPMN workflow assets from v8 to v9, ensuring compatibility with the new runtime and tooling.

## When to Use

Use this skill to:
- Upgrade BPMN XML to v9 format
- Remove v9-incompatible constructs
- Verify BPMN code generation works

## Prerequisites

- v9 project structure must be created (Sub-Task 2)
- BPMN files copied from v8 to v9
- BAMOE Developer Tools for VS Code installed
- Sub-Task 1 (Audit) must be completed first

## What This Skill Does

1. Analyzes BPMN files for v9 incompatibilities:
   - Process IDs with hyphens or dots
   - JavaScript Script Tasks
   - DROOLS gateway expressions
   - Shared KIE session patterns (`insert()`, `retract()`, `update()`, `delete()`)
2. Instructs user to open BPMN in BAMOE Developer Tools and save to trigger XML upgrade
3. Verifies no incompatible constructs remain
4. Runs `mvn clean package` to verify BPMN code generation

## Expected Output

- BPMN files opened and saved in BAMOE Developer Tools (XML upgrade applied)
- No JavaScript Script Tasks
- No DROOLS gateway expressions
- No shared KIE session patterns
- Process IDs use camelCase only
- Build succeeds with BPMN code generation

## Notes

- The XML upgrade is non-destructive (only updates IDs and character escaping)
- If JavaScript Script Tasks are found, they must be manually rewritten in Java
- If DROOLS expressions are found in gateways, they must be converted to Java expressions
- If shared KIE session patterns are found, refactor to use explicit Input/Output data mapping
- For Case Management (CMMN) projects, convert to Flexible (AdHoc) BPMN Processes by setting `AdHoc=true`
