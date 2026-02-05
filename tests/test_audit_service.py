import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog
from app.models.client import Client, ClientTier


class TestAuditService:
    """Test the AuditService class."""

    def _create_mock_db(self):
        """Create a mock database session."""
        return MagicMock()

    def _create_mock_client(self, client_id=1):
        """Create a mock Client object."""
        client = Mock(spec=Client)
        client.id = client_id
        client.name = "Test Client"
        client.email = "test@example.com"
        client.tier = ClientTier.PROFESSIONAL
        client.is_active = True
        return client

    def _create_mock_audit_log(self, log_id=1, client_id=1, action="test_action"):
        """Create a mock AuditLog object."""
        log = Mock(spec=AuditLog)
        log.id = log_id
        log.client_id = client_id
        log.action = action
        log.resource_type = None
        log.resource_id = None
        log.ip_address = None
        log.user_agent = None
        log.extra_data = None
        log.created_at = datetime.now()
        log.updated_at = datetime.now()
        return log


class TestLogAction(TestAuditService):
    """Test the log_action method."""

    def test_log_action_minimal_params(self):
        """Should create audit log with minimal required parameters."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_action(
            client=mock_client,
            action="test_action"
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        added_log = mock_db.add.call_args[0][0]
        assert isinstance(added_log, AuditLog)
        assert added_log.client_id == mock_client.id
        assert added_log.action == "test_action"
        assert added_log.resource_type is None
        assert added_log.resource_id is None

    def test_log_action_with_all_params(self):
        """Should create audit log with all parameters."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        extra_data = {"key": "value", "count": 42}
        result = service.log_action(
            client=mock_client,
            action="checkout_created",
            resource_type="subscription",
            resource_id=123,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            extra_data=extra_data
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        added_log = mock_db.add.call_args[0][0]
        assert added_log.client_id == mock_client.id
        assert added_log.action == "checkout_created"
        assert added_log.resource_type == "subscription"
        assert added_log.resource_id == 123
        assert added_log.ip_address == "192.168.1.1"
        assert added_log.user_agent == "Mozilla/5.0"
        assert added_log.extra_data == extra_data

    def test_log_action_with_ipv6_address(self):
        """Should handle IPv6 addresses."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_action(
            client=mock_client,
            action="api_request",
            ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.ip_address == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def test_log_action_with_complex_extra_data(self):
        """Should handle complex JSON data in extra_data."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        extra_data = {
            "request": {"param1": "value1", "param2": 123},
            "response": {"status": "success", "data": [1, 2, 3]},
            "metadata": {"nested": {"deeply": {"value": True}}}
        }

        result = service.log_action(
            client=mock_client,
            action="complex_operation",
            extra_data=extra_data
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.extra_data == extra_data

    def test_log_action_returns_refreshed_log(self):
        """Should return the refreshed audit log."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_action(
            client=mock_client,
            action="test_action"
        )

        assert isinstance(result, AuditLog)
        mock_db.refresh.assert_called_once_with(result)


class TestLogBillingAction(TestAuditService):
    """Test the log_billing_action method."""

    def test_log_billing_action_adds_prefix(self):
        """Should add 'billing_' prefix to action."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_billing_action(
            client=mock_client,
            action="checkout_created",
            resource_type="subscription"
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "billing_checkout_created"
        assert added_log.resource_type == "subscription"

    def test_log_billing_action_with_all_params(self):
        """Should pass through all parameters with billing prefix."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        extra_data = {"amount": 1500, "currency": "USD"}
        result = service.log_billing_action(
            client=mock_client,
            action="subscription_cancelled",
            resource_type="subscription",
            resource_id=456,
            ip_address="10.0.0.1",
            user_agent="Chrome/91.0",
            extra_data=extra_data
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "billing_subscription_cancelled"
        assert added_log.resource_type == "subscription"
        assert added_log.resource_id == 456
        assert added_log.ip_address == "10.0.0.1"
        assert added_log.user_agent == "Chrome/91.0"
        assert added_log.extra_data == extra_data

    def test_log_billing_action_checkout_resource(self):
        """Should handle checkout resource type."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_billing_action(
            client=mock_client,
            action="checkout_created",
            resource_type="checkout",
            resource_id=789
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "billing_checkout_created"
        assert added_log.resource_type == "checkout"
        assert added_log.resource_id == 789

    def test_log_billing_action_payment_resource(self):
        """Should handle payment resource type."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_billing_action(
            client=mock_client,
            action="payment_processed",
            resource_type="payment",
            resource_id=999
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "billing_payment_processed"
        assert added_log.resource_type == "payment"


class TestLogSecurityEvent(TestAuditService):
    """Test the log_security_event method."""

    def test_log_security_event_adds_prefix_and_type(self):
        """Should add 'security_' prefix and set resource_type."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_security_event(
            client=mock_client,
            event="api_key_used"
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "security_api_key_used"
        assert added_log.resource_type == "security"

    def test_log_security_event_with_all_params(self):
        """Should pass through all parameters with security prefix."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        extra_data = {"reason": "invalid_api_key", "attempts": 3}
        result = service.log_security_event(
            client=mock_client,
            event="access_denied",
            ip_address="192.168.1.100",
            user_agent="curl/7.68.0",
            extra_data=extra_data
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "security_access_denied"
        assert added_log.resource_type == "security"
        assert added_log.ip_address == "192.168.1.100"
        assert added_log.user_agent == "curl/7.68.0"
        assert added_log.extra_data == extra_data

    def test_log_security_event_api_key_used(self):
        """Should log API key usage events."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        result = service.log_security_event(
            client=mock_client,
            event="api_key_used",
            ip_address="203.0.113.1"
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "security_api_key_used"
        assert added_log.resource_type == "security"

    def test_log_security_event_suspicious_activity(self):
        """Should log suspicious activity with context."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        extra_data = {
            "pattern": "rapid_requests",
            "count": 1000,
            "timeframe": "1 minute"
        }

        result = service.log_security_event(
            client=mock_client,
            event="suspicious_activity",
            ip_address="198.51.100.1",
            extra_data=extra_data
        )

        added_log = mock_db.add.call_args[0][0]
        assert added_log.action == "security_suspicious_activity"
        assert added_log.extra_data == extra_data


class TestGetClientAuditLogs(TestAuditService):
    """Test the get_client_audit_logs method."""

    def test_get_client_audit_logs_basic(self):
        """Should retrieve audit logs for a client."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [
            self._create_mock_audit_log(1, 1, "action1"),
            self._create_mock_audit_log(2, 1, "action2"),
        ]

        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_client_audit_logs(client_id=1)

        assert result == mock_logs
        mock_db.query.assert_called_once_with(AuditLog)
        mock_order.limit.assert_called_once_with(100)

    def test_get_client_audit_logs_with_action_filter(self):
        """Should filter logs by action prefix."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [
            self._create_mock_audit_log(1, 1, "billing_checkout"),
            self._create_mock_audit_log(2, 1, "billing_payment"),
        ]

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_client_audit_logs(
            client_id=1,
            action_filter="billing_"
        )

        assert result == mock_logs
        assert mock_filter1.filter.call_count == 1

    def test_get_client_audit_logs_with_resource_type_filter(self):
        """Should filter logs by resource type."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [self._create_mock_audit_log(1, 1, "action1")]
        mock_logs[0].resource_type = "subscription"

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_client_audit_logs(
            client_id=1,
            resource_type_filter="subscription"
        )

        assert result == mock_logs
        assert mock_filter1.filter.call_count == 1

    def test_get_client_audit_logs_with_both_filters(self):
        """Should apply both action and resource type filters."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [self._create_mock_audit_log(1, 1, "billing_checkout")]
        mock_logs[0].resource_type = "subscription"

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_filter3 = mock_filter2.filter.return_value
        mock_order = mock_filter3.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_client_audit_logs(
            client_id=1,
            action_filter="billing_",
            resource_type_filter="subscription"
        )

        assert result == mock_logs
        # Verify filters were applied (client_id + action_filter + resource_type_filter)
        assert mock_query.filter.call_count == 1
        assert mock_filter1.filter.call_count == 1
        assert mock_filter2.filter.call_count == 1

    def test_get_client_audit_logs_custom_limit(self):
        """Should respect custom limit parameter."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [self._create_mock_audit_log(i, 1, f"action{i}") for i in range(10)]

        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_client_audit_logs(client_id=1, limit=10)

        mock_order.limit.assert_called_once_with(10)

    def test_get_client_audit_logs_orders_by_created_at_desc(self):
        """Should order logs by created_at descending (most recent first)."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = []

        result = service.get_client_audit_logs(client_id=1)

        mock_filter.order_by.assert_called_once()

    def test_get_client_audit_logs_empty_result(self):
        """Should return empty list when no logs found."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = []

        result = service.get_client_audit_logs(client_id=999)

        assert result == []


