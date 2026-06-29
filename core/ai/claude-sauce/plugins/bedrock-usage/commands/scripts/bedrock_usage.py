# pylint: disable=too-many-lines, too-many-instance-attributes, too-many-locals, too-many-statements,too-many-nested-blocks,
# pylint: disable=too-many-branches
# !/usr/bin/env python3
"""
AWS Bedrock Per-User Usage Report

Gets exact costs from Bedrock Model Invocation Logging (CloudWatch).
Requires Bedrock model invocation logging to be enabled.

Requirements:
    pip install boto3

Usage:
    python bedrock_usage.py
    python bedrock_usage.py --profile <aws-profile>
    python bedrock_usage.py --days 7
"""

import argparse
import json
import re
import sys
import time
import traceback
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional, Union

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print('Error: boto3 is required. Install with: pip install boto3')
    sys.exit(1)

# =============================================================================
# Data Structures for Reusable API
# =============================================================================


@dataclass
class ModelUsage:
    """Usage and cost data for a single model."""
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    calls: int = 0
    cost: Optional[float] = None
    dates: set = field(default_factory=set)

    def to_dict(self) -> dict:
        """Convert to dict with dates as sorted list.

        Returns:
            dict: Dictionary representation with all fields, dates converted to sorted list.
        """
        d = asdict(self)
        d['dates'] = sorted(list(self.dates))
        return d


@dataclass
class UserUsage:
    """Usage and cost data for a single user."""
    user_id: str
    models: dict[str, ModelUsage] = field(default_factory=dict)  # model_id -> ModelUsage
    total_cost: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dict with nested model data.

        Returns:
            dict: Dictionary containing user_id, models (as nested dicts), and total_cost.
        """
        return {
            'user_id': self.user_id,
            'models': {
                k: v.to_dict() for k, v in self.models.items()
            },
            'total_cost': self.total_cost,
        }


@dataclass
class CostBreakdown:
    """Complete cost breakdown by user and model."""
    per_user: dict[str, UserUsage] = field(default_factory=dict)  # user_id -> UserUsage
    per_model: dict[str, ModelUsage] = field(default_factory=dict)  # model_id -> ModelUsage (aggregated)
    total_cost: float = 0.0
    cost_source: str = 'unknown'  # "cost_explorer" or "price_list"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict.

        Returns:
            dict: Dictionary containing per_user, per_model (as nested dicts),
                total_cost, cost_source, and ISO-formatted date strings.
        """
        return {
            'per_user': {
                k: v.to_dict() for k, v in self.per_user.items()
            },
            'per_model': {
                k: v.to_dict() for k, v in self.per_model.items()
            },
            'total_cost': self.total_cost,
            'cost_source': self.cost_source,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }


@dataclass
class ModelPricing:
    """Pricing data for a model."""
    input: float  # price per 1k tokens
    output: float  # price per 1k tokens
    cache_read: float = 0.0  # price per 1k tokens
    cache_write: float = 0.0  # price per 1k tokens
    name: str = ''


@dataclass
class CostExplorerEntry:
    """Cost Explorer entry for a model."""
    service_name: str
    total_cost: float


# =============================================================================
# Helper Functions
# =============================================================================


def normalize_model_name_for_matching(service_name: str) -> str:
    """
    Normalize a Cost Explorer service name to match against model IDs from logs.

    Args:
        service_name: The service name from AWS Cost Explorer (e.g., "Claude 3.5 Sonnet v2 (Bedrock Edition)").

    Returns:
        str: Normalized lowercase name with dashes (e.g., "claude-3-5-sonnet-v2").

    Example:
        >>> normalize_model_name_for_matching("Claude 3.5 Sonnet v2 ( Bedrock Edition)")
        'claude-3-5-sonnet-v2'
    """
    # Remove " ( Bedrock Edition)" or "(Amazon Bedrock Edition)" suffix
    name = re.sub(r'\s*\([^)]*[Bb]edrock[^)]*\)', '', service_name).strip()
    # Convert to lowercase and replace spaces/dots with dashes
    name = name.lower().replace(' ', '-').replace('.', '-')
    # Remove duplicate dashes
    name = re.sub(r'-+', '-', name)
    return name


def extract_model_identifier(name: str) -> str:
    """
    Extract a normalized model identifier for matching across different name formats.

    Removes region prefixes, version suffixes, dates, and parenthetical content
    to produce a canonical identifier that can be matched across Cost Explorer
    and invocation log formats.

    Args:
        name: Model name in any format (Cost Explorer service name, model ARN, or model ID).

    Returns:
        str: Normalized model identifier (e.g., "claude-3-5-sonnet-v2").

    Examples:
        >>> extract_model_identifier("us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        'claude-3-5-sonnet-v2'
        >>> extract_model_identifier("anthropic.claude-opus-4-5-20251101-v1:0")
        'claude-opus-4-5'
        >>> extract_model_identifier("Claude 3.5 Sonnet v2 (Amazon Bedrock Edition)")
        'claude-3-5-sonnet-v2'
    """
    name = name.lower()

    # Remove parenthetical content like "(Amazon Bedrock Edition)"
    if '(' in name:
        name = name.split('(')[0].strip()

    # Remove API version suffix like ":0"
    if ':' in name:
        name = name.split(':')[0]

    # Get the model name part after the last provider prefix
    # "us.anthropic.claude-opus-4-5-20251101-v1" -> "claude-opus-4-5-20251101-v1"
    for prefix in ['anthropic.', 'amazon.', 'cohere.', 'meta.', 'mistral.']:
        if prefix in name:
            name = name.split(prefix)[-1]
            break

    # Normalize spaces and dots to dashes
    name = name.replace(' ', '-').replace('.', '-')

    # Process the components to remove date and handle version
    parts = name.split('-')
    result = []
    version = None

    for part in parts:
        # Capture version (v1, v2, etc.)
        if part.startswith('v') and len(part) >= 2 and part[1:].isdigit():
            version = part
        # Skip 8-digit dates (YYYYMMDD)
        elif len(part) == 8 and part.isdigit():
            continue
        else:
            result.append(part)

    # Add version back (except v1 which is implicit)
    if version and version != 'v1':
        result.append(version)

    return '-'.join(result)


