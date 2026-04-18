# Skills

A curated collection of open-source, enterprise-grade Agent Skills for Network Operations, Infrastructure-as-Code (IaC), and Security automation.

These skills conform to the [Agent Skills standard](https://agentskills.io) and provide AI agents with the structural patterns, tools, and compliance safeguards needed to operate safely in production environments.

## Available Skills

### NetOps Playbook Automation (`netops-playbook-automation`)
Transforms human-readable network troubleshooting playbooks into robust, deterministic Python workflows. It includes a built-in PII/PHI & Secret scanner to ensure no customer IPs, credentials, or proprietary data are hardcoded into generated scripts.

```
skills/
├── README.md
└── netops-playbook-automation/
    ├── SKILL.md
    ├── README.md
    ├── scripts/
    │   └── netops_pii_scanner.py
    └── templates/
        ├── t1_command_config_validation.py
        ├── t2_log_pattern_detection.py
        ├── t3_ai_llm_augmented.py
        ├── t4_protocol_deep_inspection.py
        ├── t5_multi_source_correlation.py
        └── t6_prerequisite_checklist.py
```

## Installation

You can install skills directly into your agent environment (like Roo Code, Cursor, or Claude Code) using the Agent Skills CLI:

```bash
npx skills add shuvajyotikar13/skills --skill netops-playbook-automation
```

This will download the SKILL.md instructions, the generic architectural templates, and the netops_pii_scanner.py tool into your local .roo/skills/ or equivalent directory.
