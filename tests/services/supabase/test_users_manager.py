# run this file locally with: python -m tests.services.supabase.test_supabase_users

import datetime
import os
import pytest

from config import (
    GITHUB_NOREPLY_EMAIL_DOMAIN,
    OWNER_ID,
    OWNER_NAME,
    OWNER_TYPE,
    PRODUCT_ID_FOR_FREE,
    USER_ID,
    USER_NAME,
    INSTALLATION_ID,
    UNIQUE_ISSUE_ID,
    NEW_INSTALLATION_ID,
    TEST_EMAIL,
)
from services.stripe.customer import get_subscription
from services.supabase import SupabaseManager
from services.webhook_handler import handle_webhook_event
from tests.services.supabase.wipe_data import (
    wipe_installation_owner_user_data,
)
from tests.test_payloads.deleted import deleted_payload
from tests.test_payloads.installation import (
    installation_payload,
    new_installation_payload,
)

pytest_plugins = ("pytest_asyncio",)
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
SUPABASE_URL = os.getenv("SUPABASE_URL") or ""


def test_create_and_update_user_request_works() -> None:
    """Test that I can create and complete user request in usage table"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    usage_record_id = supabase_manager.create_user_request(
        user_id=USER_ID,
        user_name=USER_NAME,
        installation_id=INSTALLATION_ID,
        unique_issue_id="U/gitautoai/nextjs-website#52",
        email=TEST_EMAIL,
    )
    assert isinstance(usage_record_id, int)
    assert (
        supabase_manager.complete_and_update_usage_record(
            usage_record_id=usage_record_id,
            token_input=1000,
            token_output=100,
            total_seconds=100,
        )
        is None
    )


# test_create_and_update_user_request_works()


def test_how_many_requests_left() -> None:
    """Test that get_how_many_requests_left_and_cycle returns the correct values"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()
    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )
    # Testing 0 requests have been made on free tier
    requests_left, request_count, end_date = (
        supabase_manager.get_how_many_requests_left_and_cycle(
            user_id=USER_ID,
            installation_id=INSTALLATION_ID,
            user_name=USER_NAME,
            owner_id=OWNER_ID,
            owner_name=OWNER_NAME,
        )
    )

    # Match request_count in Metadata in https://dashboard.stripe.com/test/products/prod_PokLGIxiVUwCi6
    assert requests_left == 5
    assert request_count == 5
    assert isinstance(end_date, datetime.datetime)

    supabase_manager.client.table("issues").insert(
        json={
            "installation_id": INSTALLATION_ID,
            "unique_id": UNIQUE_ISSUE_ID,
        }
    ).execute()
    for _ in range(1, 6):
        supabase_manager.client.table("usage").insert(
            json={
                "user_id": USER_ID,
                "installation_id": INSTALLATION_ID,
                "is_completed": True,
                "unique_issue_id": UNIQUE_ISSUE_ID,
            }
        ).execute()

    # Test no requests left
    requests_left, request_count, end_date = (
        supabase_manager.get_how_many_requests_left_and_cycle(
            user_id=USER_ID,
            installation_id=INSTALLATION_ID,
            user_name=USER_NAME,
            owner_id=OWNER_ID,
            owner_name=OWNER_NAME,
        )
    )

    assert requests_left == 0
    assert request_count == 5
    assert isinstance(end_date, datetime.datetime)

    # Clean Up
    supabase_manager.delete_installation(
        installation_id=INSTALLATION_ID, user_id=USER_ID
    )


# test_how_many_requests_left()


def test_is_users_first_issue() -> None:
    """Check if it's a users first issue."""

    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )
    assert supabase_manager.is_users_first_issue(
        user_id=USER_ID, installation_id=INSTALLATION_ID
    )

    # Set user table user's first_issue to false
    supabase_manager.set_user_first_issue_to_false(
        user_id=USER_ID, installation_id=INSTALLATION_ID
    )

    assert not supabase_manager.is_users_first_issue(
        user_id=USER_ID, installation_id=INSTALLATION_ID
    )

    # Clean Up
    wipe_installation_owner_user_data()


