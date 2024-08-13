class WrongInput(Exception):
    def __init__(self, input, current_year):
        super().__init__(
            f"Wrong input. Input should be digits and in  range of 2004 to {current_year}: {input}"
        )


class NotFoundTotalCountOfRecords(Exception):
    def __init__(
        self,
    ):
        super().__init__("Total count of records is not found!")


class TypeDoesNotExist(Exception):
    def __init__(self, type_string, all_types):
        super().__init__(
            f"{type_string} this type does not exist, Available types: {all_types}"
        )


class VariableValueIsMissing(Exception):
    def __init__(self, token_name):
        super().__init__(f"{token_name} value is missing!")
