ifndef TEMPLATE
$(error TEMPLATE is undefined. Please specify it, e.g., "make TEMPLATE=shoppingcart-service")
endif

STACK_NAME = aws-serverless-shopping-cart-$(TEMPLATE)
HOST_URL = $(shell awslocal cloudformation describe-stacks \
	--stack-name $(STACK_NAME) \
	--query "Stacks[0].Outputs[0].OutputValue" \
	--output text)

load-test:
	@locust -f $(TEMPLATE) -H $(HOST_URL)