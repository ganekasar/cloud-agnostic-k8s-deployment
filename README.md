# cloud-agnostic-k8s-deployment

Step 1: Clone the repository = 
        git clone https://github.com/ganekasar/cloud-agnostic-k8s-deployment

**AWS EKS:**

Prerequisties:
1. an AWS account with the IAM permissions listed on the EKS module documentation
2. a configured AWS CLI (https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html)
3. AWS IAM Authenticator (https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html)
4. kubectl (https://kubernetes.io/docs/tasks/tools/install-kubectl/)
5. wget (required for the eks module) (https://www.gnu.org/software/wget/)
6. Terraform CLI (https://learn.hashicorp.com/tutorials/terraform/install-cli)

Step 2.1: Change the active directory
          cd aws_eks

Step 2.2: Initialize Terraform workspace
          terraform init

Step 2.3: Provision the EKS Cluster
          terraform apply

Step 2.4: Configure Kubectl
          aws eks --region $(terraform output -raw region) update-kubeconfig --name $(terraform output -raw cluster_name)
 
Step 2.5: Destroy the workspace
          terrafrom destroy
          
          
