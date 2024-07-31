import datetime


class VerboseLogger:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str):
        if self.verbose:
            print(message)

    def begin(self, total_length: int = 40):
        if self.verbose:
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fixed_message = "Started"
            formatted_message = f"{fixed_message} {now}"

            # Use the .center method to add '*' characters around the formatted_message
            # total_length specifies the width of the final output string
            output = formatted_message.center(total_length, '*')
            print(f"{output}\n")

    def end(self, total_length: int = 40):
        if self.verbose:
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            fixed_message = "Finished"
            formatted_message = f"{fixed_message} {now}"

            # Use the .center method to add '*' characters around the formatted_message
            # total_length specifies the width of the final output string
            output = formatted_message.center(total_length, '*')
            print(f"{output}\n")
