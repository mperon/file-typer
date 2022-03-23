"""_summary_
"""
import sys


# Print iterations progress
def progress(iteration, total, prefix='', suffix='', bar_length=100):
    """_summary_

    Args:
        iteration (_type_): _description_
        total (_type_): _description_
        prefix (str, optional): _description_. Defaults to ''.
        suffix (str, optional): _description_. Defaults to ''.
        decimals (int, optional): _description_. Defaults to 1.
        bar_length (int, optional): _description_. Defaults to 100.
    """
    decimals = 1
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    p_bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write(f"\r{prefix} {percents}% |{p_bar}| [{iteration}/{total}] {suffix}")

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()
