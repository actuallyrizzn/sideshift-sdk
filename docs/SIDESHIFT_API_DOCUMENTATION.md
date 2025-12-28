# SideShift.ai REST API V2 - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Rate Limits](#rate-limits)
5. [Terminology](#terminology)
6. [Endpoints](#endpoints)
   - [GET Endpoints](#get-endpoints)
   - [POST Endpoints](#post-endpoints)

---

## Overview

SideShift.ai provides a REST API (V2) that allows you to integrate fast, direct-to-wallet cryptocurrency exchanges into your application. The API supports 200+ assets across multiple networks.

**Important Notes:**
- V1 API is deprecated. Use V2 API for all new integrations.
- V2 API handles multi-network coins more efficiently and uses clearer terminology.
- All amounts are returned as strings to preserve precision.
- The API uses JSON for request and response bodies.

---

## Authentication

### Private Key (x-sideshift-secret)

Most endpoints require authentication using your account's private key, sent in the `x-sideshift-secret` header.

**⚠️ WARNING:** Never share your Private Key with anyone. It grants full access to your account and should be kept secret.

**How to obtain:**
1. Visit https://sideshift.ai/account
2. Copy your **Private Key** (used as `x-sideshift-secret`)
3. Copy your **Account ID** (used as `affiliateId`)

### User IP Header (x-user-ip)

For server-side integrations, you must include the end-user's IP address in the `x-user-ip` header. This is required when API requests are sent from your own server rather than directly from the user's browser.

**Note:** SideShift.ai does not allow proxying user requests. Either:
- Have users directly interact with the SideShift.ai REST API, OR
- If requests are sent from your server, set `x-user-ip` to the end-user's IP address.

---

## Base URL

```
https://sideshift.ai/api/v2
```

---

## Rate Limits

Rate limits are enforced per IP address:

- **Creating Shifts:** Maximum 5 shifts per minute
  - Applies to: `/v2/shifts/fixed` and `/v2/shifts/variable`
- **Creating Quotes:** Maximum 20 quotes per minute
  - Applies to: `/v2/quotes`

**Rate Limit Response:**
- Status Code: `429`
- Message: `Rate limit exceeded`

**Note:** If you've created 5 consecutive variable rate shifts, you'll need to wait for one to expire before creating another, or manually cancel shifts using `/v2/cancel-order`.

---

## Terminology

### Deposit (Source Coin)
- `depositCoin`: Ticker of the coin user is sending (e.g., `btc`)
- `depositNetwork`: Network ID of the deposit coin (e.g., `bitcoin`, `mainnet`)
- `depositAmount`: Amount user needs to deposit
- `depositAddress`: Address user sends funds to
- `depositMemo`: Memo required for some coins (XRP, XLM, ATOM, KAVA)

### Settle (Destination Coin)
- `settleCoin`: Ticker of the coin user will receive (e.g., `eth`)
- `settleNetwork`: Network ID of the settle coin (e.g., `ethereum`, `optimism`)
- `settleAmount`: Amount user will receive
- `settleAddress`: Address where funds will be sent
- `settleMemo`: Memo for coins that require it
- `settleRate`: Exchange rate

### Coin-Network Format
Coins can be specified as:
- `coin-network` (e.g., `btc-bitcoin`, `eth-ethereum`)
- `coin-mainnet` (e.g., `btc-mainnet`, `eth-mainnet`)
- `coin` (defaults to mainnet, e.g., `btc`, `eth`)

For non-native tokens (e.g., USDT, AXS) and multi-network native tokens (e.g., ETH), you must specify the network.

---

## Endpoints

### GET Endpoints

#### 1. Get Coins

**Endpoint:** `GET /coins`

**Description:** Returns the list of coins and their respective networks available on SideShift.ai.

**Authentication:** Not required

**Parameters:** None

**Response Schema:**
```json
[
  {
    "networks": ["string[]"],
    "coin": "string",
    "name": "string",
    "hasMemo": "boolean (deprecated)",
    "fixedOnly": "string[] | boolean",
    "variableOnly": "string[] | boolean",
    "tokenDetails": {
      "network": {
        "contractAddress": "string",
        "decimals": "number"
      }
    },
    "networksWithMemo": ["string[]"],
    "depositOffline": "string[] | boolean",
    "settleOffline": "string[] | boolean"
  }
]
```

**Notes:**
- `fixedOnly`, `variableOnly`, `depositOffline`, `settleOffline` return:
  - `false` if false for every network
  - `true` for single network assets
  - Array of networks for mixed assets

**Status Codes:**
- `200`: OK

---

#### 2. Get Coin Icon

**Endpoint:** `GET /coins/icon/:coin-network`

**Description:** Returns the icon of the coin in SVG or PNG format.

**Authentication:** Not required

**Path Parameters:**
- `coin-network` (string, required): Coin identifier (e.g., `btc-bitcoin`, `btc-mainnet`, `btc`, `btc-liquid`)

**Query Parameters:** None

**Headers:**
- `Accept`: `image/svg+xml` or `image/png` (optional)

**Response:** Image file (SVG or PNG)

**Status Codes:**
- `200`: OK
- `400`: Bad Request

---

#### 3. Get Permissions

**Endpoint:** `GET /permissions`

**Description:** Returns whether or not the user is allowed to create shifts on SideShift.ai.

**Authentication:** Not required (but `x-user-ip` recommended)

**Parameters:** None

**Headers:**
- `x-user-ip` (string, optional): End-user IP address for integrations API requests

**Response Schema:**
```json
{
  "createShift": "boolean"
}
```

**Status Codes:**
- `200`: OK
- `403`: Forbidden

**Notes:**
- SideShift.ai does not allow proxying user requests
- If requests are sent from your server, include `x-user-ip` header

---

#### 4. Get Pair

**Endpoint:** `GET /pair/:from/:to`

**Description:** Returns the minimum and maximum deposit amount and the rate for a pair of coins.

**Authentication:** Required (`x-sideshift-secret`)

**Path Parameters:**
- `from` (string, required): Source coin-network (e.g., `eth-ethereum`, `eth-mainnet`, `eth`)
- `to` (string, required): Destination coin-network

**Query Parameters:**
- `affiliateId` (string, required): Your account ID
- `amount` (number, optional): Deposit value in USD (defaults to 500 USD)
- `commissionRate` (string, optional): Commission rate (use same as when creating shift/quote)

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key

**Response Schema:**
```json
{
  "min": "string",
  "max": "string",
  "rate": "string",
  "depositCoin": "string",
  "settleCoin": "string",
  "depositNetwork": "string",
  "settleNetwork": "string"
}
```

**Notes:**
- Rate is determined after incorporating network fees
- Use the same `commissionRate` as when creating shifts/quotes for accurate rates

**Status Codes:**
- `200`: OK
- `400`: Bad Request
- `500`: Internal Server Error

---

#### 5. Get Pairs

**Endpoint:** `GET /pairs`

**Description:** Returns the minimum and maximum deposit amount and the rate for every possible pair of coins listed in the query string.

**Authentication:** Required (`x-sideshift-secret`)

**Query Parameters:**
- `pairs` (string, required): Comma-separated list of coins (e.g., `btc-mainnet,usdc-bsc,bch,eth`)
- `affiliateId` (string, required): Your account ID
- `commissionRate` (string, optional): Commission rate

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key

**Response Schema:**
```json
[
  {
    "depositCoin": "string",
    "settleCoin": "string",
    "depositNetwork": "string",
    "settleNetwork": "string",
    "min": "string",
    "max": "string",
    "rate": "string"
  }
]
```

**Status Codes:**
- `200`: OK
- `500`: Internal Server Error

---

#### 6. Get Shift

**Endpoint:** `GET /shifts/:shiftId`

**Description:** Returns the shift data for a single shift. For bulk retrieval, use `/v2/shifts?ids=shiftId1,shiftId2`.

**Authentication:** Not required

**Path Parameters:**
- `shiftId` (string, required): Unique shift identifier

**Response Schema:**
The response schema varies based on shift type (Fixed/Variable) and whether there are multiple deposits. See examples in the API docs.

**Key Fields:**
- `id`: Shift ID
- `type`: `"fixed"` or `"variable"`
- `status`: Shift status
- `depositCoin`, `depositNetwork`, `depositAmount`, `depositAddress`, `depositMemo`
- `settleCoin`, `settleNetwork`, `settleAmount`, `settleAddress`, `settleMemo`
- `deposits`: Array of deposits (for multiple deposits)
- `createdAt`, `expiresAt`
- `rate`, `averageShiftSeconds`

**Notes:**
- For shifts with `multiple` status, the `deposits` array holds all deposits
- **Fixed Shifts:** Multiple deposits shown, but only first is settled; subsequent are refunded
- **Variable Shifts:** Multiple deposits processed individually
- `depositAddress` is unassigned after 60 days (40 days for EVM tokens). Once unassigned, field becomes `null` and address may be assigned to other shifts. **Persist the value when shift is created.**

**Status Codes:**
- `200`: OK
- `404`: Not Found

---

#### 7. Get Bulk Shifts

**Endpoint:** `GET /shifts`

**Description:** Returns the shift data for every `shiftId` listed in the query string.

**Authentication:** Not required

**Query Parameters:**
- `ids` (string, required): Comma-separated list of shift IDs (e.g., `f173118220f1461841da,dda3867168da23927b62`)

**Response Schema:**
Array of shift objects (same schema as Get Shift)

**Notes:**
- Same `depositAddress` expiration rules apply (60 days, 40 days for EVM tokens)

**Status Codes:**
- `200`: OK
- `404`: Not Found

---

#### 8. Get Recent Shifts

**Endpoint:** `GET /recent-shifts`

**Description:** Returns the most recent completed shifts.

**Authentication:** Not required

**Query Parameters:**
- `limit` (number, optional): Number of recent shifts to return (1-100, default: 10)

**Response Schema:**
```json
[
  {
    "createdAt": "string",
    "depositCoin": "string",
    "depositNetwork": "string",
    "depositAmount": "string",
    "settleCoin": "string",
    "settleNetwork": "string",
    "settleAmount": "string"
  }
]
```

**Notes:**
- To preserve user privacy, shifts involving privacy coins return `null` for both deposit and settle amounts

**Status Codes:**
- `200`: OK

---

#### 9. Get XAI Stats

**Endpoint:** `GET /xai/stats`

**Description:** Returns statistics about XAI coin, including its current USD price.

**Authentication:** Not required

**Parameters:** None

**Response Schema:**
```json
{
  "totalSupply": "number",
  "circulatingSupply": "number",
  "numberOfStakers": "number",
  "latestAnnualPercentageYield": "string",
  "latestDistributedXai": "string",
  "totalStaked": "string",
  "averageAnnualPercentageYield": "string",
  "totalValueLocked": "string",
  "totalValueLockedRatio": "string",
  "xaiPriceUsd": "string",
  "svxaiPriceUsd": "string",
  "svxaiPriceXai": "string"
}
```

**Status Codes:**
- `200`: OK

---

#### 10. Get Account

**Endpoint:** `GET /account`

**Description:** Returns data related to an account.

**Authentication:** Required (`x-sideshift-secret`)

**Parameters:** None

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key

**Response Schema:**
```json
{
  "id": "string",
  "lifetimeStakingRewards": "string",
  "unstaking": "string",
  "staked": "string",
  "available": "string",
  "totalBalance": "string"
}
```

**Status Codes:**
- `200`: OK
- `401`: Unauthorized
- `404`: Not Found

---

#### 11. Get Checkout

**Endpoint:** `GET /checkout/:checkoutId`

**Description:** Returns the data of a checkout created using `/v2/checkout` endpoint.

**Authentication:** Not required

**Path Parameters:**
- `checkoutId` (string, required): Unique checkout identifier

**Response Schema:**
```json
{
  "id": "string",
  "settleCoin": "string",
  "settleNetwork": "string",
  "settleAddress": "string",
  "settleMemo": "string",
  "settleAmount": "string",
  "updatedAt": "date-time",
  "createdAt": "date-time",
  "affiliateId": "string",
  "successUrl": "string",
  "cancelUrl": "string",
  "orders": [
    {
      "id": "string",
      "deposits": [
        {
          "depositHash": "string",
          "settleHash": "string"
        }
      ]
    }
  ]
}
```

**Status Codes:**
- `200`: OK
- `404`: Not Found

---

### POST Endpoints

#### 12. Request Quote

**Endpoint:** `POST /quotes`

**Description:** For fixed rate shifts, a quote should be requested first. A quote can be requested for either a `depositAmount` or a `settleAmount`.

**Authentication:** Required (`x-sideshift-secret`)

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key
- `x-user-ip` (string, optional): End-user IP address for integrations API requests

**Body Parameters:**
```json
{
  "depositCoin": "string (required)",
  "depositNetwork": "string (required for non-native tokens and multi-network native tokens)",
  "settleCoin": "string (required)",
  "settleNetwork": "string (required for non-native tokens and multi-network native tokens)",
  "depositAmount": "string (nullable, required if settleAmount is null)",
  "settleAmount": "string (nullable, required if depositAmount is null)",
  "affiliateId": "string (required)",
  "commissionRate": "string (optional)"
}
```

**Response Schema:**
```json
{
  "id": "string",
  "createdAt": "string",
  "depositCoin": "string",
  "settleCoin": "string",
  "depositNetwork": "string",
  "settleNetwork": "string",
  "expiresAt": "string",
  "depositAmount": "string",
  "settleAmount": "string",
  "rate": "string",
  "affiliateId": "string"
}
```

**Notes:**
- When defining non-native tokens (e.g., AXS, USDT) or multi-network native tokens (e.g., ETH), `depositNetwork` and `settleNetwork` must be specified
- `commissionRate` is optional (default: 0.5%, max: 2%)
- Use the same `commissionRate` in `/v2/pair` and `/v2/pairs` endpoints for accurate rate information
- If API requests are sent from your server, `x-user-ip` header must be set
- Quote expires after **15 minutes**
- Save the returned `id` as `quoteId` for creating a fixed shift

**Status Codes:**
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

#### 13. Create Fixed Shift

**Endpoint:** `POST /shifts/fixed`

**Description:** After requesting a quote, use the `quoteId` to create a fixed rate shift. The `affiliateId` must match the one used to request the quote.

**Authentication:** Required (`x-sideshift-secret`)

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key
- `x-user-ip` (string, optional): End-user IP address for integrations API requests

**Body Parameters:**
```json
{
  "settleAddress": "string (required)",
  "settleMemo": "string (optional, for coins where network is included in networksWithMemo array)",
  "affiliateId": "string (required, must match quote affiliateId)",
  "quoteId": "string (required)",
  "refundAddress": "string (optional)",
  "refundMemo": "string (optional)",
  "externalId": "string (optional, integration's own ID)"
}
```

**Response Schema:**
```json
{
  "id": "string",
  "createdAt": "string",
  "depositCoin": "string",
  "settleCoin": "string",
  "depositNetwork": "string",
  "settleNetwork": "string",
  "depositAddress": "string",
  "depositMemo": "string",
  "settleAddress": "string",
  "settleMemo": "string",
  "depositMin": "string",
  "depositMax": "string",
  "refundAddress": "string",
  "refundMemo": "string",
  "type": "string",
  "quoteId": "string",
  "depositAmount": "string",
  "settleAmount": "string",
  "expiresAt": "string",
  "status": "string",
  "averageShiftSeconds": "string",
  "externalId": "string",
  "rate": "string"
}
```

**Notes:**
- For fixed rate shifts, deposit of exactly `depositAmount` must be made before `expiresAt` timestamp, otherwise deposit will be refunded
- If `depositMemo` is returned, deposit transaction must include this memo, otherwise deposit might be lost
- For shifts settling in coins where network is in `networksWithMemo` array, you can specify `settleMemo`
- `refundAddress` and `refundMemo` are optional. If not defined, user is prompted to enter refund address manually on SideShift.ai order page if shift needs to be refunded
- If API requests are sent from your server, `x-user-ip` header must be set
- `averageShiftSeconds` represents average time in seconds for SideShift to process a shift once user's deposit is **confirmed** on the blockchain
- `externalId` is optional field for integration's own ID
- Display `depositAddress` to user and poll `/v2/shifts/{shiftId}` to monitor shift status

**Status Codes:**
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

#### 14. Create Variable Shift

**Endpoint:** `POST /shifts/variable`

**Description:** Creates a variable rate shift. Variable shifts don't require a quote.

**Authentication:** Required (`x-sideshift-secret`)

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key
- `x-user-ip` (string, optional): End-user IP address for integrations API requests

**Body Parameters:**
```json
{
  "depositCoin": "string (required)",
  "depositNetwork": "string (required for non-native tokens and multi-network native tokens)",
  "settleCoin": "string (required)",
  "settleNetwork": "string (required for non-native tokens and multi-network native tokens)",
  "settleAddress": "string (required)",
  "settleMemo": "string (optional, for coins where network is included in networksWithMemo array)",
  "affiliateId": "string (required)",
  "refundAddress": "string (optional)",
  "refundMemo": "string (optional)",
  "externalId": "string (optional, integration's own ID)"
}
```

**Response Schema:**
Similar to Create Fixed Shift response, but without `quoteId`, `depositAmount`, `settleAmount`, and `expiresAt` fields.

**Notes:**
- Variable shifts use current market rates at the time of deposit confirmation
- Same notes about `depositMemo`, `settleMemo`, `refundAddress`, `refundMemo`, `x-user-ip`, `averageShiftSeconds`, and `externalId` apply as in Create Fixed Shift
- Display `depositAddress` to user and poll `/v2/shifts/{shiftId}` to monitor shift status

**Status Codes:**
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

#### 15. Set Refund Address

**Endpoint:** `POST /shifts/:shiftId/set-refund-address`

**Description:** Sets or updates the refund address for an existing shift.

**Authentication:** Required (`x-sideshift-secret`)

**Path Parameters:**
- `shiftId` (string, required): Unique shift identifier

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key

**Body Parameters:**
```json
{
  "address": "string (required)",
  "memo": "string (optional, for addresses that require memo)"
}
```

**Response Schema:**
Returns the updated shift object (Fixed or Variable shift schema).

**Status Codes:**
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

---

#### 16. Cancel Order

**Endpoint:** `POST /cancel-order`

**Description:** Cancels an existing order after 5 minutes by expiring it.

**Authentication:** Required (`x-sideshift-secret`)

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key

**Body Parameters:**
```json
{
  "orderId": "string (required)"
}
```

**Response:** No content

**Status Codes:**
- `204`: No Content (Order successfully cancelled)
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

---

#### 17. Create Checkout

**Endpoint:** `POST /checkout`

**Description:** Creates a new checkout that can be used to facilitate payment for merchants. See the SideShift Pay integration guide for end-to-end instructions, webhook setup, and sample code.

**Authentication:** Required (`x-sideshift-secret`)

**Headers:**
- `x-sideshift-secret` (string, required): Your account private key
- `x-user-ip` (string, required): End-user IP address for integrations API requests

**Body Parameters:**
```json
{
  "settleCoin": "string (required)",
  "settleNetwork": "string (required)",
  "settleAmount": "string (required)",
  "settleAddress": "string (required)",
  "settleMemo": "string (optional, for coins where network is included in networksWithMemo array)",
  "affiliateId": "string (required)",
  "successUrl": "string (required)",
  "cancelUrl": "string (required)"
}
```

**Response Schema:**
```json
{
  "id": "string",
  "settleCoin": "string",
  "settleNetwork": "string",
  "settleAddress": "string",
  "settleMemo": "string",
  "settleAmount": "string",
  "updatedAt": "date-time",
  "createdAt": "date-time",
  "affiliateId": "string",
  "successUrl": "string",
  "cancelUrl": "string"
}
```

**Status Codes:**
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

---

## Common Response Status Codes

- `200`: OK - Request successful
- `201`: Created - Resource created successfully
- `204`: No Content - Request successful, no content to return
- `400`: Bad Request - Invalid request parameters
- `401`: Unauthorized - Authentication required or invalid
- `403`: Forbidden - Access denied
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

---

## Important Implementation Notes

### Deposit Address Expiration
- `depositAddress` is unassigned from a shift after:
  - **60 days** for most coins
  - **40 days** for EVM token deposit addresses
- Once unassigned, the field becomes `null` and the address may be assigned to other shifts
- **Always persist the `depositAddress` value when the shift is created** if you need to show it later
- **Never send funds to addresses from expired shifts**

### Multiple Deposits
- For shifts with `multiple` status, the `deposits` array contains all deposits
- **Fixed Shifts:** Multiple deposits shown, but only first deposit is settled; subsequent deposits are refunded
- **Variable Shifts:** Multiple deposits are processed individually according to current market rates
- It is not desirable for users to make multiple deposits to the same shift

### Quote Expiration
- Quotes expire after **15 minutes**
- Create the fixed shift using the `quoteId` before it expires

### Commission Rates
- Default commission rate: 0.5%
- Maximum commission rate: 2%
- Use the same `commissionRate` in `/v2/pair`, `/v2/pairs`, and when creating shifts/quotes for accurate rate information
- Rates below default offer better rates by reducing affiliate commission
- Rates above default are passed on to the user

### Memo Fields
- Some coins require memos (XRP, XLM, ATOM, KAVA, ALGO)
- Check `networksWithMemo` array in `/v2/coins` endpoint
- If `depositMemo` is returned, it must be included in the deposit transaction
- `settleMemo` can be specified for coins that require it

### Polling for Shift Status
- After creating a shift, poll `/v2/shifts/{shiftId}` to monitor status
- `averageShiftSeconds` represents average processing time after deposit is **confirmed** on blockchain

---

## Error Handling

When errors occur, the API returns appropriate HTTP status codes. Common error scenarios:

1. **Invalid Authentication:** `401 Unauthorized`
2. **Rate Limit Exceeded:** `429 Too Many Requests`
3. **Invalid Parameters:** `400 Bad Request`
4. **Resource Not Found:** `404 Not Found`
5. **Server Error:** `500 Internal Server Error`

Always check the response status code and handle errors appropriately in your application.

---

## Additional Resources

- **Account Page:** https://sideshift.ai/account
- **Developer Chat:** https://t.me/joinchat/UuTn4HeK-2EUG1zZ
- **GitHub:** https://github.com/sideshift
- **Postman Collection:** https://www.postman.com/speeding-resonance-938720/sideshift-ai-public/collection/pwxl06f/sideshift-ai-rest-api
- **SideShift Pay Integration Guide:** See `/sideshift-pay-integration` in docs

---

## Document Version

This document was generated from the SideShift.ai API documentation on December 28, 2024, covering all V2 API endpoints as of that date.

## Verification Status

✅ **100% Complete** - All 17 V2 API endpoints documented:
- 11 GET endpoints
- 6 POST endpoints

**Verified Against:**
- Official SideShift.ai documentation sidebar navigation
- Individual endpoint documentation pages
- Postman collection (available at link above)

**Note:** V1 API endpoints are deprecated and not included in this documentation. The web search results mentioning additional endpoints (affiliate, assets, networks, methods) are from the deprecated V1 API or internal/admin endpoints not available in the public V2 API documentation.

