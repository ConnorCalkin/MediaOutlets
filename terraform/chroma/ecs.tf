resource "aws_ecs_cluster" "chroma" {
    name = "c22-dashboard-divas-chroma-cluster"
}

resource "aws_iam_role" "ecs_execution" {
    name = "c22-dashboard-divas-chroma-ecs-execution-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
        {
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
                Service = "ecs-tasks.amazonaws.com"
            }
        }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
    role       = aws_iam_role.ecs_execution.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "chroma" {
    name              = "/ecs/c22-dashboard-divas-chroma"
    retention_in_days = 7
}

resource "aws_ecs_task_definition" "chroma" {
    family                   = "c22-dashboard-divas-chroma"
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    cpu                      = "1024"
    memory                   = "2048"
    execution_role_arn       = aws_iam_role.ecs_execution.arn

    volume {
        name = "chroma-data"

        efs_volume_configuration {
            file_system_id     = aws_efs_file_system.chroma.id
            transit_encryption = "ENABLED"
            root_directory     = "/"
        }
    }

    container_definitions = jsonencode([
    {
        name      = "chroma"
        image     = "chromadb/chroma:latest"
        essential = true

        portMappings = [
        {
            containerPort = 8000
            hostPort      = 8000
            protocol      = "tcp"
        }
        ]

        environment = [
            { name = "PERSIST_DIRECTORY", value = "/data" }
        ]

        mountPoints = [
        {
            sourceVolume  = "chroma-data"
            containerPath = "/data"
            readOnly      = false
        }
        ]

        logConfiguration = {
            logDriver = "awslogs"
            options = {
                awslogs-group         = aws_cloudwatch_log_group.chroma.name
                awslogs-region        = var.aws_region
                awslogs-stream-prefix = "ecs"
            }
        }
    }
    ])
}

resource "aws_ecs_service" "chroma" {
    name            = "c22-dashboard-divas-chroma-service"
    cluster         = aws_ecs_cluster.chroma.id
    task_definition = aws_ecs_task_definition.chroma.arn
    desired_count   = 0
    launch_type     = "FARGATE"
    platform_version = "1.4.0"

    depends_on = [
        aws_cloudwatch_log_group.chroma
    ]

    network_configuration {
        subnets          = var.public_subnet_ids
        security_groups  = [aws_security_group.chroma_ecs.id]
        assign_public_ip = true
    }
}