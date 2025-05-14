from rest_framework import serializers
from core.models import Users

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'id', 'name', 'surname',
            'birthday_year','birthday_month','birthday_day',
            'rank','company',
            'email','gender','nickname',
            'created_at','updated_at',
        ]
