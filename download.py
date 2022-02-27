
import threading
import queue
import os
import requests
import tqdm
import shutil
from .file import GuessFileExtension

class SingleDownloadPack:
  def __init__(self) -> None:
    self.url = None
    self.local_path = None
    self.display_name = None

def GetLocalSameNameFilesAtPath(seed_path):
  result = []
  folder, full_name = os.path.split(seed_path)
  name, ext = os.path.splitext(full_name)
  for folder_file in os.listdir(folder):
    if folder_file.startswith(name):
      result.append(os.path.join(folder, folder_file))
  return result

def DownloadSinglePack(sess, pack, thread_idx=0, verbose_level=10, auto_file_ext=False):
  chunk_size = 16384
  response_stream = sess.get(pack.url, stream=True)
  total_size = int(response_stream.headers['Content-length'])
  # file_name = os.path.splitext(os.path.split(pack.local_path)[1])[0]
  desc_notify = pack.display_name

  # file duplicate check
  download_needed = True
  local_result_path = pack.local_path
  local_same_name_files = GetLocalSameNameFilesAtPath(local_result_path)
  for file in local_same_name_files:
    local_size = os.path.getsize(file)
    if local_size == total_size:
      # regard download complete
      download_needed = False
      local_result_path = file
      print("{} download complete, will not do download".format(local_result_path))
      break

  if download_needed:
    if len(desc_notify) > 30:
      desc_notify = desc_notify[:30] 
    with open(pack.local_path, "wb") as f:
      if verbose_level == 0:
        for b in response_stream.iter_content(chunk_size=chunk_size):
          f.write(b)
      else:
        progress_bar = tqdm.tqdm(total=total_size, desc=desc_notify, unit='iB', unit_scale=True, position=thread_idx)
        for b in response_stream.iter_content(chunk_size=chunk_size):
          progress_bar.update(len(b))
          f.write(b)
        progress_bar.close()
  response_stream.close()

  if auto_file_ext:
    folder, full_name = os.path.split(local_result_path)
    name, ext = os.path.splitext(full_name)
    if ext == "":
      guess_ext = GuessFileExtension(local_result_path)
      if guess_ext != "":
        print("auto ext: {} -> {}".format(local_result_path, os.path.join(folder, name+guess_ext)))
        shutil.move(local_result_path, os.path.join(folder, name+guess_ext))

def ThreadLoopFn(pack_queue: queue.Queue, sess=None, thread_idx=0, get_pack_fn=None):
  if sess is None:
    sess = requests.Session()
  while True:
    item = pack_queue.get(block=True)
    if item is None:
      break
    if get_pack_fn is not None:
      item = get_pack_fn(item)
      if item is None:
        print("item is none after get pack fn, discarded")
        continue
    assert(isinstance(item, SingleDownloadPack))
    DownloadSinglePack(sess, item, thread_idx)

class Downloader:
  def __init__(self):
    self.download_item_queue = queue.Queue(4)
    self.thread_count = 1
    self._threads = []
    self.sess = None
    self.get_pack_fn = None

  def StartThreads(self):
    assert self.thread_count >= 1
    for i in range(self.thread_count):
      thread = threading.Thread(target=ThreadLoopFn, args=[self.download_item_queue], kwargs={
        "sess": self.sess,
        "thread_idx": i,
        "get_pack_fn": self.get_pack_fn
      })
      thread.start()
      self._threads.append(thread)
    
  def JoinThreads(self):
    for _ in range(self.thread_count):
      self.download_item_queue.put(None)

    for i in range(self.thread_count):
      self._threads[i].join()

  def FeedItems(self, iter_items):
    for item in iter_items:
      self.download_item_queue.put(item)