resource "azurerm_resource_group" "main" {
  name     = "${var.prefix}-resources"
  location = var.location
}

resource "azurerm_virtual_network" "main" {
  name                = "${var.prefix}-network"
  address_space       = [var.vpc_cidr_block]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

resource "azurerm_network_security_group" "example" {
  name                = "${var.prefix}-sg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "${var.prefix}-rule"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    environment = "DEV"
  }
}

resource "azurerm_subnet" "internal" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [var.subnet_cidr_block]
}

resource "azurerm_public_ip" "main" {
  name                = "${var.prefix}-pip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
}

resource "azurerm_network_interface" "main" {
  name                = "${var.prefix}-nic"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.main.id
  }
}

resource "azurerm_network_interface_security_group_association" "example" {
  network_interface_id      = azurerm_network_interface.main.id
  network_security_group_id = azurerm_network_security_group.example.id
}

resource "azurerm_linux_virtual_machine" "main" {
  name                            = "${var.prefix}-vm"
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  size                            = var.size
  admin_username                  = var.user

  network_interface_ids = [
    azurerm_network_interface.main.id,
  ]

  admin_ssh_key {
    username   = var.user
    public_key = file(var.public_key_location)
  }

  source_image_reference {
    publisher = var.publisher
    offer     = var.offer
    sku       = var.sku
    version   = var.image_version
  }

  os_disk {
    storage_account_type = "Standard_LRS"
    caching              = "ReadWrite"
  }

  provisioner "remote-exec" {
    inline = [
      "ls -la /tmp",
    ]

    connection {
      host     = self.public_ip_address
      user     = self.admin_username
      private_key = file(var.private_key_location)
    }
  }

  provisioner "local-exec" {
    command = format("%s %s","ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -u ${var.user} -i ${self.public_ip_address}, --private-key ${var.private_key_location} ../ansible/linux_playbook.yml",var.ansible_command)
  }

  provisioner "local-exec" {
    command = "az login --service-principal -u ${var.client_id} --password ${var.client_secret} --tenant ${var.tenant_id}"  
  }

  provisioner "local-exec" {
    command = "az vm deallocate --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_linux_virtual_machine.main.name}"
  }

  provisioner "local-exec" {
    command = "az vm generalize --resource-group ${azurerm_resource_group.main.name} --name ${azurerm_linux_virtual_machine.main.name}"
  } 
}

resource "azurerm_resource_group" "for_image_storage" {
  name     = "${var.prefix}-image-resources"
  location = var.location
}

resource "azurerm_image" "my-image" {
  name                      = "${var.prefix}-image"
  location                  = var.location
  resource_group_name       = azurerm_resource_group.for_image_storage.name
  source_virtual_machine_id = azurerm_linux_virtual_machine.main.id
}