resource "google_compute_firewall" "webserverrule" {
  name    = "${var.prefix}-webserver"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22","80","443","27017"]
  }

  source_ranges = ["0.0.0.0/0"] 
  target_tags   = ["webserver"]
}

resource "google_compute_address" "static" {
  name = "${var.prefix}-public-address"
  depends_on = [ google_compute_firewall.webserverrule ]
}

resource "google_compute_instance" "dev" {
  provider     = google-beta
  name         = "${var.prefix}-vm"
  machine_type = var.machine_type
  tags         = ["webserver"]

  boot_disk {
    initialize_params {
      image = var.boot_image
    }
  }

  network_interface {
    network = "default"

    access_config {
      nat_ip = google_compute_address.static.address
    }
  }

  provisioner "remote-exec" {
    connection {
      host        = google_compute_address.static.address
      type        = "ssh"
      user        = var.user
      timeout     = "500s"
      private_key = file(var.private_key_location)
    }

    inline = [
      "mkdir newDir",
      "rmdir newDir"
    ]
  }

   provisioner "local-exec" {
    command = format("%s %s","ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -u ${var.user}   -i ${google_compute_address.static.address}, --private-key ${var.private_key_location} ../ansible/linux_playbook.yml",var.ansible_command)
  }

  depends_on = [ google_compute_firewall.webserverrule ]

  metadata = {
    ssh-keys = "${var.user}:${file(var.public_key_location)}"
  }
}

resource "google_compute_machine_image" "image" {
  provider        = google-beta
  name            = "${var.prefix}-image"
  source_instance = google_compute_instance.dev.self_link
  depends_on = [google_compute_instance.dev]
}