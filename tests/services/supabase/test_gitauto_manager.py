# run this file locally with: python -m tests.services.supabase.test_gitauto_manager
import os
from config import OWNER_TYPE, TEST_EMAIL, USER_NAME
from services.supabase import SupabaseManager
from tests.services.supabase.wipe_data import (
    wipe_installation_owner_user_data,
)

SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")


def test_create_update_user_request_works() -> None:
    """Tests based on creating a record and updating it in usage table"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    usage_record_id = supabase_manager.create_user_request(
        user_id=user_id,
        user_name=USER_NAME,
        installation_id=installation_id,
        # fake issue creation
        unique_issue_id="U/gitautoai/test#01",
        email=TEST_EMAIL,
    )
    assert isinstance(
        usage_record_id,
        int,
    )
    assert (
        supabase_manager.complete_and_update_usage_record(
            usage_record_id=usage_record_id,
            token_input=1000,
            token_output=100,
            total_seconds=100,
        )
        is None
    )

    # Clean Up
    wipe_installation_owner_user_data()


# test_create_update_user_request_works()


def test_complete_and_update_usage_record_only_updates_one_record() -> None:
    """Tests based on creating a record and updating it in usage table"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1
    unique_issue_id = "U/gitautoai/test#01"

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    # Creating multiple usage records where is_completed = false.
    for _ in range(0, 5):
        supabase_manager.create_user_request(
            user_id=user_id,
            user_name=USER_NAME,
            installation_id=installation_id,
            # fake issue creation
            unique_issue_id=unique_issue_id,
            email=TEST_EMAIL,
        )

    usage_record_id = supabase_manager.create_user_request(
        user_id=user_id,
        user_name=USER_NAME,
        installation_id=installation_id,
        # fake issue creation
        unique_issue_id=unique_issue_id,
        email=TEST_EMAIL,
    )
    assert isinstance(
        usage_record_id,
        int,
    )
    assert (
        supabase_manager.complete_and_update_usage_record(
            usage_record_id=usage_record_id,
            token_input=1000,
            token_output=100,
            total_seconds=100,
        )
        is None
    )

    data, _ = (
        supabase_manager.client.table("usage")
        .select("*")
        .eq("user_id", user_id)
        .eq("installation_id", installation_id)
        .eq("is_completed", True)
        .execute()
    )
    assert len(data[1]) == 1
    # Clean Up
    wipe_installation_owner_user_data()


def test_create_installation() -> None:
    """Test the create_installation method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    data, _ = (
        supabase_manager.client.table("installations")
        .select("*")
        .eq("installation_id", installation_id)
        .execute()
    )
    assert len(data[1]) == 1

    # Clean Up
    wipe_installation_owner_user_data()


def test_delete_installation() -> None:
    """Test the delete_installation method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    # delete the installation
    supabase_manager.delete_installation(installation_id=installation_id, user_id=user_id)

    data, _ = (
        supabase_manager.client.table("installations")
        .select("*")
        .eq("installation_id", installation_id)
        .execute()
    )
    assert data[1][0]["uninstalled_at"] is not None

    # Clean Up
    wipe_installation_owner_user_data()


def test_get_installation_id() -> None:
    """Test the get_installation_id method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1
    owner_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=owner_id,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    retrieved_installation_id = supabase_manager.get_installation_id(owner_id=owner_id)
    assert retrieved_installation_id == installation_id

    # Clean Up
    wipe_installation_owner_user_data()


def test_get_installation_ids() -> None:
    """Test the get_installation_ids method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    installation_ids = supabase_manager.get_installation_ids()
    assert installation_id in installation_ids

    # Clean Up
    wipe_installation_owner_user_data()


def test_is_users_first_issue() -> None:
    """Test the is_users_first_issue method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    is_first_issue = supabase_manager.is_users_first_issue(user_id=user_id, installation_id=installation_id)
    assert is_first_issue is True

    # Clean Up
    wipe_installation_owner_user_data()


def test_set_issue_to_merged() -> None:
    """Test the set_issue_to_merged method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1
    unique_issue_id = "U/gitautoai/test#01"

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
        owner_type=OWNER_TYPE,
        owner_name="gitautoai",
        owner_id=-1,
        user_id=user_id,
        user_name=USER_NAME,
        email=TEST_EMAIL,
    )

    # create a user request
    supabase_manager.create_user_request(
        user_id=user_id,
        user_name=USER_NAME,
        installation_id=installation_id,
        unique_issue_id=unique_issue_id,
        email=TEST_EMAIL,
    )

    # set the issue to merged
    supabase_manager.set_issue_to_merged(unique_issue_id=unique_issue_id)

    data, _ = (
        supabase_manager.client.table("issues")
        .select("*")
        .eq("unique_id", unique_issue_id)
        .execute()
    )
    assert data[1][0]["merged"] is True

    # Clean Up
    wipe_installation_owner_user_data()


def test_set_user_first_issue_to_false() -> None:
    """Test the set_user_first_issue_to_false method"""
    supabase_manager = SupabaseManager(url=SUPABASE_URL, key=SUPABASE_SERVICE_ROLE_KEY)

    # using -1 to not conflict with real data
    user_id = -1
    installation_id = -1

    # Clean up at the beginning just in case a prior test failed to clean
    wipe_installation_owner_user_data()

    # insert data into the db -> create installation
    supabase_manager.create_installation(
        installation_id=installation_id,
