resource "aws_security_group" "chroma_efs" {
    name   = "c22-dashboard-divas-chroma-efs-sg"
    vpc_id = var.vpc_id

    tags = {
        Name = "chroma-efs-sg"
    }
}

resource "aws_security_group" "chroma_ecs" {
    name   = "c22-dashboard-divas-chroma-ecs-sg"
    vpc_id = var.vpc_id

    tags = {
        Name = "c22-dashboard-divas-chroma-ecs-sg"
    }
}

resource "aws_security_group_rule" "efs_ingress" {
    type                     = "ingress"
    from_port                = 2049
    to_port                  = 2049
    protocol                 = "tcp"
    security_group_id        = aws_security_group.chroma_efs.id
    source_security_group_id = aws_security_group.chroma_ecs.id
}

resource "aws_security_group_rule" "chroma_ecs_egress_all" {
    type              = "egress"
    from_port         = 0
    to_port           = 0
    protocol          = "-1"
    security_group_id = aws_security_group.chroma_ecs.id
    cidr_blocks       = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "chroma_ecs_ingress_8000" {
    type              = "ingress"
    from_port         = 8000
    to_port           = 8000
    protocol          = "tcp"
    security_group_id = aws_security_group.chroma_ecs.id
    cidr_blocks       = ["0.0.0.0/0"]
}