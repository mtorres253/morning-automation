# Morning Automation

A personal automation system for daily workflows, powered by AWS Lambda and OpenClaw.

## Overview

This workspace contains three core automation skills that run on AWS Lambda, triggered daily via EventBridge:

- **Job Search** (9:00 AM PDT) — Curated job opportunities matching director/principal PM roles in civic tech, gov tech, and related industries
- **Gmail Digest** (9:00 AM PDT) — Categorized summary of inbox activity from the last 24 hours
- **Morning Journal** (8:00 AM PDT) — Daily reflection prompt for gratitude, tasks, and personal strengths

All results are delivered via email to keep workflows asynchronous and non-intrusive.

## Workspace Structure

```
.
├── README.md                          # This file
├── SOUL.md                            # Personal identity and values
├── USER.md                            # User profile
├── IDENTITY.md                        # Agent identity
├── AGENTS.md                          # Agent guidelines
├── TOOLS.md                           # Local setup notes
├── MEMORY.md                          # Long-term memory and context
├── HEARTBEAT.md                       # Heartbeat task configuration
├── ARCHITECTURE.md                    # System design documentation
├── CASE_STUDY.md                      # Implementation notes
├── README_JOB_PORTFOLIO.md            # Job search capability details
│
├── skills/                            # OpenClaw skill implementations
│   ├── job-search/
│   │   ├── SKILL.md
│   │   ├── job-search-config.json     # Search criteria and scoring
│   │   └── sent-jobs.json             # Deduplication tracking
│   ├── gmail-digest/
│   │   ├── SKILL.md
│   │   └── secrets/
│   │       └── gmail_oauth.json       # Gmail OAuth tokens
│   └── morning-journal/
│       └── SKILL.md
│
├── assets/                            # Supporting materials
│   └── job-search/
│       └── resumes.md                 # Role-specific resume templates
│
├── memory/                            # Daily and archived memory
│   └── archive/                       # Older memory files
│
├── archive/                           # Historical records
│   └── debug/                         # Debug logs and setup notes
│
└── .gitignore                         # Git configuration
```

## Key Files

- **SOUL.md** — Read this to understand the agent's values and operating principles
- **MEMORY.md** — Long-term context, system configuration, and important decisions
- **ARCHITECTURE.md** — Technical details on Lambda deployment and skill architecture
- **skills/job-search/job-search-config.json** — Customize job search criteria here
- **skills/gmail-digest/secrets/gmail_oauth.json** — Gmail OAuth refresh token (git-ignored)

## Getting Started

### Local Development

1. Explore the `skills/` directory for individual skill implementations
2. Check `MEMORY.md` for current system status and configuration
3. Review `ARCHITECTURE.md` for Lambda deployment details

### Running Skills Locally

Each skill can be tested locally by reading its `SKILL.md` file and following the instructions.

### Modifying Job Search Criteria

Edit `skills/job-search/job-search-config.json` to customize:
- Target roles and keywords
- Salary range
- Geographic preferences
- Company stage filters

### Adding New Skills

New skills can be created in the `skills/` directory following the OpenClaw skill specification. Update this README when adding new automations.

## Deployment

All three core skills are deployed on AWS Lambda with CloudWatch logs for debugging. Refer to `ARCHITECTURE.md` for deployment details and troubleshooting.

## Security

- Sensitive credentials (OAuth tokens, API keys) are stored in `secrets/` and git-ignored
- Gmail OAuth uses refresh tokens for long-term access without storing passwords
- All Lambda functions have minimal IAM permissions (least privilege)

## Notes

- This workspace uses OpenClaw for orchestration and agent management
- Memory is split between daily notes (`memory/YYYY-MM-DD.md`) and long-term context (`MEMORY.md`)
- Older memory files are archived in `memory/archive/` to optimize initial context loading
