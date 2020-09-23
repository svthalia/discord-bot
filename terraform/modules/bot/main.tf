##################
# Base resources #
##################

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "http" "myip" {
  url = "https://api.ipify.org"
}

data "aws_subnet_ids" "all" {
  vpc_id = module.vpc.vpc_id

  depends_on = [
    module.vpc
  ]
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-arm64-gp2"]
  }
}

#######
# VPC #
#######

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 2.0"

  name = "${var.prefix}-vpc"
  cidr = "10.0.0.0/16"

  azs            = ["${data.aws_region.current.name}a"]
  public_subnets = ["10.0.100.0/24"]

  enable_ipv6 = true
}

#######
# IAM #
#######

module "ec2_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 2.0"

  name        = "${var.prefix}-ec2-role"
  description = "Custom policy for the EC2 instance that runs the Discord bot"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem",
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem"
      ],
      "Effect": "Allow",
      "Resource": [
        "${var.users_table_arn}",
        "${var.users_table_arn}/*"
      ]
    }
  ]
}
EOF
}

module "ec2_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "~> 2.0"

  create_role             = true
  create_instance_profile = true
  role_requires_mfa       = false

  role_name        = "${var.prefix}-ec2-role"
  role_description = "Role for the EC2 instance that runs the Discord bot"

  custom_role_policy_arns = [module.ec2_policy.arn]

  trusted_role_services = [
    "ec2.amazonaws.com"
  ]
}

############
# Security #
############

resource "aws_key_pair" "key" {
  key_name   = "${var.prefix}-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

module "egress_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  name        = "${var.prefix}-ec2-http-security-group"
  description = "Security group for the EC2 instance that runs the Discord bot defining egress all"
  vpc_id      = module.vpc.vpc_id

  egress_rules = ["all-all"]
}

module "ssh_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  name        = "${var.prefix}-ec2-ssh-security-group"
  description = "SSH Security group for the EC2 instance that runs the Discord bot"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks = ["${chomp(data.http.myip.body)}/32"]
  ingress_rules       = ["ssh-tcp"]
}

# module "http_security_group" {
#   source  = "terraform-aws-modules/security-group/aws"
#   version = "~> 3.0"

#   name        = "${var.prefix}-ec2-http-security-group"
#   description = "Security group for the EC2 instance that runs the Discord bot"
#   vpc_id      = module.vpc.vpc_id

#   ingress_cidr_blocks = ["0.0.0.0/0"]
#   ingress_rules       = ["http-80-tcp", "all-icmp"]
# }

######
# EC2
######

module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 2.0"

  instance_count = 1
  name           = "${var.prefix}-runner"
  ami            = data.aws_ami.amazon_linux_2.id
  instance_type  = "t4g.nano"

  user_data = <<-EOF
    #!/bin/bash -xe
    exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

    yum update -y
    amazon-linux-extras enable python3.8
    yum install git python38 python38-devel gcc -y

    useradd deploy

    git clone https://github.com/svthalia/discord-bot.git /opt/app
    chown -R deploy:deploy /opt/app 
    cd /opt/app/

    touch .env

    echo "AWS_DEFAULT_REGION = \"${data.aws_region.current.name}\"" >> .env

    echo "DISCORD_GUILD_ID = \"${var.discord_guild_id}\"" >> .env
    echo "DISCORD_BOT_TOKEN = \"${var.discord_bot_token}\"" >> .env

    echo "THALIA_CLIENT_ID = \"${var.thalia_client_id}\"" >> .env
    echo "THALIA_CLIENT_SECRET = \"${var.thalia_client_secret}\"" >> .env
    echo "THALIA_SERVER_URL = \"${var.thalia_server_url}\"" >> .env

    echo "USERS_TABLE = \"${split("/", var.users_table_arn)[1]}\"" >> .env
    echo "DOMAIN_NAME = \"${var.domain_name}\"" >> .env

    su deploy -c 'bash ./resources/deploy_ec2.sh'
  EOF


  associate_public_ip_address = true
  monitoring                  = true

  key_name  = aws_key_pair.key.key_name
  subnet_id = tolist(data.aws_subnet_ids.all.ids)[0]
  vpc_security_group_ids = [
    module.egress_security_group.this_security_group_id,
    module.ssh_security_group.this_security_group_id
  ]
  iam_instance_profile = module.ec2_role.this_iam_instance_profile_name
}