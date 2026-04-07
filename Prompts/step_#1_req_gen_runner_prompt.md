Act as a senior software architect.

You are given two inputs:

1) INPUT DESCRIPTION (source of truth)
2) REQUIREMENT PROMPT (rules and structure)

---

## INPUT DESCRIPTION

<PASTE CONTENT OF input_description.md>

---

## REQUIREMENT PROMPT

<PASTE CONTENT OF requirement_prompt.md>

---

## TASK

Using the REQUIREMENT PROMPT as strict instructions, transform the INPUT DESCRIPTION into a structured requirement document.

---

## RULES

- Follow the REQUIREMENT PROMPT exactly
- Do NOT invent features not present in the input
- If something is unclear, make reasonable assumptions but keep them minimal
- Ensure all requirements are:
  - atomic
  - testable
  - unambiguous

---

## OUTPUT

- Generate ONLY the final Markdown document
- No explanations
- No extra commentary
- Output must be directly savable as: requirements.md
