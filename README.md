# cloud-agnostic-k8s-deployment

Step 1: *Clone the repository* 
        &emsp; ```git clone https://github.com/ganekasar/cloud-agnostic-k8s-deployment```

**AWS EKS:**

Prerequisties:
1. *an AWS account with the IAM permissions listed on the EKS module documentation*
2. [*a configured AWS CLI*](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html) 
3. [*AWS IAM Authenticator*](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html)
4. [*kubectl*](https://kubernetes.io/docs/tasks/tools/install-kubectl/) 
5. [*wget*](https://www.gnu.org/software/wget/) (required for the eks module) 
6. [*Terraform CLI*](https://learn.hashicorp.com/tutorials/terraform/install-cli) 

Step 2.1: Change the active directory  &emsp; ```cd aws_eks```
          
Step 2.2: Initialize Terraform workspace &emsp;```terraform init```
           
Step 2.3: Provision the EKS Cluster  &emsp;```terraform apply```

Step 2.4: Configure Kubectl &emsp;```aws eks --region $(terraform output -raw region) update-kubeconfig --name $(terraform output -raw cluster_name)```
          
Step 2.5: Destroy the workspace &emsp;```terrafrom destroy```
          
**Azure AKS:**

Prerequisites:
1. *an Azure Account*
2. *[a configured Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)*
3. [*kubectl*](https://kubernetes.io/docs/tasks/tools/install-kubectl/) 
4. [*Terraform CLI*](https://learn.hashicorp.com/tutorials/terraform/install-cli) 

Step 3.1: Change the active directory  &emsp ``cd azure_aks/terraform-aks-cluster``
          
Step 3.2: Create an Active Directory service principal account  &emsp ``az ad sp create-for-rbac --skip-assignment``

Step 3.3: Update your terraform.tfvars file 
          _Replace appID and password in terraform.tfvars with the appID and password obtainted after previous command_

Step 3.4: Initialize Terraform  &emsp ``terraform init``

Step 3.5: Provision the AKS cluster  &emsp ``terraform apply``

Step 3.6: Configure Kubectl  &emsp ``az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw kubernetes_cluster_name)``

Step 3.7: Access Kubernetes Dashboard  &emsp ``az aks browse --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw kubernetes_cluster_name)``

Step 3.8: Clean up workspace  &emsp ``terraform destroy``

**Google Cloud GKE:**

Prerequisites:
1. *An google cloud account*
2. *[kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)* 
3. *[Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli)* 
4. *Having Kubernetes Engine API enabled*

Step 4.1: Change the active directory &emsp ``cd gcp_gke``
          
Step 4.2: Update your variables.tf file
          _Replace varibales in variables.tf with the appropriate values and set path for the credentials file in main.tf file

Step 4.3: Initialize Terraform &emsp ``terraform init``

Step 4.4: Provision the GKE cluster &emsp ``terraform apply``

Step 4.6: Inspect the cluster pods using the generated kubeconfig file &emsp ``kubectl get pods --all-namespaces --kubeconfig=kubeconfig-prod``

Step 4.7: Clean up workspace &emsp ``terraform destroy``
