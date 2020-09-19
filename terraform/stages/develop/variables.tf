variable "name" {
  description = "Name to be used on all the resources as identifier"
  default     = ""
}

variable "stage" {
  description = "Name of this stage"
  default     = ""
}

variable "aws_account_id" {
  description = "AWS account id"
  default     = ""
}

variable "aws_profile" {
  description = "Name of profile to use for aws"
  default     = ""
}

variable "aws_region" {
  description = "AWS Region to use"
  default     = ""
}