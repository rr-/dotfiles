import unittest
from datetime import datetime, timedelta, timezone
from typing import Any

from authenticator.data import ClientData


class CoreClientDataTests(unittest.TestCase):
    """Tests for the data module."""

    def __init__(self, *args: Any) -> None:
        """Constructor."""
        lt = datetime.now()
        ut = datetime.utcnow()
        lt2 = datetime.now()
        if ut.second == lt2.second:
            lt = lt2
        dt = ut - lt
        offset_minutes = 0
        if 0 == dt.days:
            offset_minutes = dt.seconds // 60
        else:
            dt = lt - ut
            offset_minutes = dt.seconds // 60
            offset_minutes *= -1
        dt = timedelta(minutes=offset_minutes)
        self.__tz = timezone(dt)
        self.__utz = timezone(timedelta(0))

        super().__init__(*args)

    def setUp(self) -> None:
        """Create data used by the test cases."""
        self.isoFmt = "%Y%m%dT%H%M%S%z"
        self.jsonStringExample01 = "\n".join(
            (
                "{",
                '    "client_id": "What.Ever.Dude",',
                '    "password_length": 6,',
                '    "period": 30,',
                '    "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"',
                "}",
            )
        )
        self.jsonStringExample02 = "\n".join(
            (
                "{",
                '    "client_id": "You.Dont.Say",',
                '    "password_length": 6,',
                '    "period": 30,',
                '    "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"',
                "}",
            )
        )
        self.jsonStringExample03 = "\n".join(
            (
                "{",
                '    "client_id": "Well.I.Never",',
                '    "password_length": 8,',
                '    "period": 15,',
                '    "shared_secret": "ABCDGNBVGY3TQOJQGEZDGNBVGY3TQCBA"',
                "}",
            )
        )

    def test_constructor_no_client_id(self) -> None:
        """Test for __init__().

        No client_id provided.

        """
        args: dict[str, Any]
        args = {"shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"}
        with self.assertRaises(TypeError):
            ClientData(**args)

    def test_constructor_empty_client_id(self) -> None:
        """Test for __init__().

        Empty client_id provided.

        """
        args: dict[str, Any]
        args = {
            "client_id": "",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
        }
        with self.assertRaises(ValueError):
            ClientData(**args)

    def test_constructor_no_shared_secret(self) -> None:
        """Test for __init__().

        No shared_secret provided.

        """
        args: dict[str, Any]
        args = {"client_id": "What.Ever.Dude"}
        with self.assertRaises(TypeError):
            ClientData(**args)

    def test_constructor_empty_shared_secret(self) -> None:
        """Test for __init__().

        Empty shared_secret provided.

        """
        args: dict[str, Any]
        args = {"client_id": "What.Ever.Dude", "shared_secret": ""}
        with self.assertRaises(ValueError):
            ClientData(**args)

    def test_constructor_period(self) -> None:
        """Test for __init__().

        Happy path period.

        """
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
        }
        cut = ClientData(**args)
        self.assertEqual(30, cut.period)
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "period": 60,
        }
        cut = ClientData(**args)
        self.assertEqual(60, cut.period)

    def test_constructor_period_bad_type(self) -> None:
        """Test for __init__().

        Bad value type for period.

        """
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "period": (1, 2, 3),
        }
        with self.assertRaises(TypeError):
            ClientData(**args)

    def test_constructor_period_bad_value(self) -> None:
        """Test for __init__().

        Bad value for period.

        """
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "period": -1,
        }
        with self.assertRaises(ValueError):
            ClientData(**args)

    def test_constructor_password_length(self) -> None:
        """Test for __init__().

        Happy path password length.

        """
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
        }
        cut = ClientData(**args)
        self.assertEqual(6, cut.password_length)
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "password_length": 1,
        }
        cut = ClientData(**args)
        self.assertEqual(1, cut.password_length)

    def test_constructor_password_length_bad_type(self) -> None:
        """Test for __init__().

        Bad value type for period.

        """
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "password_length": (1, 2, 3),
        }
        with self.assertRaises(TypeError):
            ClientData(**args)

    def test_constructor_password_length_bad_value(self) -> None:
        """Test for __init__().

        Bad value for password length.

        """
        args: dict[str, Any]
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "password_length": 0,
        }
        with self.assertRaises(ValueError):
            ClientData(**args)
        args = {
            "client_id": "What.Ever.Dude",
            "shared_secret": "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ",
            "password_length": 11,
        }
        with self.assertRaises(ValueError):
            ClientData(**args)
