import time

def CatchExceptionTillSuccessDecorator(f):
  def decorated(*args, **kwargs):
    try_count = 0
    try_count_max = 20
    while try_count < try_count_max:
      try:
        return f(*args, **kwargs)
      except Exception as e:
        print("exception has raised in {}".format(f.__name__))
        print("type:", type(e))
        print(e)
        try_count += 1
        time.sleep((try_count / try_count_max) * 30)
        continue
    raise ValueError("{} exceed retry limit".format(f.__name__))
  return decorated