variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t4g.small"
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
  default     = "aquifer-ec2-test"
}

variable "security_group_name" {
  description = "Name for the security group"
  type        = string
  default     = "ec2-test-open-sg"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

