import os
import unittest

from flask import current_app
from flask_testing import TestCase

from project import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertEqual(app.config['SECRET_KEY'], '{{secret_key}}')
        self.assertFalse(current_app is None)
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('DATABASE_URL'))


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertEqual(app.config['SECRET_KEY'], '{{secret_key}}')
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('DATABASE_TEST_URL'))


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertEqual(app.config['SECRET_KEY'], '{{secret_key}}')
        self.assertFalse(app.config['TESTING'])


if __name__ == '__main__':
    unittest.main()
