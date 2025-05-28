from rest_framework import serializers

class SummarySerializer(serializers.Serializer):
    totalEntries = serializers.IntegerField()
    matchCount   = serializers.IntegerField()
    matchPct     = serializers.FloatField()

class FirstEmotionSerializer(serializers.Serializer):
    date         = serializers.DateField()
    firstEmotion = serializers.CharField()

class FrequencySerializer(serializers.Serializer):
    emotion   = serializers.CharField()
    userCount = serializers.IntegerField()
    aiCount   = serializers.IntegerField()
