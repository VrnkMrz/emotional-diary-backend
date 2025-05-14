# #!/usr/bin/env python
# # backend/assign_passwords.py
#
# import os
# import sys
# import binascii
# from django.utils import timezone
#
# # ---- bootstrap Django environment ----
# # Додаємо поточну папку (де лежить manage.py та емоційну аплікацію) в sys.path
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, BASE_DIR)
#
# # Вказуємо модуль налаштувань
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotional_diary_backend.settings')
#
# # Підтягуємо Django
# import django
# django.setup()
# # ---------------------------------------
#
# from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# from core.models import Diaryentries, EncryptionKeys
#
# # Один разочок: ваш 256-бітний ключ в hex-форматі
# AES_ENCRYPTION_KEY_HEX = '0d1a0ed50b6db9e4a1c8f2d3b4e5f6a7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3'
#
# def main():
#     # Розбираємо ключ
#     try:
#         key = binascii.unhexlify(AES_ENCRYPTION_KEY_HEX)
#     except (TypeError, ValueError) as e:
#         print(f"❌ Невірний формат AES_ENCRYPTION_KEY_HEX: {e}")
#         return
#
#     aesgcm = AESGCM(key)
#
#     # Створюємо запис у таблиці EncryptionKeys
#     version = timezone.now().strftime('%Y%m%d%H%M%S')
#     ek = EncryptionKeys.objects.create(
#         key_version=version,
#         created_at=timezone.now()
#     )
#     print(f"→ Створено EncryptionKey id={ek.pk} version={version}")
#
#     # Знаходимо всі записи без зашифрованого тексту
#     qs = Diaryentries.objects.filter(encrypted_text__isnull=True, text__isnull=False)
#     total = qs.count()
#     if total == 0:
#         print("✔️ Немає жодного запису для шифрування.")
#         return
#
#     done = 0
#     for entry in qs:
#         iv = os.urandom(12)  # 96-бітний IV
#         plaintext = entry.text.encode('utf-8')
#         ct_and_tag = aesgcm.encrypt(iv, plaintext, None)
#         ciphertext, tag = ct_and_tag[:-16], ct_and_tag[-16:]
#
#         entry.encrypted_text   = ciphertext
#         entry.iv               = iv
#         entry.auth_tag         = tag
#         entry.encryption_key   = ek
#         entry.save(update_fields=['encrypted_text','iv','auth_tag','encryption_key'])
#         print(f"  • зашифровано entry id={entry.pk}")
#         done += 1
#
#     print(f"✔️ Успішно зашифровано {done}/{total} записів.")
#
# if __name__ == '__main__':
#     main()
