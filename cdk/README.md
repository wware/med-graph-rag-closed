# CDK Infrastructure

This directory contains the AWS Cloud Development Kit (CDK) code for deploying the Medical Knowledge Graph infrastructure.

## Contents

*   `app.py`: The entry point for the CDK application. Defines the stacks to be deployed.
*   `CDK_SETUP.py`: Likely contains the stack definition, including resources like Amazon OpenSearch Service, IAM roles, and potentially other AWS services required for the application.

## Proposed Pytest Cases

Since this is Infrastructure as Code, testing ensures that the generated CloudFormation templates match expectations and that resources are configured correctly.

### Unit Tests (Snapshot Testing)
*   **Stack Synthesis**: Verify that the stack synthesizes successfully without errors.
*   **Snapshot Tests**: Compare the synthesized CloudFormation template against a stored snapshot to detect unintended changes in the infrastructure definition.

### Fine-Grained Assertions
*   **Resource Existence**:
    *   Verify that an OpenSearch Domain is created.
    *   Verify that necessary IAM roles (e.g., for Bedrock access, OpenSearch access) are created.
*   **Configuration Checks**:
    *   Ensure OpenSearch is configured with the correct instance type and version.
    *   Check that encryption at rest and in transit are enabled.
    *   Verify that access policies are correctly scoped (least privilege).

### Integration Tests (Post-Deployment)
*   **Endpoint Reachability**: After deployment, verify that the OpenSearch endpoint is reachable (if public or from a bastion).
*   **Permissions**: Verify that the created IAM roles can actually perform the intended actions (e.g., invoke Bedrock models).
