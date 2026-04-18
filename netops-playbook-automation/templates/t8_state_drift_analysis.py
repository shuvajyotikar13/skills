"""
Template 8: State Drift & Differential Analysis
================================================
Captures operational state (routes, ARP, MAC tables, neighbors) 
and compares it against a baseline to detect missing entries or drift.
"""

@workflow_tool(
    name="generic:state_drift_analyzer",
    description="Compares two sets of operational data to find missing routes or neighbors",
)
def state_drift_analysis_workflow(
    baseline_data: dict, # Captured previously
    current_context: dict = None
) -> dict:
    
    findings = []
    
    # Step 1: Capture Current State
    current_arp = execute_cli(current_context, "show arp")
    current_routes = execute_cli(current_context, "show ip route")
    current_bgp = execute_cli(current_context, "show bgp summary")

    # Step 2: Parse into comparable sets
    base_routes = set(parse_routing_table(baseline_data.get("routes", "")))
    curr_routes = set(parse_routing_table(current_routes))
    
    base_bgp = parse_bgp_peers(baseline_data.get("bgp", ""))
    curr_bgp = parse_bgp_peers(current_bgp)

    # Step 3: Calculate the Differential
    missing_routes = base_routes - curr_routes
    if missing_routes:
        findings.append({
            "severity": "critical",
            "description": f"Post-maintenance drift: Missing {len(missing_routes)} routes present in baseline."
        })

    for peer, base_state in base_bgp.items():
        curr_state = curr_bgp.get(peer, "Unknown")
        if base_state == "Established" and curr_state != "Established":
            findings.append({
                "severity": "critical",
                "description": f"BGP Peer {peer} drifted from Established to {curr_state}"
            })

    return {
        "status": "error" if findings else "success",
        "drift_summary": {"missing_routes": list(missing_routes)},
        "findings": findings
    }
