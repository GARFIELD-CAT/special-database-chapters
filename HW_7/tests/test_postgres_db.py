import pytest
from sqlalchemy.exc import IntegrityError

from HW_7.models import User, Post


class TestUserCRUD:
    def test_create_user(self, db_session, create_user):
        user = create_user()

        assert user.id is not None
        assert user.username is not None
        assert '@' in user.email
        assert len(user.full_name) > 0

        saved_user = db_session.query(User).filter_by(id=user.id).first()

        assert saved_user is not None
        assert saved_user.username == user.username

    def test_create_user_with_duplicate_username(self, db_session, create_user):
        username = 'not-unique-username'
        create_user(username=username)

        with pytest.raises(IntegrityError):
            create_user(username=username)

    def test_read_user(self, db_session, create_user):
        original_user = create_user()

        found_user = db_session.query(User).filter_by(id=original_user.id).first()

        assert found_user is not None
        assert found_user.username == original_user.username
        assert found_user.email == original_user.email
        assert found_user.full_name == original_user.full_name

    def test_update_user(self, db_session, create_user, faker):
        user = create_user()
        new_email = faker.email()
        new_full_name = faker.name()

        user.email = new_email
        user.full_name = new_full_name
        db_session.commit()

        found_user = db_session.query(User).filter_by(id=user.id).first()
        assert found_user.email == new_email
        assert found_user.full_name == new_full_name

    def test_delete_user(self, db_session, create_user):
        user = create_user()
        user_id = user.id

        found_user = db_session.query(User).filter_by(id=user_id).first()
        assert found_user is not None

        db_session.delete(user)
        db_session.commit()

        deleted_user = db_session.query(User).filter_by(id=user_id).first()
        assert deleted_user is None


class TestUserAndPostRelationship:
    def test_user_with_multiple_posts(self, db_session, create_user, create_multiple_posts):
        user = create_user()
        expected_post_count = 3
        posts = create_multiple_posts(count=expected_post_count, author_id=user.id)

        found_user_posts = db_session.query(Post).filter_by(author_id=user.id).all()

        assert len(found_user_posts) == expected_post_count

        for post in posts:
            assert post in found_user_posts


class TestQueryWithFaker:
    def test_filter_operations_with_faker_data(self, db_session, create_multiple_users):
        users = create_multiple_users(count=5)

        sample_username = users[0].username[:3]
        filtered_users = db_session.query(User).filter(
            User.username.like(f'{sample_username}%')
        ).all()

        assert len(filtered_users) >= 1

    def test_count_operation(self, db_session, create_multiple_users):
        initial_count = db_session.query(User).count()
        new_users_count = 3
        create_multiple_users(count=new_users_count)

        new_count = db_session.query(User).count()

        assert new_count == initial_count + new_users_count