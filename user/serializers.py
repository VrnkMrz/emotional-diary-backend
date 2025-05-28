from rest_framework import serializers
from core.models import Users, Company, Rank, Diaryentries

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'location']

class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ['id', 'rank_name', 'description']

class UserProfileSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    rank = RankSerializer(read_only=True)
    birthday = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            'id',
            'name',
            'surname',
            'nickname',
            'email',
            'gender',
            'birthday',
            'company',
            'rank',
            'created_at',
            'updated_at',
        ]

    def get_birthday(self, obj):
        return f"{obj.birthday_year:04d}-{obj.birthday_month:02d}-{obj.birthday_day:02d}"

class DiaryEntrySerializer(serializers.ModelSerializer):
    user_emotion = serializers.CharField(source='user_emotion.emotion_name')
    ai_emotion   = serializers.CharField(source='ai_emotion.emotion_name')
    date         = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Diaryentries
        fields = ['id', 'date', 'user_emotion', 'ai_emotion']
