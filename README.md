Terraform Setup for Google Cloud Dataform

This repository contains Terraform code to set up a Dataform repository along with its associated workflow and release configurations on Google Cloud Platform (GCP) using the Google Beta provider.

Prerequisites:

GCP Account: Ensure you have access to a Google Cloud account with permissions to create Dataform resources.

Terraform: You need to have Terraform installed on your machine. Version 1.0 or higher is required.

GCP Credentials: Create a service account in GCP and download the JSON key file. Save it as cred.json in the root directory of this repository.



Project Structure

.
├── main.tf                   # Main configuration file
├── variables.tf              # Variables definition
└── provider.tf               # Provider configuration

main.tf
This file defines the resources necessary for setting up the Dataform repository, release configurations, and workflow configurations.

variables.tf
This file contains variable definitions used in the Terraform configurations.

provider.tf
This file specifies the required providers and their configurations, including authentication using the service account.



Usage


Clone the repository:

git clone <repository_url>
cd <repository_directory>


Initialize Terraform:

Run the following command to initialize Terraform and download the required providers:

terraform init


Check what changes Terraform will make by running:

terraform plan


Apply the configuration:

terraform apply


Confirm the action when prompted.


Deployment

After applying the Terraform configuration, your Dataform repository, along with its workflow and release configurations, will be set up in your GCP project. 
Verify the deployment through the Google Cloud Console to ensure everything is configured as expected.