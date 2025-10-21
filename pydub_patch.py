import pydub.utils
pydub.utils.audioop = None  # Disable gracefully for Python 3.13
print("Pydub patched!")
