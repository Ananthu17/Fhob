import datetime
from enum import unique
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserMessage(models.Model):
    from_user = models.ForeignKey('hobo_user.CustomUser',
                                  verbose_name=_("From"),
                                  related_name='message_from_user',
                                  on_delete=models.CASCADE)
    to_user = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("To"),
                                related_name='message_to_user',
                                on_delete=models.CASCADE)
    subject = models.CharField(_("Subject"),
                               max_length=1000,
                               null=True, blank=True)
    msg_thread = models.CharField(_("Message thread ID"),
                                  max_length=1000,
                                  null=True, blank=True)
    message = models.TextField(_("Message"), null=True, blank=True)
    created_time = models.DateTimeField(_('Created Time'),
                                        default=datetime.datetime.now,
                                        blank=False)
    delete_for = models.ManyToManyField('hobo_user.CustomUser',
                                        blank=True,
                                        related_name='deleted_for',
                                        verbose_name=_("Delete For")
                                        )

    def __str__(self):
        return self.to_user.get_full_name()

    def generate_msg_thread(self, from_user_id, to_user_id):
        if from_user_id < to_user_id:
            thread_id = "chat_"+str(from_user_id)+"_"+str(to_user_id)
        else:
            thread_id = "chat_"+str(to_user_id)+"_"+str(from_user_id)
        return thread_id

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'


class SpamMessage(models.Model):
    spam_user = models.ForeignKey('hobo_user.CustomUser',
                                  verbose_name=_("Spam Message From"),
                                  related_name='spam_user',
                                  on_delete=models.CASCADE)
    reported_by = models.ForeignKey('hobo_user.CustomUser',
                                    verbose_name=_("Reported By"),
                                    related_name='reported_by_user',
                                    on_delete=models.CASCADE)
    created_time = models.DateTimeField(_('Created Time'),
                                        default=datetime.datetime.now,
                                        blank=False)

    def __str__(self):
        return self.spam_user.get_full_name()

    class Meta:
        verbose_name = 'Spam Message'
        verbose_name_plural = 'Spam Messages'


class MessageStatus(models.Model):
    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("User"),
                             related_name='user_message',
                             on_delete=models.CASCADE)
    msg_thread = models.CharField(_("Message thread ID"),
                                  max_length=1000,
                                  null=True, blank=True)
    is_read = models.BooleanField(_('Is Read'), default=False)
    is_priority = models.BooleanField(_('Is Priority'), default=False)
    is_spam = models.BooleanField(_('Is Spam'), default=False)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'Message Status'
        verbose_name_plural = 'Messages Status'


class MessageNotification(models.Model):
    READ = 'read'
    UNREAD = 'unread'
    STATUS_CHOICES = [
                    (READ, 'Read'),
                    (UNREAD, 'Unread'),
                    ]
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='msg_notification_to',
                             verbose_name=_("User"),
                             null=True)
    from_user = models.ForeignKey("hobo_user.CustomUser",
                                  on_delete=models.CASCADE,
                                  related_name='msg_notification_from',
                                  verbose_name=_("Notification From"),
                                  null=True)
    status_type = models.CharField(_("Status Type"),
                                   choices=STATUS_CHOICES,
                                   max_length=150, default=UNREAD)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)
    notification_message = models.TextField(_("Message"), null=True, blank=True)
    msg_thread = models.CharField(_("Message thread ID"),
                                  max_length=1000,
                                  null=True, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Message Notification'
        verbose_name_plural = 'Message Notifications'


class UserMessageImages(models.Model):
    message = models.ForeignKey(UserMessage,
                                on_delete=models.CASCADE,
                                related_name='msg_image',
                                verbose_name=_("User"),
                                null=True)
    image = models.ImageField(upload_to='gallery/messages/')

    def __str__(self):
        return str(self.message)
    class Meta:
        verbose_name = 'User Message Image'
        verbose_name_plural = 'User Message Images'


class UserMessageFileUpload(models.Model):
    PDF = 'pdf'
    EXCEL = 'excel'
    WORD = 'word'
    FILE_TYPE_CHOICES = [
                    (PDF, 'Pdf'),
                    (EXCEL, 'Excel'),
                    (WORD, 'Word'),
                    ]
    message = models.ForeignKey(UserMessage,
                                on_delete=models.CASCADE,
                                related_name='msg_file',
                                verbose_name=_("User"),
                                null=True)
    file = models.FileField(upload_to='message_files/')
    file_type = models.CharField(_("File Type"),
                                 choices=FILE_TYPE_CHOICES,
                                 max_length=150,
                                 default=PDF)

    def __str__(self):
        return str(self.message)

    class Meta:
        verbose_name = 'User Message File Upload'
        verbose_name_plural = 'User Message File Uploads'
