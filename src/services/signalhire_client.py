"""SignalHire API client service for interacting with SignalHire's API.

This service handles API authentication, rate limiting, and provides methods
for searching prospects and checking credit usage.
"""

import asyncio
import json
import logging
import os
import random
import uuid
from collections import deque
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import httpx
import structlog


@dataclass
class APIResponse:
    """Wrapper for API responses."""
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    status_code: int | None = None
    credits_used: int = 0
    credits_remaining: int | None = None


class SignalHireAPIError(Exception):
    """Custom exception for SignalHire API errors."""
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimiter:
    """Enhanced rate limiter with daily usage tracking and API limit enforcement."""
    def __init__(self, max_requests: int = 600, time_window: int = 60, daily_limit: int = 100):
        self.max_requests = max_requests
        self.time_window = time_window
        self.daily_limit = daily_limit  # API daily limit (100 reveals/day)
        self.requests = []
        self.daily_usage = {"credits_used": 0, "reveals": 0, "last_reset": datetime.now().date()}

    async def _check_daily_usage(self) -> dict:
        """Check current daily usage from operation tracking."""
        try:
            from pathlib import Path

            # Try to load from local operation tracking
            operations_dir = Path.home() / '.signalhire-agent' / 'operations'
            if operations_dir.exists():
                usage_data = {"credits_used": 0, "reveals": 0}
                one_day_ago = datetime.now() - timedelta(days=1)

                for op_file in operations_dir.glob("*.json"):
                    try:
                        import json
                        with open(op_file) as f:
                            op_data = json.load(f)

                        created_time = datetime.fromisoformat(op_data.get('created_at', '').replace('Z', '+00:00'))
                        if created_time.replace(tzinfo=None) < one_day_ago:
                            continue

                        if op_data.get("type") == "reveal" and op_data.get("status") == "completed":
                            usage_data["reveals"] += 1
                            if op_data.get("results"):
                                usage_data["credits_used"] += op_data["results"].get("credits_used", 0)
                    except (ValueError, TypeError, json.JSONDecodeError):
                        continue

                return usage_data
        except (OSError, ImportError):
            pass

        return {"credits_used": 0, "reveals": 0}

    async def check_daily_limits(self) -> dict:
        """Check if daily limits are approaching or exceeded."""
        current_usage = await self._check_daily_usage()
        remaining_daily = max(0, self.daily_limit - current_usage["credits_used"])

        result = {
            "current_usage": current_usage["credits_used"],
            "daily_limit": self.daily_limit,
            "remaining": remaining_daily,
            "percentage_used": (current_usage["credits_used"] / self.daily_limit) * 100 if self.daily_limit > 0 else 0,
            "can_proceed": remaining_daily > 0,
            "warning_level": "none"
        }

        # Set warning levels
        if result["percentage_used"] >= 90:
            result["warning_level"] = "critical"
        elif result["percentage_used"] >= 75:
            result["warning_level"] = "high"
        elif result["percentage_used"] >= 50:
            result["warning_level"] = "moderate"

        return result

    async def wait_if_needed(self, credits_needed: int = 1) -> dict:
        """Wait if rate limit would be exceeded, with daily limit checking."""
        now = datetime.now()

        # Reset daily counter if it's a new day
        if now.date() != self.daily_usage["last_reset"]:
            self.daily_usage = {"credits_used": 0, "reveals": 0, "last_reset": now.date()}

        # Check daily limits first
        daily_status = await self.check_daily_limits()

        if credits_needed > daily_status["remaining"]:
            raise SignalHireAPIError(f"Insufficient daily credits. Need {credits_needed}, have {daily_status['remaining']} remaining")

        if not daily_status["can_proceed"]:
            raise SignalHireAPIError(f"Daily API limit exceeded ({self.daily_limit} credits/day). Current usage: {daily_status['current_usage']}")

        # Check per-minute rate limiting
        self.requests = [req_time for req_time in self.requests
                        if now - req_time < timedelta(seconds=self.time_window)]

        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Record this request
        self.requests.append(now)

        # Update daily usage tracking
        self.daily_usage["credits_used"] += credits_needed
        self.daily_usage["reveals"] += 1

        return daily_status


@dataclass
class QueueItem:
    """Represents an item in the processing queue."""
    id: str
    prospect_id: str
    priority: int = 1  # 1=normal, 2=high, 3=urgent
    added_at: datetime = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.added_at is None:
            self.added_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class RetryStrategy:
    """
    Advanced retry strategy with circuit breaker and error classification.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.25,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        jitter_range: float = 0.1,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter_range = jitter_range
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout

        # Circuit breaker state
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False

        # Error classification
        self.transient_errors = {408, 429, 500, 502, 503, 504}  # HTTP status codes
        self.client_errors = {400, 401, 403, 404, 422}  # Usually non-retryable
        self.server_errors = {500, 502, 503, 504}  # Usually retryable

        # Retry statistics
        self.retry_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "circuit_breaker_trips": 0,
            "error_counts": {}
        }

    def classify_error(self, status_code: int | None, error_message: str | None) -> str:
        """
        Classify the type of error for retry decision.
        Returns: 'transient', 'client', 'server', or 'unknown'
        """
        if status_code:
            if status_code in self.transient_errors:
                return "transient"
            if status_code in self.client_errors:
                return "client"
            if status_code in self.server_errors:
                return "server"

        # Check error message for known patterns
        if error_message:
            error_lower = error_message.lower()
            if any(keyword in error_lower for keyword in ["timeout", "connection", "network"]) or any(keyword in error_lower for keyword in ["rate limit", "too many requests"]):
                return "transient"
            if any(keyword in error_lower for keyword in ["unauthorized", "forbidden", "not found"]):
                return "client"

        return "unknown"

    def should_retry(self, attempt: int, status_code: int | None, error_message: str | None) -> bool:
        """
        Determine if a request should be retried based on error classification.
        """
        # Check circuit breaker
        if self.circuit_open:
            if self.last_failure_time and (datetime.now() - self.last_failure_time).total_seconds() > self.circuit_breaker_timeout:
                # Try to close the circuit
                self.circuit_open = False
                self.failure_count = 0
            else:
                return False

        # Check max retries
        if attempt >= self.max_retries:
            return False

        # Classify error and decide
        error_type = self.classify_error(status_code, error_message)

        # Never retry client errors (4xx except specific cases)
        if error_type == "client":
            return False

        # Always retry transient and server errors
        if error_type in ["transient", "server"]:
            return True

        # For unknown errors, be conservative and retry
        return attempt < 2

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt with exponential backoff and jitter.
        """
        # Exponential backoff
        delay = self.base_delay * (self.backoff_factor ** attempt)

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        jitter = random.uniform(-self.jitter_range, self.jitter_range) * delay
        delay += jitter

        # Ensure minimum delay
        return max(delay, 0.1)

    def record_attempt(self, success: bool, status_code: int | None = None, error_message: str | None = None):
        """
        Record the result of a retry attempt for analytics.
        """
        self.retry_stats["total_attempts"] += 1

        if success:
            self.retry_stats["successful_retries"] += 1
            # Reset circuit breaker on success
            self.failure_count = 0
            self.circuit_open = False
        else:
            self.retry_stats["failed_retries"] += 1
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            # Check if circuit breaker should open
            if self.failure_count >= self.circuit_breaker_threshold:
                self.circuit_open = True
                self.retry_stats["circuit_breaker_trips"] += 1

            # Track error types
            error_type = self.classify_error(status_code, error_message)
            self.retry_stats["error_counts"][error_type] = self.retry_stats["error_counts"].get(error_type, 0) + 1

    def get_stats(self) -> dict[str, Any]:
        """
        Get retry statistics and circuit breaker status.
        """
        return {
            "retry_stats": self.retry_stats.copy(),
            "circuit_breaker": {
                "open": self.circuit_open,
                "failure_count": self.failure_count,
                "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "threshold": self.circuit_breaker_threshold,
                "timeout": self.circuit_breaker_timeout
            },
            "configuration": {
                "max_retries": self.max_retries,
                "base_delay": self.base_delay,
                "max_delay": self.max_delay,
                "backoff_factor": self.backoff_factor
            }
        }

    def reset_stats(self):
        """Reset retry statistics."""
        self.retry_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "circuit_breaker_trips": 0,
            "error_counts": {}
        }


