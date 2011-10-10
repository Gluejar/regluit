from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

class WishlistTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_add_remove(self):
        # add a book to the wishlist
        r = self.client.post("/wishlist/", {"googlebooks_id": "2NyiPwAACAAJ"}, 
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.user.wishlist.works.all().count(), 1)

        # remove the book
        r = self.client.post("/wishlist/", {"remove_work_id": "1"}, 
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.user.wishlist.works.all().count(), 0)
