# CopyImageToClipboard


Win10 下复制图片发送到 QQ 群总是变成文件，每次要`打开图片-复制-关闭图片`也很繁琐。

市面上现有的工具不多：

- [xclip](https://github.com/astrand/xclip)，仅限 Linux 平台使用。
- [CopyContents](https://www.softpedia.com/get/Office-tools/Clipboard/Copy-Contents.shtml)，免费试用 15 天，每次右键复制图片内容都提示一次，还有个巨复古的浮框。


## Talk Is Cheap
保存为 `pyw` 文件用 `pythonw.exe` 执行避免出现一闪而过的黑框。

```python
# coding:utf-8

import sys
import traceback
import win32clipboard

from io import BytesIO
from PIL import Image


def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()


def copy_image_to_clipboard(args):
    image = Image.open(args)
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    send_to_clipboard(win32clipboard.CF_DIB, data)


if __name__ == "__main__":
    try:
        copy_image_to_clipboard(sys.argv[1])
    except Exception:
        traceback.print_exc()
```


## 注册表
简单功能不用特意找 `winreg` 标准库写一大堆东西，参考 [如何使用 .reg 文件添加、修改或删除注册表子项和值](https://support.microsoft.com/zh-cn/topic/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8-reg-%E6%96%87%E4%BB%B6%E6%B7%BB%E5%8A%A0-%E4%BF%AE%E6%94%B9%E6%88%96%E5%88%A0%E9%99%A4%E6%B3%A8%E5%86%8C%E8%A1%A8%E5%AD%90%E9%A1%B9%E5%92%8C%E5%80%BC-9c7f37cf-a5e9-e1cd-c4fa-2a26218a1a23)

### 添加
只关联了 `JPG` 和 `PNG` 格式
```python
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\SystemFileAssociations\.png\Shell\CopyImage]
@="CopyImage"
[HKEY_CLASSES_ROOT\SystemFileAssociations\.png\Shell\CopyImage\command]
@="<Your Python Path>\\pythonw.exe <Your Scipt Path>.pyw %1"

[HKEY_CLASSES_ROOT\SystemFileAssociations\.jpg\Shell\CopyImage]
@="CopyImage"
[HKEY_CLASSES_ROOT\SystemFileAssociations\.jpg\Shell\CopyImage\command]
@="<Your Python Path>\\pythonw.exe <Your Scipt Path>.pyw %1"
```

### 删除
在主菜单前加 `-` 即可
```python
[-HKEY_CLASSES_ROOT\SystemFileAssociations\.png\Shell\CopyImage]
[-HKEY_CLASSES_ROOT\SystemFileAssociations\.jpg\Shell\CopyImage]
```

## 效果
![](https://s2.loli.net/2023/02/08/lhdyCcXMGRUqnVe.png)

![](https://s2.loli.net/2023/02/08/5n1WbJIokVKlHiE.png)

## References：
[pyperclip/issues/198](https://github.com/asweigart/pyperclip/issues/198#issuecomment-1050828479)

[Windows下.py文件右键没有Edit with IDLE的解决办法](https://www.polarxiong.com/archives/windows-python-edit-with-idle.html)

[运行python程序不显示cmd的方法](https://codeantenna.com/a/nOuvp1qnE9)

