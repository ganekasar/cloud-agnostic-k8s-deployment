variable region {
    description = " Specify region"
    default = "asia-south1"
}

variable zone {
    description = " Specify zone"
    default = "asia-south1-a"
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

variable machine_type {
    description = "Specify machine type"
    default = "f1-micro"
}

variable boot_image {
    description = "Specify boot image to be used"
    default = "ubuntu-os-cloud/ubuntu-1804-lts"
}
variable ansible_command {
    description = "Command to pass variables to ansible playbook"   
}