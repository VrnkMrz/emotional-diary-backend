from rest_framework import serializers
from core.models import Diaryentries, Emotions
import binascii, uuid
from django.conf import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class DiaryEntrySerializer(serializers.ModelSerializer):
    user_emotion   = serializers.CharField(source='user_emotion.emotion_name', read_only=True)
    ai_emotion     = serializers.CharField(source='ai_emotion.emotion_name',   read_only=True)
    decrypted_text = serializers.SerializerMethodField()

    class Meta:
        model = Diaryentries
        fields = [
            'id',
            'date',
            'decrypted_text',
            'user_emotion',
            'ai_emotion',
        ]
        read_only_fields = fields

    def get_decrypted_text(self, obj):
        key = binascii.unhexlify(settings.AES_ENCRYPTION_KEY_HEX)
        aesgcm = AESGCM(key)

        ciphertext = bytes(obj.encrypted_text)
        iv = bytes(obj.iv)

        raw_tag = obj.auth_tag
        if isinstance(raw_tag, uuid.UUID):
            tag = raw_tag.bytes
        else:
            tag = bytes(raw_tag)

        plaintext = aesgcm.decrypt(iv, ciphertext + tag, None)
        return plaintext.decode('utf-8')

class DiaryEntryCreateSerializer(serializers.ModelSerializer):
    encrypted_text = serializers.CharField(write_only=True)
    iv             = serializers.CharField(write_only=True)
    auth_tag       = serializers.CharField(write_only=True)
    user_emotion = serializers.PrimaryKeyRelatedField(
        queryset=Emotions.objects.all()
    )
    ai_emotion   = serializers.PrimaryKeyRelatedField(
        queryset=Emotions.objects.all()
    )

    class Meta:
        model = Diaryentries
        fields = [
            'encrypted_text', 'iv', 'auth_tag',
            'user_emotion', 'ai_emotion', 'date'
        ]

    def validate(self, data):
        if not data.get('encrypted_text'):
            raise serializers.ValidationError("Зашифрований текст обовʼязковий.")
        if not data.get('user_emotion'):
            raise serializers.ValidationError("Емоція користувача обовʼязкова.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['encrypted_text'] = binascii.unhexlify(
            validated_data.pop('encrypted_text')
        )
        validated_data['iv']             = binascii.unhexlify(
            validated_data.pop('iv')
        )
        validated_data['auth_tag']       = binascii.unhexlify(
            validated_data.pop('auth_tag')
        )
        if not validated_data.get('date'):
            validated_data['date'] = serializers.DateField().to_representation(
                serializers.DateField().to_internal_value(None)
            )
        return super().create(validated_data)

