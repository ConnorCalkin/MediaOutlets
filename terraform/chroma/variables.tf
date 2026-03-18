variable "vpc_id" {
    type = string
    default = "vpc-03f0d39570fbaa750"
}

variable "private_subnet_ids" {
    type = list(string)
    default = [
        "subnet-060cced5eb04380bf",
        "subnet-0fea0e0a59c4a45ad",
        "subnet-03d6ad56638c7aa28"
    ]
}