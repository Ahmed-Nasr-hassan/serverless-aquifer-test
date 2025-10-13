output "ec2_test_instance_id" {
  value       = module.ec2_test.instance_id
  description = "ID of the EC2 test instance"
}

output "ec2_test_public_ip" {
  value       = module.ec2_test.public_ip
  description = "Elastic public IP of the EC2 test instance"
}

output "ec2_test_private_key_pem" {
  value       = module.ec2_test.private_key_pem
  description = "Private key PEM for SSH (TESTING ONLY)"
  sensitive   = true
}

