resource "google_dialogflow_cx_agent" "agent" {
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


resource "google_dialogflow_cx_webhook" "good_webhook" {
  parent       = google_dialogflow_cx_agent.agent.id
  display_name = "GoodWebhook"
  enable_stackdriver_logging = true
  generic_web_service {
        uri = "https://paloaltonetworks.com"
    }
}

resource "google_dialogflow_cx_webhook" "bad_webhook" {
  parent       = google_dialogflow_cx_agent.agent.id
  display_name = "BadWebhook"
  enable_stackdriver_logging = false
  generic_web_service {
        uri = "https://paloaltonetworks.com"
    }
}

resource "google_dialogflow_cx_webhook" "bad_unset_webhook" {
  parent       = google_dialogflow_cx_agent.agent.id
  display_name = "BadUnsetWebhook"
  generic_web_service {
        uri = "https://paloaltonetworks.com"
    }
}