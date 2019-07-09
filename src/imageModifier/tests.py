from django.core.urlresolvers import reverse
from django.test import TestCase


# Create your tests here.


class UploadTransformableImageViewTests(TestCase):
    def test_upload_image_view_with_no_image_and_not_logged_in(self):
        """
        The basic view should always be displayable.
        """
        response = self.client.get(reverse('imageModifier:uploadTransformableImage'))
        self.assertEqual(response.status_code, 200)

    # def test_upload_image_view_post_new_image(self):
    #     """
    #     Post a new picture.
    #     """
    #     with open('media/testPicture.jpg') as image_imported:
    #         response = self.client.post(reverse('imageModifier:uploadTransformableImage'),
    #                                     {'uploaded_image': image_imported})
    #     self.assertEqual(response.status_code, 200)
