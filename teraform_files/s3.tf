resource "aws_s3_bucket" "covid_raw" {
  bucket = "covid-raw-data-270524" 
}

resource "aws_s3_bucket_ownership_controls" "covid_raw" {
  bucket = aws_s3_bucket.covid_raw.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "covid_raw" {
  depends_on = [aws_s3_bucket_ownership_controls.covid_raw]
  bucket     = aws_s3_bucket.covid_raw.id
  acl        = "private"
}