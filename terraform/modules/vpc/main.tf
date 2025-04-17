resource "aws_vpc" "this" {
  cidr_block           = var.cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support
  
  tags = merge(
    {
      "Name" = var.name
    },
    var.tags
  )
}

resource "aws_subnet" "public" {
  count = length(var.public_subnets)

  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnets[count.index]
  availability_zone       = element(var.azs, count.index)
  map_public_ip_on_launch = true
  
  tags = merge(
    {
      "Name" = format(
        "${var.name}-public-%s",
        element(var.azs, count.index),
      )
    },
    var.public_subnet_tags
  )
}

resource "aws_subnet" "private" {
  count = length(var.private_subnets)

  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnets[count.index]
  availability_zone = element(var.azs, count.index)
  
  tags = merge(
    {
      "Name" = format(
        "${var.name}-private-%s",
        element(var.azs, count.index),
      )
    },
    var.private_subnet_tags
  )
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  
  tags = merge(
    {
      "Name" = var.name
    },
    var.tags
  )
}

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.azs)) : 0
  
  domain = "vpc"
  
  tags = merge(
    {
      "Name" = format(
        "${var.name}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags
  )
}

resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.azs)) : 0

  allocation_id = element(aws_eip.nat.*.id, count.index)
  subnet_id     = element(aws_subnet.public.*.id, count.index)
  
  tags = merge(
    {
      "Name" = format(
        "${var.name}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags
  )

  depends_on = [aws_internet_gateway.this]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  
  tags = merge(
    {
      "Name" = "${var.name}-public"
    },
    var.tags
  )
}

resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

resource "aws_route_table" "private" {
  count = length(var.private_subnets) > 0 ? (var.single_nat_gateway ? 1 : length(var.azs)) : 0

  vpc_id = aws_vpc.this.id
  
  tags = merge(
    {
      "Name" = var.single_nat_gateway ? "${var.name}-private" : format(
        "${var.name}-private-%s",
        element(var.azs, count.index),
      )
    },
    var.tags
  )
}

resource "aws_route" "private_nat_gateway" {
  count = var.enable_nat_gateway ? length(aws_route_table.private) : 0

  route_table_id         = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = element(aws_nat_gateway.this.*.id, var.single_nat_gateway ? 0 : count.index)
}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnets)

  subnet_id      = element(aws_subnet.public.*.id, count.index)
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnets)

  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = element(
    aws_route_table.private.*.id,
    var.single_nat_gateway ? 0 : count.index,
  )
}

# Flow logs
resource "aws_flow_log" "this" {
  count = var.enable_flow_log ? 1 : 0

  log_destination      = var.flow_log_destination_arn
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.this.id
  
  tags = merge(
    {
      "Name" = "${var.name}-flow-logs"
    },
    var.tags
  )
}