variable "name" {
  type = string
}

variable "prefix" {
  type = string
}

variable "api_gateway_arn" {
  type = string
}

variable "attach_policy_statements" {
  type    = bool
  default = false
}

variable "policy_statements" {
  type    = any
  default = {}
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}