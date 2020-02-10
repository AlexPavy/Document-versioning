import flask
import time
app = flask.Flask(__name__)


_DEFAULT_DOCUMENTS = {
    "maize": "Maize also known as corn, is a cereal grain first domesticated by indigenous peoples "
             "in southern Mexico about 10,000 years ago. The leafy stalk of the plant produces "
             "pollen inflorescences and separate ovuliferous inflorescences called ears that yield "
             "kernels or seeds, which are fruits.",
    "rice": "Rice is the seed of the grass species Oryza sativa (Asian rice) or Oryza glaberrima "
            "(African rice). As a cereal grain, it is the most widely consumed staple food for a large "
            "part of the world's human population, especially in Asia. It is the agricultural commodity "
            "with the third-highest worldwide production (rice, 741.5 million tonnes in 2014), after "
            "sugarcane (1.9 billion tonnes) and maize (1.0 billion tonnes)"
}


class DocumentsDb:
    """Database of documents

    Only in memory for this test
    """
    def __init__(self):
        self._docs = {}

    def add(self, title: str, content: str) -> int:
        ts = int(time.time())
        if title in self._docs:
            self._docs[title][str(ts)] = content
            self._docs[title]["latest_ts"] = ts
        else:
            self._docs[title] = {}
            self._docs[title][str(ts)] = content
            self._docs[title]["latest_ts"] = ts
        return ts

    def get_all_titles(self):
        return list(self._docs.keys())

    def get_revisions(self, title: str):
        return {
            "title": title,
            "revisions": self._docs[title]
        }

    def get_document(self, title: str, ts: str):
        if title not in self._docs:
            return None

        if ts == "latest" or not ts:
            ts = self._docs[title]["latest_ts"]

        if ts not in self._docs[title]:
            return None

        return {
            "title": title,
            "timestamp": ts,
            "content": self._docs[title][ts]
        }


db = DocumentsDb()


@app.route("/")
def app_name():
    return flask.jsonify({"app": "wiki"})


@app.route("/documents", defaults={"title": None, "timestamp": None}, methods=["GET"])
@app.route("/documents/<title>", defaults={"timestamp": None}, methods=["GET", "POST"])
@app.route("/documents/<title>/<timestamp>", methods=["GET"])
def documents(title, timestamp):
    result = None
    if flask.request.method == "GET":
        if title is None:
            result = db.get_all_titles()
        elif timestamp is None:
            result = db.get_revisions(title)
        else:
            result = db.get_document(title, timestamp)
    elif flask.request.method == "POST":
        if not flask.request.json:
            return {"reason": "No JSON content"}, 400

        content = flask.request.json["content"]
        ts = db.add(title, content)
        result = {
            "title": title,
            "content": content,
            "timestamp": ts,
        }
    if result is None:
        return {"reason": "No results"}, 404
    else:
        return flask.jsonify(result), 200


if __name__ == "__main__":
    for key, val in _DEFAULT_DOCUMENTS.items():
        db.add(key, val)
    app.run()
