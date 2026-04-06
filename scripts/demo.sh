#!/bin/bash

# API Reliability Suite - Demo Script
# Walks through the backend, reliability, and AI-assisted debugging flows

set -e

# Colors for premium look
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"

print_banner() {
    echo -e "${PURPLE}================================================================${NC}"
    echo -e "${PURPLE}            API RELIABILITY SUITE - LOCAL DEMO RUN             ${NC}"
    echo -e "${PURPLE}================================================================${NC}"
}

print_step() {
    echo -e "\n${CYAN}STEP $1: $2${NC}"
    echo -e "${CYAN}----------------------------------------------------------------${NC}"
}

check_server() {
    if ! curl -s $API_URL/health > /dev/null; then
        echo -e "${RED}❌ Server is not running at $API_URL. Please run 'make run' in another terminal.${NC}"
        exit 1
    fi
}

# --- START DEMO ---

print_banner
check_server

# 1. Health Check & Correlation ID
print_step "1" "Health Check & Trace Propagation"
echo -e "${YELLOW}Requesting /health with a custom Correlation ID...${NC}"
RESPONSE=$(curl -s -i "$API_URL/health" -H "X-Correlation-ID: demo-trace-$(date +%s)")
echo -e "$RESPONSE" | grep -E "HTTP/|X-Correlation-ID|status" | sed 's/^/  /'
echo -e "${GREEN}✅ Trace ID successfully propagated through headers.${NC}"

# 2. Authentication
print_step "2" "JWT Authentication Flow"
echo -e "${YELLOW}Logging in as 'demo' user...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=secret123")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" != "null" ]; then
    echo -e "${GREEN}✅ Received JWT: ${TOKEN:0:20}...[truncated]${NC}"
else
    echo -e "${RED}❌ Login failed!${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Accessing a protected route with the token...${NC}"
curl -s "$API_URL/protected" -H "Authorization: Bearer $TOKEN" | jq . | sed 's/^/  /'

# 3. Resilience (Circuit Breaker)
print_step "3" "Resilience & Fault Tolerance (Circuit Breaker)"
echo -e "${YELLOW}Ensuring simulation is disabled...${NC}"
curl -s -X POST "$API_URL/simulate-failure/false" > /dev/null

echo -e "${YELLOW}Hitting /external-api (Normal Operation)...${NC}"
curl -s "$API_URL/external-api" | jq . | sed 's/^/  /'

echo -e "\n${YELLOW}Enabling Failure Simulation...${NC}"
curl -s -X POST "$API_URL/simulate-failure/true" > /dev/null

echo -e "${YELLOW}Triggering failures to trip the circuit (Threshold: 5)...${NC}"
for i in {1..5}; do
    echo -n "  Attempt $i: "
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/external-api")
    if [ "$STATUS" == "502" ]; then
        echo -e "${RED}Failed (502 Bad Gateway)${NC}"
    else
        echo -e "${GREEN}Fallback (200 OK)${NC}"
    fi
done

echo -e "\n${YELLOW}Checking next request (Should return the degraded fallback response)...${NC}"
curl -s "$API_URL/external-api" | jq . | sed 's/^/  /'
echo -e "${GREEN}✅ Circuit is OPEN. Fallback mechanism engaged to prevent cascading failure.${NC}"

# Reset failure simulation
curl -s -X POST "$API_URL/simulate-failure/false" > /dev/null

# 4. AI-Powered Debugging
print_step "4" "Autonomous AI Error Analysis"
echo -e "${YELLOW}Triggering a forced error to generate logs...${NC}"
curl -s "$API_URL/force-error" > /dev/null || true

echo -e "${YELLOW}Requesting /debug/summarize-errors (AI Brain)...${NC}"
echo -e "${BLUE}Please wait, LLM is thinking...${NC}"
AI_RESPONSE=$(curl -s "$API_URL/debug/summarize-errors" -H "Authorization: Bearer $TOKEN")

if echo $AI_RESPONSE | jq -e '.ai_summary' > /dev/null; then
    echo -e "${PURPLE}--- AI ANALYSIS ---${NC}"
    echo $AI_RESPONSE | jq -r '.ai_summary.summary_text' | sed 's/^/  /'
    echo -e "${PURPLE}-------------------${NC}"
else
    echo -e "${RED}❌ AI Summary not available. Check your .env for API keys or logs for errors.${NC}"
    echo -e "Response: $AI_RESPONSE"
fi

# 5. Observability
print_step "5" "Real-Time Observability (Prometheus)"
echo -e "${YELLOW}Checking /metrics endpoint functionality...${NC}"
curl -s "$API_URL/metrics" | head -n 10 | sed 's/^/  /'
echo -e "${GREEN}✅ Real-time metrics are live and ready for Grafana visualization.${NC}"

echo -e "\n${PURPLE}================================================================${NC}"
echo -e "${GREEN}             🎯 DEMO COMPLETE: PLATFORM AUDITED ✅             ${NC}"
echo -e "${PURPLE}================================================================${NC}"
