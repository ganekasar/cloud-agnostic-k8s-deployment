variable "tenant_id" {
    default = "ab77d0b8-ab42-469a-ace5-7a30504a0538"
}
variable "client_id" {
    default = "naraharipapshetwar@gmail.com"
}
variable "client_secret" {
    default = "Hari@2018BTECS00012"
}

variable public_key_location {
    description = "Specify location for your public key generated via (ssh-keygen)"
    default = "~/.ssh/id_rsa.pub"
}

variable private_key_location {
    description = "Specify location for your private key generated via (ssh-keygen)"
    default = "~/.ssh/id_rsa"
}

variable user {
    description = "Specify user's name that will be used for creating VM's"
    default = "automation"
}

variable prefix {
    description = "The prefix which should be used for all resources"
    default = "automation"
}

variable "location" {
  description = "The Azure Region in which all resources in this example should be created."
  default = "westeurope"
}

variable "vpc_cidr_block" {
    description = "specify VPC cidr block"
    default = "10.0.0.0/16"
}

variable "subnet_cidr_block" {
    description = "specify subnet cidr block"
    default = "10.0.0.0/24"
}

variable "size" {
    description = "Specify size of vm"
    default = "Standard_F2"
}

variable "publisher" {
     description = "specify source image reference publisher" 
     default = "Canonical" 
}

variable "offer" {  
    description = "specify source image reference offer"
    default     = "UbuntuServer" 
}

variable "sku" {  
    description = "specify source image reference sku" 
    default       = "16.04-LTS" 
}

variable "image_version" { 
    description = "specify source image reference version"
    default   = "latest" 
}

variable ansible_command {
    description = "Command to pass variables to ansible playbook"   
}