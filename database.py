import pysondb as db


class Database:
    def __init__(self, file_path):
        self.data = db.getDb(file_path)

    def add_question(self, text: str, correct_answer: str, desk: str):
        self.data.add(
            {
                "text": text,
                "correct_answer": correct_answer,
                "desk": desk
            }
        )

    def get_question(self, id: int):
        try:
            return self.data.get(id + 1)[id]
        except IndexError:
            return None

