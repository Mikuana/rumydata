from rumydata.rule import ColumnsRule


class GreaterThanColumn(ColumnsRule):
    def evaluator(self):
        return lambda x, y: x > y

    def explain(self) -> str:
        return f"must be greater than column '{self.compare_to}'"
