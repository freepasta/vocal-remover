#!/usr/bin/env python3
import urllib.request
import os

url = "https://github.com/deezer/spleeter/raw/master/audio/example.mp3"
output_path = "docs/test_input/sample.mp3"

os.makedirs(os.path.dirname(output_path), exist_ok=True)

print(f"Downloading sample from {url}")
response = urllib.request.urlopen(url)
data = response.read()

with open(output_path, "wb") as f:
    f.write(data)

print(f"Downloaded {len(data)} bytes to {output_path}")
