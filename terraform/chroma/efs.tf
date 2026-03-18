resource "aws_efs_file_system" "chroma" {
    creation_token = "c22-dashboard-divas-chroma-efs"
    encrypted      = true

    tags = {
        Name = "c22-dashboard-divas-chroma-efs"
    }
}

resource "aws_efs_mount_target" "chroma" {
    for_each = toset(var.private_subnet_ids)

    file_system_id  = aws_efs_file_system.chroma.id
    subnet_id       = each.value
    security_groups = [aws_security_group.chroma_efs.id]
}