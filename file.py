
from . import mime_type

def RefineLocalName(name):
  replace_dict = {
    ord('\\'): '[backslash]',
    ord('/'): '[slash]',
    ord(':'): '[colon]',
    ord('*'): '[asterisk]',
    ord('?'): '[question]',
    ord('"'): '[doublequote]',
    ord('<'): '[greaterthan]',
    ord('>'): '[lessthan]',
    ord('|'): '[verticalline]',
  }
  return name.translate(replace_dict)

def GuessFileExtension(file_path):
  try:
    import magic
    file_magic = magic.Magic(magic_file=r'E:\.pyenv\pyenv-win\bin\magic.mgc', mime=True)
    with open(file_path, "rb") as f:
      content = f.read()
    mime = file_magic.from_buffer(content)
    mime_dict = mime_type.GetMimeTypeDict()
    get_ext_result = mime_dict.get(mime, "")
    if get_ext_result:
      return ".{}".format(get_ext_result)
    else:
      return ""
  except Exception as e:
    return ""