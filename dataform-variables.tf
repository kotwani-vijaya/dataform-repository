variable "project_id" {
  type        = string
  default     = "gcp-project-id"
}

variable "location" {
  type        = string
  default     = "us"
}

variable "dataform_location" {
  description = "The location of the bucket."
  type        = string
  default     = "us-central1"
}

variable "database" {
  description = "Specifies the action's database"
  type        = string
  default     = "gcp-example-project"
}

variable "schema" {
  description = "Specifies the action's schema, within database."
  type        = string
  default     = "example-dataset"
}

variable "assertion_schema" {
  description = "Specifies the action's schema, within database."
  type        = string
  default     = "example-assertion-dataset"
}

variable "project_name" {
  description = "The name of the dataform repository"
  type        = string
  default     = "demo"
}

variable "environment_name" {
  type        = string
  default     = "qa"
}

variable "git_commitish" {
  description = "specifies the branch"
  type        = string
  default     = "main"
}

variable "time_zone" {
  description = "Specifies the time zone to be used when interpreting cronSchedule."
  type        = string
  default     = "UTC"
}

variable "dataform_location" {
  description = "The location of the bucket."
  type        = string
  default     = "us-central1"
}

variable "google_dataform_repo_name" {
  type    = list(string)
  default = ["my_repo1"]
}

variable "google_dataform_repository_release_config" {
  type    = list(string)
  default = ["my_release1"]
}

variable "cron_release_config" {
  type = map(string)
  default = {
    "my_release1" = "0 8 * * *"
  }
}

variable "release_config_time_zone" {
  type    = map(string)
  default = {
    "my_release1" = "UTC"
  }
}

variable "google_dataform_repository_workflow_config" {
  type    = list(string)
  default = ["my_workflow1"]
}

variable "workflow_config_release_config" {
  type    = map(string)
  default = {
    "my_workflow1" = "my_release1"
  }
}

variable "release_config_repo_name" {
  type    = map(string)
  default = {
    "my_release1" = "my_repo1"
  }
}

variable "workflow_config_repo_name" {
  type    = map(string)
  default = {
    "my_workflow1" = "my_release1"
  }
}

variable "cron_workflow_config" {
  type = map(string)
  default = {
    "my_workflow1" = "10 * * * *"
  }
}

variable "workflow_config_time_zone" {
  type    = map(string)
  default = {
    "my_workflow1" = "UTC"
  }
}