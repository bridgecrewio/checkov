resource "google_dialogflow_agent" "agent_good" {
  display_name = "dialogflow-agent-good"
  default_language_code = "en"
  time_zone = "America/New_York"
  enable_logging = true
  match_mode = "MATCH_MODE_ML_ONLY"
  classification_threshold = 0.3
  api_version = "API_VERSION_V2_BETA_1"
  tier = "TIER_STANDARD"
}

resource "google_dialogflow_agent" "agent_bad" {
  display_name = "dialogflow-agent-bad"
  default_language_code = "en"
  time_zone = "America/New_York"
  enable_logging = false
  match_mode = "MATCH_MODE_ML_ONLY"
  classification_threshold = 0.3
  api_version = "API_VERSION_V2_BETA_1"
  tier = "TIER_STANDARD"
}

resource "google_dialogflow_agent" "agent_bad_unset" {
  display_name = "dialogflow-agent-bad-unset"
  default_language_code = "en"
  time_zone = "America/New_York"
  match_mode = "MATCH_MODE_ML_ONLY"
  classification_threshold = 0.3
  api_version = "API_VERSION_V2_BETA_1"
  tier = "TIER_STANDARD"
}