class RowBuilder:
    def __init__(self, schema):
        self.schema = schema

    def row(self, **data):
        return {col: data.get(col, "") for col in self.schema}

    def empty(self):
        return {col: "" for col in self.schema}

    def summary(self, **data):
        return {col: data.get(col, "") for col in self.schema}