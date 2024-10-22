resource "google_dialogflow_cx_agent" "good" {
  display_name = "dialogflowcx-agent"
  location = "global"
  default_language_code = "en"
  supported_language_codes = ["it","de","es"]
  time_zone = "America/New_York"
  description = "Example description."
  enable_spell_correction    = true
  enable_stackdriver_logging = true
  speech_to_text_settings {
    enable_speech_adaptation = true
  }
}

resource "google_dialogflow_cx_agent" "bad" {
  display_name = "dialogflowcx-agent"
  location = "global"
  default_language_code = "en"
  supported_language_codes = ["it","de","es"]
  time_zone = "America/New_York"
  description = "Example description."
  enable_spell_correction    = true
  enable_stackdriver_logging = false
  speech_to_text_settings {
    enable_speech_adaptation = true
  }
}

resource "google_dialogflow_cx_agent" "bad_unset" {
  display_name = "dialogflowcx-agent"
  location = "global"
  default_language_code = "en"
  supported_language_codes = ["it","de","es"]
  time_zone = "America/New_York"
  description = "Example description."
  enable_spell_correction    = true
  speech_to_text_settings {
    enable_speech_adaptation = true
  }
}


