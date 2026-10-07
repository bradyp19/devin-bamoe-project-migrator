# BAMOE Audit v8 Project

Audits a BAMOE v8 project to create a migration inventory, identifying all assets that need migration, conversion, or replacement in v9.

## When to Use

Use this skill when starting a BAMOE v8 to v9 migration to:
- Identify all asset types in the v8 project
- Classify assets by migration action required
- Identify v9-incompatible constructs
- Generate a migration-inventory.md document

## Prerequisites

- v8 project must be exported to `v8-projects/<project-name>/`
- Java 21+ installed
- Maven 3.9.11+ installed
- BAMOE Maven Repository configured in `~/.m2/settings.xml`

## What This Skill Does

1. Runs `find . -type f` on the v8 project directory to catalog all files
2. Analyzes BPMN files for:
   - Process IDs (checks for hyphens/dots)
   - Script Tasks and their languages
   - Gateway expression languages
   - Shared KIE session patterns (`insert()`, `retract()`, etc.)
3. Lists all configuration files to delete (kmodule.xml, kie-deployment-descriptor.xml, etc.)
4. Lists all form files (.frm) that need regeneration
5. Checks for unsupported features:
   - PMML models
   - Guided rules/decision tables
   - DSL/DSLR
   - Scorecards
   - Case Management (CMMN)
   - JavaScript scripting
6. Lists custom WIHs, event listeners, and security classes
7. Generates `migration-inventory.md` with:
   - Complete asset inventory
   - Migration categorization (Migrate as-is, Requires update, Must replace)
   - v9 incompatibility flags
   - Current Java/Maven versions
   - v8 source path and v9 output path

## Expected Output

A `migration-inventory.md` file at the workspace root containing:
- Asset summary table
- Detailed BPMN analysis
- Configuration files to delete
- Forms requiring regeneration
- Custom code requiring migration
- Complexity assessment
- Next steps

## Notes

- This skill does NOT modify any files - it only reads and analyzes
- All analysis is grounded against BAMOE 9.5.x documentation
- The inventory guides subsequent migration sub-tasks
