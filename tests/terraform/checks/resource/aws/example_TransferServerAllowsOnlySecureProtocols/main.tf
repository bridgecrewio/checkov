# pass
resource "aws_transfer_server" "stfp" {
  protocols = ["SFTP"]
}


# pass
resource "aws_transfer_server" "default" {
}


# fail
resource "aws_transfer_server" "ftp" {
  protocols = ["FTP", "FTPS"]
}