import time, random, json

def SaveByteContentAsTxt(byte_content, target_path):
  with open(target_path, "wb") as f:
    f.write(byte_content)

def LoadTxtAsByteContent(target_path):
  with open(target_path, "rb") as f:
    bts = f.read()
  return bts

def LoadTxtAsJsonContent(target_path, encoding="utf-8"):
  with open(target_path, "r", encoding=encoding) as f:
    j = json.load(f)
  return j

def RandomSleep(min_seconds = 0, max_seconds = 1):
  sleep_time = random.random() * (max_seconds - min_seconds) + min_seconds
  time.sleep(sleep_time)

def ParsePastedKVPair(headers_str):
  lines = headers_str.split("\n")
  result = {}
  for line in lines:
    line = line.strip()
    if line == "":
      continue
    first_colon_idx = line.index(":")
    name = line[:first_colon_idx].strip()
    content = line[first_colon_idx+1:].strip()
    result[name] = content
  return result