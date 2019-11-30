from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Field choices
ch_semester = (
    ('Fall', 'Fall'),
    ('Winter', 'Winter'),
    ('Summer', 'Summer'),
)

ch_difficulty = (
    ('Basic', 'Basic'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
)

ch_user_status = (
    ('Pending', 'Pending Admin Approval'),
    ('Registered', 'Approved by Admin'),
)

ch_code_status = (
    ('Inactive', 'Access code has not been used'),
    ('Active', 'Access code has been used')
)

# Course & Prompt Models
class Course(models.Model):
    name = models.CharField(max_length=64)
    semester = models.CharField(max_length=64, choices=ch_semester)
    year = models.CharField(max_length=4)

    def __str__(self):
        return "[{} {}] {}".format(self.semester, self.year, self.name)

class PromptSet(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return "[{}] {}".format(self.course.name, self.name)

class Prompt(models.Model):
    name = models.CharField(max_length=100)
    ref = models.PositiveIntegerField(verbose_name="Question #")
    difficulty = models.CharField(max_length=64, choices=ch_difficulty, default="Intermediate")

    description = models.TextField(help_text="Leave blank to suggest users to refer to the PDF.", blank=True)
    hint = models.TextField(blank=True)

    rating = models.DecimalField(verbose_name="Satisfaction", max_digits=4, decimal_places=2, default=0)
    complete_count = models.PositiveIntegerField(verbose_name="# Completed", default=0)

    prompt_set = models.ForeignKey(PromptSet, on_delete=models.CASCADE)

    def __str__(self):
        return "{} #{}: {}".format(self.prompt_set.name, self.ref, self.name)

    def get_summary(self):
        output = ""

        if (not self.description) or (self.description == ""):
            output = "Please refer to PDF document for more information."
        else:
            output += self.description
            output = output[:100] + "..."

        return output

    def get_description(self):
        output = ""

        if (not self.description) or (self.description == ""):
            output = "Please refer to PDF document for more information."
        else:
            output += self.description

        return output

    def get_hint(self):
        output = ""

        if (not self.hint) or (self.hint == ""):
            output = "No hints sorry :/"
        else:
            output += self.hint

        return output

    def get_difficulty_color(self, type=0):
        diff = self.difficulty
        color = ""

        if diff == "Basic":
            color = "text-success"
        elif diff == "Intermediate":
            color = "text-primary"
        elif diff == "Advanced":
            color = "text-danger"
        else:
            color = "text-dark"

        return color

# Profile related models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usertag = models.CharField(max_length=64, blank=True)

    completed = models.ManyToManyField(Prompt, blank=True)
    status = models.CharField(max_length=64, choices=ch_user_status, default="Pending")

    def __str__(self):
        return "[{}] {}".format(self.user.username, self.usertag)

    def get_complete_count(self):
        return len(self.completed.all())

    def get_percentile(self):
        profiles = []

        query = Profile.objects.all()
        profiles += query

        profiles.sort(key=lambda x: x.get_complete_count())

        ref = profiles.index(self) + 1

        percentile = "{}th".format(int((ref/len(profiles))*100))

        return percentile

class AccessCode(models.Model):
    code = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=32, choices=ch_code_status, default='Inactive')

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, default=1)

    def __str__(self):
        return self.code
