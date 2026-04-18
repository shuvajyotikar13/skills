"""
Template 9: Closed-Loop Remediation & State Mutator
====================================================
Drafts a configuration or state-changing command based on diagnostics, 
pauses for human approval, and executes the change if authorized.
"""

@workflow_tool(
    name="generic:quarantine_endpoint",
    description="Diagnoses a malicious IP and drafts a quarantine configuration.",
    requires_approval=True # Tells the Agent SDK to pause
)
def remediation_workflow(
    malicious_ip: str,
    authorization_token: str = None, # Passed back after human clicks 'Approve'
    diagnostic_context: dict = None
) -> dict:
    
    # Phase 1: Diagnostic & Draft (Run if no auth token provided)
    if not authorization_token:
        # Check if IP is actually active on the network
        arp_data = execute_cli(diagnostic_context, f"show arp | include {malicious_ip}")
        if not arp_data:
            return {"status": "success", "message": "IP not found. No action needed."}
            
        # Draft the vendor-specific remediation commands
        proposed_commands = [
            "configure terminal",
            f"ip route {malicious_ip} 255.255.255.255 Null0",
            "commit",
            "exit"
        ]
        
        return {
            "status": "pending_approval",
            "message": f"Malicious IP {malicious_ip} found. Requesting permission to Null-route.",
            "proposed_changes": proposed_commands
        }

    # Phase 2: Execution (Run only if auth token is present and valid)
    try:
        execution_results = execute_config_commands(diagnostic_context, proposed_commands)
        
        # Verify the change was successful
        verify_route = execute_cli(diagnostic_context, f"show ip route {malicious_ip}")
        if "Null0" in verify_route:
            return {"status": "success", "message": "Endpoint successfully quarantined."}
        else:
            return {"status": "error", "message": "Commands executed but verification failed."}
            
    except Exception as e:
        return {"status": "error", "message": f"Configuration failed: {str(e)}"}
