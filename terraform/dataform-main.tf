resource "google_dataform_repository" "repository" {
  provider = google-beta
  for_each      = toset(var.google_dataform_repo_name)
  name = "${each.value}"
  region   = var.dataform_location
}


resource "google_dataform_repository_release_config" "release" {
  provider = google-beta
  for_each = toset(var.google_dataform_repository_release_config)
  project    = var.project_id
  region     = var.dataform_location
  repository = var.release_config_repo_name[each.value]
  depends_on = [google_dataform_repository.repository]
  name = "${each.value}"
  
  git_commitish = var.git_commitish
  cron_schedule = var.cron_release_config[each.value]
  time_zone     = var.release_config_time_zone[each.value]

  code_compilation_config {
    default_database = var.database
    default_schema   = var.schema
    default_location = var.dataform_location
    assertion_schema = var.assertion_schema
    database_suffix  = ""
    schema_suffix    = ""
    table_prefix     = ""
    vars = {
      var1 = "value"
    }
  }
}


resource "google_dataform_repository_workflow_config" "workflow" {
  provider = google-beta
  for_each = toset(var.google_dataform_repository_workflow_config)

  project        = var.project_id
  region         = var.dataform_location
  repository     = var.workflow_config_repo_name[each.value]
  name           = "${each.value}"
  depends_on = [google_dataform_repository_release_config.release]
  release_config = var.workflow_config_release_config[each.value]
  invocation_config {
    included_targets {
      database = var.database
      schema   = var.schema
      name     = "target_1" 


    }
    included_targets {
      database = var.database
      schema   = var.schema
      name     = "target_2"
    }
    included_tags                            = ["tag_1"]
    transitive_dependencies_included         = false
    transitive_dependents_included           = false
    fully_refresh_incremental_tables_enabled = false
  }

  cron_schedule   = var.cron_workflow_config[each.value]
  time_zone       = var.workflow_config_time_zone[each.value]
}
