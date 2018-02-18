class InvalidCriteriaException(ValueError):
    pass


class WhereCriteria:
    def __init__(self, field_name):
        self.field_name = field_name
        self.expected_value = None

    @classmethod
    def where(cls, field_name):
        return cls(field_name)

    def eq(self, expected_value):
        self.expected_value = expected_value
        return self

    def _validate(self):
        if not isinstance(self.expected_value, str) or not isinstance(self.field_name, str):
            raise InvalidCriteriaException('Field name and expected value should be string')
        return self

    def __and__(self, other):
        return AndCriteria(self, other)


class AndCriteria:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def _validate(self):
        self.left._validate()
        self.right._validate()
        return self


where = WhereCriteria.where
available_criteria = {WhereCriteria, AndCriteria}