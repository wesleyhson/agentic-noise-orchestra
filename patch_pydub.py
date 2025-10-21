import pydub.utils
pydub.utils.audioop = None  # Disable gracefully
print("Pydub patched for Python 3.13")
