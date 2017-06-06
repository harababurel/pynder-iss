from pynder.constants import GENDER_MAP, GENDER_MAP_REVERSE
from pynder.models.me import ProfileDescriptor
from wtforms import Form, BooleanField, IntegerField, RadioField, SelectMultipleField, validators, TextAreaField, widgets


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class GenderDescriptorModified(ProfileDescriptor):
    def __get__(self, instance, owner):
        gender = super(GenderDescriptorModified, self).__get__(instance, owner)
        return GENDER_MAP[gender]

    def __set__(self, instance, value):
        gender = GENDER_MAP_REVERSE[value]
        return super(GenderDescriptorModified, self).__set__(instance, gender)


class InterestedInDescriptorModified(ProfileDescriptor):
    # makes gender human readable

    def __get__(self, instance, owner):
        interested_in = super(InterestedInDescriptorModified, self).\
            __get__(instance, owner)
        return map(lambda x: GENDER_MAP[x], interested_in)

    def __set__(self, instance, value):
        interested_in = list(map(lambda x: GENDER_MAP_REVERSE[x], value))
        return super(InterestedInDescriptorModified, self).\
            __set__(instance, interested_in)


class SettingsForm(Form):
    age_min = IntegerField('Minimum Age', [validators.data_required(),validators.number_range(min=18, max=100)])
    age_max = IntegerField('Maximum Age', [validators.data_required(), validators.number_range(min=18, max=100)])
    gender = RadioField('Gender', choices=[('male','Male'),('female','Female')])
    # interested_in = MultiCheckboxField('Interested in:', choices=[('male', 'Male'), ('female', 'Female')])
    bio = TextAreaField("Bio")
    discoverable = BooleanField("Discoverable")
    distance_filter = IntegerField("Distance Filter", [validators.data_required(), validators.number_range(min=1, max=100)])


    def set_fields_from_profile(self, profile):
        # self.interested_in.data = list(InterestedInDescriptorModified('interested_in').__get__(profile, None)) - not working - API related
        self.age_min.data = ProfileDescriptor('age_filter_min').__get__(profile, None)
        self.age_max.data = ProfileDescriptor('age_filter_max').__get__(profile, None)
        self.gender.data = GenderDescriptorModified('gender').__get__(profile, None)
        self.bio.data = ProfileDescriptor('bio').__get__(profile, None)
        self.distance_filter.data = ProfileDescriptor('distance_filter').__get__(profile, None)
        self.discoverable.data = ProfileDescriptor('discoverable').__get__(profile, None)

    def set_profile_from_fields(self, profile):
        ProfileDescriptor('bio').__set__(profile, self.bio.data)
        ProfileDescriptor('discoverable').__set__(profile, self.discoverable.data)
        ProfileDescriptor('distance_filter').__set__(profile, self.distance_filter.data)
        ProfileDescriptor('age_filter_min').__set__(profile, self.age_min.data)
        ProfileDescriptor('age_filter_max').__set__(profile, self.age_max.data)
        GenderDescriptorModified('gender').__set__(profile, self.gender.data)
        # InterestedInDescriptorModified('interested_in').__set__(profile, self.interested_in.data)
