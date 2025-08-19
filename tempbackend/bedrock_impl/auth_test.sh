USER_POOL_CLIENT_ID="4bn7v978lsk24u3uuai3mrlsfp"
USERNAME=""
PASSWORD=""
API_URL="https://gc6p3xa5c7.execute-api.us-east-1.amazonaws.com/Prod/rag/bedrock"

ACCESS_TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id "$USER_POOL_CLIENT_ID" \
  --auth-parameters USERNAME="$USERNAME",PASSWORD="$PASSWORD" \
  --query 'AuthenticationResult.IdToken' \
  --output text)

echo $ACCESS_TOKEN

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: $ACCESS_TOKEN" \
  -d '{"query": "Can I filter the API response?"}'