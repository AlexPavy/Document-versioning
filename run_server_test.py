import json
import time
import unittest
from run_server import app, db


class ServerTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        db.clear()

    def test_gets_documents_empty(self):
        docs = self.app.get("/documents")
        self.assertListEqual([], docs.json)

    def test_get_documents(self):
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        docs = self.app.get("/documents")
        self.assertListEqual(['firstdoc'], docs.json)

    def test_get_documents_2docs(self):
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        self.app.post(
            "/documents/seconddoc",
            data=json.dumps({"content": "The second document"}),
            content_type='application/json'
        )
        docs = self.app.get("/documents")
        self.assertListEqual(['firstdoc', 'seconddoc'], docs.json)

    def test_get_revisions_not_found(self):
        err = self.app.get("/documents/notexist")
        self.assertEqual(404, err.status_code)

    def test_get_revisions(self):
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        time.sleep(0.1)
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document updated"}),
            content_type='application/json'
        )
        doc = self.app.get("/documents/firstdoc")
        self.assertIn(
            'The first document',
            list(doc.json["revisions"].values())
        )
        self.assertIn(
            'The first document updated',
            list(doc.json["revisions"].values())
        )

    def test_get_by_timestamp(self):
        res1 = self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        time.sleep(0.1)
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document updated"}),
            content_type='application/json'
        )
        ts1 = res1.json["timestamp"]
        doc = self.app.get(f"/documents/firstdoc/{ts1}")
        self.assertEqual('The first document', doc.json["content"])

    def test_get_by_latest_timestamp(self):
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        time.sleep(0.1)
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document updated"}),
            content_type='application/json'
        )
        doc = self.app.get(f"/documents/firstdoc/latest")
        self.assertEqual('The first document updated', doc.json["content"])

    def test_get_by_timestamp_before_doc(self):
        ts1 = str(time.time())
        time.sleep(0.2)
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        err = self.app.get(f"/documents/firstdoc/{ts1}")
        self.assertEqual(404, err.status_code)

    def test_get_by_timestamp_after_doc(self):
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        time.sleep(0.2)
        ts1 = str(time.time())
        doc = self.app.get(f"/documents/firstdoc/{ts1}")
        self.assertEqual('The first document', doc.json["content"])

    def test_get_by_timestamp_between_2_revisions(self):
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document"}),
            content_type='application/json'
        )
        time.sleep(0.1)
        ts1 = str(time.time())
        time.sleep(0.1)
        self.app.post(
            "/documents/firstdoc",
            data=json.dumps({"content": "The first document updated"}),
            content_type='application/json'
        )
        doc = self.app.get(f"/documents/firstdoc/{ts1}")
        self.assertEqual('The first document', doc.json["content"])

    def test_post_document(self):
        # tested by test_get_by_timestamp
        pass


if __name__ == "__main__":
    unittest.main()
