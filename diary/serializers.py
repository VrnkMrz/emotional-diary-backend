import binascii

from django.conf import settings
from rest_framework import serializers
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.models import Diaryentries, Emotions

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
        """
        Дешифруємо AES-GCM: беремо ключ із settings, IV, ciphertext та auth_tag,
        повертаємо UTF-8 рядок.
        """
        key_hex = settings.AES_ENCRYPTION_KEY_HEX
        key     = binascii.unhexlify(key_hex)

        aesgcm = AESGCM(key)

        ciphertext = obj.encrypted_text  # BYTEA
        tag        = obj.auth_tag
        iv         = obj.iv

        plaintext = aesgcm.decrypt(iv, ciphertext + tag, None)
        return plaintext.decode('utf-8')
