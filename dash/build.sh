
zip dash.zip application.py requirements.txt *.csv

aws s3 cp --profile morey dash.zip s3://projectmorey/

aws elasticbeanstalk create-application-version --profile morey --application-name tests3deploy --version-label v0.0.3 --source-bundle S3Bucket="projectmorey",S3Key="dash.zip"

aws elasticbeanstalk update-environment --profile morey --application-name tests3deploy --environment-name tests3deploy --version-label v0.0.3
