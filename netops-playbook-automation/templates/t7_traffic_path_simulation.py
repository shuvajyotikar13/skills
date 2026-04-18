"""
Template 7: Traffic Path & Reachability Simulation
===================================================
Traces a theoretical or active packet flow through the device's 
routing, NAT, and security policy engines.
"""

@workflow_tool(
    name="generic:traffic_path_trace",
    description="Simulates packet flow to determine why traffic is dropping",
    diagnostic_data={"commands": []} # Commands generated dynamically based on input
)
def traffic_path_simulation_workflow(
    source_ip: str,
    destination_ip: str,
    protocol: str = "tcp",
    destination_port: str = "443",
    diagnostic_context: dict = None
) -> dict:
    
    findings = []
    path_details = {}

    # Step 1: Routing Lookup (Egress Interface & Next Hop)
    # e.g., execute_cli(..., f"show ip route {destination_ip}")
    route_data = execute_cli(diagnostic_context, f"lookup_route {destination_ip}")
    path_details["routing"] = parse_route_lookup(route_data)
    
    if not path_details["routing"].get("route_found"):
        findings.append({"severity": "critical", "description": f"No route to host {destination_ip}"})
        return {"status": "error", "findings": findings} # Short-circuit

    # Step 2: NAT Translation Check
    nat_data = execute_cli(diagnostic_context, f"lookup_nat {source_ip} {destination_ip}")
    path_details["nat"] = parse_nat_rules(nat_data)

    # Step 3: Security Policy / ACL Evaluation
    # Using the translated IPs if NAT is applied
    eval_src = path_details["nat"].get("translated_src", source_ip)
    acl_data = execute_cli(diagnostic_context, f"simulate_acl {eval_src} {destination_ip} {protocol} {destination_port}")
    policy_result = parse_acl_simulation(acl_data)
    
    if policy_result.get("action") == "drop":
        findings.append({
            "severity": "critical", 
            "description": f"Traffic dropped by policy/ACL: {policy_result.get('rule_name')}"
        })

    return {
        "status": "error" if findings else "success",
        "path_analysis": path_details,
        "findings": findings
    }