# test_is_users_first_issue()


def test_parse_subscription_object() -> None:
    """Test parse_subscription_object function"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()
    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    def assertion_test(customer_id: str, product_id: str):
        subscription = get_subscription(customer_id)
        _, _, product_id_output = supabase_manager.parse_subscription_object(
            subscription,
            USER_ID,
            INSTALLATION_ID,
            customer_id,
            USER_NAME,
            OWNER_ID,
            OWNER_NAME,
        )
        assert product_id_output == product_id

    # All active ##
    # [free, paid] -> paid
    # assertion_test(customer_id="cus_PtCxNdGs23X4QR", product_id=PRODUCT_ID_FOR_STANDARD)
    assertion_test(customer_id="cus_PtCxNdGs23X4QR", product_id=PRODUCT_ID_FOR_FREE)

    # [paid, free] -> paid
    assertion_test(customer_id="cus_PpmpFh1sw0Gfcz", product_id=PRODUCT_ID_FOR_FREE)

    # Clean Up
    wipe_installation_owner_user_data()


# test_parse_subscription_object()


@pytest.mark.asyncio
async def test_install_uninstall_install() -> None:
    """Testing install uninstall methods"""
    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()
    wipe_installation_owner_user_data(NEW_INSTALLATION_ID)

    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    await handle_webhook_event(event_name="installation", payload=installation_payload)

    # Check Owners Record (owner_id, stripe_customer_id)
    owners_data, _ = (
        supabase_manager.client.table(table_name="owners")
        .select("*")
        .eq(column="owner_id", value=OWNER_ID)
        .execute()
    )
    assert owners_data[1][0]["owner_id"] == OWNER_ID
    assert isinstance(owners_data[1][0]["stripe_customer_id"], str)

    # Check Installation Record
    installation_data, _ = (
        supabase_manager.client.table(table_name="installations")
        .select("*")
        .eq(column="installation_id", value=INSTALLATION_ID)
        .execute()
    )

    assert installation_data[1][0]["installation_id"] == INSTALLATION_ID
    assert installation_data[1][0]["owner_name"] == OWNER_NAME
    assert installation_data[1][0]["owner_id"] == OWNER_ID
    assert installation_data[1][0]["owner_type"] == OWNER_TYPE
    assert installation_data[1][0]["uninstalled_at"] is None

    # Check Users Record
    users_data, _ = (
        supabase_manager.client.table(table_name="users")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .execute()
    )

    assert users_data[1][0]["user_id"] == USER_ID
    assert users_data[1][0]["user_name"] == USER_NAME
    # Check User Installation Record
    users_data, _ = (
        supabase_manager.client.table(table_name="user_installations")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .eq(column="installation_id", value=INSTALLATION_ID)
        .execute()
    )

    assert users_data[1][0]["user_id"] == USER_ID
    assert users_data[1][0]["installation_id"] == INSTALLATION_ID
    # Should be selected since it's the only user -> used for account selected in website
    assert users_data[1][0]["is_selected"] is True
    assert (
        users_data[1][0]["first_issue"] is True
    )  # first issue since hasn't had an issue
    assert users_data[1][0]["is_user_assigned"] is False
    assert users_data[1][0]["deleted_at"] is None
    assert users_data[1][0]["deleted_by"] is None

    await handle_webhook_event(event_name="installation", payload=deleted_payload)
    # We're going to check the same things, except that installation should have uninstalled_at

    # Check Owners Record (owner_id, stripe_customer_id)
    owners_data, _ = (
        supabase_manager.client.table(table_name="owners")
        .select("*")
        .eq(column="owner_id", value=OWNER_ID)
        .execute()
    )
    assert owners_data[1][0]["owner_id"] == OWNER_ID
    assert isinstance(owners_data[1][0]["stripe_customer_id"], str)

    # Check Installation Record
    installation_data, _ = (
        supabase_manager.client.table(table_name="installations")
        .select("*")
        .eq(column="installation_id", value=INSTALLATION_ID)
        .execute()
    )

    assert installation_data[1][0]["installation_id"] == INSTALLATION_ID
    assert installation_data[1][0]["owner_name"] == OWNER_NAME
    assert installation_data[1][0]["owner_id"] == OWNER_ID
    assert installation_data[1][0]["owner_type"] == OWNER_TYPE
    assert installation_data[1][0]["uninstalled_at"] is not None

    # Check Users Record
    users_data, _ = (
        supabase_manager.client.table(table_name="users")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .execute()
    )

    assert users_data[1][0]["user_id"] == USER_ID
    assert users_data[1][0]["user_name"] == USER_NAME
    # Check User Installation Record
    users_data, _ = (
        supabase_manager.client.table(table_name="user_installations")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .eq(column="installation_id", value=INSTALLATION_ID)
        .execute()
    )

    assert users_data[1][0]["user_id"] == USER_ID
    assert users_data[1][0]["installation_id"] == INSTALLATION_ID
    # Should be selected since it's the only user -> used for account selected in website
    assert users_data[1][0]["is_selected"] is True
    assert (
        users_data[1][0]["first_issue"] is True
    )  # first issue since hasn't had an issue
    assert users_data[1][0]["is_user_assigned"] is False
    assert users_data[1][0]["deleted_at"] is None
    assert users_data[1][0]["deleted_by"] is None

    await handle_webhook_event(
        event_name="installation", payload=new_installation_payload
    )

    # Check Owners Record (owner_id, stripe_customer_id)
    owners_data, _ = (
        supabase_manager.client.table(table_name="owners")
        .select("*")
        .eq(column="owner_id", value=OWNER_ID)
        .execute()
    )
    assert owners_data[1][0]["owner_id"] == OWNER_ID
    assert isinstance(owners_data[1][0]["stripe_customer_id"], str)

    # Check Installation Record
    installation_data, _ = (
        supabase_manager.client.table(table_name="installations")
        .select("*")
        .eq(column="installation_id", value=NEW_INSTALLATION_ID)
        .execute()
    )

    assert installation_data[1][0]["installation_id"] == NEW_INSTALLATION_ID
    assert installation_data[1][0]["owner_name"] == OWNER_NAME
    assert installation_data[1][0]["owner_id"] == OWNER_ID
    assert installation_data[1][0]["owner_type"] == OWNER_TYPE
    assert installation_data[1][0]["uninstalled_at"] is None

    # Check Users Record
    users_data, _ = (
        supabase_manager.client.table(table_name="users")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .execute()
    )

    assert users_data[1][0]["user_id"] == USER_ID
    assert users_data[1][0]["user_name"] == USER_NAME
    # Check User Installation Record
    users_data, _ = (
        supabase_manager.client.table(table_name="user_installations")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .eq(column="installation_id", value=NEW_INSTALLATION_ID)
        .execute()
    )

    assert users_data[1][0]["user_id"] == USER_ID
    assert users_data[1][0]["installation_id"] == NEW_INSTALLATION_ID
    # Should be selected since it's the only user -> used for account selected in website
    assert users_data[1][0]["is_selected"] is True
    assert (
        users_data[1][0]["first_issue"] is True
    )  # first issue since hasn't had an issue
    assert users_data[1][0]["is_user_assigned"] is False
    assert users_data[1][0]["deleted_at"] is None
    assert users_data[1][0]["deleted_by"] is None

    # Clean Up
    wipe_installation_owner_user_data()
    wipe_installation_owner_user_data(NEW_INSTALLATION_ID)


def test_handle_user_email_update() -> None:
    """Test updating a user's email in the users table"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # Insert a user into the database
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )
    # Verify github no-reply email is not updated
    json_data = {"user_id": USER_ID, "user_name": USER_NAME}
    json_data["email"] = f"no_reply_email@{GITHUB_NOREPLY_EMAIL_DOMAIN}"
    supabase_manager.upsert_user(**json_data)
    user_data = supabase_manager.get_user(user_id=USER_ID)
    assert user_data["email"] == TEST_EMAIL

    # Verify None email is not updated
    json_data["email"] = None
    supabase_manager.upsert_user(**json_data)
    user_data = supabase_manager.get_user(user_id=USER_ID)
    assert user_data["email"] == TEST_EMAIL

    # Verify valid email is updated
    new_email = "new_email@example.com"
    json_data["email"] = "new_email@example.com"
    supabase_manager.upsert_user(**json_data)
    user_data = supabase_manager.get_user(user_id=USER_ID)
    assert user_data["email"] == new_email

    # Clean Up
    wipe_installation_owner_user_data()


