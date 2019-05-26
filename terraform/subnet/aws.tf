
provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region = "${var.network.region}"
}

resource "aws_subnet" "network" {
  vpc_id = "${var.network.vpc_id}"
  availability_zone = "${var.zone}"
  cidr_block = "${var.cidr}"
  map_public_ip_on_launch = "${var.use_public_ip}"
  assign_ipv6_address_on_creation = false

  tags = {
    Name = "cenv-network"
  }
}
output "subnet_id" {
  value = "${aws_subnet.network.id}"
}

resource "aws_eip" "nat" {
  count = "${var.use_nat ? 1 : 0}"
  vpc = true
}
resource "aws_nat_gateway" "nat" {
  count = "${var.use_nat ? 1 : 0}"
  allocation_id = "${aws_eip.nat.0.id}"
  subnet_id = "${aws_subnet.network.id}"
}
resource "aws_route_table" "nat" {
  count = "${var.use_nat ? 1 : 0}"
  vpc_id = "${var.network.vpc_id}"
  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = "${aws_nat_gateway.nat.0.id}"
  }
}
output "nat_id" {
  value = "${var.use_nat ? aws_nat_gateway.nat.0.id : null}"
}
output "nat_private_ip" {
  value = "${var.use_nat ? aws_nat_gateway.nat.0.private_ip : null}"
}
output "nat_public_ip" {
  value = "${var.use_nat ? aws_nat_gateway.nat.0.public_ip : null}"
}
output "nat_route_table_id" {
  value = "${var.use_nat ? aws_route_table.nat.0.id : null}"
}

resource "aws_route_table_association" "public" {
  count = "${var.use_public_ip ? 1 : 0}"
  subnet_id = "${aws_subnet.network.id}"
  route_table_id = "${var.network.route_table_id}"
}
resource "aws_route_table_association" "private" {
  count = "${var.use_nat_route_table && !var.use_public_ip ? 1 : 0}"
  subnet_id = "${aws_subnet.network.id}"
  route_table_id = "${var.nat_subnet != null ? var.nat_subnet.nat_route_table_id : null}"
}
