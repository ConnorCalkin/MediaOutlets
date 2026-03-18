# data source for dashboard, which will be the ecr repository
data "aws_ecr_repository" "dashboard-repo" {
  name = "c22-dashboard-divas-dashboard-repo"
}

#create execution role for ecs task
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "c22-dashboard-divas-ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_dynamodb_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
}

# task definition for dashboard service
resource "aws_ecs_task_definition" "dashboard-task" {
  family                   = "c22-dashboard-divas-dashboard-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "c22-dashboard-divas-dashboard-container",
      image     = "${data.aws_ecr_repository.dashboard-repo.repository_url}:latest",
      essential = true,
      portMappings = [
        {
          containerPort = 80,
          hostPort      = 80,
          protocol      = "tcp"
        },
        {
          containerPort = 8501,
          hostPort      = 8501,
          protocol      = "tcp"
        }
      ]
    }
  ])
}

# security group for dashboard service
resource "aws_security_group" "ecs_sg" {
  name        = "c22-dashboard-divas-ecs-sg"
  description = "Security group for ECS services"
  vpc_id      = var.vpc_id
    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = 8501
        to_port     = 8501
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

#ecs service for dashboard
resource "aws_ecs_service" "dashboard_service" {
    name            = "c22-dashboard-divas-dashboard-service"
    cluster         = aws_ecs_cluster.dashboard_cluster.id
    task_definition = aws_ecs_task_definition.dashboard-task.arn
    desired_count   = 1
    launch_type     = "FARGATE"
    network_configuration {
        subnets         = var.subnet_ids
        security_groups = [aws_security_group.ecs_sg.id]
        assign_public_ip = true
    }
}

#ecs cluster for dashboard
resource "aws_ecs_cluster" "dashboard_cluster" {
  name = "c22-dashboard-divas-dashboard-cluster"
}


