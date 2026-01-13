---
description: Refresh the THREAT_MODEL.md based on the current repository state
---

1.  **Analyze Context**:
    - Check for the existence of `THREAT_MODEL_CONTEXT.md`. If it exists, read it for manually provided architectural context, business logic risks, or specific user concerns.
    - Review `README.md` for high-level data flow.
    - Examine **all source code** for API interactions, data processing logic, and data sinks.
    - Review **all infrastructure-as-code** (e.g., Terraform, CloudFormation) for infrastructure trust boundaries, IAM permissions, and networking configurations.
2.  **Conduct STRIDE Analysis**: Evaluate the system against Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.
3.  **Identify Mitigations**: Map existing security controls to the identified threats, incorporating any specific context from `THREAT_MODEL_CONTEXT.md`.
4.  **Update THREAT_MODEL.md**: 
    - Rewrite `THREAT_MODEL.md` to reflect the total current system state.
    - **Include an ASCII diagram** representing the logical data flow and trust boundaries.
    - Organize by Trust Boundaries.
    - Include a "Changelog" section summarizing the latest change.
5.  **Identify Gaps**: Flag any threats that lack sufficient mitigation for the user to review, for any gaps, incorperate feedback from the file `THREAT_MODEL_FEEDBACK.md`