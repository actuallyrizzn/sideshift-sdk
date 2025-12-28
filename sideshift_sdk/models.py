"""Pydantic models for SideShift API responses and requests."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ============================================================================
# Enums
# ============================================================================


class ShiftStatus(str, Enum):
    """Shift status values."""

    WAITING = "waiting"
    COMPLETE = "complete"
    MULTIPLE = "multiple"
    REFUNDED = "refunded"


# ============================================================================
# Coin Models
# ============================================================================


class TokenNetworkDetails(BaseModel):
    """Token network details."""

    contract_address: str = Field(..., alias="contractAddress", min_length=1)
    decimals: int = Field(..., gt=0)


class NetworkTokenDetails(BaseModel):
    """Network token details."""

    network: TokenNetworkDetails


class Coin(BaseModel):
    """Coin information from GET /coins."""

    networks: list[str]
    coin: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    has_memo: bool | None = Field(None, alias="hasMemo")  # deprecated
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

    min: str = Field(..., min_length=1)
    max: str = Field(..., min_length=1)
    rate: str = Field(..., min_length=1)
    deposit_coin: str = Field(..., alias="depositCoin", min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    deposit_network: str = Field(..., alias="depositNetwork", min_length=1)
    settle_network: str = Field(..., alias="settleNetwork", min_length=1)

    class Config:
        populate_by_name = True


# ============================================================================
# Quote Models
# ============================================================================


class QuoteRequest(BaseModel):
    """Request model for POST /quotes."""

    deposit_coin: str = Field(..., alias="depositCoin", min_length=1)
    deposit_network: str | None = Field(None, alias="depositNetwork", min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    settle_network: str | None = Field(None, alias="settleNetwork", min_length=1)
    deposit_amount: str | None = Field(None, alias="depositAmount", min_length=1)
    settle_amount: str | None = Field(None, alias="settleAmount", min_length=1)
    affiliate_id: str | None = Field(None, alias="affiliateId", min_length=1)
    commission_rate: str | None = Field(None, alias="commissionRate", min_length=1)

    @field_validator("deposit_amount", "settle_amount", "commission_rate", mode="before")
    @classmethod
    def validate_positive_amount(cls, v: str | None) -> str | None:
        """Validate that amount strings represent positive numbers."""
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Amount must be a string")
        if not v.strip():
            return None  # Empty string becomes None
        try:
            amount = float(v)
            if amount <= 0:
                raise ValueError(f"Amount must be positive, got {v}")
        except ValueError as e:
            if "could not convert" in str(e).lower():
                raise ValueError(f"Amount must be a valid number, got {v}") from e
            raise
        return v

    @model_validator(mode="after")
    def validate_amounts(self) -> "QuoteRequest":
        """Validate that either deposit_amount or settle_amount is provided."""
        if not self.deposit_amount and not self.settle_amount:
            raise ValueError("Either deposit_amount or settle_amount must be provided")
        return self

    class Config:
        populate_by_name = True


class Quote(BaseModel):
    """Quote response from POST /quotes."""

    id: str = Field(..., min_length=1)
    created_at: datetime = Field(..., alias="createdAt")
    deposit_coin: str = Field(..., alias="depositCoin", min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    deposit_network: str = Field(..., alias="depositNetwork", min_length=1)
    settle_network: str = Field(..., alias="settleNetwork", min_length=1)
    expires_at: datetime = Field(..., alias="expiresAt")
    deposit_amount: str = Field(..., alias="depositAmount", min_length=1)
    settle_amount: str = Field(..., alias="settleAmount", min_length=1)
    rate: str = Field(..., min_length=1)
    affiliate_id: str | None = Field(None, alias="affiliateId", min_length=1)

    class Config:
        populate_by_name = True


# ============================================================================
# Shift Models
# ============================================================================


class DepositInfo(BaseModel):
    """Deposit information in a shift."""

    deposit_hash: str | None = Field(None, alias="depositHash", min_length=1)
    settle_hash: str | None = Field(None, alias="settleHash", min_length=1)
    deposit_amount: str | None = Field(None, alias="depositAmount", min_length=1)
    settle_amount: str | None = Field(None, alias="settleAmount", min_length=1)

    class Config:
        populate_by_name = True


class FixedShiftRequest(BaseModel):
    """Request model for POST /shifts/fixed."""

    settle_address: str = Field(..., alias="settleAddress", min_length=1)
    settle_memo: str | None = Field(None, alias="settleMemo", min_length=1)
    affiliate_id: str = Field(..., alias="affiliateId", min_length=1)
    quote_id: str = Field(..., alias="quoteId", min_length=1)
    refund_address: str | None = Field(None, alias="refundAddress", min_length=1)
    refund_memo: str | None = Field(None, alias="refundMemo", min_length=1)
    external_id: str | None = Field(None, alias="externalId", min_length=1)

    class Config:
        populate_by_name = True


class VariableShiftRequest(BaseModel):
    """Request model for POST /shifts/variable."""

    deposit_coin: str = Field(..., alias="depositCoin", min_length=1)
    deposit_network: str | None = Field(None, alias="depositNetwork", min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    settle_network: str | None = Field(None, alias="settleNetwork", min_length=1)
    settle_address: str = Field(..., alias="settleAddress", min_length=1)
    settle_memo: str | None = Field(None, alias="settleMemo", min_length=1)
    affiliate_id: str = Field(..., alias="affiliateId", min_length=1)
    refund_address: str | None = Field(None, alias="refundAddress", min_length=1)
    refund_memo: str | None = Field(None, alias="refundMemo", min_length=1)
    external_id: str | None = Field(None, alias="externalId", min_length=1)

    class Config:
        populate_by_name = True


class SetRefundAddressRequest(BaseModel):
    """Request model for POST /shifts/:shiftId/set-refund-address."""

    address: str = Field(..., min_length=1)
    memo: str | None = Field(None, min_length=1)


class Shift(BaseModel):
    """Shift information from GET /shifts/:shiftId or POST /shifts/fixed or POST /shifts/variable."""

    id: str = Field(..., min_length=1)
    created_at: datetime = Field(..., alias="createdAt")
    deposit_coin: str = Field(..., alias="depositCoin", min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    deposit_network: str = Field(..., alias="depositNetwork", min_length=1)
    settle_network: str = Field(..., alias="settleNetwork", min_length=1)
    deposit_address: str | None = Field(None, alias="depositAddress", min_length=1)
    deposit_memo: str | None = Field(None, alias="depositMemo", min_length=1)
    settle_address: str = Field(..., alias="settleAddress", min_length=1)
    settle_memo: str | None = Field(None, alias="settleMemo", min_length=1)
    deposit_min: str | None = Field(None, alias="depositMin", min_length=1)
    deposit_max: str | None = Field(None, alias="depositMax", min_length=1)
    refund_address: str | None = Field(None, alias="refundAddress", min_length=1)
    refund_memo: str | None = Field(None, alias="refundMemo", min_length=1)
    type: Literal["fixed", "variable"]
    quote_id: str | None = Field(None, alias="quoteId", min_length=1)
    deposit_amount: str | None = Field(None, alias="depositAmount", min_length=1)
    settle_amount: str | None = Field(None, alias="settleAmount", min_length=1)
    expires_at: datetime | None = Field(None, alias="expiresAt")
    status: ShiftStatus = Field(...)
    average_shift_seconds: str | None = Field(None, alias="averageShiftSeconds", min_length=1)
    external_id: str | None = Field(None, alias="externalId", min_length=1)
    rate: str | None = Field(None, min_length=1)
    deposits: list[DepositInfo] | None = None

    class Config:
        populate_by_name = True


class RecentShift(BaseModel):
    """Recent shift information from GET /recent-shifts."""

    created_at: datetime = Field(..., alias="createdAt")
    deposit_coin: str = Field(..., alias="depositCoin", min_length=1)
    deposit_network: str = Field(..., alias="depositNetwork", min_length=1)
    deposit_amount: str | None = Field(None, alias="depositAmount", min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    settle_network: str = Field(..., alias="settleNetwork", min_length=1)
    settle_amount: str | None = Field(None, alias="settleAmount", min_length=1)

    class Config:
        populate_by_name = True


class CancelOrderRequest(BaseModel):
    """Request model for POST /cancel-order."""

    order_id: str = Field(..., alias="orderId", min_length=1)

    class Config:
        populate_by_name = True


# ============================================================================
# Account Models
# ============================================================================


class Account(BaseModel):
    """Account information from GET /account."""

    id: str = Field(..., min_length=1)
    lifetime_staking_rewards: str = Field(..., alias="lifetimeStakingRewards", min_length=1)
    unstaking: str = Field(..., min_length=1)
    staked: str = Field(..., min_length=1)
    available: str = Field(..., min_length=1)
    total_balance: str = Field(..., alias="totalBalance", min_length=1)

    class Config:
        populate_by_name = True


class Permissions(BaseModel):
    """Permissions information from GET /permissions."""

    create_shift: bool = Field(..., alias="createShift")

    class Config:
        populate_by_name = True


class XAIStats(BaseModel):
    """XAI statistics from GET /xai/stats."""

    total_supply: int = Field(..., alias="totalSupply", ge=0)
    circulating_supply: int = Field(..., alias="circulatingSupply", ge=0)
    number_of_stakers: int = Field(..., alias="numberOfStakers", ge=0)
    latest_annual_percentage_yield: str = Field(..., alias="latestAnnualPercentageYield", min_length=1)
    latest_distributed_xai: str = Field(..., alias="latestDistributedXai", min_length=1)
    total_staked: str = Field(..., alias="totalStaked", min_length=1)
    average_annual_percentage_yield: str = Field(..., alias="averageAnnualPercentageYield", min_length=1)
    total_value_locked: str = Field(..., alias="totalValueLocked", min_length=1)
    total_value_locked_ratio: str = Field(..., alias="totalValueLockedRatio", min_length=1)
    xai_price_usd: str = Field(..., alias="xaiPriceUsd", min_length=1)
    svxai_price_usd: str = Field(..., alias="svxaiPriceUsd", min_length=1)
    svxai_price_xai: str = Field(..., alias="svxaiPriceXai", min_length=1)

    class Config:
        populate_by_name = True


# ============================================================================
# Checkout Models
# ============================================================================


class CheckoutOrderDeposit(BaseModel):
    """Deposit information in a checkout order."""

    deposit_hash: str | None = Field(None, alias="depositHash", min_length=1)
    settle_hash: str | None = Field(None, alias="settleHash", min_length=1)

    class Config:
        populate_by_name = True


class CheckoutOrder(BaseModel):
    """Order information in a checkout."""

    id: str = Field(..., min_length=1)
    deposits: list[CheckoutOrderDeposit] | None = None


class CheckoutRequest(BaseModel):
    """Request model for POST /checkout."""

    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    settle_network: str = Field(..., alias="settleNetwork", min_length=1)
    settle_amount: str = Field(..., alias="settleAmount", min_length=1)
    settle_address: str = Field(..., alias="settleAddress", min_length=1)
    settle_memo: str | None = Field(None, alias="settleMemo", min_length=1)
    affiliate_id: str = Field(..., alias="affiliateId", min_length=1)
    success_url: str = Field(..., alias="successUrl", min_length=1)
    cancel_url: str = Field(..., alias="cancelUrl", min_length=1)

    @field_validator("settle_amount", mode="before")
    @classmethod
    def validate_positive_amount(cls, v: str) -> str:
        """Validate that settle_amount is a positive number."""
        if not isinstance(v, str):
            raise ValueError("settle_amount must be a string")
        if not v.strip():
            raise ValueError("settle_amount cannot be empty")
        try:
            amount = float(v)
            if amount <= 0:
                raise ValueError(f"settle_amount must be positive, got {v}")
        except ValueError as e:
            if "could not convert" in str(e).lower():
                raise ValueError(f"settle_amount must be a valid number, got {v}") from e
            raise
        return v

    class Config:
        populate_by_name = True


class Checkout(BaseModel):
    """Checkout information from GET /checkout/:checkoutId or POST /checkout."""

    id: str = Field(..., min_length=1)
    settle_coin: str = Field(..., alias="settleCoin", min_length=1)
    settle_network: str = Field(..., alias="settleNetwork", min_length=1)
    settle_address: str = Field(..., alias="settleAddress", min_length=1)
    settle_memo: str | None = Field(None, alias="settleMemo", min_length=1)
    settle_amount: str = Field(..., alias="settleAmount", min_length=1)
    updated_at: datetime = Field(..., alias="updatedAt")
    created_at: datetime = Field(..., alias="createdAt")
    affiliate_id: str = Field(..., alias="affiliateId", min_length=1)
    success_url: str = Field(..., alias="successUrl", min_length=1)
    cancel_url: str = Field(..., alias="cancelUrl", min_length=1)
    orders: list[CheckoutOrder] | None = None

    class Config:
        populate_by_name = True
