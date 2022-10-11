class EmployeeFloatError(Exception):
    """
    Custom exception for when the number for salary has to bee float.
    """

    def __init__(self, val):
        self.message = f"{val} needs to be a number (float)."
        super().__init__(self.message)


class EmployeeStrError(Exception):
    """
    Custom exception for when the employee string isn't a string.
    """

    def __init__(self, val):
        self.message = f"{val} needs to be a string."
        super().__init__(self.message)
