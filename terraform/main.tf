# SQS Module
module "sqs" {
  source = "./modules/sqs"

  queue_name              = "${var.function_name}-queue"
  dlq_name               = "${var.function_name}-dlq"
  visibility_timeout     = var.sqs_visibility_timeout
  max_receive_count      = var.sqs_max_receive_count
  message_retention_days = 1

  tags = local.common_tags
}

# Lambda Module
module "lambda" {
  source = "./modules/lambda"

  function_name        = var.function_name
  ecr_repository_url   = "835410374509.dkr.ecr.us-east-1.amazonaws.com/aquifer-test-simulation"
  sqs_queue_arn        = module.sqs.queue_arn
  timeout              = var.lambda_timeout
  memory_size          = var.lambda_memory_size
  log_retention_days   = var.log_retention_days
  environment_variables = {
    ENVIRONMENT = var.environment
    LOG_LEVEL   = "INFO"
  }

  tags = local.common_tags
}

# Lambda Event Source Mapping (SQS Trigger)
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = module.sqs.queue_arn
  function_name    = module.lambda.function_arn
  batch_size       = 1  # Process one message at a time
  enabled          = true

  depends_on = [module.lambda]
}

module "ec2_test" {
  source = "./modules/ec2_test"

  instance_type       = "t4g.small"
  instance_name       = "aquifer-ec2-test"
  security_group_name = "ec2-test-open-sg"
  tags                = local.common_tags
}
