"""
Template 1: Command + Config Validation Workflow
=================================================
Parse CLI command outputs and structured configuration (JSON/XML/YANG) to 
validate settings against known-good states and compliance policies.

Use this template when:
- Primary data comes from CLI commands and/or structured config.
- Analysis is deterministic (no AI/LLM needed).
"""

import re

# =========================================================================
# CONSTANTS 
# =========================================================================
# TODO: Define expected values, supported OS versions, required baseline settings
# REQUIRED_BASE_CONFIG = {"snmp_enabled": True, "ssh_version": 2}

# =========================================================================
# HELPER FUNCTIONS
# =========================================================================
def parse_device_info(output: str) -> dict:
    """Generic parser for device version/inventory output."""
    parsed = {}
    # Abstract regex patterns that catch major vendor outputs (Cisco, Juniper, Arista)
    patterns = {
        'hostname': r"(?i)hostname[:\s]*(.*)",
        'model': r"(?i)(?:model|hardware|chassis)[:\s]*(.*)",
        'os_version': r"(?i)(?:version|software|image)[:\s]*(.*)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            parsed[key] = match.group(1).strip()
    return parsed

# =========================================================================
# MAIN WORKFLOW
# =========================================================================
@workflow_tool(
    name="TODO:workflow_name", 
    description="TODO: Describe what this workflow validates",
    diagnostic_data={
        "commands": ["show version"], # TODO: Add vendor-specific baseline commands
    }
)
def config_validation_workflow(
    device_id: str = None,
    diagnostic_context: dict = None,
    **kwargs,
) -> dict:
    
    findings = []
    
    if not diagnostic_context:
        return {"status": "error", "message": "No diagnostic data provided."}

    # Step 1: Get device info (Abstracted SDK Call)
    raw_output = execute_cli(diagnostic_context, "show version")
    device_info = parse_device_info(raw_output)

    # Step 2: Validate Configuration 
    config_data = get_structured_config(diagnostic_context)
    
    # TODO: Implement generic config validation logic here
    # if config_data.get("insecure_protocols", {}).get("telnet") == "enabled":
    #     findings.append({
    #         "severity": "critical", 
    #         "description": "Telnet is enabled, violating baseline security policy."
    #     })

    status = "error" if any(f["severity"] == "critical" for f in findings) else "success"

    return {
        "status": status,
        "device": device_info.get("hostname", "Unknown"),
        "findings": findings
    }
