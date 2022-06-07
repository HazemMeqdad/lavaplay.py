import random


def generate_resume_key():
    return "".join(random.choice("0123456789abcdef") for _ in range(16))