class TestGetRecentBillingLogs(TestAuditService):
    """Test the get_recent_billing_logs method."""

    def test_get_recent_billing_logs_default_limit(self):
        """Should retrieve recent billing logs with default limit."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [
            self._create_mock_audit_log(1, 1, "billing_checkout"),
            self._create_mock_audit_log(2, 1, "billing_payment"),
        ]

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_recent_billing_logs(client_id=1)

        assert result == mock_logs
        mock_order.limit.assert_called_once_with(50)

    def test_get_recent_billing_logs_custom_limit(self):
        """Should respect custom limit parameter."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [self._create_mock_audit_log(i, 1, f"billing_action{i}") for i in range(20)]

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_recent_billing_logs(client_id=1, limit=20)

        mock_order.limit.assert_called_once_with(20)

    def test_get_recent_billing_logs_filters_by_billing_prefix(self):
        """Should only return logs with 'billing_' action prefix."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_logs = [
            self._create_mock_audit_log(1, 1, "billing_checkout"),
            self._create_mock_audit_log(2, 1, "billing_subscription"),
        ]

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = mock_logs

        result = service.get_recent_billing_logs(client_id=1)

        assert result == mock_logs
        assert mock_filter1.filter.call_count == 1

    def test_get_recent_billing_logs_empty_result(self):
        """Should return empty list when no billing logs found."""
        mock_db = self._create_mock_db()
        service = AuditService(mock_db)

        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_limit = mock_order.limit.return_value
        mock_limit.all.return_value = []

        result = service.get_recent_billing_logs(client_id=999)

        assert result == []


class TestAuditServiceIntegration(TestAuditService):
    """Integration tests for common audit service workflows."""

    def test_billing_workflow(self):
        """Should log complete billing workflow."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        service.log_billing_action(
            client=mock_client,
            action="checkout_created",
            resource_type="checkout",
            resource_id=1
        )

        service.log_billing_action(
            client=mock_client,
            action="payment_processed",
            resource_type="payment",
            resource_id=1
        )

        service.log_billing_action(
            client=mock_client,
            action="subscription_activated",
            resource_type="subscription",
            resource_id=1
        )

        assert mock_db.add.call_count == 3
        assert mock_db.commit.call_count == 3

    def test_security_monitoring_workflow(self):
        """Should log security monitoring events."""
        mock_db = self._create_mock_db()
        mock_client = self._create_mock_client()
        service = AuditService(mock_db)

        service.log_security_event(
            client=mock_client,
            event="api_key_used",
            ip_address="192.168.1.1"
        )

        service.log_security_event(
            client=mock_client,
            event="rate_limit_exceeded",
            ip_address="192.168.1.1",
            extra_data={"requests": 1000, "window": "1 minute"}
        )

        assert mock_db.add.call_count == 2
        assert mock_db.commit.call_count == 2

    def test_multiple_clients(self):
        """Should handle logs for different clients."""
        mock_db = self._create_mock_db()
        client1 = self._create_mock_client(client_id=1)
        client2 = self._create_mock_client(client_id=2)
        service = AuditService(mock_db)

        service.log_action(client=client1, action="action1")
        service.log_action(client=client2, action="action2")

        assert mock_db.add.call_count == 2
        calls = mock_db.add.call_args_list
        assert calls[0][0][0].client_id == 1
        assert calls[1][0][0].client_id == 2
