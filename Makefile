all: backend frontend-build

TEMPLATES = auth product-mock shoppingcart-service
REGION := us-east-1
# REGION := $(shell python3 -c 'import boto3; print(boto3.Session().region_name)')
ifndef S3_BUCKET
ACCOUNT_ID := 000000000000
# ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)
S3_BUCKET = aws-serverless-shopping-cart-src-$(ACCOUNT_ID)-$(REGION)
endif

# awslocal s3 mb s3://aws-serverless-shopping-cart-src-000000000000-us-east-1 --region us-east-1

backend: create-bucket
	$(MAKE) -C backend TEMPLATE=auth S3_BUCKET=$(S3_BUCKET) REGION=${REGION}
	$(MAKE) -C backend TEMPLATE=product-mock S3_BUCKET=$(S3_BUCKET) REGION=${REGION}
	$(MAKE) -C backend TEMPLATE=shoppingcart-service S3_BUCKET=$(S3_BUCKET) REGION=${REGION}

backend-delete:
	$(MAKE) -C backend delete TEMPLATE=auth REGION=${REGION}
	$(MAKE) -C backend delete TEMPLATE=product-mock REGION=${REGION}
	$(MAKE) -C backend delete TEMPLATE=shoppingcart-service REGION=${REGION}

backend-tests:
	$(MAKE) -C backend tests

load-tests:
	$(MAKE) -C test load-test TEMPLATE=shoppingcart-service

create-bucket:
	@echo "Checking if S3 bucket exists s3://$(S3_BUCKET)"
	@awslocal s3api head-bucket --bucket $(S3_BUCKET) || (echo "bucket does not exist at s3://$(S3_BUCKET), creating it..."; $(shell awslocal s3 mb s3://$(S3_BUCKET) --region $(REGION)))

amplify-deploy:
	aws cloudformation deploy \
		--template-file ./amplify-ci/amplify-template.yaml \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			OauthToken=$(GITHUB_OAUTH_TOKEN) \
			Repository=$(GITHUB_REPO) \
			BranchName=$(GITHUB_BRANCH) \
			SrcS3Bucket=$(S3_BUCKET) \
		--stack-name CartApp

frontend-serve: 
	$(MAKE) -C frontend serve

frontend-build: 
	$(MAKE) -C frontend build

create-volume:
	@docker volume inspect clickhouse-data > NUL 2>&1 || docker volume create clickhouse-data

localstack: create-volume
	@docker compose -f deployment/docker-compose.yml up

localstack-stop:
	@docker compose -f deployment/docker-compose.yml stop

.PHONY: all backend backend-delete backend-tests create-bucket amplify-deploy frontend-serve frontend-build create-volume localstack localstack-stop
