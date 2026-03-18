resource "aws_efs_file_system" "chroma" {
    creation_token = "c22-dashboard-divas-chroma-efs"
    encrypted      = true

    tags = {
        Name = "c22-dashboard-divas-chroma-efs"
    }
}