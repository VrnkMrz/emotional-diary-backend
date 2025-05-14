from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    commander = models.ForeignKey('Users', models.DO_NOTHING, db_column='commander', blank=True, null=True, related_name = 'commanded_companies')

    class Meta:
        managed = False
        db_table = 'company'


class Diaryentries(models.Model):
    text = models.TextField()
    user_emotion = models.ForeignKey('Emotions', models.DO_NOTHING, blank=True, null=True)
    ai_emotion = models.ForeignKey('Emotions', models.DO_NOTHING, related_name='diaryentries_ai_emotion_set', blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    date = models.DateField(blank=True, null=True)
    encrypted_text = models.BinaryField(blank=True, null=True)
    iv = models.BinaryField(blank=True, null=True)
    auth_tag = models.BinaryField(blank=True, null=True)
    encryption_key = models.ForeignKey('EncryptionKeys', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diaryentries'


class EmotionAnalysis(models.Model):
    entry = models.OneToOneField(Diaryentries, models.DO_NOTHING)
    auto_emotion = models.ForeignKey('Emotions', models.DO_NOTHING)
    user_emotion = models.ForeignKey('Emotions', models.DO_NOTHING, related_name='emotionanalysis_user_emotion_set')
    model_version = models.CharField(max_length=50)
    analyzed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'emotion_analysis'


class Emotions(models.Model):
    emotion_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'emotions'


class EncryptionKeys(models.Model):
    key_version = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'encryption_keys'


class MonthlyReports(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'yyyy_mm')
    user = models.ForeignKey('Users', models.DO_NOTHING)
    yyyy_mm = models.CharField(max_length=7)
    match_count = models.IntegerField()
    total_count = models.IntegerField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'monthly_reports'


class Rank(models.Model):
    rank_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rank'


class Users(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    birthday_year = models.IntegerField()
    birthday_month = models.IntegerField()
    birthday_day = models.IntegerField()
    rank = models.ForeignKey(Rank, models.DO_NOTHING, db_column='rank', blank=True, null=True)
    company = models.ForeignKey(Company, models.DO_NOTHING, blank=True, null=True)
    email = models.TextField()
    gender = models.TextField()
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    nickname = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
