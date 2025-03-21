
class ParseError(Exception):
    def __init__(self, message, token):
        super().__init__(f"Error at token {token}: {message}")
        self.token = token
