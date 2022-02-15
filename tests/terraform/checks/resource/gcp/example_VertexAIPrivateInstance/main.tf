
resource "google_notebooks_instance" "pass1" {
  name = "pass1-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  # This configures a private Vertex AI instance
  no_public_ip = true
}


resource "google_notebooks_instance" "fail1" {
  name = "fail1-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }

  # This configures a public Vertex AI instance
  no_public_ip = false
}

# This configures a public Vertex AI instance
# b/c there is no "no_public_ip" setting configured
resource "google_notebooks_instance" "fail2" {
  name = "fail2-instance"
  location = "us-west1-a"
  machine_type = "e2-medium"
  vm_image {
    project      = "deeplearning-platform-release"
    image_family = "tf-latest-cpu"
  }
}
