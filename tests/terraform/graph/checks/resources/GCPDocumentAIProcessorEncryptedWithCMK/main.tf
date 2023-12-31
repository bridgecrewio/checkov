resource "google_document_ai_processor" "processor_bad" {
  location = "us"
  display_name = "bad-processor"
  type = "OCR_PROCESSOR"
}

resource "google_document_ai_processor" "processor_good" {
  location = "us"
  display_name = "good-processor"
  type = "OCR_PROCESSOR"
  kms_key_name = "my_super_secret_key_name"
}