# =============================================================================
# BedrockCostCalculator - Main Reusable API Class
# =============================================================================


class BedrockCostCalculator:
    """
    Calculate AWS Bedrock usage costs per model and per user for a given time period.

    This class fetches invocation logs from CloudWatch, pricing data from AWS APIs,
    and calculates costs. It caches API responses for efficiency.

    Usage:
        session = boto3.Session(profile_name="my-profile")
        calc = BedrockCostCalculator(session, region="us-east-1")

        # Get full cost breakdown
        result = calc.get_usage(days=30)

        # Or with explicit date range
        result = calc.get_usage(start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))

        # Access data
        print(result.total_cost)
        for user_id, user_data in result.per_user.items():
            print(f"{user_id}: ${user_data.total_cost:.2f}")
    """

    def __init__(
        self,
        session: boto3.Session,
        region: str = 'us-east-1',
        log_group: Optional[str] = None,
        verbose: bool = True,
    ):
        """
        Initialize the calculator.

        Args:
            session: boto3 Session with AWS credentials
            region: AWS region for Bedrock
            log_group: Override CloudWatch log group (auto-detected if None)
            verbose: Print progress messages
        """
        self.session = session
        self.region = region
        self._log_group = log_group
        self.verbose = verbose

        # Instance-level caches
        self._pricing_cache: Optional[dict[str, ModelPricing]] = None
        self._model_mapping_cache: Optional[dict[str, str]] = None
        self._model_name_cache: Optional[dict[str, str]] = None
        self._cost_explorer_cache: Optional[dict[str, CostExplorerEntry]] = None

    def get_usage(
        self,
        days: Optional[int] = None,
        start_date: Optional[Union[date, datetime]] = None,
        end_date: Optional[Union[date, datetime]] = None,
        user_filter: Optional[str] = None,
    ) -> CostBreakdown:
        """
        Get Bedrock usage and costs for the specified time period.

        Per-user costs are always calculated using Price List API pricing (tokens × price per token).
        Cost Explorer data, if requested, is fetched for reference only.

        Args:
            days: Number of days to look back (default: 30)
            start_date: Explicit start date (overrides days)
            end_date: Explicit end date (defaults to today)
            user_filter: Optional user ID substring filter

        Returns:
            CostBreakdown with per-user and per-model cost data calculated from Price List API
        """
        start_dt, end_dt = self._resolve_date_range(days, start_date, end_date)

        # Verify logging is enabled
        log_group = self._get_log_group()
        if not log_group:
            raise ValueError('Bedrock model invocation logging is not enabled')

        self._log(f"Found invocation logging enabled: {log_group}")

        # Fetch invocation logs
        logs = self._fetch_invocation_logs(log_group, start_dt, end_dt)
        if not logs:
            return CostBreakdown(
                start_date=start_dt,
                end_date=end_dt,
                cost_source='none',
            )

        self._log(f"Found {len(logs)} invocation log entries.")

        # Analyze logs into user/model structure
        user_usage = self._analyze_logs(logs)

        # Always fetch pricing data for absolute cost calculation
        self._log('Fetching pricing from AWS Price List API...')
        self._fetch_pricing()
        self._fetch_model_mapping()

        # Build cost breakdown
        result = self._build_cost_breakdown(user_usage, start_dt, end_dt)

        # Apply user filter if specified
        if user_filter:
            filter_lower = user_filter.lower()
            result.per_user = {k: v for k, v in result.per_user.items() if filter_lower in k.lower()}
            # Recalculate total
            result.total_cost = sum(u.total_cost or 0 for u in result.per_user.values())

        return result

    def get_costs_per_model(
        self,
        days: Optional[int] = None,
        start_date: Optional[Union[date, datetime]] = None,
        end_date: Optional[Union[date, datetime]] = None,
    ) -> dict[str, ModelUsage]:
        """
        Get aggregated costs per model for the specified time period.

        Args:
            days: Number of days to look back (default: 30).
            start_date: Explicit start date (overrides days).
            end_date: Explicit end date (defaults to today).

        Returns:
            dict[str, ModelUsage]: Dictionary mapping model_id to ModelUsage with
                aggregated token counts and costs across all users.
        """
        breakdown = self.get_usage(days=days, start_date=start_date, end_date=end_date)
        return breakdown.per_model

    def get_costs_per_user(
        self,
        days: Optional[int] = None,
        start_date: Optional[Union[date, datetime]] = None,
        end_date: Optional[Union[date, datetime]] = None,
    ) -> dict[str, UserUsage]:
        """
        Get costs per user for the specified time period.

        Args:
            days: Number of days to look back (default: 30).
            start_date: Explicit start date (overrides days).
            end_date: Explicit end date (defaults to today).

        Returns:
            dict[str, UserUsage]: Dictionary mapping user_id to UserUsage containing
                per-model breakdown and total cost for each user.
        """
        breakdown = self.get_usage(days=days, start_date=start_date, end_date=end_date)
        return breakdown.per_user

    @staticmethod
    def _analyze_logs(logs: list[dict[str, Any]]) -> dict[str, dict[str, ModelUsage]]:
        """
        Analyze invocation logs and group token usage by user and model.

        Parses CloudWatch log entries to extract user identity (from ARN or principal ID)
        and model usage metrics (input/output tokens, cache tokens, call counts).

        Args:
            logs: List of parsed CloudWatch log event dictionaries from Bedrock invocation logs.

        Returns:
            dict[str, dict[str, ModelUsage]]: Nested dictionary where outer key is user_id,
                inner key is model_id, and value is ModelUsage with aggregated metrics.
        """
        user_usage: dict[str, dict[str, ModelUsage]] = defaultdict(dict)

        for log in logs:
            try:
                identity = log.get('identity', {})
                arn = identity.get('arn', '')
                user = arn.split('/')[-1] if arn and '/' in arn else identity.get('principalId', identity.get('accountId', 'unknown'))

                model_id = log.get('modelId', 'unknown-model')
                if '/' in model_id:
                    model_id = model_id.split('/')[-1]

                input_data = log.get('input', {}) or {}
                output_data = log.get('output', {}) or {}

                # Initialize ModelUsage if not exists
                if model_id not in user_usage[user]:
                    user_usage[user][model_id] = ModelUsage(model_id=model_id)

                model_usage = user_usage[user][model_id]
                model_usage.input_tokens += input_data.get('inputTokenCount', 0) or 0
                model_usage.output_tokens += output_data.get('outputTokenCount', 0) or 0
                model_usage.cache_read_tokens += input_data.get('cacheReadInputTokenCount', 0) or 0
                model_usage.cache_write_tokens += input_data.get('cacheWriteInputTokenCount', 0) or 0
                model_usage.calls += 1

                timestamp = log.get('timestamp', '')
                if timestamp:
                    model_usage.dates.add(timestamp[:10])
            except Exception as e:
                print(f'Failed analyzing logs. Error: {str(e)}')

        return user_usage

    def _build_cost_breakdown(
        self,
        user_usage: dict[str, dict[str, ModelUsage]],
        start_dt: datetime,
        end_dt: datetime,
    ) -> CostBreakdown:
        """
        Build complete CostBreakdown from analyzed usage and cost data.

        Calculates per-user costs using Price List API pricing (tokens × price per token).
        Cost Explorer data, if provided, is kept for reference only and not used for
        per-user cost calculation.

        Args:
            user_usage: Nested dict from _analyze_logs with per-user, per-model usage.
            start_dt: Start of the reporting period (UTC).
            end_dt: End of the reporting period (UTC).

        Returns:
            CostBreakdown: Complete breakdown with per_user, per_model aggregates,
                total_cost calculated from Price List, cost_source set to "price_list",
                and date range.
        """
        result = CostBreakdown(
            start_date=start_dt,
            end_date=end_dt,
            cost_source='price_list',
        )

        # Build per-user data
        for user, models in user_usage.items():
            user_data = UserUsage(user_id=user)
            user_total_cost = 0.0

            for model_id, model_usage in models.items():
                # Always calculate cost using Price List pricing (absolute cost per user)
                model_usage.cost = self._calculate_cost(
                    model_id,
                    model_usage.input_tokens,
                    model_usage.output_tokens,
                    model_usage.cache_read_tokens,
                    model_usage.cache_write_tokens,
                )

                if model_usage.cost:
                    user_total_cost += model_usage.cost

                user_data.models[model_id] = model_usage

                # Aggregate into per_model
                if model_id not in result.per_model:
                    result.per_model[model_id] = ModelUsage(model_id=model_id)

                agg = result.per_model[model_id]
                agg.input_tokens += model_usage.input_tokens
                agg.output_tokens += model_usage.output_tokens
                agg.cache_read_tokens += model_usage.cache_read_tokens
                agg.cache_write_tokens += model_usage.cache_write_tokens
                agg.calls += model_usage.calls
                agg.dates.update(model_usage.dates)
                if model_usage.cost:
                    agg.cost = (agg.cost or 0) + model_usage.cost

            user_data.total_cost = user_total_cost
            result.per_user[user] = user_data
            result.total_cost += user_total_cost

        return result

    def _log(self, msg: str) -> None:
        """
        Print a progress message if verbose mode is enabled.

        Args:
            msg: Message to print.
        """
        if self.verbose:
            print(msg)

    def _get_log_group(self) -> Optional[str]:
        """
        Get the CloudWatch log group for Bedrock model invocation logs.

        Queries the Bedrock API for the logging configuration and extracts
        the CloudWatch log group name. Result is cached for subsequent calls.

        Returns:
            Optional[str]: Log group name if invocation logging is enabled, None otherwise.
        """
        if self._log_group:
            return self._log_group

        try:
            bedrock = self.session.client('bedrock', region_name=self.region)
            response = bedrock.get_model_invocation_logging_configuration()
            logging_config = response.get('loggingConfig', {})
            cloudwatch_config = logging_config.get('cloudWatchConfig', {})
            log_group = cloudwatch_config.get('logGroupName')
            if log_group:
                self._log_group = log_group
                return log_group
            return None
        except ClientError:
            return None
        except Exception:
            return None

    @staticmethod
    def _resolve_date_range(
        days: Optional[int] = None,
        start_date: Optional[Union[date, datetime]] = None,
        end_date: Optional[Union[date, datetime]] = None,
    ) -> tuple[datetime, datetime]:
        """
        Resolve date range from various input formats.

        Args:
            days: Number of days to look back (from today)
            start_date: Explicit start date
            end_date: Explicit end date (defaults to today)

        Returns:
            Tuple of (start_datetime, end_datetime) in UTC
        """
        now = datetime.now(timezone.utc)

        if start_date is not None:
            if isinstance(start_date, date) and not isinstance(start_date, datetime):
                start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
            else:
                start_dt = start_date if start_date.tzinfo else start_date.replace(tzinfo=timezone.utc)

            if end_date is not None:
                if isinstance(end_date, date) and not isinstance(end_date, datetime):
                    end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
                else:
                    end_dt = end_date if end_date.tzinfo else end_date.replace(tzinfo=timezone.utc)
            else:
                end_dt = now
        elif days is not None:
            end_dt = now
            start_dt = now - timedelta(days=days)
        else:
            # Default to 30 days
            end_dt = now
            start_dt = now - timedelta(days=30)

        return start_dt, end_dt

    def _fetch_pricing(self) -> dict[str, ModelPricing]:
        """
        Fetch Bedrock model pricing from AWS Price List API.

        Retrieves on-demand pricing for all Bedrock models in the configured region.
        Results are cached for the lifetime of the calculator instance.

        Returns:
            dict[str, ModelPricing]: Dictionary mapping lowercase model name to ModelPricing
                with input/output/cache token prices per 1K tokens.
        """
        if self._pricing_cache is not None:
            return self._pricing_cache

        pricing_data = {}
        try:
            pricing_client = self.session.client('pricing', region_name='us-east-1')
            paginator = pricing_client.get_paginator('get_products')
            page_iterator = paginator.paginate(
                ServiceCode='AmazonBedrockFoundationModels',
                Filters=[
                    {
                        'Type': 'TERM_MATCH',
                        'Field': 'regionCode',
                        'Value': self.region
                    },
                ],
                MaxResults=100,
            )

            for page in page_iterator:
                for price_item_json in page.get('PriceList', []):
                    try:
                        price_item = json.loads(price_item_json)
                        attributes = price_item.get('product', {}).get('attributes', {})
                        servicename = attributes.get('servicename', '')
                        usagetype = attributes.get('usagetype', '')

                        if not servicename or 'Global' in usagetype or 'Batch' in usagetype:
                            continue

                        is_input = 'InputTokenCount-Units' in usagetype and 'Cache' not in usagetype
                        is_output = 'OutputTokenCount-Units' in usagetype and 'Cache' not in usagetype
                        is_cache_read = 'CacheReadInputTokenCount-Units' in usagetype
                        is_cache_write = 'CacheWriteInputTokenCount-Units' in usagetype

                        if not any([is_input, is_output, is_cache_read, is_cache_write]):
                            continue

                        model_name = servicename.replace(' (Amazon Bedrock Edition)', '').strip()
                        model_key = model_name.lower()

                        terms = price_item.get('terms', {}).get('OnDemand', {})
                        for term in terms.values():
                            price_dimensions = term.get('priceDimensions', {})
                            for dimension in price_dimensions.values():
                                price_per_million = float(dimension.get('pricePerUnit', {}).get('USD', 0))
                                price_per_1k = price_per_million / 1000

                                if model_key not in pricing_data:
                                    pricing_data[model_key] = ModelPricing(
                                        input=0,
                                        output=0,
                                        cache_read=0,
                                        cache_write=0,
                                        name=model_name,
                                    )
                                if is_input:
                                    pricing_data[model_key].input = price_per_1k
                                elif is_output:
                                    pricing_data[model_key].output = price_per_1k
                                elif is_cache_read:
                                    pricing_data[model_key].cache_read = price_per_1k
                                elif is_cache_write:
                                    pricing_data[model_key].cache_write = price_per_1k
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            self._pricing_cache = pricing_data
            self._log(f"Loaded pricing for {len(pricing_data)} models from AWS Price List API.")
        except ClientError as e:
            if 'AccessDenied' in str(e):
                self._log('Warning: No permission to access Pricing API.')
        except Exception as e:
            self._log(f"Warning: Could not fetch pricing: {e}")

        return pricing_data

    def _fetch_model_mapping(self) -> dict[str, str]:
        """
        Fetch model ID to pricing name mapping from Bedrock API.

        Queries the Bedrock API for all foundation models and builds a mapping
        from model IDs to their human-readable names for pricing lookups.
        Results are cached for the lifetime of the calculator instance.

        Returns:
            dict[str, str]: Dictionary mapping lowercase model_id to pricing name.
                Includes both full IDs and region-stripped variants.
        """
        if self._model_mapping_cache is not None:
            return self._model_mapping_cache

        model_mapping: dict[str, str] = {}
        model_name_map: dict[str, str] = {}

        try:
            bedrock = self.session.client('bedrock', region_name=self.region)
            response = bedrock.list_foundation_models()

            for model in response.get('modelSummaries', []):
                model_id = model.get('modelId', '')
                model_name = model.get('modelName', '')
                if not model_id or not model_name:
                    continue

                pricing_name = model_name.lower()
                model_mapping[model_id.lower()] = pricing_name
                model_name_map[model_id.lower()] = model_name

                if '.' in model_id:
                    parts = model_id.split('.')
                    if len(parts) >= 2 and len(parts[0]) <= 3:
                        model_id_no_region = '.'.join(parts[1:])
                        model_mapping[model_id_no_region.lower()] = pricing_name
                        model_name_map[model_id_no_region.lower()] = model_name

            self._model_mapping_cache = model_mapping
            self._model_name_cache = model_name_map
            self._log(f"Loaded {len(response.get('modelSummaries', []))} foundation models from Bedrock API.")
        except ClientError as e:
            if 'AccessDenied' in str(e):
                self._log('Warning: No permission to list foundation models.')
        except Exception as e:
            self._log(f"Warning: Could not fetch foundation models: {e}")

        return model_mapping

    def _fetch_cost_explorer(self, start_date: datetime, end_date: datetime) -> dict[str, CostExplorerEntry]:
        """
        Fetch actual Bedrock costs from AWS Cost Explorer API.

        Queries Cost Explorer day-by-day to get unblended costs grouped by
        service and usage type. Only includes Bedrock-related entries.

        Args:
            start_date: Start of the date range (UTC).
            end_date: End of the date range (UTC).

        Returns:
            dict[str, CostExplorerEntry]: Dictionary mapping normalized model key to
                CostExplorerEntry with service_name and accumulated total_cost.
        """
        # Note: We don't cache across different date ranges for accuracy
        costs_by_model: dict[str, CostExplorerEntry] = {}

        try:
            ce_client = self.session.client('ce', region_name='us-east-1')
            current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = end_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            total_days = (end_dt - current_date).days
            days_processed = 0

            while current_date < end_dt:
                next_date = current_date + timedelta(days=1)
                start_str = current_date.strftime('%Y-%m-%d')
                end_str = next_date.strftime('%Y-%m-%d')

                next_page_token = None
                while True:
                    kwargs = {
                        'TimePeriod': {
                            'Start': start_str,
                            'End': end_str
                        },
                        'Granularity': 'DAILY',
                        'Metrics': ['UnblendedCost'],
                        'GroupBy': [
                            {
                                'Type': 'DIMENSION',
                                'Key': 'SERVICE'
                            },
                            {
                                'Type': 'DIMENSION',
                                'Key': 'USAGE_TYPE'
                            },
                        ],
                    }
                    if next_page_token:
                        kwargs['NextPageToken'] = next_page_token

                    response = ce_client.get_cost_and_usage(**kwargs)

                    for result in response.get('ResultsByTime', []):
                        for group in result.get('Groups', []):
                            keys = group.get('Keys', [])
                            if len(keys) < 2:
                                continue

                            service_name = keys[0]
                            if 'Bedrock' not in service_name and 'bedrock' not in service_name.lower():
                                continue

                            cost = float(group.get('Metrics', {}).get('UnblendedCost', {}).get('Amount', 0))
                            if cost <= 0:
                                continue

                            model_key = normalize_model_name_for_matching(service_name)
                            if model_key not in costs_by_model:
                                costs_by_model[model_key] = CostExplorerEntry(
                                    service_name=service_name,
                                    total_cost=0.0,
                                )
                            costs_by_model[model_key].total_cost += cost

                    next_page_token = response.get('NextPageToken')
                    if not next_page_token:
                        break

                current_date = next_date
                days_processed += 1
                if days_processed % 5 == 0 or days_processed == total_days:
                    self._log(f"  Cost Explorer: processed {days_processed}/{total_days} days...")

            total_cost = sum(m.total_cost for m in costs_by_model.values())
            self._log(f"Loaded costs for {len(costs_by_model)} models from Cost Explorer (Total: ${total_cost:.2f})")
        except ClientError as e:
            if 'AccessDenied' in str(e):
                self._log('Warning: No permission to access Cost Explorer API.')
        except Exception as e:
            self._log(f"Warning: Could not fetch Cost Explorer data: {e}")

        return costs_by_model

    def _fetch_invocation_logs_with_pagination(
        self,
        logs_client,
        log_group: str,
        start_ms: int,
        end_ms: int,
    ) -> list[dict[str, Any]]:
        """
        Query CloudWatch Logs with automatic pagination and retry handling.

        Handles pagination tokens and implements exponential backoff for
        rate limiting (ThrottlingException, LimitExceededException).

        Args:
            logs_client: boto3 CloudWatch Logs client.
            log_group: CloudWatch log group name.
            start_ms: Start timestamp in milliseconds since epoch.
            end_ms: End timestamp in milliseconds since epoch.

        Returns:
            list[dict[str, Any]]: List of parsed JSON log event messages.

        Raises:
            ClientError: If max retries exceeded or non-throttling error occurs.
        """
        events: list[dict[str, Any]] = []
        next_token = None
        retry_count = 0
        max_retries = 5

        while True:
            kwargs = {
                'logGroupName': log_group,
                'startTime': start_ms,
                'endTime': end_ms,
                'limit': 10000,
            }
            if next_token:
                kwargs['nextToken'] = next_token

            try:
                response = logs_client.filter_log_events(**kwargs)
                retry_count = 0
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code in ['ThrottlingException', 'LimitExceededException'] and retry_count < max_retries:
                    retry_count += 1
                    wait_time = (2**retry_count) + (0.1 * retry_count)
                    self._log(f"  Rate limited, waiting {wait_time:.1f}s before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                raise

            for event in response.get('events', []):
                try:
                    message = json.loads(event.get('message', '{}'))
                    events.append(message)
                except json.JSONDecodeError:
                    continue

            next_token = response.get('nextToken')
            if not next_token:
                break

        return events

    def _fetch_invocation_logs(self, log_group: str, start_time: datetime, end_time: datetime) -> list[dict[str, Any]]:
        """
        Query CloudWatch Logs for Bedrock model invocation logs.

        Fetches logs day-by-day to handle large date ranges efficiently.
        Progress is reported if verbose mode is enabled.

        Args:
            log_group: CloudWatch log group name containing Bedrock invocation logs.
            start_time: Start of the time range (UTC).
            end_time: End of the time range (UTC).

        Returns:
            list[dict[str, Any]]: List of parsed invocation log entries, each containing
                identity, modelId, input/output token counts, and timestamp.
        """
        logs_client = self.session.client('logs', region_name=self.region)
        self._log(f"Querying invocation logs from {log_group}...")

        events: list[dict[str, Any]] = []
        total_days = (end_time - start_time).days + 1
        days_processed = 0
        current_date = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        final_end = end_time

        while current_date < final_end:
            next_date = min(current_date + timedelta(days=1), final_end)
            start_ms = int(current_date.timestamp() * 1000)
            end_ms = int(next_date.timestamp() * 1000)

            try:
                day_events = self._fetch_invocation_logs_with_pagination(logs_client, log_group, start_ms, end_ms)
                events.extend(day_events)
            except ClientError as e:
                if 'ResourceNotFoundException' in str(e):
                    self._log(f"Log group {log_group} not found.")
                    return []
                raise

            current_date = next_date
            days_processed += 1
            if days_processed % 5 == 0 or days_processed == total_days:
                self._log(f"  CloudWatch Logs: {days_processed}/{total_days} days, {len(events):,} events retrieved...")

        self._log(f"  CloudWatch Logs: completed - {len(events):,} total events")
        return events

    def _calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> Optional[float]:
        """
        Calculate cost for given token counts using cached pricing data.

        Args:
            model: Model ID or name to look up pricing for.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            cache_read_tokens: Number of cache read tokens (default: 0).
            cache_write_tokens: Number of cache write tokens (default: 0).

        Returns:
            Optional[float]: Total cost in USD, or None if pricing not found for model.
        """
        pricing = self._get_price_for_model(model)
        if pricing is None:
            return None
        input_cost = (input_tokens / 1000) * pricing.input
        output_cost = (output_tokens / 1000) * pricing.output
        cache_read_cost = (cache_read_tokens / 1000) * pricing.cache_read
        cache_write_cost = (cache_write_tokens / 1000) * pricing.cache_write
        return input_cost + output_cost + cache_read_cost + cache_write_cost

    def _get_price_for_model(self, model_id: str) -> Optional[ModelPricing]:
        """
        Get pricing information for a specific model ID.

        Looks up pricing using multiple strategies: direct mapping, region-stripped
        ID lookup, and fuzzy string matching as fallback.

        Args:
            model_id: Model ID from invocation logs (e.g., "us.anthropic.claude-3-5-sonnet:0").

        Returns:
            Optional[ModelPricing]: Pricing data with per-1K-token rates, or None if not found.
        """
        pricing_data = self._pricing_cache or {}
        model_mapping = self._model_mapping_cache

        if not pricing_data:
            return None

        model_lower = model_id.lower()
        model_base = re.sub(r':\d+$', '', model_lower)

        if model_mapping:
            if model_base in model_mapping:
                pricing_name = model_mapping[model_base]
                if pricing_name in pricing_data:
                    return pricing_data[pricing_name]

            if '.' in model_base:
                parts = model_base.split('.')
                if len(parts) >= 2 and len(parts[0]) <= 3:
                    model_no_region = '.'.join(parts[1:])
                    if model_no_region in model_mapping:
                        pricing_name = model_mapping[model_no_region]
                        if pricing_name in pricing_data:
                            return pricing_data[pricing_name]

        if model_lower in pricing_data:
            return pricing_data[model_lower]

        best_match = None
        best_match_len = 0
        for price_key, prices in pricing_data.items():
            normalized_key = price_key.replace(' ', '').replace('.', '')
            if normalized_key in model_lower.replace('-', '').replace('.', ''):
                if len(price_key) > best_match_len:
                    best_match = prices
                    best_match_len = len(price_key)

        return best_match

    def _get_official_model_name(self, model_id: str) -> Optional[str]:
        """
        Get the official human-readable model name for Cost Explorer matching.

        Looks up the model name from the cached Bedrock foundation models list.

        Args:
            model_id: Model ID from invocation logs.

        Returns:
            Optional[str]: Official model name (e.g., "Claude 3.5 Sonnet"), or None if not found.
        """
        if self._model_name_cache is None:
            return None

        model_lower = model_id.lower()
        model_base = re.sub(r':\d+$', '', model_lower)

        if model_base in self._model_name_cache:
            return self._model_name_cache[model_base]

        if '.' in model_base:
            parts = model_base.split('.')
            if len(parts) >= 2 and len(parts[0]) <= 3:
                model_no_region = '.'.join(parts[1:])
                if model_no_region in self._model_name_cache:
                    return self._model_name_cache[model_no_region]

        return None


# =============================================================================
# CLI Display Function
# =============================================================================


def display_cost_breakdown(breakdown: CostBreakdown) -> None:
    """
    Display cost breakdown in a formatted ASCII table.

    Prints a detailed report showing per-user and per-model token usage
    and costs, sorted by cost descending.

    Args:
        breakdown: CostBreakdown instance with per-user and per-model data.
    """
    if not breakdown.per_user:
        print('\nNo Bedrock usage found for the specified period.')
        return

    has_pricing = breakdown.cost_source != 'none'
    date_range = f'{breakdown.start_date.strftime("%Y-%m-%d")} to {breakdown.end_date.strftime("%Y-%m-%d")}'
    table_width = 156

    # Header
    print(f'\n{"=" * table_width}')
    if breakdown.cost_source == 'price_list':
        print(f'BEDROCK USAGE BY USER ({date_range}) - COSTS CALCULATED FROM PRICE LIST API')
    else:
        print(f'BEDROCK USAGE BY USER ({date_range}) - TOKEN COUNTS ONLY (pricing unavailable)')
    print(f'{"=" * table_width}')

    grand_total_calls = 0
    grand_total_input = 0
    grand_total_output = 0
    grand_total_cache_read = 0
    grand_total_cache_write = 0
    grand_total_cost = 0.0
    problem_models = set()

    # Sort users by cost (descending)
    user_list = sorted(
        breakdown.per_user.items(),
        key=lambda x: x[1].total_cost or 0,
        reverse=True,
    )

    for user_id, user_data in user_list:
        total_calls = sum(m.calls for m in user_data.models.values())
        total_input = sum(m.input_tokens for m in user_data.models.values())
        total_output = sum(m.output_tokens for m in user_data.models.values())
        total_cache_read = sum(m.cache_read_tokens for m in user_data.models.values())
        total_cache_write = sum(m.cache_write_tokens for m in user_data.models.values())
        total_cost = user_data.total_cost or 0.0

        print(f'\n{"-" * table_width}')
        print(f'User: {user_id}')
        print(f'{"-" * table_width}')
        print(f'{"Model":<50} {"Calls":<8} {"Input Tok":<14} {"Output Tok":<14} {"Cache Read":<16} {"Cache Write":<16} {"Cost":<12}')
        print(f'{"-" * table_width}')

        # Sort models by cost
        model_list = sorted(
            user_data.models.items(),
            key=lambda x: x[1].cost or 0,
            reverse=True,
        )

        for model_id, model_usage in model_list:
            if model_usage.cost is not None:
                print(f'{model_id:<50} {model_usage.calls:<8} '
                      f'{model_usage.input_tokens:<14,} {model_usage.output_tokens:<14,} '
                      f'{model_usage.cache_read_tokens:<16,} {model_usage.cache_write_tokens:<16,} ${model_usage.cost:<11.4f}')
            else:
                print(f'{model_id:<50} {model_usage.calls:<8} '
                      f'{model_usage.input_tokens:<14,} {model_usage.output_tokens:<14,} '
                      f'{model_usage.cache_read_tokens:<16,} {model_usage.cache_write_tokens:<16,} {"N/A":<12}')
                problem_models.add(model_id)

        print(f'{"-" * table_width}')
        if has_pricing:
            print(f'{"TOTAL":<50} {total_calls:<8} {total_input:<14,} '
                  f'{total_output:<14,} {total_cache_read:<16,} '
                  f'{total_cache_write:<16,} ${total_cost:<11.4f}')
        else:
            print(f'{"TOTAL":<50} {total_calls:<8} {total_input:<14,} '
                  f'{total_output:<14,} {total_cache_read:<16,} '
                  f'{total_cache_write:<16,} {"N/A":<12}')

        grand_total_calls += total_calls
        grand_total_input += total_input
        grand_total_output += total_output
        grand_total_cache_read += total_cache_read
        grand_total_cache_write += total_cache_write
        grand_total_cost += total_cost

    # Grand total
    print(f'\n{"=" * table_width}')
    print(f'GRAND TOTAL: {len(breakdown.per_user)} users, {grand_total_calls:,} calls')
    print(f'  Input tokens: {grand_total_input:,}, Output tokens: {grand_total_output:,}')
    if grand_total_cache_read > 0 or grand_total_cache_write > 0:
        print(f'  Cache read: {grand_total_cache_read:,}, Cache write: {grand_total_cache_write:,}')

    if has_pricing:
        print(f'TOTAL COST: ${grand_total_cost:.4f}')

    if problem_models:
        print(f'\nNote: Pricing not available for: {", ".join(sorted(problem_models))}')

    print(f'{"=" * table_width}')


def get_current_user(session: boto3.Session) -> Optional[str]:
    """
    Get the current AWS user's identity from STS.

    Extracts the username from the caller identity ARN.

    Args:
        session: boto3 Session with AWS credentials.

    Returns:
        Optional[str]: Username portion of the ARN, or None if unavailable.
    """
    try:
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        arn = identity.get('Arn', '')
        if '/' in arn:
            return arn.split('/')[-1]
        return None
    except Exception:
        return None


# =============================================================================
# Convenience Function for Simple Imports
# =============================================================================


def get_bedrock_costs(
    profile: Optional[str] = None,
    region: str = 'us-east-1',
    days: int = 30,
    start_date: Optional[Union[date, datetime]] = None,
    end_date: Optional[Union[date, datetime]] = None,
    verbose: bool = True,
) -> CostBreakdown:
    """
    Get Bedrock usage costs with minimal setup.

    This is a convenience function that creates a session and calculator internally.

    Args:
        profile: AWS profile name (optional)
        region: AWS region (default: us-east-1)
        days: Number of days to look back (default: 30, ignored if start_date provided)
        start_date: Explicit start date
        end_date: Explicit end date
        verbose: Print progress messages

    Returns:
        CostBreakdown with per-user and per-model cost data

    Example:
        from bedrock_usage import get_bedrock_costs

        # Simple usage
        result = get_bedrock_costs(days=7)
        print(f"Total cost: ${result.total_cost:.2f}")

        # With date range
        from datetime import date
        result = get_bedrock_costs(start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
    """
    session_kwargs = {}
    if profile:
        session_kwargs['profile_name'] = profile
    session = boto3.Session(**session_kwargs)

    calc = BedrockCostCalculator(session, region=region, verbose=verbose)
    return calc.get_usage(days=days, start_date=start_date, end_date=end_date)


def main(days=None, start_date=None, all_users=None):
    """
    Main CLI function for AWS Bedrock usage reporting.

    Can be called programmatically with parameters or via command-line arguments.

    Args:
        days: Number of days to look back (default: None, uses argparse value or 30)
        start_date: Start date string in 'YYYY-MM-DD' format (default: None, uses argparse value)
        all_users: Whether to show all users (default: None, uses argparse value or False)

    Examples:
        # CLI usage (from command line)
        python bedrock_usage.py --days 7
        python bedrock_usage.py --start-date 2026-01-01 --end-date 2026-01-31
        python bedrock_usage.py --profile my-profile --all

        # Programmatic usage (from Python code)
        from bedrock_usage import main

        # Use CLI args (when called from command line)
        main()

        # Override days
        main(days=7)

        # Override start_date
        main(start_date="2026-01-01")

        # Show all users programmatically
        main(all_users=True)

        # Show only current user
        main(all_users=False)

        # Combine parameters
        main(days=7, all_users=True)

    Note:
        For more flexible programmatic usage, consider using BedrockCostCalculator
        directly or the get_bedrock_costs() convenience function.
    """
    parser = argparse.ArgumentParser(description='Get AWS Bedrock usage per user with exact costs from invocation logs')
    parser.add_argument(
        '--profile',
        '-p',
        help='AWS profile name to use',
        default=None,
    )
    parser.add_argument(
        '--days',
        '-d',
        help='Number of days to look back (default: 30, ignored if --start-date is used)',
        type=int,
        default=30,
    )
    parser.add_argument(
        '--start-date',
        help='Start date in YYYY-MM-DD format (e.g., 2026-01-25)',
        type=str,
        default=None,
    )
    parser.add_argument(
        '--end-date',
        help='End date in YYYY-MM-DD format (e.g., 2026-01-29). Defaults to today if --start-date is used',
        type=str,
        default=None,
    )
    parser.add_argument(
        '--region',
        '-r',
        help='AWS region (default: us-east-1)',
        default='us-east-1',
    )
    parser.add_argument(
        '--json',
        '-j',
        action='store_true',
        help='Output raw JSON data',
    )
    parser.add_argument(
        '--all',
        '-a',
        action='store_true',
        help='Show all users (default: show only current user)',
    )
    parser.add_argument(
        '--user',
        '-u',
        help='Filter to a specific user (email or username)',
        default=None,
    )
    parser.add_argument(
        '--data-source',
        choices=['cost_explorer', 'price_list'],
        default='cost_explorer',
        help=("Data source for cost calculation: 'cost_explorer' "
              "(default, exact billing match) or 'price_list' "
              '(calculated from API pricing)'),
    )

    args = parser.parse_args()
    start_time = time.time()

    # Use function parameters if provided, otherwise use args
    effective_days = days if days is not None else args.days
    effective_start_date_str = start_date if start_date is not None else args.start_date
    effective_all = all_users if all_users is not None else args.all

    try:
        # Set up AWS session
        session_kwargs = {}
        if args.profile:
            session_kwargs['profile_name'] = args.profile
        session = boto3.Session(**session_kwargs)

        # Parse date range
        parsed_start_date = None
        end_date = None
        if effective_start_date_str:
            try:
                parsed_start_date = datetime.strptime(effective_start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"Error: Invalid start date format '{effective_start_date_str}'. "
                      'Use YYYY-MM-DD (e.g., 2026-01-25)')
                sys.exit(1)

            if args.end_date:
                try:
                    end_date = datetime.strptime(args.end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                except ValueError:
                    print(f"Error: Invalid end date format '{args.end_date}'. "
                          'Use YYYY-MM-DD (e.g., 2026-01-29)')
                    sys.exit(1)

        # Determine user filter
        user_filter = None
        if args.user:
            user_filter = args.user
            print(f'Filtering to user: {user_filter}')
        elif not effective_all:
            user_filter = get_current_user(session)
            if user_filter:
                print(f'Showing usage for: {user_filter} (use --all to see all users)')
            else:
                print('Warning: Could not detect current user. Showing all users.')

        # Create calculator and get usage
        calc = BedrockCostCalculator(session, region=args.region, verbose=True)

        try:
            breakdown = calc.get_usage(
                days=effective_days if not parsed_start_date else None,
                start_date=parsed_start_date,
                end_date=end_date,
                user_filter=user_filter,
            )
        except ValueError as e:
            if 'logging is not enabled' in str(e):
                print('\n' + '=' * 80)
                print('ERROR: Bedrock model invocation logging is not enabled.')
                print('=' * 80)
                print('\nThis tool requires Bedrock model invocation logging to be enabled')
                print('in order to provide accurate usage and cost data.')
                print('\nTo enable invocation logging:')
                print('  1. Go to AWS Console > Amazon Bedrock > Settings')
                print("  2. Enable 'Model invocation logging'")
                print('  3. Configure CloudWatch Logs as the destination')
                print('\nFor more information:')
                print('  https://docs.aws.amazon.com/bedrock/latest/userguide/'
                      'model-invocation-logging.html')
                print('=' * 80)
                sys.exit(1)
            raise

        if not breakdown.per_user:
            date_range_str = f'{breakdown.start_date.strftime("%Y-%m-%d")} to {breakdown.end_date.strftime("%Y-%m-%d")}'
            print(f'\nNo invocation logs found for the period {date_range_str}.')
            print('This could mean:')
            print('  - No Bedrock API calls were made in this period')
            print('  - Invocation logging was recently enabled')
            print('  - Logs have been deleted or expired')
            if user_filter:
                print(f"  - No usage found for user matching '{user_filter}'")
            sys.exit(0)

        # Output results
        if args.json:
            print(json.dumps(breakdown.to_dict(), indent=2))
        else:
            display_cost_breakdown(breakdown)

        # Print elapsed time
        elapsed = time.time() - start_time
        print(f'\nElapsed time: {elapsed:.2f} seconds')

    except NoCredentialsError:
        print('Error: AWS credentials not found.')
        print('Configure credentials via:')
        print('  - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)')
        print('  - AWS credentials file (~/.aws/credentials)')
        print('  - IAM role (if running on AWS)')
        sys.exit(1)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f'AWS Error ({error_code}): {error_msg}')
        if 'AccessDenied' in error_code:
            print('\nEnsure your IAM user/role has required permissions:')
            print('  - bedrock:GetModelInvocationLoggingConfiguration')
            print('  - logs:FilterLogEvents')
            print('  - pricing:GetProducts (for cost calculation)')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    # for calculating all users starting <start date>
    # main(start_date="2026-02-01", all_users=True)
    main()
