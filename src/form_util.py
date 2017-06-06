from pynder.constants import GENDER_MAP, GENDER_MAP_REVERSE
from pynder.models.me import ProfileDescriptor
from wtforms import Form, BooleanField, IntegerField, RadioField, SelectMultipleField, validators, TextAreaField, widgets


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# class GenderDescriptorModified(ProfileDescriptor):

#     def __get__(self, instance, owner):
#         gender = super(GenderDescriptorModified, self).__get__(instance, owner)
#         return GENDER_MAP[gender]

#     def __set__(self, instance, value):
#         gender = GENDER_MAP_REVERSE[value]
# return super(GenderDescriptorModified, self).__set__(instance, gender)


# class InterestedInDescriptorModified(ProfileDescriptor):
#     # makes gender human readable

#     def __get__(self, instance, owner):
#         interested_in = super(InterestedInDescriptorModified, self).\
#             __get__(instance, owner)
#         return map(lambda x: GENDER_MAP[x], interested_in)

#     def __set__(self, instance, value):
#         interested_in = list(map(lambda x: GENDER_MAP_REVERSE[x], value))
#         return super(InterestedInDescriptorModified, self).\
#             __set__(instance, interested_in)


class SettingsForm(Form):
    age_min = IntegerField('Minimum Age', [
                           validators.data_required(), validators.number_range(min=18, max=100)])
    age_max = IntegerField('Maximum Age', [
                           validators.data_required(), validators.number_range(min=18, max=100)])
    gender_filter = RadioField('Interested in', choices=[
        ('male', 'Men'), ('female', 'Women')])
    bio = TextAreaField("Bio")
    discoverable = BooleanField("Discoverable")
    distance_filter = IntegerField("Distance Filter", [
                                   validators.data_required(), validators.number_range(min=1, max=100)])

    def fill_fields_from_profile(self, pynder_session):
        profile = pynder_session.profile

        self.age_min.data = profile.age_filter_min
        self.age_max.data = profile.age_filter_max
        self.gender_filter.data = profile.interested_in
        self.bio.data = profile.bio
        self.distance_filter.data = profile.distance_filter
        self.discoverable.data = profile.discoverable

    def update_profile_from_fields(self, pynder_session):
        new_settings = {
            'bio': self.bio.data,
            'discoverable': self.discoverable.data,
            'distance_filter': self.distance_filter.data,
            'age_filter_min': self.age_min.data,
            'age_filter_max': self.age_max.data,
            'gender_filter': {
                'male': 0,
                'female': 1
            }[self.gender_filter.data],
        }

        print("Updating profile with the following settings:")
        print(new_settings)

        response = pynder_session.update_profile(new_settings)

        print("Updated profile. Response:")
        print(response)

        # ProfileDescriptor('bio').__set__(profile, self.bio.data)
        # ProfileDescriptor('discoverable').__set__(
        #     profile, self.discoverable.data)
        # ProfileDescriptor('distance_filter').__set__(
        #     profile, self.distance_filter.data)
        # ProfileDescriptor('age_filter_min').__set__(profile, self.age_min.data)
        # ProfileDescriptor('age_filter_max').__set__(profile, self.age_max.data)
        # GenderDescriptorModified('gender').__set__(profile, self.gender.data)
        # InterestedInDescriptorModified('interested_in').__set__(profile, self.interested_in.data)
