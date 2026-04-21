# Resume Generation Guardrails

**Purpose:** Ensure resume drafts preserve original content from `resumes.md` while adding structure, organization, and mapping to job requirements.

## Before Creating Any Resume Draft

### 1. Content Source Declaration
- [ ] Confirm with user: "Should I preserve original `resumes.md` content as-is, or adapt/rewrite it?"
- [ ] Document user's preference clearly before proceeding
- [ ] If user says "preserve," treat all content as read-only

### 2. Read Source Material
- [ ] Read the full `resumes.md` file before creating draft
- [ ] Identify what sections will be used (summary, capabilities, work history, education, certifications)
- [ ] Note exact wording of bullets and descriptions

### 3. Structural Changes Only (If Preserving Content)
These are allowed WITHOUT rewriting content:
- [ ] Reordering sections (e.g., moving certifications to bottom)
- [ ] Adding annotations in parentheses or footnotes
- [ ] Reformatting (bold, italics, line breaks)
- [ ] Removing duplicates (if exact content appears twice)
- [ ] Adding contact info row if missing
- [ ] Adding section headers if missing

### 4. Content Changes NOT Allowed (If Preserving)
These require explicit user approval:
- [ ] Rewording bullets or descriptions
- [ ] Combining or condensing multiple bullets into one
- [ ] Splitting one bullet into multiple
- [ ] Changing emphasis or focus of a bullet
- [ ] Removing bullets (unless user explicitly asks)
- [ ] Adding new bullets or examples
- [ ] Paraphrasing or synonym replacement

### 5. Mapping/Annotation Guidelines
If adding job requirement mappings:
- [ ] Use exact quotes from the job description where possible
- [ ] Put mapping text in annotations `*(Addresses: "...")*` or footnotes
- [ ] Keep annotations separate from original content
- [ ] Do not embed annotations into original bullets
- [ ] Make clear which content is from resume vs. from job description

### 6. Quality Checks
- [ ] Read draft line-by-line and compare against `resumes.md`
- [ ] Verify no bullet was reworded
- [ ] Verify no content was removed without user request
- [ ] Verify all original content is present
- [ ] Verify structure/format changes are transparent

### 7. User Notification
- [ ] If any content appears to need rewording to fit a job, ASK user first
- [ ] Show user the "before and after" if rewriting is needed
- [ ] Get explicit approval before changing any original language
- [ ] Document user's decision in MEMORY.md or file header

---

## Default Mode (Michael's Preference)

**ALWAYS assume:**
- ✅ Preserve all original content from resumes.md exactly as written
- ✅ Organize content in optimal structure for the job
- ✅ Add annotations showing how content addresses job requirements
- ✅ Never rewrite, paraphrase, or reword any content

**Only ask Michael if:**
- Job description is missing or unclear
- Need clarification on desired structure/format
- Unsure which resume section to use

---

## Checklist for Generation

When creating a resume draft:

```
1. Read full resumes.md and job description
2. Select optimal structure:
   - Name, contact, summary, skills, jobs (reverse chrono), education, certs
   - Max bullets per job? (default: 7)
   - Any special sections requested?
3. Preserve ALL original content word-for-word
4. Add annotations mapping content to job requirements
5. Quality check: No rewriting, no paraphrasing, no changes
6. Deliver draft
```

---

## Example: Content-Preserving Workflow

**User request:** "Create a resume draft for Job X using my resumes.md"

**My response:**
1. "Should I keep all original content from resumes.md exactly as-is, or would you like me to tailor/rewrite it to better match this job description?"
2. [Wait for user answer]
3. If "preserve as-is": Create draft with structure + annotations only
4. If "adapt": Show user proposed rewrites for approval before final draft

---

## Critical Rules (Never Violate)

- 🛑 **Never** change wording of any bullet (even synonyms)
- 🛑 **Never** combine bullets
- 🛑 **Never** remove bullets
- 🛑 **Never** add new bullets or examples
- 🛑 **Never** paraphrase or rephrase
- 🛑 **Never** reorder elements within a bullet
- 🛑 **Never** change emphasis of content

**Exception:** Only if Michael explicitly requests a change in that specific resume draft

## Approved Changes (Content-Preserving Mode)

✅ Reorder sections (jobs by date, move education to bottom)  
✅ Reformat (bold, italics, add spacing)  
✅ Add annotations/footnotes (for job mapping)  
✅ Add missing headers/metadata (name, contact row)  
✅ Remove exact duplicates (identical bullets)  
✅ Trim excessive whitespace  

---

## Approved Changes (If User Explicitly Asks)

✅ Reword bullets for concision  
✅ Combine bullets  
✅ Add new examples  
✅ Emphasize different aspect  
✅ Remove bullets  

**But require user approval first.**

---

Last updated: April 17, 2026
