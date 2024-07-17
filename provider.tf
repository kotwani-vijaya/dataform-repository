terraform {
  required_version = "~> 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0, <6"
    }
 

    google-beta = {
      source  = "hashicorp/google-beta"
      version = "5.18.0"
    }
  }
}


provider "google" {
  project = var.project_id
  region  = var.location
  credentials = file("cred.json") 
}

provider "google-beta" {
  project     = var.project_id
  region      = var.location
  credentials = file("cred.json")
}