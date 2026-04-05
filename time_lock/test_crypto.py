import os
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import crypto


class TestCrypto(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "messages.json")
        with patch.object(crypto, 'DATA_FILE', self.test_file):
            pass

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    def test_encrypt_and_decrypt_message(self):
        with patch.object(crypto, 'DATA_FILE', self.test_file):
            past_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            result = crypto.encrypt_message("Hello World", past_date, "testpassword")
            
            self.assertIn("id", result)
            self.assertEqual(result["unlock_date"], past_date)
            
            decrypt_result = crypto.decrypt_message(result["id"], "testpassword")
            self.assertEqual(decrypt_result["status"], "unlocked")
            self.assertEqual(decrypt_result["content"], "Hello World")

    def test_decrypt_message_locked(self):
        with patch.object(crypto, 'DATA_FILE', self.test_file):
            future_date = (datetime.now() + timedelta(days=30)).strftime("%Y%m%d")
            result = crypto.encrypt_message("Secret", future_date, "password")
            
            decrypt_result = crypto.decrypt_message(result["id"], "password")
            self.assertEqual(decrypt_result["status"], "locked")
            self.assertIn("remaining", decrypt_result)

    def test_decrypt_message_wrong_password(self):
        with patch.object(crypto, 'DATA_FILE', self.test_file):
            past_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            result = crypto.encrypt_message("Secret", past_date, "correctpassword")
            
            decrypt_result = crypto.decrypt_message(result["id"], "wrongpassword")
            self.assertEqual(decrypt_result["status"], "error")
            self.assertEqual(decrypt_result["message"], "密码错误")

    def test_decrypt_nonexistent_message(self):
        with patch.object(crypto, 'DATA_FILE', self.test_file):
            result = crypto.decrypt_message("nonexistent", "password")
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["message"], "消息不存在")

    def test_list_messages(self):
        with patch.object(crypto, 'DATA_FILE', self.test_file):
            future_date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
            past_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            
            r1 = crypto.encrypt_message("msg1", future_date, "pass")
            r2 = crypto.encrypt_message("msg2", past_date, "pass")
            
            messages = crypto.list_messages()
            self.assertEqual(len(messages), 2)
            
            msg_ids = [m["id"] for m in messages]
            self.assertIn(r1["id"], msg_ids)
            self.assertIn(r2["id"], msg_ids)


if __name__ == "__main__":
    unittest.main()