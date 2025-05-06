terraform {
  backend "gcs" {
    bucket = "tfstate-chatbot-dp03"   
    prefix = "terraform/state"        
  }
}
