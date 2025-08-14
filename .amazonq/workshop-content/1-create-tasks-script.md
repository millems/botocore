mwinit -s
---
q chat --agent workshop
---
Run pdd from genai_poweruser_agent_script_get
---
Idea: /Users/millem/source/genai-workshop-1/.amazonq/rules/toml-sep/design.md to support https://code.amazon.com/packages/AwsDrSeps/commits/93b12ef10c116a65e5c472aa66e22cb25d4e8567
project_dir: ./.amazonq/rules/toml-sep/pdd/
checkpointing: false
---
Default
---
For 2, we should have separate parsing for TOML and not try to reuse the INI parsing pieces. For 1 and 3, we should make sure that users of session.py do not break, so we'll want to match the existing data types when we return from those methods. I think these are small enough to include in earlier phases.
---
Boto supports python 3.9+. Let's focus on 3.11+ for earlier milestones, and add support for 3.9 and 3.10 later. We'll use conditional imports in those versions.
---
Before I answer, can you provide an example of where (4) would be a concern?
---
In cases 1-3, we should fail. Case 4 is not a concern.
---
Let's have the config provider for TOML arrays do the conversion to match the format of INI, for backwards-compatibility. This is the only array we need to consider.
---
Proceed to research phase.
---
You also have access to index the codebase with code_cerebro_build_code_index, for use in your research.
---
Proceed to the design phase.
---
Create code tasks based on the `/Users/millem/source/genai-workshop-1/./.amazonq/rules/toml-sep/pdd/implementation/prompt-plan.md`, and add those code tasks to `./.amazonq/tasks/toml-sep/`.