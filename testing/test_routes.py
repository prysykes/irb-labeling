# tests/test_routes.py
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from application import application, db, TestingConfig

# Use the TestingConfig when setting up the app for testing
application.config.from_object(TestingConfig)

@pytest.fixture
def client():
    application.config['TESTING'] = True
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with application.test_client() as client:
        with application.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_tracking_configuration_route(client):
    response = client.get('/track_completion')
    assert response.status_code == 302  # Assuming the route redirects upon success
    # Add more assertions based on the behavior of your route
