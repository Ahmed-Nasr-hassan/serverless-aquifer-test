output "instance_id" {
  value       = aws_instance.ec2_test.id
  description = "ID of the EC2 instance"
}

output "public_ip" {
  value       = aws_eip.ec2_test_eip.public_ip
  description = "Elastic public IP address"
}

output "security_group_id" {
  value       = aws_security_group.ec2_test_sg.id
  description = "ID of the security group"
}

output "private_key_pem" {
  value       = tls_private_key.this.private_key_pem
  description = "Private key PEM for SSH (TESTING ONLY)"
  sensitive   = true
}

