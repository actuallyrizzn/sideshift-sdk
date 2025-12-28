"""Pydantic models for SideShift API responses and requests."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================================
# Coin Models
# ============================================================================


class TokenNetworkDetails(BaseModel):
    """Token network details."""

    contract_address: str = Field(..., alias="contractAddress")
    decimals: int


class NetworkTokenDetails(BaseModel):
    """Network token details."""

    network: TokenNetworkDetails


class Coin(BaseModel):
    """Coin information from GET /coins."""

    networks: list[str]
    coin: str
    name: str
    has_memo: bool = Field(..., alias="hasMemo")  # deprecated
    fixed_only: list[str] | bool = Field(..., alias="fixedOnly")
    variable_only: list[str] | bool = Field(..., alias="variableOnly")
    token_details: dict[str, NetworkTokenDetails] | None = Field(None, alias="tokenDetails")
    networks_with_memo: list[str] = Field(..., alias="networksWithMemo")
    deposit_offline: list[str] | bool | None = Field(None, alias="depositOffline")
    settle_offline: list[str] | bool | None = Field(None, alias="settleOffline")

    class Config:
        populate_by_name = True


# ============================================================================
# Pair Models
# ============================================================================


class PairInfo(BaseModel):
    """Pair information from GET /pair or GET /pairs."""

    min: str
    max: str
    rate: str
    deposit_coin: str = Field(..., alias="depositCoin")
    settle_coin: str = Field(..., alias="settleCoin")
    deposit_network: str = Field(..., alias="depositNetwork")
    settle_network: str = Field(..., alias="settleNetwork")

    class Config:
        populate_by_name = True


# ============================================================================
# Quote Models
# ============================================================================


class QuoteRequest(BaseModel):
    """Request model for POST /quotes."""

    deposit_coin: str = Field(..., alias="depositCoin")
    deposit_network: str | None = Field(None, alias="depositNetwork")
    settle_coin: str = Field(..., alias="settleCoin")
    settle_network: str | None = Field(None, alias="settleNetwork")
    deposit_amount: str | None = Field(None, alias="depositAmount")
    settle_amount: str | None = Field(None, alias="settleAmount")
    affiliate_id: str = Field(..., alias="affiliateId")
    commission_rate: str | None = Field(None, alias="commissionRate")

    class Config:
        populate_by_name = True


class Quote(BaseModel):
    """Quote response from POST /quotes."""

    id: str
    created_at: str = Field(..., alias="createdAt")
    deposit_coin: str = Field(..., alias="depositCoin")
    settle_coin: str = Field(..., alias="settleCoin")
    deposit_network: str = Field(..., alias="depositNetwork")
    settle_network: str = Field(..., alias="settleNetwork")
    expires_at: str = Field(..., alias="expiresAt")
    deposit_amount: str = Field(..., alias="depositAmount")
    settle_amount: str = Field(..., alias="settleAmount")
    rate: str
    affiliate_id: str | None = Field(None, alias="affiliateId")

    class Config:
        populate_by_name = True


# ============================================================================
# Shift Models
# ============================================================================


class DepositInfo(BaseModel):
    """Deposit information in a shift."""

    deposit_hash: str | None = Field(None, alias="depositHash")
    settle_hash: str | None = Field(None, alias="settleHash")
    deposit_amount: str | None = Field(None, alias="depositAmount")
    settle_amount: str | None = Field(None, alias="settleAmount")

    class Config:
        populate_by_name = True


class FixedShiftRequest(BaseModel):
    """Request model for POST /shifts/fixed."""

    settle_address: str = Field(..., alias="settleAddress")
    settle_memo: str | None = Field(None, alias="settleMemo")
    affiliate_id: str = Field(..., alias="affiliateId")
    quote_id: str = Field(..., alias="quoteId")
    refund_address: str | None = Field(None, alias="refundAddress")
    refund_memo: str | None = Field(None, alias="refundMemo")
    external_id: str | None = Field(None, alias="externalId")

    class Config:
        populate_by_name = True


class VariableShiftRequest(BaseModel):
    """Request model for POST /shifts/variable."""

    deposit_coin: str = Field(..., alias="depositCoin")
    deposit_network: str | None = Field(None, alias="depositNetwork")
    settle_coin: str = Field(..., alias="settleCoin")
    settle_network: str | None = Field(None, alias="settleNetwork")
    settle_address: str = Field(..., alias="settleAddress")
    settle_memo: str | None = Field(None, alias="settleMemo")
    affiliate_id: str = Field(..., alias="affiliateId")
    refund_address: str | None = Field(None, alias="refundAddress")
    refund_memo: str | None = Field(None, alias="refundMemo")
    external_id: str | None = Field(None, alias="externalId")

    class Config:
        populate_by_name = True


class SetRefundAddressRequest(BaseModel):
    """Request model for POST /shifts/:shiftId/set-refund-address."""

    address: str
    memo: str | None = None


class Shift(BaseModel):
    """Shift information from GET /shifts/:shiftId or POST /shifts/fixed or POST /shifts/variable."""

    id: str
    created_at: str = Field(..., alias="createdAt")
    deposit_coin: str = Field(..., alias="depositCoin")
    settle_coin: str = Field(..., alias="settleCoin")
    deposit_network: str = Field(..., alias="depositNetwork")
    settle_network: str = Field(..., alias="settleNetwork")
    deposit_address: str | None = Field(None, alias="depositAddress")
    deposit_memo: str | None = Field(None, alias="depositMemo")
    settle_address: str = Field(..., alias="settleAddress")
    settle_memo: str | None = Field(None, alias="settleMemo")
    deposit_min: str | None = Field(None, alias="depositMin")
    deposit_max: str | None = Field(None, alias="depositMax")
    refund_address: str | None = Field(None, alias="refundAddress")
    refund_memo: str | None = Field(None, alias="refundMemo")
    type: Literal["fixed", "variable"]
    quote_id: str | None = Field(None, alias="quoteId")
    deposit_amount: str | None = Field(None, alias="depositAmount")
    settle_amount: str | None = Field(None, alias="settleAmount")
    expires_at: str | None = Field(None, alias="expiresAt")
    status: str
    average_shift_seconds: str | None = Field(None, alias="averageShiftSeconds")
    external_id: str | None = Field(None, alias="externalId")
    rate: str | None = None
    deposits: list[DepositInfo] | None = None

    class Config:
        populate_by_name = True


class RecentShift(BaseModel):
    """Recent shift information from GET /recent-shifts."""

    created_at: str = Field(..., alias="createdAt")
    deposit_coin: str = Field(..., alias="depositCoin")
    deposit_network: str = Field(..., alias="depositNetwork")
    deposit_amount: str | None = Field(None, alias="depositAmount")
    settle_coin: str = Field(..., alias="settleCoin")
    settle_network: str = Field(..., alias="settleNetwork")
    settle_amount: str | None = Field(None, alias="settleAmount")

    class Config:
        populate_by_name = True


class CancelOrderRequest(BaseModel):
    """Request model for POST /cancel-order."""

    order_id: str = Field(..., alias="orderId")

    class Config:
        populate_by_name = True


# ============================================================================
# Account Models
# ============================================================================


class Account(BaseModel):
    """Account information from GET /account."""

    id: str
    lifetime_staking_rewards: str = Field(..., alias="lifetimeStakingRewards")
    unstaking: str
    staked: str
    available: str
    total_balance: str = Field(..., alias="totalBalance")

    class Config:
        populate_by_name = True


class Permissions(BaseModel):
    """Permissions information from GET /permissions."""

    create_shift: bool = Field(..., alias="createShift")

    class Config:
        populate_by_name = True


class XAIStats(BaseModel):
    """XAI statistics from GET /xai/stats."""

    total_supply: int = Field(..., alias="totalSupply")
    circulating_supply: int = Field(..., alias="circulatingSupply")
    number_of_stakers: int = Field(..., alias="numberOfStakers")
    latest_annual_percentage_yield: str = Field(..., alias="latestAnnualPercentageYield")
    latest_distributed_xai: str = Field(..., alias="latestDistributedXai")
    total_staked: str = Field(..., alias="totalStaked")
    average_annual_percentage_yield: str = Field(..., alias="averageAnnualPercentageYield")
    total_value_locked: str = Field(..., alias="totalValueLocked")
    total_value_locked_ratio: str = Field(..., alias="totalValueLockedRatio")
    xai_price_usd: str = Field(..., alias="xaiPriceUsd")
    svxai_price_usd: str = Field(..., alias="svxaiPriceUsd")
    svxai_price_xai: str = Field(..., alias="svxaiPriceXai")

    class Config:
        populate_by_name = True


# ============================================================================
# Checkout Models
# ============================================================================


class CheckoutOrderDeposit(BaseModel):
    """Deposit information in a checkout order."""

    deposit_hash: str | None = Field(None, alias="depositHash")
    settle_hash: str | None = Field(None, alias="settleHash")

    class Config:
        populate_by_name = True


class CheckoutOrder(BaseModel):
    """Order information in a checkout."""

    id: str
    deposits: list[CheckoutOrderDeposit] | None = None


class CheckoutRequest(BaseModel):
    """Request model for POST /checkout."""

    settle_coin: str = Field(..., alias="settleCoin")
    settle_network: str = Field(..., alias="settleNetwork")
    settle_amount: str = Field(..., alias="settleAmount")
    settle_address: str = Field(..., alias="settleAddress")
    settle_memo: str | None = Field(None, alias="settleMemo")
    affiliate_id: str = Field(..., alias="affiliateId")
    success_url: str = Field(..., alias="successUrl")
    cancel_url: str = Field(..., alias="cancelUrl")

    class Config:
        populate_by_name = True


class Checkout(BaseModel):
    """Checkout information from GET /checkout/:checkoutId or POST /checkout."""

    id: str
    settle_coin: str = Field(..., alias="settleCoin")
    settle_network: str = Field(..., alias="settleNetwork")
    settle_address: str = Field(..., alias="settleAddress")
    settle_memo: str | None = Field(None, alias="settleMemo")
    settle_amount: str = Field(..., alias="settleAmount")
    updated_at: datetime = Field(..., alias="updatedAt")
    created_at: datetime = Field(..., alias="createdAt")
    affiliate_id: str = Field(..., alias="affiliateId")
    success_url: str = Field(..., alias="successUrl")
    cancel_url: str = Field(..., alias="cancelUrl")
    orders: list[CheckoutOrder] | None = None

    class Config:
        populate_by_name = True

