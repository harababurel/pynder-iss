from wtforms import Form, BooleanField, IntegerField, RadioField, \
    SelectMultipleField, validators, TextAreaField, widgets


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SettingsForm(Form):
    age_min = IntegerField('Minimum Age',
                           [validators.data_required(),
                            validators.number_range(min=18, max=100)])
    age_max = IntegerField('Maximum Age',
                           [validators.data_required(),
                            validators.number_range(min=18, max=100)])
    gender_filter = RadioField('Interested in', choices=[
        ('male', 'Men'), ('female', 'Women')])
    gender = RadioField('Gender', choices=[
        ('male', 'Male'), ('female', 'Female')])

    bio = TextAreaField("Bio")
    discoverable = BooleanField("Discoverable")
    distance_filter = IntegerField("Distance Filter",
                                   [validators.data_required(),
                                    validators.number_range(min=1, max=100)])

    def fill_fields_from_profile(self, pynder_session):
        profile = pynder_session.profile

        self.age_min.data = profile.age_filter_min
        self.age_max.data = profile.age_filter_max
        try:
            self.gender_filter.data = list(profile.interested_in)[0]
        except:
            self.gender_filter.data = 'nothing'

        print("profile.interested_in = %r" % self.gender_filter.data)
        self.bio.data = profile.bio
        print("profile.bio = %r" % profile.bio)
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
                'female': 1,
            }[self.gender_filter.data],
        }

        print("Updating profile with the following settings:")
        print(new_settings)

        # bio might need to be set in the profile as well
        # in order to show up as updated in the form
        pynder_session.profile.bio = self.bio.data
        response = pynder_session.update_profile(new_settings)

        print("Updated profile. Response:")
        print(response)
