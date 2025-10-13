data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu_arm64" {
  owners = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*"]
  }

  filter {
    name   = "architecture"
    values = ["arm64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  most_recent = true
}

resource "aws_security_group" "ec2_test_sg" {
  name        = var.security_group_name
  description = "OPEN INBOUND/OUTBOUND FOR TESTING ONLY"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Allow all IPv4 inbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description      = "Allow all IPv6 inbound"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = var.tags
}

resource "aws_instance" "ec2_test" {
  ami                         = data.aws_ami.ubuntu_arm64.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default_vpc_subnets.ids[0]
  vpc_security_group_ids      = [aws_security_group.ec2_test_sg.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.this.key_name

  tags = merge(var.tags, {
    Name = var.instance_name
  })
}

# SSH key pair for the instance (TESTING ONLY - exposes private key)
resource "tls_private_key" "this" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "this" {
  key_name   = "${var.instance_name}-key"
  public_key = tls_private_key.this.public_key_openssh
}

resource "aws_eip" "ec2_test_eip" {
  domain = "vpc"

  tags = merge(var.tags, {
    Name = "${var.instance_name}-eip"
  })
}

resource "aws_eip_association" "ec2_test_assoc" {
  instance_id   = aws_instance.ec2_test.id
  allocation_id = aws_eip.ec2_test_eip.id
}

