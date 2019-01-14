import unittest

from project import db
from project.models import Indicator
from project.tests.base import BaseTestCase


class TestIndicatorModel(BaseTestCase):
    """ Tests for the Indicator database model """

    def test_indicator_creation(self):
        ind = Indicator(_type_id=1, value='123456', _confidence_id=1, _impact_id=1, _status_id=1)
        db.session.add(ind)
        db.session.commit()

        results = db.session.query(Indicator).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].value, '123456')

    def test_indicator_child_relationships(self):
        # Setup and initial state
        ind1 = Indicator(_type_id=1, value='12345', _confidence_id=1, _impact_id=1, _status_id=1)
        ind2 = Indicator(_type_id=2, value='67890', _confidence_id=1, _impact_id=1, _status_id=1)
        ind3 = Indicator(_type_id=2, value='99999', _confidence_id=1, _impact_id=1, _status_id=1)
        ind4 = Indicator(_type_id=2, value='88888', _confidence_id=1, _impact_id=1, _status_id=1)
        db.session.add(ind1)
        db.session.add(ind2)
        db.session.add(ind3)
        db.session.add(ind4)

        self.assertEqual(ind1.get_children(), [])
        self.assertEqual(ind1.get_parent(), None)
        self.assertEqual(ind2.get_children(), [])
        self.assertEqual(ind2.get_parent(), None)
        self.assertEqual(ind3.get_children(), [])
        self.assertEqual(ind3.get_parent(), None)
        self.assertEqual(ind4.get_children(), [])
        self.assertEqual(ind4.get_parent(), None)

        # Create test children
        ind1.add_child(ind2)
        ind2.add_child(ind3)
        ind2.add_child(ind4)

        db.session.commit()

        """
        The relationships now look as follows:

        1
         \
          2
          |\
          3 4
        """

        # Direct relationships
        self.assertTrue(ind1.is_parent(ind2, grandchildren=False))
        self.assertTrue(ind2.is_child(ind1, grandchildren=False))
        self.assertFalse(ind1.is_child(ind2, grandchildren=False))
        self.assertFalse(ind2.is_parent(ind1, grandchildren=False))
        self.assertEqual(ind1, ind2.get_parent())
        self.assertEqual(len(ind1.get_children(grandchildren=False)), 1)

        self.assertTrue(ind2.is_parent(ind3, grandchildren=False))
        self.assertTrue(ind3.is_child(ind2, grandchildren=False))
        self.assertFalse(ind2.is_child(ind3, grandchildren=False))
        self.assertFalse(ind3.is_parent(ind2, grandchildren=False))
        self.assertEqual(ind2, ind3.get_parent())

        self.assertTrue(ind2.is_parent(ind4, grandchildren=False))
        self.assertTrue(ind4.is_child(ind2, grandchildren=False))
        self.assertFalse(ind2.is_child(ind4, grandchildren=False))
        self.assertFalse(ind4.is_parent(ind2, grandchildren=False))
        self.assertEqual(ind2, ind4.get_parent())
        self.assertEqual(len(ind2.get_children(grandchildren=False)), 2)

        # Indirect relationships
        self.assertTrue(ind1.is_parent(ind3))
        self.assertTrue(ind3.is_child(ind1))
        self.assertFalse(ind1.is_child(ind3))
        self.assertFalse(ind3.is_parent(ind1))

        self.assertTrue(ind1.is_parent(ind4))
        self.assertTrue(ind4.is_child(ind1))
        self.assertFalse(ind1.is_child(ind4))
        self.assertFalse(ind4.is_parent(ind1))
        self.assertEqual(len(ind1.get_children()), 3)

        # Try and add an indicator as its own child.
        # This shouldn't do anything.
        ind1.add_child(ind1)
        db.session.commit()

        self.assertFalse(ind1.is_parent(ind1))
        self.assertFalse(ind1.is_child(ind1))
        self.assertEqual(len(ind1.get_children(grandchildren=False)), 1)

        # Try and add a child to second parent.
        # This shouldn't do anything since it's okay to be a single-parent.
        ind1.add_child(ind3)
        db.session.commit()

        self.assertFalse(ind1.is_parent(ind3, grandchildren=False))
        self.assertFalse(ind3.is_child(ind1, grandchildren=False))
        self.assertEqual(len(ind1.get_children(grandchildren=False)), 1)
        self.assertEqual(len(ind1.get_children()), 3)

        # Remove relationship and emancipate a child.
        ind1.remove_child(ind2)
        db.session.commit()

        """
        The relationships now look as follows:

        1
         
          2
          |\
          3 4
        """

        # Direct relationships
        self.assertFalse(ind1.is_parent(ind2, grandchildren=False))
        self.assertFalse(ind2.is_child(ind1, grandchildren=False))
        self.assertFalse(ind1.is_child(ind2, grandchildren=False))
        self.assertFalse(ind2.is_parent(ind1, grandchildren=False))
        self.assertEqual(None, ind2.get_parent())
        self.assertEqual(len(ind1.get_children(grandchildren=False)), 0)

        self.assertTrue(ind2.is_parent(ind3, grandchildren=False))
        self.assertTrue(ind3.is_child(ind2, grandchildren=False))
        self.assertFalse(ind2.is_child(ind3, grandchildren=False))
        self.assertFalse(ind3.is_parent(ind2, grandchildren=False))
        self.assertEqual(ind2, ind3.get_parent())

        self.assertTrue(ind2.is_parent(ind4, grandchildren=False))
        self.assertTrue(ind4.is_child(ind2, grandchildren=False))
        self.assertFalse(ind2.is_child(ind4, grandchildren=False))
        self.assertFalse(ind4.is_parent(ind2, grandchildren=False))
        self.assertEqual(ind2, ind4.get_parent())
        self.assertEqual(len(ind2.get_children(grandchildren=False)), 2)

        # Indirect relationships
        self.assertFalse(ind1.is_parent(ind3))
        self.assertFalse(ind3.is_child(ind1))
        self.assertFalse(ind1.is_child(ind3))
        self.assertFalse(ind3.is_parent(ind1))

        self.assertFalse(ind1.is_parent(ind4))
        self.assertFalse(ind4.is_child(ind1))
        self.assertFalse(ind1.is_child(ind4))
        self.assertFalse(ind4.is_parent(ind1))
        self.assertEqual(len(ind1.get_children()), 0)

    def test_indicator_equal_relationships(self):
        # Setup and initial state
        ind1 = Indicator(_type_id=1, value='12345', _confidence_id=1, _impact_id=1, _status_id=1)
        ind2 = Indicator(_type_id=2, value='67890', _confidence_id=1, _impact_id=1, _status_id=1)
        ind3 = Indicator(_type_id=2, value='99999', _confidence_id=1, _impact_id=1, _status_id=1)
        ind4 = Indicator(_type_id=2, value='88888', _confidence_id=1, _impact_id=1, _status_id=1)
        db.session.add(ind1)
        db.session.add(ind2)
        db.session.add(ind3)
        db.session.add(ind4)

        self.assertEqual(ind1.get_equal(), [])
        self.assertEqual(ind2.get_equal(), [])
        self.assertEqual(ind3.get_equal(), [])
        self.assertEqual(ind4.get_equal(), [])

        # Create test relationships
        ind1.make_equal(ind2)
        ind2.make_equal(ind3)
        ind4.make_equal(ind1)

        db.session.commit()

        """
        The relationships now look as follows:

        1 - 2 - 3
         \
          4
        """

        # Direct relationships
        self.assertTrue(ind1.is_equal(ind2, recursive=False))
        self.assertTrue(ind2.is_equal(ind1, recursive=False))

        self.assertTrue(ind1.is_equal(ind4, recursive=False))
        self.assertTrue(ind4.is_equal(ind1, recursive=False))

        self.assertTrue(ind2.is_equal(ind3, recursive=False))
        self.assertTrue(ind3.is_equal(ind2, recursive=False))

        self.assertEqual(len(ind1.get_equal(recursive=False)), 2)
        self.assertEqual(len(ind2.get_equal(recursive=False)), 2)
        self.assertEqual(len(ind3.get_equal(recursive=False)), 1)
        self.assertEqual(len(ind4.get_equal(recursive=False)), 1)

        # Indirect relationships
        self.assertFalse(ind1.is_equal(ind3, recursive=False))
        self.assertFalse(ind3.is_equal(ind1, recursive=False))
        self.assertTrue(ind1.is_equal(ind3))
        self.assertTrue(ind3.is_equal(ind1))

        self.assertFalse(ind4.is_equal(ind3, recursive=False))
        self.assertFalse(ind3.is_equal(ind4, recursive=False))
        self.assertTrue(ind4.is_equal(ind3))
        self.assertTrue(ind3.is_equal(ind4))

        self.assertFalse(ind4.is_equal(ind2, recursive=False))
        self.assertFalse(ind2.is_equal(ind4, recursive=False))
        self.assertTrue(ind4.is_equal(ind2))
        self.assertTrue(ind2.is_equal(ind4))

        self.assertEqual(len(ind1.get_equal()), 3)
        self.assertEqual(len(ind2.get_equal()), 3)
        self.assertEqual(len(ind3.get_equal()), 3)
        self.assertEqual(len(ind4.get_equal()), 3)

        # Try to add a redundant indirect relationship
        # This shouldn't do anything since 3 is already indirectly equal to 4.
        ind4.make_equal(ind3)
        db.session.commit()

        self.assertEqual(len(ind3.get_equal(recursive=False)), 1)
        self.assertEqual(len(ind4.get_equal(recursive=False)), 1)
        self.assertEqual(len(ind3.get_equal()), 3)
        self.assertEqual(len(ind4.get_equal()), 3)

        # Try to make an indicator equal to itself.
        # This shouldn't work.
        ind1.make_equal(ind1)
        db.session.commit()

        self.assertFalse(ind1.is_equal(ind1))
        self.assertEqual(len(ind1.get_equal(recursive=False)), 2)

        # Remove relationship
        ind1.remove_equal(ind2)
        db.session.commit()

        """
        The relationships now look as follows:

        1   2 - 3
         \
          4
        """

        # Direct relationships
        self.assertFalse(ind1.is_equal(ind2, recursive=False))
        self.assertFalse(ind2.is_equal(ind1, recursive=False))

        self.assertTrue(ind1.is_equal(ind4, recursive=False))
        self.assertTrue(ind4.is_equal(ind1, recursive=False))

        self.assertTrue(ind2.is_equal(ind3, recursive=False))
        self.assertTrue(ind3.is_equal(ind2, recursive=False))

        self.assertEqual(len(ind1.get_equal(recursive=False)), 1)
        self.assertEqual(len(ind2.get_equal(recursive=False)), 1)
        self.assertEqual(len(ind3.get_equal(recursive=False)), 1)
        self.assertEqual(len(ind4.get_equal(recursive=False)), 1)

        # Indirect relationships
        self.assertFalse(ind1.is_equal(ind3, recursive=False))
        self.assertFalse(ind3.is_equal(ind1, recursive=False))
        self.assertFalse(ind1.is_equal(ind3))
        self.assertFalse(ind3.is_equal(ind1))

        self.assertFalse(ind4.is_equal(ind3, recursive=False))
        self.assertFalse(ind3.is_equal(ind4, recursive=False))
        self.assertFalse(ind4.is_equal(ind3))
        self.assertFalse(ind3.is_equal(ind4))

        self.assertFalse(ind4.is_equal(ind2, recursive=False))
        self.assertFalse(ind2.is_equal(ind4, recursive=False))
        self.assertFalse(ind4.is_equal(ind2))
        self.assertFalse(ind2.is_equal(ind4))

        self.assertEqual(len(ind1.get_equal()), 1)
        self.assertEqual(len(ind2.get_equal()), 1)
        self.assertEqual(len(ind3.get_equal()), 1)
        self.assertEqual(len(ind4.get_equal()), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
