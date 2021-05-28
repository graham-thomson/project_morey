#!/bin/bash

VERSION=v0.0.11
APP_NAME="Project Morey"
ENV_NAME="Projectmorey-env"
PROFILE=morey
S3_BUCKET="projectmorey"
ZIP_NAME=dash.zip

black .

zip $ZIP_NAME *.py requirements.txt *.csv

aws s3 cp --profile morey $ZIP_NAME s3://$S3_BUCKET/

aws elasticbeanstalk create-application-version --profile $PROFILE --application-name "${APP_NAME}" --version-label $VERSION --source-bundle S3Bucket=$S3_BUCKET,S3Key="${ZIP_NAME}"

aws elasticbeanstalk update-environment --profile $PROFILE --application-name "${APP_NAME}" --environment-name $ENV_NAME --version-label $VERSION
