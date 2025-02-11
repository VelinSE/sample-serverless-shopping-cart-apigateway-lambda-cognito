ifndef TEMPLATE
$(error TEMPLATE is undefined. Please specify it, e.g., "make TEMPLATE=shoppingcart-service")
endif

STACK_NAME := aws-serverless-shopping-cart-$(TEMPLATE)
HOST_URL := $(shell awslocal cloudformation describe-stacks \
	--stack-name $(STACK_NAME) \
	--query "Stacks[0].Outputs[0].OutputValue" \
	--output text)
AUTH_USER_POOL_ID := $(shell awslocal cloudformation describe-stacks \
	--stack-name $(STACK_NAME) \
	--query "Stacks[0].Parameters[?ParameterKey=='UserPoolId'].ResolvedValue" \
	--output text)
AUTH_CLIENT_ID := $(shell awslocal cognito-idp list-user-pool-clients \
	--user-pool-id=$(AUTH_USER_POOL_ID) \
	--query "UserPoolClients[0].ClientId" \
	--output text)
AUTH_CLIENT_SECRET := $(shell awslocal cognito-idp describe-user-pool-client \
	--user-pool-id=$(AUTH_USER_POOL_ID) \
	--client-id=$(AUTH_CLIENT_ID) \
	--query "UserPoolClient.ClientSecret" \
	--output text)

load-test: export client_id=$(AUTH_CLIENT_ID)
load-test: export client_secret=$(AUTH_CLIENT_SECRET)

load-test:
	@locust -f $(TEMPLATE) -H $(HOST_URL)