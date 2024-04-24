class WrongInput(Exception):
    def __init__(self, input, current_year):
        super().__init__(
            f"Wrong input. Input should be digits and in  range of 2004 to {current_year}: {input}"
        )


class DataFetchError(Exception):
    def __init__(self, status_code, url):
        super().__init__(f"Data fetch failure, status_code={status_code}, url={url}")