class BatchQueue:
    """
    Queue management system for batch operations within API limits.
    Handles queuing, prioritization, and automatic batching of prospect
    contact reveals while respecting API rate limits and daily quotas.
    """

    def __init__(self, max_batch_size: int = 10, max_daily_contacts: int = 100):
        self.queue: deque[QueueItem] = deque()
        self.processing: set[str] = set()  # Currently processing items
        self.completed: dict[str, QueueItem] = {}  # Successfully completed
        self.failed: dict[str, QueueItem] = {}  # Failed items
        self.max_batch_size = max_batch_size
        self.max_daily_contacts = max_daily_contacts
        self.daily_count = 0
        self.day_start = datetime.now().date()
        self.logger = structlog.get_logger(__name__)

    def reset_daily_count(self) -> None:
        """Reset daily contact count if it's a new day."""
        today = datetime.now().date()
        if today != self.day_start:
            self.daily_count = 0
            self.day_start = today
            self.logger.info("Daily contact count reset", new_day=today.isoformat())

    def add_item(self, prospect_id: str, priority: int = 1, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a prospect to the processing queue.
        Returns the queue item ID for tracking.
        """
        item_id = str(uuid.uuid4())
        item = QueueItem(
            id=item_id,
            prospect_id=prospect_id,
            priority=priority,
            metadata=metadata or {}
        )

        # Insert based on priority (higher priority = processed first)
        if priority >= 3:  # Urgent
            self.queue.appendleft(item)
        elif priority >= 2:  # High
            # Insert after other high priority items
            insert_pos = 0
            for i, existing_item in enumerate(self.queue):
                if existing_item.priority < 2:
                    insert_pos = i
                    break
            else:
                insert_pos = len(self.queue)
            self.queue.insert(insert_pos, item)
        else:  # Normal
            self.queue.append(item)

        self.logger.info(
            "Item added to queue",
            item_id=item_id,
            prospect_id=prospect_id,
            priority=priority,
            queue_size=len(self.queue)
        )

        return item_id

    def add_batch(self, prospect_ids: list[str], priority: int = 1, metadata: dict[str, Any] | None = None) -> list[str]:
        """
        Add multiple prospects to the queue.
        Returns list of queue item IDs.
        """
        item_ids = []
        for prospect_id in prospect_ids:
            item_id = self.add_item(prospect_id, priority, metadata)
            item_ids.append(item_id)

        self.logger.info(
            "Batch added to queue",
            batch_size=len(prospect_ids),
            priority=priority,
            total_queue_size=len(self.queue)
        )

        return item_ids

    def get_next_batch(self, batch_size: int | None = None) -> list[QueueItem]:
        """
        Get the next batch of items to process.
        Respects daily limits and returns items that can be processed.
        """
        self.reset_daily_count()

        if batch_size is None:
            batch_size = self.max_batch_size

        # Check daily limit
        available_slots = self.max_daily_contacts - self.daily_count
        if available_slots <= 0:
            self.logger.warning(
                "Daily contact limit reached",
                daily_count=self.daily_count,
                max_daily=self.max_daily_contacts
            )
            return []

        batch_size = min(batch_size, available_slots)
        batch = []

        while len(batch) < batch_size and self.queue:
            item = self.queue.popleft()

            # Skip if already processing or completed
            if item.id in self.processing or item.id in self.completed:
                continue

            # Check retry limit
            if item.retry_count >= item.max_retries:
                self.failed[item.id] = item
                self.logger.warning(
                    "Item exceeded max retries",
                    item_id=item.id,
                    prospect_id=item.prospect_id,
                    retry_count=item.retry_count
                )
                continue

            batch.append(item)
            self.processing.add(item.id)

        if batch:
            self.logger.info(
                "Batch prepared for processing",
                batch_size=len(batch),
                remaining_queue=len(self.queue),
                daily_count=self.daily_count
            )

        return batch

    def mark_completed(self, item_id: str, success: bool = True) -> None:
        """
        Mark an item as completed (success or failure).
        """
        if item_id in self.processing:
            self.processing.remove(item_id)

            if success:
                # Find the item and move to completed
                for item in list(self.queue) + list(self.completed.values()) + list(self.failed.values()):
                    if item.id == item_id:
                        self.completed[item_id] = item
                        self.daily_count += 1
                        break
            else:
                # Move back to queue for retry
                for item in list(self.completed.values()) + list(self.failed.values()):
                    if item.id == item_id:
                        item.retry_count += 1
                        if item.retry_count < item.max_retries:
                            self.queue.append(item)
                        else:
                            self.failed[item_id] = item
                        break

    def get_queue_stats(self) -> dict[str, Any]:
        """
        Get comprehensive queue statistics.
        """
        self.reset_daily_count()

        return {
            "queue_size": len(self.queue),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "daily_count": self.daily_count,
            "daily_limit": self.max_daily_contacts,
            "daily_remaining": max(0, self.max_daily_contacts - self.daily_count),
            "total_processed": len(self.completed) + len(self.failed),
            "success_rate": len(self.completed) / max(1, len(self.completed) + len(self.failed)) * 100,
            "timestamp": datetime.now().isoformat()
        }

    def clear_completed(self) -> int:
        """
        Clear completed items from memory.
        Returns number of items cleared.
        """
        cleared_count = len(self.completed)
        self.completed.clear()
        self.logger.info("Completed items cleared", cleared_count=cleared_count)
        return cleared_count


class SignalHireClient:
    """
    SignalHire API client for searching prospects and managing credits.
    Note: This client handles API operations only. For bulk contact reveals
    (1000+ contacts), use the browser automation service instead.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://www.signalhire.com",
        api_prefix: str = "/api/v1",
    ):
        # Allow environment variables to override defaults
        env_base = os.getenv("SIGNALHIRE_API_BASE_URL")
        env_prefix = os.getenv("SIGNALHIRE_API_PREFIX")
        self.api_key = api_key or os.getenv("SIGNALHIRE_API_KEY")
        self.base_url = (env_base or base_url).rstrip("/")
        prefix_value = env_prefix if env_prefix is not None else api_prefix
        self.api_prefix = ("/" + prefix_value.strip("/")) if prefix_value else ""
        self.rate_limiter = RateLimiter(max_requests=600, time_window=60)  # 600/minute
        self.session: httpx.AsyncClient | None = None
        self._credits_cache: dict[str, Any] | None = None
        self._cache_timestamp: datetime | None = None
        self._cache_ttl = 300  # 5 minutes
        # Enhanced controls
        self.max_concurrency: int = 5
        self.max_retries: int = 3
        self.retry_backoff_base: float = 0.25
        self.logger = structlog.get_logger(__name__)
        # Queue management
        self.batch_queue = BatchQueue(max_batch_size=10, max_daily_contacts=100)
        # Enhanced retry strategy
        self.retry_strategy = RetryStrategy(
            max_retries=self.max_retries,
            base_delay=self.retry_backoff_base,
            max_delay=30.0,
            circuit_breaker_threshold=10,
            circuit_breaker_timeout=120.0
        )
        # Search API concurrency limit (max 3 concurrent requests)
        self._search_semaphore = asyncio.Semaphore(3)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()

    async def start_session(self) -> None:
        """Start the HTTP session."""
        if self.session is None:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "SignalHire-Agent/1.0",
            }

            if self.api_key:
                headers["apikey"] = self.api_key

            self.session = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0
            )

    async def close_session(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make an API request with rate limiting and error handling."""
        if not self.session:
            await self.start_session()

        # Apply rate limiting with daily usage tracking
        daily_status = await self.rate_limiter.wait_if_needed()

        # Log warnings for high daily usage
        if daily_status["warning_level"] in ["high", "critical"]:
            logger = logging.getLogger(__name__)
            if daily_status["warning_level"] == "critical":
                logger.warning(f"CRITICAL: Daily API limit nearly exceeded ({daily_status['percentage_used']:.1f}%)")
            else:
                logger.info(f"High daily usage: {daily_status['percentage_used']:.1f}% of daily limit used")

        endpoint_path = "/" + endpoint.lstrip("/")
        url = f"{self.base_url}{self.api_prefix}{endpoint_path}"

        try:
            response = await self.session.request(method, url, **kwargs)

            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {"raw_response": response.text}

            # Check for success
            if response.is_success:
                # Extract credits info if available
                credits_used = data.get("credits_used", 0)
                # Prefer header X-Credits-Left when present
                credits_remaining_header = response.headers.get("X-Credits-Left") or response.headers.get("x-credits-left")
                credits_remaining = (
                    int(credits_remaining_header)
                    if credits_remaining_header and credits_remaining_header.isdigit()
                    else data.get("credits_remaining")
                )

                return APIResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code,
                    credits_used=credits_used,
                    credits_remaining=credits_remaining
                )
            error_message = data.get("error") or data.get("message") or response.text or f"HTTP {response.status_code}"

            # Enhance error messages for specific HTTP status codes
            if response.status_code == 429:
                # Rate limit exceeded
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        retry_seconds = int(retry_after)
                        error_message = f"Rate limit exceeded. Please wait {retry_seconds} seconds before retrying."
                    except ValueError:
                        error_message = "Rate limit exceeded. Please wait before retrying."
                else:
                    error_message = "Rate limit exceeded. Please reduce request frequency or wait before retrying."

                # Add helpful suggestions
                error_message += " Consider using browser mode for bulk operations or reducing batch size."

            elif response.status_code == 402:
                # Payment required (insufficient credits)
                error_message = "Insufficient credits. Please check your account balance or purchase additional credits."

            elif response.status_code == 403:
                # Forbidden - could be authentication or permissions
                if "api" in error_message.lower():
                    error_message = "API access denied. Please check your API key and permissions."
                else:
                    error_message = "Access forbidden. Please check your credentials and account status."

            elif response.status_code == 404:
                # Not found
                error_message = "Resource not found. Please check the prospect ID or endpoint URL."

            elif response.status_code >= 500:
                # Server errors
                error_message = f"Server error ({response.status_code}). This is usually temporary - please try again later."

            return APIResponse(
                success=False,
                error=error_message,
                status_code=response.status_code,
                data=data
            )

        except httpx.TimeoutException:
            return APIResponse(
                success=False,
                error="Request timed out. This may be due to network issues or high server load. Please try again.",
                status_code=408
            )
        except httpx.ConnectError:
            return APIResponse(
                success=False,
                error="Connection failed. Please check your internet connection and try again.",
                status_code=None
            )
        except httpx.RequestError as e:
            error_msg = str(e)
            if "ssl" in error_msg.lower():
                enhanced_error = "SSL connection error. This may be due to network restrictions or certificate issues."
            elif "dns" in error_msg.lower():
                enhanced_error = "DNS resolution failed. Please check your network connection and try again."
            else:
                enhanced_error = f"Network request failed: {error_msg}. Please check your connection and try again."

            return APIResponse(
                success=False,
                error=enhanced_error,
                status_code=None
            )

    async def check_credits(self) -> APIResponse:
        """Check current credit balance and usage."""
        # Check cache first
        if (self._credits_cache and self._cache_timestamp and
            datetime.now() - self._cache_timestamp < timedelta(seconds=self._cache_ttl)):
            return APIResponse(
                success=True,
                data=self._credits_cache
            )

        response = await self._make_request("GET", "/credits")

        # Cache successful responses
        if response.success and response.data:
            self._credits_cache = response.data
            self._cache_timestamp = datetime.now()

        return response

    async def search_prospects(self, search_criteria: dict[str, Any],
                             size: int = 25) -> APIResponse:
        """
        Search for prospects using the SignalHire Search API.
        Supports filtering by currentTitle, location, keywords, and other criteria.
        Returns profiles with scrollId for pagination if more results available.
        Args:
            search_criteria: Dict with search filters (currentTitle, location, keywords, etc.)
            size: Number of results per batch (1-100, default 25)
        Returns:
            APIResponse with profiles array, total count, and scrollId if applicable
        """
        # Validate size parameter
        size = max(1, min(size, 100))

        # Prepare search data
        search_data = {
            "size": size,
            **search_criteria
        }

        # Enforce single-concurrency per client for Search API
        async with self._search_semaphore:
            return await self._make_request("POST", "/candidate/searchByQuery", json=search_data)

    async def scroll_search(self, request_id: int, scroll_id: str) -> APIResponse:
        """Fetch next batch using POST /candidate/scrollSearch/{requestId} with JSON body {scrollId}."""
        endpoint = f"/candidate/scrollSearch/{request_id}"
        body = {"scrollId": scroll_id}
        async with self._search_semaphore:
            return await self._make_request("POST", endpoint, json=body)

    async def get_prospect_details(self, prospect_id: str) -> APIResponse:
        """Get detailed information for a specific prospect."""
        return await self._make_request("GET", f"/prospects/{prospect_id}")

    async def reveal_contact_by_identifier(self, identifier: str, callback_url: str) -> APIResponse:
        """
        Reveal contact information using SignalHire's Person API.
        Args:
            identifier: LinkedIn URL, email, phone, or 32-character UID
            callback_url: URL where results will be sent
        Returns:
            APIResponse with request ID if successful
        """
        data = {
            "items": [identifier],
            "callbackUrl": callback_url
        }

        return await self._make_request("POST", "/candidate/search", json=data)

    async def reveal_contact(self, prospect_id: str) -> APIResponse:
        """Reveal contact for a single prospect with retry logic (compatibility path)."""
        attempt = 0
        while True:
            # Circuit breaker check
            if self.retry_strategy.circuit_open:
                self.logger.warning("Circuit breaker open, skipping request", prospect_id=prospect_id, attempt=attempt)
                return APIResponse(success=False, error="Circuit breaker open - too many recent failures", status_code=503)

            resp = await self._make_request("POST", f"/prospects/{prospect_id}/reveal")
            attempt += 1
            self.retry_strategy.record_attempt(resp.success, resp.status_code, resp.error)

            if resp.success:
                if attempt > 1:
                    self.logger.info("Request succeeded after retry", prospect_id=prospect_id, attempts=attempt, final_status=resp.status_code)
                return resp

            if not self.retry_strategy.should_retry(attempt, resp.status_code, resp.error):
                error_type = self.retry_strategy.classify_error(resp.status_code, resp.error)
                self.logger.warning("Request failed permanently", prospect_id=prospect_id, attempts=attempt, status_code=resp.status_code, error_type=error_type, error=resp.error)
                return resp

            delay = self.retry_strategy.calculate_delay(attempt)
            self.logger.info("Retrying request", prospect_id=prospect_id, attempt=attempt, max_retries=self.retry_strategy.max_retries, delay=round(delay, 2), status_code=resp.status_code, error=resp.error)
            await asyncio.sleep(delay)

    async def batch_reveal_contacts(
        self,
        prospect_ids: list[str],
        batch_size: int = 10,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> list[APIResponse]:
        """
        Reveal contacts for multiple prospects in batches with enhanced progress reporting.
        Limited to API constraints (~100 total). For larger operations,
        use browser automation service.
        """
        # Validate inputs
        if not isinstance(prospect_ids, list) or any(not isinstance(p, str) for p in prospect_ids):
            raise SignalHireAPIError("prospect_ids must be a list of strings")
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise SignalHireAPIError("batch_size must be a positive integer")

        total = len(prospect_ids)
        if total > 100:
            raise SignalHireAPIError(
                "API batch reveal limited to 100 prospects. Use browser automation for larger batches."
            )

        # Credit pre-check (assume 1 credit per reveal)
        try:
            credits_response = await self.check_credits()
            remaining = (credits_response.data or {}).get("credits_remaining") if credits_response.success else None
            if isinstance(remaining, int) and remaining < total:
                raise SignalHireAPIError(
                    f"Insufficient credits: need {total}, have {remaining}",
                    status_code=402,
                    response_data={"needed": total, "remaining": remaining},
                )
        except SignalHireAPIError:
            # Propagate credit errors
            raise
        except Exception as e:
            # If credits check fails for other reasons, proceed but log the issue
            self.logger.warning("Credit pre-check failed", error=str(e))

        # Enhanced progress tracking
        start_time = datetime.now()
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrency)

        # Progress statistics
        stats = {
            "total": total,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "start_time": start_time,
            "last_update": start_time,
            "batch_size": batch_size,
            "errors": [],
            "estimated_completion": None
        }

        async def wrapped_reveal(pid: str) -> APIResponse:
            async with semaphore:
                try:
                    result = await self.reveal_contact(pid)

                    # Update statistics
                    stats["processed"] += 1
                    if result.success:
                        stats["successful"] += 1
                    else:
                        stats["failed"] += 1
                        if result.error:
                            stats["errors"].append({
                                "prospect_id": pid,
                                "error": result.error,
                                "status_code": result.status_code
                            })

                    # Calculate progress metrics
                    elapsed = (datetime.now() - start_time).total_seconds()
                    success_rate = stats["successful"] / stats["processed"] if stats["processed"] > 0 else 0
                    avg_time_per_contact = elapsed / stats["processed"] if stats["processed"] > 0 else 0
                    remaining_contacts = total - stats["processed"]

                    # Estimate completion time
                    if avg_time_per_contact > 0:
                        estimated_remaining = remaining_contacts * avg_time_per_contact
                        stats["estimated_completion"] = datetime.now() + timedelta(seconds=estimated_remaining)

                    # Enhanced progress report
                    progress_data = {
                        "current": stats["processed"],
                        "total": total,
                        "successful": stats["successful"],
                        "failed": stats["failed"],
                        "success_rate": round(success_rate * 100, 1),
                        "elapsed_seconds": round(elapsed, 1),
                        "avg_time_per_contact": round(avg_time_per_contact, 2),
                        "estimated_completion": stats["estimated_completion"].isoformat() if stats["estimated_completion"] else None,
                        "remaining_contacts": remaining_contacts,
                        "batch_size": batch_size,
                        "recent_errors": stats["errors"][-3:] if stats["errors"] else [],  # Last 3 errors
                        "credits_used": stats["successful"],
                        "credits_remaining": remaining
                    }

                    # Call progress callback if provided
                    if progress_callback:
                        with suppress(Exception):
                            await progress_callback(progress_data)

                    return result

                except Exception as ex:
                    # Update failure statistics
                    stats["processed"] += 1
                    stats["failed"] += 1
                    stats["errors"].append({
                        "prospect_id": pid,
                        "error": str(ex),
                        "status_code": None
                    })

                    # Return error response
                    return APIResponse(success=False, error=str(ex), data={"prospect_id": pid})

        # Process in smaller batches to respect rate limits
        for i in range(0, total, batch_size):
            batch = prospect_ids[i : i + batch_size]
            batch_results = await asyncio.gather(*(wrapped_reveal(pid) for pid in batch))
            results.extend(batch_results)

            # Log batch completion
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            self.logger.info(
                "Batch completed",
                batch=batch_num,
                total_batches=total_batches,
                batch_successful=sum(1 for r in batch_results if r.success),
                batch_failed=sum(1 for r in batch_results if not r.success)
            )

        # Final progress report
        total_elapsed = (datetime.now() - start_time).total_seconds()
        final_success_rate = stats["successful"] / total if total > 0 else 0

        self.logger.info(
            "Batch reveal completed",
            total=total,
            successful=stats["successful"],
            failed=stats["failed"],
            success_rate=round(final_success_rate * 100, 1),
            total_time=round(total_elapsed, 1),
            avg_time_per_contact=round(total_elapsed / total, 2) if total > 0 else 0,
            credits_used=stats["successful"]
        )

        return results

    async def get_search_suggestions(self, query: str) -> APIResponse:
        """Get search suggestions for companies, titles, or locations."""
        params = {"q": query}
        return await self._make_request("GET", "/suggestions", params=params)

    async def validate_api_key(self) -> bool:
        """Validate the current API key."""
        response = await self.check_credits()
        return response.success

    def invalidate_credits_cache(self) -> None:
        """Invalidate the credits cache to force a fresh check."""
        self._credits_cache = None
        self._cache_timestamp = None

    def get_retry_stats(self) -> dict[str, Any]:
        """
        Get comprehensive retry statistics and circuit breaker status.
        """
        return self.retry_strategy.get_stats()

    def reset_retry_stats(self):
        """
        Reset retry statistics (useful for testing or fresh monitoring periods).
        """
        self.retry_strategy.reset_stats()
        self.logger.info("Retry statistics reset")

    # Queue Management Methods

    def queue_prospect(self, prospect_id: str, priority: int = 1, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a single prospect to the processing queue.
        Returns queue item ID for tracking.
        """
        return self.batch_queue.add_item(prospect_id, priority, metadata)

    def queue_batch(self, prospect_ids: list[str], priority: int = 1, metadata: dict[str, Any] | None = None) -> list[str]:
        """
        Add multiple prospects to the processing queue.
        Returns list of queue item IDs.
        """
        return self.batch_queue.add_batch(prospect_ids, priority, metadata)

    async def process_queue_batch(
        self,
        batch_size: int | None = None,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None
    ) -> dict[str, Any]:
        """
        Process the next batch from the queue.
        Returns processing results and statistics.
        """
        batch = self.batch_queue.get_next_batch(batch_size)

        if not batch:
            return {
                "processed": 0,
                "message": "No items available for processing",
                "queue_stats": self.batch_queue.get_queue_stats()
            }

        # Extract prospect IDs for processing
        prospect_ids = [item.prospect_id for item in batch]
        item_ids = [item.id for item in batch]

        self.logger.info(
            "Processing queue batch",
            batch_size=len(batch),
            prospect_ids=prospect_ids[:5],  # Log first 5 for debugging
            total_in_batch=len(prospect_ids)
        )

        # Process the batch using existing batch_reveal_contacts method
        results = await self.batch_reveal_contacts(
            prospect_ids,
            batch_size=len(prospect_ids),
            progress_callback=progress_callback
        )

        # Update queue status based on results
        for i, (item_id, result) in enumerate(zip(item_ids, results, strict=False)):
            success = result.success
            self.batch_queue.mark_completed(item_id, success)

            if not success:
                self.logger.warning(
                    "Queue item failed",
                    item_id=item_id,
                    prospect_id=prospect_ids[i],
                    error=result.error
                )

        # Return comprehensive results
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        return {
            "processed": len(results),
            "successful": len(successful_results),
            "failed": len(failed_results),
            "credits_used": sum(r.credits_used for r in successful_results),
            "queue_stats": self.batch_queue.get_queue_stats(),
            "results": [
                {
                    "prospect_id": prospect_ids[i],
                    "success": result.success,
                    "error": result.error if not result.success else None,
                    "credits_used": result.credits_used
                }
                for i, result in enumerate(results)
            ]
        }

    async def process_queue_until_empty(
        self,
        batch_size: int | None = None,
        max_batches: int | None = None,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
        batch_delay: float = 1.0
    ) -> dict[str, Any]:
        """
        Process the entire queue until empty or limits reached.
        Args:
            batch_size: Size of each processing batch
            max_batches: Maximum number of batches to process (None = unlimited)
            progress_callback: Callback for progress updates
            batch_delay: Delay between batches in seconds
        Returns:
            Comprehensive processing statistics
        """
        total_processed = 0
        total_successful = 0
        total_failed = 0
        total_credits_used = 0
        batches_processed = 0
        start_time = datetime.now()

        self.logger.info("Starting queue processing", queue_size=self.batch_queue.queue.qsize())

        while True:
            # Check if we've reached the batch limit
            if max_batches and batches_processed >= max_batches:
                self.logger.info("Reached maximum batch limit", batches_processed=batches_processed)
                break

            # Check if queue is empty
            if not self.batch_queue.queue:
                self.logger.info("Queue is empty, processing complete")
                break

            # Process next batch
            batch_result = await self.process_queue_batch(batch_size, progress_callback)

            if batch_result["processed"] == 0:
                # No items were processed (likely due to daily limits)
                self.logger.info("No items processed, likely due to limits")
                break

            # Update totals
            total_processed += batch_result["processed"]
            total_successful += batch_result["successful"]
            total_failed += batch_result["failed"]
            total_credits_used += batch_result["credits_used"]
            batches_processed += 1

            # Log batch completion
            self.logger.info(
                "Batch completed",
                batch=batches_processed,
                processed=batch_result["processed"],
                successful=batch_result["successful"],
                failed=batch_result["failed"],
                credits_used=batch_result["credits_used"]
            )

            # Delay between batches to respect rate limits
            if batch_delay > 0:
                await asyncio.sleep(batch_delay)

        # Calculate final statistics
        total_time = (datetime.now() - start_time).total_seconds()
        success_rate = total_successful / max(1, total_processed) * 100

        final_stats = {
            "total_processed": total_processed,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate": round(success_rate, 1),
            "total_credits_used": total_credits_used,
            "batches_processed": batches_processed,
            "total_time_seconds": round(total_time, 1),
            "avg_time_per_contact": round(total_time / max(1, total_processed), 2),
            "final_queue_stats": self.batch_queue.get_queue_stats(),
            "completion_timestamp": datetime.now().isoformat()
        }

        self.logger.info(
            "Queue processing completed",
            **final_stats
        )

        return final_stats

    def get_queue_status(self) -> dict[str, Any]:
        """
        Get current queue status and statistics.
        """
        return self.batch_queue.get_queue_stats()

    def clear_completed_queue_items(self) -> int:
        """
        Clear completed items from the queue to free memory.
        Returns number of items cleared.
        """
        return self.batch_queue.clear_completed()

    # Compatibility shim for CLI reveal_commands expecting bulk_reveal(RevealOp)
    async def bulk_reveal(self, operation, progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None) -> dict[str, Any]:
        """
        Bulk reveal contacts with enhanced progress reporting.
        Compatibility method for CLI operations with detailed progress tracking.
        """
        prospect_ids = getattr(operation, "prospect_ids", [])
        batch_size = getattr(operation, "batch_size", 10)

        # Use enhanced batch_reveal_contacts with progress reporting
        results = await self.batch_reveal_contacts(
            prospect_ids,
            batch_size=batch_size,
            progress_callback=progress_callback
        )

        success = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        # Calculate final statistics
        total_credits_used = sum(r.credits_used for r in results if r.success)

        return {
            "operation_id": getattr(operation, "id", "op_unknown"),
            "total_prospects": len(prospect_ids),
            "revealed_count": len(success),
            "failed_count": len(failed),
            "success_rate": round(len(success) / len(prospect_ids) * 100, 1) if prospect_ids else 0,
            "prospects": [
                {
                    "id": getattr(r.data or {}, "prospect_id", None) or prospect_ids[i] if i < len(prospect_ids) else None,
                    "status": "success" if r.success else "failed",
                    "error": r.error if not r.success else None
                }
                for i, r in enumerate(results)
            ],
            "credits_used": total_credits_used,
            "errors": [
                {
                    "prospect_id": getattr(r.data or {}, "prospect_id", None) or prospect_ids[i] if i < len(prospect_ids) else None,
                    "error": r.error
                }
                for i, r in enumerate(results) if not r.success
            ]
        }


# Utility functions

async def create_signalhire_client(api_key: str | None = None) -> SignalHireClient:
    """Create and initialize a SignalHire client."""
    client = SignalHireClient(api_key=api_key)
    await client.start_session()
    return client


async def test_api_connection(api_key: str | None = None) -> bool:
    """Test the API connection and authentication."""
    async with SignalHireClient(api_key=api_key) as client:
        return await client.validate_api_key()


# Example usage patterns for documentation

async def example_search_workflow():
    """Example of a complete search and reveal workflow using the API."""
    async with SignalHireClient(api_key="your-api-key") as client:
        # Check credits first
        credits_response = await client.check_credits()
        if not credits_response.success:
            print(f"Failed to check credits: {credits_response.error}")
            return

        print(f"Available credits: {credits_response.data}")

        # Search for prospects
        search_criteria = {
            "title": "Software Engineer",
            "location": "San Francisco",
            "company_size": "50-200"
        }

        search_response = await client.search_prospects(search_criteria, limit=50)
        if not search_response.success:
            print(f"Search failed: {search_response.error}")
            return

        prospects = search_response.data.get("prospects", [])
        print(f"Found {len(prospects)} prospects")

        # Reveal contacts for first 10 prospects
        prospect_ids = [p["id"] for p in prospects[:10]]
        reveal_results = await client.batch_reveal_contacts(prospect_ids)

        successful_reveals = [r for r in reveal_results if r.success]
        print(f"Successfully revealed {len(successful_reveals)} contacts")


if __name__ == "__main__":
    # Example usage
    asyncio.run(example_search_workflow())


@dataclass
class APIResponse:
    """Wrapper for API responses."""
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    status_code: int | None = None
    credits_used: int = 0
    credits_remaining: int | None = None


class SignalHireAPIError(Exception):
    """Custom exception for SignalHire API errors."""
    def __init__(self, message: str, status_code: int | None = None, response_data: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RateLimiter:
    """Enhanced rate limiter with daily usage tracking and API limit enforcement."""
    def __init__(self, max_requests: int = 600, time_window: int = 60, daily_limit: int = 100):
        self.max_requests = max_requests
        self.time_window = time_window
        self.daily_limit = daily_limit  # API daily limit (100 reveals/day)
        self.requests = []
        self.daily_usage = {"credits_used": 0, "reveals": 0, "last_reset": datetime.now().date()}

    async def _check_daily_usage(self) -> dict:
        """Check current daily usage from operation tracking."""
        try:
            from pathlib import Path

            # Try to load from local operation tracking
            operations_dir = Path.home() / '.signalhire-agent' / 'operations'
            if operations_dir.exists():
                usage_data = {"credits_used": 0, "reveals": 0}
                one_day_ago = datetime.now() - timedelta(days=1)

                for op_file in operations_dir.glob("*.json"):
                    try:
                        import json
                        with open(op_file) as f:
                            op_data = json.load(f)

                        created_time = datetime.fromisoformat(op_data.get('created_at', '').replace('Z', '+00:00'))
                        if created_time.replace(tzinfo=None) < one_day_ago:
                            continue

                        if op_data.get("type") == "reveal" and op_data.get("status") == "completed":
                            usage_data["reveals"] += 1
                            if op_data.get("results"):
                                usage_data["credits_used"] += op_data["results"].get("credits_used", 0)
                    except Exception:
                        continue

                return usage_data
        except Exception:
            pass

        return {"credits_used": 0, "reveals": 0}

    async def check_daily_limits(self) -> dict:
        """Check if daily limits are approaching or exceeded."""
        current_usage = await self._check_daily_usage()
        remaining_daily = max(0, self.daily_limit - current_usage["credits_used"])

        result = {
            "current_usage": current_usage["credits_used"],
            "daily_limit": self.daily_limit,
            "remaining": remaining_daily,
            "percentage_used": (current_usage["credits_used"] / self.daily_limit) * 100 if self.daily_limit > 0 else 0,
            "can_proceed": remaining_daily > 0,
            "warning_level": "none"
        }

        # Set warning levels
        if result["percentage_used"] >= 90:
            result["warning_level"] = "critical"
        elif result["percentage_used"] >= 75:
            result["warning_level"] = "high"
        elif result["percentage_used"] >= 50:
            result["warning_level"] = "moderate"

        return result

    async def wait_if_needed(self, credits_needed: int = 1) -> dict:
        """Wait if rate limit would be exceeded, with daily limit checking."""
        now = datetime.now()

        # Reset daily counter if it's a new day
        if now.date() != self.daily_usage["last_reset"]:
            self.daily_usage = {"credits_used": 0, "reveals": 0, "last_reset": now.date()}

        # Check daily limits first
        daily_status = await self.check_daily_limits()

        if credits_needed > daily_status["remaining"]:
            raise Exception(f"Insufficient daily credits. Need {credits_needed}, have {daily_status['remaining']} remaining")

        if not daily_status["can_proceed"]:
            raise Exception(f"Daily API limit exceeded ({self.daily_limit} credits/day). Current usage: {daily_status['current_usage']}")

        # Check per-minute rate limiting
        self.requests = [req_time for req_time in self.requests
                        if now - req_time < timedelta(seconds=self.time_window)]

        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Record this request
        self.requests.append(now)

        # Update daily usage tracking
        self.daily_usage["credits_used"] += credits_needed
        self.daily_usage["reveals"] += 1

        return daily_status


@dataclass
class QueueItem:
    """Represents an item in the processing queue."""
    id: str
    prospect_id: str
    priority: int = 1  # 1=normal, 2=high, 3=urgent
    added_at: datetime = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.added_at is None:
            self.added_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class RetryStrategy:
    """
    Advanced retry strategy with circuit breaker and error classification.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.25,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        jitter_range: float = 0.1,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter_range = jitter_range
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout

        # Circuit breaker state
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False

        # Error classification
        self.transient_errors = {408, 429, 500, 502, 503, 504}  # HTTP status codes
        self.client_errors = {400, 401, 403, 404, 422}  # Usually non-retryable
        self.server_errors = {500, 502, 503, 504}  # Usually retryable

        # Retry statistics
        self.retry_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "circuit_breaker_trips": 0,
            "error_counts": {}
        }

    def classify_error(self, status_code: int | None, error_message: str | None) -> str:
        """
        Classify the type of error for retry decision.
        
        Returns: 'transient', 'client', 'server', or 'unknown'
        """
        if status_code:
            if status_code in self.transient_errors:
                return "transient"
            if status_code in self.client_errors:
                return "client"
            if status_code in self.server_errors:
                return "server"

        # Check error message for known patterns
        if error_message:
            error_lower = error_message.lower()
            if any(keyword in error_lower for keyword in ["timeout", "connection", "network"]) or any(keyword in error_lower for keyword in ["rate limit", "too many requests"]):
                return "transient"
            if any(keyword in error_lower for keyword in ["unauthorized", "forbidden", "not found"]):
                return "client"

        return "unknown"

    def should_retry(self, attempt: int, status_code: int | None, error_message: str | None) -> bool:
        """
        Determine if a request should be retried based on error classification.
        """
        # Check circuit breaker
        if self.circuit_open:
            if self.last_failure_time and (datetime.now() - self.last_failure_time).total_seconds() > self.circuit_breaker_timeout:
                # Try to close the circuit
                self.circuit_open = False
                self.failure_count = 0
            else:
                return False

        # Check max retries
        if attempt >= self.max_retries:
            return False

        # Classify error and decide
        error_type = self.classify_error(status_code, error_message)

        # Never retry client errors (4xx except specific cases)
        if error_type == "client":
            return False

        # Always retry transient and server errors
        if error_type in ["transient", "server"]:
            return True

        # For unknown errors, be conservative and retry
        return attempt < 2

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next retry attempt with exponential backoff and jitter.
        """
        # Exponential backoff
        delay = self.base_delay * (self.backoff_factor ** attempt)

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        jitter = random.uniform(-self.jitter_range, self.jitter_range) * delay
        delay += jitter

        # Ensure minimum delay
        delay = max(delay, 0.1)

        return delay

    def record_attempt(self, success: bool, status_code: int | None = None, error_message: str | None = None):
        """
        Record the result of a retry attempt for analytics.
        """
        self.retry_stats["total_attempts"] += 1

        if success:
            self.retry_stats["successful_retries"] += 1
            # Reset circuit breaker on success
            self.failure_count = 0
            self.circuit_open = False
        else:
            self.retry_stats["failed_retries"] += 1
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            # Check if circuit breaker should open
            if self.failure_count >= self.circuit_breaker_threshold:
                self.circuit_open = True
                self.retry_stats["circuit_breaker_trips"] += 1

            # Track error types
            error_type = self.classify_error(status_code, error_message)
            self.retry_stats["error_counts"][error_type] = self.retry_stats["error_counts"].get(error_type, 0) + 1

    def get_stats(self) -> dict[str, Any]:
        """
        Get retry statistics and circuit breaker status.
        """
        return {
            "retry_stats": self.retry_stats.copy(),
            "circuit_breaker": {
                "open": self.circuit_open,
                "failure_count": self.failure_count,
                "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "threshold": self.circuit_breaker_threshold,
                "timeout": self.circuit_breaker_timeout
            },
            "configuration": {
                "max_retries": self.max_retries,
                "base_delay": self.base_delay,
                "max_delay": self.max_delay,
                "backoff_factor": self.backoff_factor
            }
        }

    def reset_stats(self):
        """Reset retry statistics."""
        self.retry_stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "circuit_breaker_trips": 0,
            "error_counts": {}
        }


class BatchQueue:
    """
    Queue management system for batch operations within API limits.
    
    Handles queuing, prioritization, and automatic batching of prospect
    contact reveals while respecting API rate limits and daily quotas.
    """

    def __init__(self, max_batch_size: int = 10, max_daily_contacts: int = 100):
        self.queue: deque[QueueItem] = deque()
        self.processing: set[str] = set()  # Currently processing items
        self.completed: dict[str, QueueItem] = {}  # Successfully completed
        self.failed: dict[str, QueueItem] = {}  # Failed items
        self.max_batch_size = max_batch_size
        self.max_daily_contacts = max_daily_contacts
        self.daily_count = 0
        self.day_start = datetime.now().date()
        self.logger = structlog.get_logger(__name__)

    def reset_daily_count(self) -> None:
        """Reset daily contact count if it's a new day."""
        today = datetime.now().date()
        if today != self.day_start:
            self.daily_count = 0
            self.day_start = today
            self.logger.info("Daily contact count reset", new_day=today.isoformat())

    def add_item(self, prospect_id: str, priority: int = 1, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a prospect to the processing queue.
        
        Returns the queue item ID for tracking.
        """
        item_id = str(uuid.uuid4())
        item = QueueItem(
            id=item_id,
            prospect_id=prospect_id,
            priority=priority,
            metadata=metadata or {}
        )

        # Insert based on priority (higher priority = processed first)
        if priority >= 3:  # Urgent
            self.queue.appendleft(item)
        elif priority >= 2:  # High
            # Insert after other high priority items
            insert_pos = 0
            for i, existing_item in enumerate(self.queue):
                if existing_item.priority < 2:
                    insert_pos = i
                    break
            else:
                insert_pos = len(self.queue)
            self.queue.insert(insert_pos, item)
        else:  # Normal
            self.queue.append(item)

        self.logger.info(
            "Item added to queue",
            item_id=item_id,
            prospect_id=prospect_id,
            priority=priority,
            queue_size=len(self.queue)
        )

        return item_id

    def add_batch(self, prospect_ids: list[str], priority: int = 1, metadata: dict[str, Any] | None = None) -> list[str]:
        """
        Add multiple prospects to the queue.
        
        Returns list of queue item IDs.
        """
        item_ids = []
        for prospect_id in prospect_ids:
            item_id = self.add_item(prospect_id, priority, metadata)
            item_ids.append(item_id)

        self.logger.info(
            "Batch added to queue",
            batch_size=len(prospect_ids),
            priority=priority,
            total_queue_size=len(self.queue)
        )

        return item_ids

    def get_next_batch(self, batch_size: int | None = None) -> list[QueueItem]:
        """
        Get the next batch of items to process.
        
        Respects daily limits and returns items that can be processed.
        """
        self.reset_daily_count()

        if batch_size is None:
            batch_size = self.max_batch_size

        # Check daily limit
        available_slots = self.max_daily_contacts - self.daily_count
        if available_slots <= 0:
            self.logger.warning(
                "Daily contact limit reached",
                daily_count=self.daily_count,
                max_daily=self.max_daily_contacts
            )
            return []

        batch_size = min(batch_size, available_slots)
        batch = []

        while len(batch) < batch_size and self.queue:
            item = self.queue.popleft()

            # Skip if already processing or completed
            if item.id in self.processing or item.id in self.completed:
                continue

            # Check retry limit
            if item.retry_count >= item.max_retries:
                self.failed[item.id] = item
                self.logger.warning(
                    "Item exceeded max retries",
                    item_id=item.id,
                    prospect_id=item.prospect_id,
                    retry_count=item.retry_count
                )
                continue

            batch.append(item)
            self.processing.add(item.id)

        if batch:
            self.logger.info(
                "Batch prepared for processing",
                batch_size=len(batch),
                remaining_queue=len(self.queue),
                daily_count=self.daily_count
            )

        return batch

    def mark_completed(self, item_id: str, success: bool = True) -> None:
        """
        Mark an item as completed (success or failure).
        """
        if item_id in self.processing:
            self.processing.remove(item_id)

            if success:
                # Find the item and move to completed
                for item in list(self.queue) + list(self.completed.values()) + list(self.failed.values()):
                    if item.id == item_id:
                        self.completed[item_id] = item
                        self.daily_count += 1
                        break
            else:
                # Move back to queue for retry
                for item in list(self.completed.values()) + list(self.failed.values()):
                    if item.id == item_id:
                        item.retry_count += 1
                        if item.retry_count < item.max_retries:
                            self.queue.append(item)
                        else:
                            self.failed[item_id] = item
                        break

    def get_queue_stats(self) -> dict[str, Any]:
        """
        Get comprehensive queue statistics.
        """
        self.reset_daily_count()

        return {
            "queue_size": len(self.queue),
            "processing": len(self.processing),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "daily_count": self.daily_count,
            "daily_limit": self.max_daily_contacts,
            "daily_remaining": max(0, self.max_daily_contacts - self.daily_count),
            "total_processed": len(self.completed) + len(self.failed),
            "success_rate": len(self.completed) / max(1, len(self.completed) + len(self.failed)) * 100,
            "timestamp": datetime.now().isoformat()
        }

    def clear_completed(self) -> int:
        """
        Clear completed items from memory.
        
        Returns number of items cleared.
        """
        cleared_count = len(self.completed)
        self.completed.clear()
        self.logger.info("Completed items cleared", cleared_count=cleared_count)
        return cleared_count


class SignalHireClient:
    """
    SignalHire API client for searching prospects and managing credits.
    
    Note: This client handles API operations only. For bulk contact reveals
    (1000+ contacts), use the browser automation service instead.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://www.signalhire.com",
        api_prefix: str = "/api/v1",
    ):
        # Allow environment variables to override defaults
        env_base = os.getenv("SIGNALHIRE_API_BASE_URL")
        env_prefix = os.getenv("SIGNALHIRE_API_PREFIX")
        self.api_key = api_key or os.getenv("SIGNALHIRE_API_KEY")
        self.base_url = (env_base or base_url).rstrip("/")
        prefix_value = env_prefix if env_prefix is not None else api_prefix
        self.api_prefix = ("/" + prefix_value.strip("/")) if prefix_value else ""
        self.rate_limiter = RateLimiter(max_requests=600, time_window=60)  # 600/minute
        self.session: httpx.AsyncClient | None = None
        self._credits_cache: dict[str, Any] | None = None
        self._cache_timestamp: datetime | None = None
        self._cache_ttl = 300  # 5 minutes
        # Enhanced controls
        self.max_concurrency: int = 5
        self.max_retries: int = 3
        self.retry_backoff_base: float = 0.25
        self.logger = structlog.get_logger(__name__)
        # Queue management
        self.batch_queue = BatchQueue(max_batch_size=10, max_daily_contacts=100)
        # Enhanced retry strategy
        self.retry_strategy = RetryStrategy(
            max_retries=self.max_retries,
            base_delay=self.retry_backoff_base,
            max_delay=30.0,
            circuit_breaker_threshold=10,
            circuit_breaker_timeout=120.0
        )
        # Search API concurrency limit (max 3 concurrent requests)
        self._search_semaphore = asyncio.Semaphore(3)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()

    async def start_session(self) -> None:
        """Start the HTTP session."""
        if self.session is None:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "SignalHire-Agent/1.0",
            }

            if self.api_key:
                headers["apikey"] = self.api_key

            self.session = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0
            )

    async def close_session(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make an API request with rate limiting and error handling."""
        if not self.session:
            await self.start_session()

        # Apply rate limiting with daily usage tracking
        daily_status = await self.rate_limiter.wait_if_needed()

        # Log warnings for high daily usage
        if daily_status["warning_level"] in ["high", "critical"]:
            logger = logging.getLogger(__name__)
            if daily_status["warning_level"] == "critical":
                logger.warning(f"CRITICAL: Daily API limit nearly exceeded ({daily_status['percentage_used']:.1f}%)")
            else:
                logger.info(f"High daily usage: {daily_status['percentage_used']:.1f}% of daily limit used")

        endpoint_path = "/" + endpoint.lstrip("/")
        url = f"{self.base_url}{self.api_prefix}{endpoint_path}"

        try:
            response = await self.session.request(method, url, **kwargs)

            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {"raw_response": response.text}

            # Check for success
            if response.is_success:
                # Extract credits info if available
                credits_used = data.get("credits_used", 0)
                # Prefer header X-Credits-Left when present
                credits_remaining_header = response.headers.get("X-Credits-Left") or response.headers.get("x-credits-left")
                credits_remaining = (
                    int(credits_remaining_header)
                    if credits_remaining_header and credits_remaining_header.isdigit()
                    else data.get("credits_remaining")
                )

                return APIResponse(
                    success=True,
                    data=data,
                    status_code=response.status_code,
                    credits_used=credits_used,
                    credits_remaining=credits_remaining
                )
            error_message = data.get("error") or data.get("message") or response.text or f"HTTP {response.status_code}"

            # Enhance error messages for specific HTTP status codes
            if response.status_code == 429:
                # Rate limit exceeded
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        retry_seconds = int(retry_after)
                        error_message = f"Rate limit exceeded. Please wait {retry_seconds} seconds before retrying."
                    except ValueError:
                        error_message = "Rate limit exceeded. Please wait before retrying."
                else:
                    error_message = "Rate limit exceeded. Please reduce request frequency or wait before retrying."

                # Add helpful suggestions
                error_message += " Consider using browser mode for bulk operations or reducing batch size."

            elif response.status_code == 402:
                # Payment required (insufficient credits)
                error_message = "Insufficient credits. Please check your account balance or purchase additional credits."

            elif response.status_code == 403:
                # Forbidden - could be authentication or permissions
                if "api" in error_message.lower():
                    error_message = "API access denied. Please check your API key and permissions."
                else:
                    error_message = "Access forbidden. Please check your credentials and account status."

            elif response.status_code == 404:
                # Not found
                error_message = "Resource not found. Please check the prospect ID or endpoint URL."

            elif response.status_code >= 500:
                # Server errors
                error_message = f"Server error ({response.status_code}). This is usually temporary - please try again later."

            return APIResponse(
                success=False,
                error=error_message,
                status_code=response.status_code,
                data=data
            )

        except httpx.TimeoutException:
            return APIResponse(
                success=False,
                error="Request timed out. This may be due to network issues or high server load. Please try again.",
                status_code=408
            )
        except httpx.ConnectError:
            return APIResponse(
                success=False,
                error="Connection failed. Please check your internet connection and try again.",
                status_code=None
            )
        except httpx.RequestError as e:
            error_msg = str(e)
            if "ssl" in error_msg.lower():
                enhanced_error = "SSL connection error. This may be due to network restrictions or certificate issues."
            elif "dns" in error_msg.lower():
                enhanced_error = "DNS resolution failed. Please check your network connection and try again."
            else:
                enhanced_error = f"Network request failed: {error_msg}. Please check your connection and try again."

            return APIResponse(
                success=False,
                error=enhanced_error,
                status_code=None
            )

    async def check_credits(self) -> APIResponse:
        """Check current credit balance and usage."""
        # Check cache first
        if (self._credits_cache and self._cache_timestamp and
            datetime.now() - self._cache_timestamp < timedelta(seconds=self._cache_ttl)):
            return APIResponse(
                success=True,
                data=self._credits_cache
            )

        response = await self._make_request("GET", "/credits")

        # Cache successful responses
        if response.success and response.data:
            self._credits_cache = response.data
            self._cache_timestamp = datetime.now()

        return response

    async def search_prospects(self, search_criteria: dict[str, Any],
                             size: int = 25) -> APIResponse:
        """
        Search for prospects using the SignalHire Search API.
        
        Supports filtering by currentTitle, location, keywords, and other criteria.
        Returns profiles with scrollId for pagination if more results available.
        
        Args:
            search_criteria: Dict with search filters (currentTitle, location, keywords, etc.)
            size: Number of results per batch (1-100, default 25)
        
        Returns:
            APIResponse with profiles array, total count, and scrollId if applicable
        """
        # Validate size parameter
        size = max(1, min(size, 100))

        # Prepare search data
        search_data = {
            "size": size,
            **search_criteria
        }

        # Enforce single-concurrency per client for Search API
        async with self._search_semaphore:
            return await self._make_request("POST", "/candidate/searchByQuery", json=search_data)

    async def scroll_search(self, request_id: int, scroll_id: str) -> APIResponse:
        """Fetch next batch using POST /candidate/scrollSearch/{requestId} with JSON body {scrollId}."""
        endpoint = f"/candidate/scrollSearch/{request_id}"
        body = {"scrollId": scroll_id}
        async with self._search_semaphore:
            return await self._make_request("POST", endpoint, json=body)

    async def get_prospect_details(self, prospect_id: str) -> APIResponse:
        """Get detailed information for a specific prospect."""
        return await self._make_request("GET", f"/prospects/{prospect_id}")

    async def reveal_contact_by_identifier(self, identifier: str, callback_url: str) -> APIResponse:
        """
        Reveal contact information using SignalHire's Person API.
        
        Args:
            identifier: LinkedIn URL, email, phone, or 32-character UID
            callback_url: URL where results will be sent
        
        Returns:
            APIResponse with request ID if successful
        """
        data = {
            "items": [identifier],
            "callbackUrl": callback_url
        }

        return await self._make_request("POST", "/candidate/search", json=data)

    async def reveal_contact(self, prospect_id: str) -> APIResponse:
        """Reveal contact for a single prospect with retry logic (compatibility path)."""
        attempt = 0
        while True:
            # Circuit breaker check
            if self.retry_strategy.circuit_open:
                self.logger.warning("Circuit breaker open, skipping request", prospect_id=prospect_id, attempt=attempt)
                return APIResponse(success=False, error="Circuit breaker open - too many recent failures", status_code=503)

            resp = await self._make_request("POST", f"/prospects/{prospect_id}/reveal")
            attempt += 1
            self.retry_strategy.record_attempt(resp.success, resp.status_code, resp.error)

            if resp.success:
                if attempt > 1:
                    self.logger.info("Request succeeded after retry", prospect_id=prospect_id, attempts=attempt, final_status=resp.status_code)
                return resp

            if not self.retry_strategy.should_retry(attempt, resp.status_code, resp.error):
                error_type = self.retry_strategy.classify_error(resp.status_code, resp.error)
                self.logger.warning("Request failed permanently", prospect_id=prospect_id, attempts=attempt, status_code=resp.status_code, error_type=error_type, error=resp.error)
                return resp

            delay = self.retry_strategy.calculate_delay(attempt)
            self.logger.info("Retrying request", prospect_id=prospect_id, attempt=attempt, max_retries=self.retry_strategy.max_retries, delay=round(delay, 2), status_code=resp.status_code, error=resp.error)
            await asyncio.sleep(delay)

    async def batch_reveal_contacts(
        self,
        prospect_ids: list[str],
        batch_size: int = 10,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    ) -> list[APIResponse]:
        """
        Reveal contacts for multiple prospects in batches with enhanced progress reporting.
        
        Limited to API constraints (~100 total). For larger operations,
        use browser automation service.
        """
        # Validate inputs
        if not isinstance(prospect_ids, list) or any(not isinstance(p, str) for p in prospect_ids):
            raise SignalHireAPIError("prospect_ids must be a list of strings")
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise SignalHireAPIError("batch_size must be a positive integer")

        total = len(prospect_ids)
        if total > 100:
            raise SignalHireAPIError(
                "API batch reveal limited to 100 prospects. Use browser automation for larger batches."
            )

        # Credit pre-check (assume 1 credit per reveal)
        try:
            credits = await self.check_credits()
            remaining = (credits.data or {}).get("credits_remaining") if credits.success else None
            if isinstance(remaining, int) and remaining < total:
                raise SignalHireAPIError(
                    f"Insufficient credits: need {total}, have {remaining}",
                    status_code=402,
                    response_data={"needed": total, "remaining": remaining},
                )
        except SignalHireAPIError:
            # Propagate credit errors
            raise
        except Exception as e:
            # If credits check fails for other reasons, proceed but log the issue
            self.logger.warning("Credit pre-check failed", error=str(e))

        # Enhanced progress tracking
        start_time = datetime.now()
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrency)

        # Progress statistics
        stats = {
            "total": total,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "start_time": start_time,
            "last_update": start_time,
            "batch_size": batch_size,
            "errors": [],
            "estimated_completion": None
        }

        async def wrapped_reveal(pid: str) -> APIResponse:
            async with semaphore:
                try:
                    result = await self.reveal_contact(pid)

                    # Update statistics
                    stats["processed"] += 1
                    if result.success:
                        stats["successful"] += 1
                    else:
                        stats["failed"] += 1
                        if result.error:
                            stats["errors"].append({
                                "prospect_id": pid,
                                "error": result.error,
                                "status_code": result.status_code
                            })

                    # Calculate progress metrics
                    elapsed = (datetime.now() - start_time).total_seconds()
                    success_rate = stats["successful"] / stats["processed"] if stats["processed"] > 0 else 0
                    avg_time_per_contact = elapsed / stats["processed"] if stats["processed"] > 0 else 0
                    remaining_contacts = total - stats["processed"]

                    # Estimate completion time
                    if avg_time_per_contact > 0:
                        estimated_remaining = remaining_contacts * avg_time_per_contact
                        stats["estimated_completion"] = datetime.now() + timedelta(seconds=estimated_remaining)

                    # Enhanced progress report
                    progress_data = {
                        "current": stats["processed"],
                        "total": total,
                        "successful": stats["successful"],
                        "failed": stats["failed"],
                        "success_rate": round(success_rate * 100, 1),
                        "elapsed_seconds": round(elapsed, 1),
                        "avg_time_per_contact": round(avg_time_per_contact, 2),
                        "estimated_completion": stats["estimated_completion"].isoformat() if stats["estimated_completion"] else None,
                        "remaining_contacts": remaining_contacts,
                        "batch_size": batch_size,
                        "recent_errors": stats["errors"][-3:] if stats["errors"] else [],  # Last 3 errors
                        "credits_used": stats["successful"],
                        "credits_remaining": remaining
                    }

                    # Call progress callback if provided
                    if progress_callback:
                        try:
                            await progress_callback(progress_data)
                        except Exception as cb_err:
                            self.logger.warning("Progress callback failed", error=str(cb_err))

                    return result

                except Exception as ex:
                    # Update failure statistics
                    stats["processed"] += 1
                    stats["failed"] += 1
                    stats["errors"].append({
                        "prospect_id": pid,
                        "error": str(ex),
                        "status_code": None
                    })

                    # Return error response
                    return APIResponse(success=False, error=str(ex), data={"prospect_id": pid})

        # Process in smaller batches to respect rate limits
        for i in range(0, total, batch_size):
            batch = prospect_ids[i : i + batch_size]
            batch_results = await asyncio.gather(*(wrapped_reveal(pid) for pid in batch))
            results.extend(batch_results)

            # Log batch completion
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            self.logger.info(
                "Batch completed",
                batch=batch_num,
                total_batches=total_batches,
                batch_successful=sum(1 for r in batch_results if r.success),
                batch_failed=sum(1 for r in batch_results if not r.success)
            )

        # Final progress report
        total_elapsed = (datetime.now() - start_time).total_seconds()
        final_success_rate = stats["successful"] / total if total > 0 else 0

        self.logger.info(
            "Batch reveal completed",
            total=total,
            successful=stats["successful"],
            failed=stats["failed"],
            success_rate=round(final_success_rate * 100, 1),
            total_time=round(total_elapsed, 1),
            avg_time_per_contact=round(total_elapsed / total, 2) if total > 0 else 0,
            credits_used=stats["successful"]
        )

        return results

    async def get_search_suggestions(self, query: str) -> APIResponse:
        """Get search suggestions for companies, titles, or locations."""
        params = {"q": query}
        return await self._make_request("GET", "/suggestions", params=params)

    async def validate_api_key(self) -> bool:
        """Validate the current API key."""
        response = await self.check_credits()
        return response.success

    def invalidate_credits_cache(self) -> None:
        """Invalidate the credits cache to force a fresh check."""
        self._credits_cache = None
        self._cache_timestamp = None

    def get_retry_stats(self) -> dict[str, Any]:
        """
        Get comprehensive retry statistics and circuit breaker status.
        """
        return self.retry_strategy.get_stats()

    def reset_retry_stats(self):
        """
        Reset retry statistics (useful for testing or fresh monitoring periods).
        """
        self.retry_strategy.reset_stats()
        self.logger.info("Retry statistics reset")

    # Queue Management Methods

    def queue_prospect(self, prospect_id: str, priority: int = 1, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a single prospect to the processing queue.
        
        Returns queue item ID for tracking.
        """
        return self.batch_queue.add_item(prospect_id, priority, metadata)

    def queue_batch(self, prospect_ids: list[str], priority: int = 1, metadata: dict[str, Any] | None = None) -> list[str]:
        """
        Add multiple prospects to the processing queue.
        
        Returns list of queue item IDs.
        """
        return self.batch_queue.add_batch(prospect_ids, priority, metadata)

    async def process_queue_batch(
        self,
        batch_size: int | None = None,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None
    ) -> dict[str, Any]:
        """
        Process the next batch from the queue.
        
        Returns processing results and statistics.
        """
        batch = self.batch_queue.get_next_batch(batch_size)

        if not batch:
            return {
                "processed": 0,
                "message": "No items available for processing",
                "queue_stats": self.batch_queue.get_queue_stats()
            }

        # Extract prospect IDs for processing
        prospect_ids = [item.prospect_id for item in batch]
        item_ids = [item.id for item in batch]

        self.logger.info(
            "Processing queue batch",
            batch_size=len(batch),
            prospect_ids=prospect_ids[:5],  # Log first 5 for debugging
            total_in_batch=len(prospect_ids)
        )

        # Process the batch using existing batch_reveal_contacts method
        results = await self.batch_reveal_contacts(
            prospect_ids,
            batch_size=len(prospect_ids),
            progress_callback=progress_callback
        )

        # Update queue status based on results
        for i, (item_id, result) in enumerate(zip(item_ids, results, strict=False)):
            success = result.success
            self.batch_queue.mark_completed(item_id, success)

            if not success:
                self.logger.warning(
                    "Queue item failed",
                    item_id=item_id,
                    prospect_id=prospect_ids[i],
                    error=result.error
                )

        # Return comprehensive results
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        return {
            "processed": len(results),
            "successful": len(successful_results),
            "failed": len(failed_results),
            "credits_used": sum(r.credits_used for r in successful_results),
            "queue_stats": self.batch_queue.get_queue_stats(),
            "results": [
                {
                    "prospect_id": prospect_ids[i],
                    "success": result.success,
                    "error": result.error if not result.success else None,
                    "credits_used": result.credits_used
                }
                for i, result in enumerate(results)
            ]
        }

    async def process_queue_until_empty(
        self,
        batch_size: int | None = None,
        max_batches: int | None = None,
        progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
        batch_delay: float = 1.0
    ) -> dict[str, Any]:
        """
        Process the entire queue until empty or limits reached.
        
        Args:
            batch_size: Size of each processing batch
            max_batches: Maximum number of batches to process (None = unlimited)
            progress_callback: Callback for progress updates
            batch_delay: Delay between batches in seconds
        
        Returns:
            Comprehensive processing statistics
        """
        total_processed = 0
        total_successful = 0
        total_failed = 0
        total_credits_used = 0
        batches_processed = 0
        start_time = datetime.now()

        self.logger.info("Starting queue processing", queue_size=self.batch_queue.queue.qsize())

        while True:
            # Check if we've reached the batch limit
            if max_batches and batches_processed >= max_batches:
                self.logger.info("Reached maximum batch limit", batches_processed=batches_processed)
                break

            # Check if queue is empty
            if not self.batch_queue.queue:
                self.logger.info("Queue is empty, processing complete")
                break

            # Process next batch
            batch_result = await self.process_queue_batch(batch_size, progress_callback)

            if batch_result["processed"] == 0:
                # No items were processed (likely due to daily limits)
                self.logger.info("No items processed, likely due to limits")
                break

            # Update totals
            total_processed += batch_result["processed"]
            total_successful += batch_result["successful"]
            total_failed += batch_result["failed"]
            total_credits_used += batch_result["credits_used"]
            batches_processed += 1

            # Log batch completion
            self.logger.info(
                "Batch completed",
                batch=batches_processed,
                processed=batch_result["processed"],
                successful=batch_result["successful"],
                failed=batch_result["failed"],
                credits_used=batch_result["credits_used"]
            )

            # Delay between batches to respect rate limits
            if batch_delay > 0:
                await asyncio.sleep(batch_delay)

        # Calculate final statistics
        total_time = (datetime.now() - start_time).total_seconds()
        success_rate = total_successful / max(1, total_processed) * 100

        final_stats = {
            "total_processed": total_processed,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate": round(success_rate, 1),
            "total_credits_used": total_credits_used,
            "batches_processed": batches_processed,
            "total_time_seconds": round(total_time, 1),
            "avg_time_per_contact": round(total_time / max(1, total_processed), 2),
            "final_queue_stats": self.batch_queue.get_queue_stats(),
            "completion_timestamp": datetime.now().isoformat()
        }

        self.logger.info(
            "Queue processing completed",
            **final_stats
        )

        return final_stats

    def get_queue_status(self) -> dict[str, Any]:
        """
        Get current queue status and statistics.
        """
        return self.batch_queue.get_queue_stats()

    def clear_completed_queue_items(self) -> int:
        """
        Clear completed items from the queue to free memory.
        
        Returns number of items cleared.
        """
        return self.batch_queue.clear_completed()

    # Compatibility shim for CLI reveal_commands expecting bulk_reveal(RevealOp)
    async def bulk_reveal(self, operation, progress_callback: Callable[[dict[str, Any]], Awaitable[None]] | None = None) -> dict[str, Any]:
        """
        Bulk reveal contacts with enhanced progress reporting.
        
        Compatibility method for CLI operations with detailed progress tracking.
        """
        prospect_ids = getattr(operation, "prospect_ids", [])
        batch_size = getattr(operation, "batch_size", 10)

        # Use enhanced batch_reveal_contacts with progress reporting
        results = await self.batch_reveal_contacts(
            prospect_ids,
            batch_size=batch_size,
            progress_callback=progress_callback
        )

        success = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        # Calculate final statistics
        total_credits_used = sum(r.credits_used for r in results if r.success)

        return {
            "operation_id": getattr(operation, "id", "op_unknown"),
            "total_prospects": len(prospect_ids),
            "revealed_count": len(success),
            "failed_count": len(failed),
            "success_rate": round(len(success) / len(prospect_ids) * 100, 1) if prospect_ids else 0,
            "prospects": [
                {
                    "id": getattr(r.data or {}, "prospect_id", None) or prospect_ids[i] if i < len(prospect_ids) else None,
                    "status": "success" if r.success else "failed",
                    "error": r.error if not r.success else None
                }
                for i, r in enumerate(results)
            ],
            "credits_used": total_credits_used,
            "errors": [
                {
                    "prospect_id": getattr(r.data or {}, "prospect_id", None) or prospect_ids[i] if i < len(prospect_ids) else None,
                    "error": r.error
                }
                for i, r in enumerate(results) if not r.success
            ]
        }


# Utility functions

async def create_signalhire_client(api_key: str | None = None) -> SignalHireClient:
    """Create and initialize a SignalHire client."""
    client = SignalHireClient(api_key=api_key)
    await client.start_session()
    return client


async def test_api_connection(api_key: str | None = None) -> bool:
    """Test the API connection and authentication."""
    async with SignalHireClient(api_key=api_key) as client:
        return await client.validate_api_key()


# Example usage patterns for documentation

async def example_search_workflow():
    """Example of a complete search and reveal workflow using the API."""
    async with SignalHireClient(api_key="your-api-key") as client:
        # Check credits first
        credits_response = await client.check_credits()
        if not credits_response.success:
            print(f"Failed to check credits: {credits_response.error}")
            return

        print(f"Available credits: {credits_response.data}")

        # Search for prospects
        search_criteria = {
            "title": "Software Engineer",
            "location": "San Francisco",
            "company_size": "50-200"
        }

        search_response = await client.search_prospects(search_criteria, limit=50)
        if not search_response.success:
            print(f"Search failed: {search_response.error}")
            return

        prospects = search_response.data.get("prospects", [])
        print(f"Found {len(prospects)} prospects")

        # Reveal contacts for first 10 prospects
        prospect_ids = [p["id"] for p in prospects[:10]]
        reveal_results = await client.batch_reveal_contacts(prospect_ids)

        successful_reveals = [r for r in reveal_results if r.success]
        print(f"Successfully revealed {len(successful_reveals)} contacts")


if __name__ == "__main__":
    # Example usage
    asyncio.run(example_search_workflow())
