import {
  to = module.compute.aws_iam_role.ssm
  id = "coderhouse-ec2-ssm"
}

import {
  to = module.compute.aws_iam_instance_profile.ssm
  id = "coderhouse-ec2-ssm"
}

import {
  to = module.compute.aws_iam_role_policy_attachment.ssm
  id = "coderhouse-ec2-ssm/arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
