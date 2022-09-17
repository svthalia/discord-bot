variable "name" {
  type = string
}

variable "path" {
  type = string
}

variable "prefix" {
  type = string
}

variable "timeout" {
  type = number
}

variable "tags" {
  type = map(string)
}

variable "api_gateway_arn" {
  type = string
  default = null
}

variable "schedule_expression" {
  type = string
  default = null
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
