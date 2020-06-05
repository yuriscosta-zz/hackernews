from django.db import models
from django.conf import settings


class Link(models.Model):
    url = models.URLField(max_length=200)
    description = models.TextField(blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  null=True,
                                  on_delete=models.CASCADE)

    def __str__(self):
        return self.url


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    link = models.ForeignKey(Link,
                             related_name='votes',
                             on_delete=models.CASCADE)