# test_handle_user_email_update()

def test_check_email_is_valid() -> None:
    """Test the check_email_is_valid function"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    users_manager = supabase_manager.users_manager

    # Test valid email
    assert users_manager.check_email_is_valid("test@example.com") is True

    # Test invalid email (None)
    assert users_manager.check_email_is_valid(None) is False

    # Test invalid email (missing @)
    assert users_manager.check_email_is_valid("testexample.com") is False

    # Test invalid email (missing .)
    assert users_manager.check_email_is_valid("test@examplecom") is False

    # Test invalid email (GitHub noreply)
    assert users_manager.check_email_is_valid(f"test@{GITHUB_NOREPLY_EMAIL_DOMAIN}") is False


def test_is_user_eligible_for_seat_handler() -> None:
    """Test the is_user_eligible_for_seat_handler function"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    users_manager = supabase_manager.users_manager

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    # Test user is eligible for seat
    assert users_manager.is_user_eligible_for_seat_handler(USER_ID, INSTALLATION_ID, 1) is True

    # Test user is not eligible for seat (quantity exceeded)
    assert users_manager.is_user_eligible_for_seat_handler(USER_ID, INSTALLATION_ID, 0) is False

    # Clean Up
    wipe_installation_owner_user_data()


def test_get_user() -> None:
    """Test the get_user function"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    users_manager = supabase_manager.users_manager

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=INSTALLATION_ID,
        owner_type=OWNER_TYPE,
        owner_name=OWNER_NAME,
        owner_id=OWNER_ID,
        user_id=USER_ID,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    # Test get_user returns correct user data
    user_data = users_manager.get_user(USER_ID)
    assert user_data is not None
    assert user_data["user_id"] == USER_ID
    assert user_data["user_name"] == USER_NAME

    # Test get_user returns None for non-existent user
    assert users_manager.get_user(999999) is None

    # Clean Up
    wipe_installation_owner_user_data()


def test_upsert_user() -> None:
    """Test the upsert_user function"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    users_manager = supabase_manager.users_manager

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # Insert a user into the database
    users_manager.upsert_user(USER_ID, USER_NAME, TEST_EMAIL)

    # Verify user data is correct
    user_data = users_manager.get_user(USER_ID)
    assert user_data is not None
    assert user_data["user_id"] == USER_ID
    assert user_data["user_name"] == USER_NAME
    assert user_data["email"] == TEST_EMAIL

    # Update user data
    new_email = "new_email@example.com"
    users_manager.upsert_user(USER_ID, USER_NAME, new_email)

    # Verify user data is updated
    user_data = users_manager.get_user(USER_ID)
    assert user_data is not None
    assert user_data["user_id"] == USER_ID
    assert user_data["user_name"] == USER_NAME
    assert user_data["email"] == new_email

    # Clean Up
    wipe_installation_owner_user_data()


def test_upsert_user_installation() -> None:
    """Test the upsert_user_installation function"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)
    users_manager = supabase_manager.users_manager

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # Insert a user installation into the database
    users_manager.upsert_user_installation(USER_ID, INSTALLATION_ID)

    # Verify user installation data is correct
    user_installation_data, _ = (
        supabase_manager.client.table(table_name="user_installations")
        .select("*")
        .eq(column="user_id", value=USER_ID)
        .eq(column="installation_id", value=INSTALLATION_ID)
        .execute()
    )
    assert user_installation_data[1][0]["user_id"] == USER_ID
    assert user_installation_data[1][0]["installation_id"] == INSTALLATION_ID
    assert user_installation_data[1][0]["is_selected"] is True

    # Clean Up
    wipe_installation_owner_user_data()
