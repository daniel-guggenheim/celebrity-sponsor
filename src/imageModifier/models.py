import datetime
from io import BytesIO
import os

from django.conf import settings

from django.core.files.base import ContentFile

from django.db import models

from PIL import Image

from aiaUsers.models import Company, UserDetails


class CompanyLogoImage(models.Model):
    pub_date = models.DateTimeField('date uploaded')
    companyImageUploaded = models.ImageField(upload_to='companiesLogos')
    related_company = models.ForeignKey(Company, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "pk = " + str(self.pk) + ";  company = " + str(self.related_company) + \
               "; image: " + self.companyImageUploaded.name


class TransformedImageBuilder(models.Model):
    '''
    Class that helps to construct the transformed image.
    '''
    upload_date = models.DateTimeField('upload date')
    last_update_date = models.DateTimeField('last update', null=False, blank=False)
    base_image = models.ImageField(upload_to='baseImages')
    intermediary_image = models.ImageField(upload_to='intermediaryImages', blank=True)
    company_logo = models.ForeignKey(CompanyLogoImage, null=True, blank=True, on_delete=models.SET_NULL)
    user_proposition = models.OneToOneField('campaignManager.UserProposition', on_delete=models.CASCADE, null=True, blank=True)
    image_parameter_logo_width = models.FloatField(null=True, blank=True)
    image_parameter_logo_left_position = models.FloatField(null=True, blank=True)
    image_parameter_logo_top_position = models.FloatField(null=True, blank=True)
    image_parameter_base_image_ratio = models.FloatField(null=True, blank=True)

    def generate_intermediary_image(self):
        if not self.__possible_to_make_intermediary_image():
            return False
        else:
            self.make_intermediary_image(self.image_parameter_logo_width, self.image_parameter_logo_left_position,
                                         self.image_parameter_logo_top_position, self.image_parameter_base_image_ratio)

    def make_intermediary_image(self, logo_width, logo_left_pos, logo_top_pos, ratio):
        """
        Makes the intermediary image by pasting the company_logo onto the base_image.
        Requires that the class run the method __possible_to_make_intermediary_image()
        :return: boolean
                tells if the intermediary_image was saved or not.
        """
        if not self.__possible_to_make_intermediary_image():
            return False
        try:
            print("entering try")
            pil_intermediary_image = self.__blend_logo_and_base_images_to_pil(logo_width, logo_left_pos, logo_top_pos,
                                                                              ratio)
            # pil_intermediary_image.show()
            print("pil made")
            self.__save_pil_image_as_intermediary_image_field(pil_intermediary_image)
            print("image saved.")
        except Exception as e:
            print("There is an error converting or saving the pil image.")
            print(e)

    def __blend_logo_and_base_images_to_pil(self, logo_width, logo_left_pos, logo_top_pos, ratio):
        logo_object = self.company_logo.companyImageUploaded
        paste_position = (int(logo_left_pos * ratio), int(logo_top_pos * ratio))
        logo_new_size = (int(logo_width * ratio), int(logo_object.height / logo_object.width * logo_width * ratio))
        logo_object.open()

        bg_image_pil = Image.open(self.base_image)
        logo_image_pil = Image.open(logo_object)

        # Change logo size and paste it on background image
        logo_image_pil = logo_image_pil.resize(logo_new_size, Image.ANTIALIAS)
        bg_image_pil.paste(logo_image_pil, paste_position, logo_image_pil)  # paste logo in a transparent way
        return bg_image_pil

    def __save_pil_image_as_intermediary_image_field(self, pil_intermediary_image):
        """
        Transform the pil image pil_intermediary_image into an image made for the django ImageField.
        Save the image in the intermediary_image_field of the TransformedImageBuilder class.
        :param pil_intermediary_image: A PIL image made before with the PIL library
        :return: nothing
        """
        new_file_format = 'png'
        now_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        new_image_name = TransformedImageBuilder.filename_minus_extension(
            self.base_image.name) + '_transformed' + now_string + '.' + new_file_format
        print("New file name is :" + new_image_name)

        image_io = BytesIO()
        # TODO : if the image is not saved correctly, we loose the last image
        try:
            pil_intermediary_image.save(image_io, format=new_file_format)
            image_file = image_io.getvalue()
            self.intermediary_image.delete(save=False)
            try:
                self.intermediary_image
            except AttributeError:
                print("intermediary image attribute has been erased correctly.")
            else:
                print("!! intermediary image attribute NOT erased !!")
            self.intermediary_image.save(new_image_name, ContentFile(image_file))
            # self.intermediary_image.save()
        except:
            print("Problem in saving file. Last image might have been erased! Bug to correct!")
        finally:
            image_io.close()

    @staticmethod
    def filename_minus_extension(file_name):
        basename, extension = os.path.splitext(os.path.basename(file_name))
        return basename

    # TODO implement this method
    def __possible_to_make_intermediary_image(self):
        """
        Check if it is possible to make an intermediary image with the current class attributes.
        Check that the following class attributes are non-null: base_image, company_logo, logo_size, logo_position
        :return: boolean
                State if it is possible to create an intermediary_image by using the method make_intermediary_image.
        """
        return True

    def __str__(self):
        res = "pk = " + str(self.pk) + "; image: " + self.base_image.name
        if self.company_logo is not None:
            res += " ; logo: " + self.company_logo.companyImageUploaded.name
        return res


class TransformedImage(models.Model):
    transformed_image_builder = models.OneToOneField(TransformedImageBuilder, on_delete=models.CASCADE)
    transformed_image = models.ImageField(upload_to='transformedImages')
    creation_date = models.DateTimeField('creation date')

# def get_upload_path(name):
#     return 'company_{0}'.format(name)


# def user_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return 'user_{0}/{1}'.format(instance.user.id, filename)
#
#
# class MyModel(models.Model):
#     upload = models.FileField(upload_to=user_directory_path)
