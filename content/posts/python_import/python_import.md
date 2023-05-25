---
title: "python import"
date: 2023-02-21T18:31:38+08:00
draft: true
tags: ["Python"]
categories: ["Python"]
---

## 目录结构
    C:\USERS\EVILMASS\DESKTOP\PATH0
    │   server.py
    ├───path1
    │   │   func.py
    │   │   __init__.py
    └───path2
        │   func.py
        │   __init__.py
        ├───path2_1
        │   │   func.py
        │   │   __init__.py
        │   ├───path2_1_1
        │   │   │   func.py
        │   │   │   special.py
        │   │   │   __init__.py

## \_\_init__.py
一个 `module1.py` 文件可以看作一个模块：`import module1`

`__init__.py` 则是将一个文件夹变为 `package`

每一次 `import` 都会执行 `__init__.py` 内的代码。
```python
# no __init__.py
from path2.path2_1.func import echo
from path2.path2_1.special import echo_special

# has __init__.py
from .func import *
from .special import *
from path2.path2_1 import echo, echo_special
```

## sys.path
实际遇到的绝大部分问题都是**引用路径**和**循环引用**问题，添加临时引用可以解决但请使用

**绝对路径！**

**绝对路径！**

**绝对路径！**

### 临时引用
针对不频繁调用的模块可以在入口处添加临时引用
```python
import sys
from os.path import abspath, join, dirname
# 添加临时引用目录
sys.path.append(join(abspath(dirname(__file__)), "path2/path2_1/path2_1_1"))
from special import echo_special

echo_special()
>>> echo_special from: C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1
```

### 路径引用问题
`path0\path2\path2_1\path2_1_1\special.py` 调用同级 `text` 文件夹下的 `echo` 模块
```python
# path0\path2\path2_1\path2_1_1\__init__.py
from .func *

# path0\path2\path2_1\path2_1_1\special.py\text\__init__.py
from .func *

# path0\path2\path2_1\path2_1_1\special.py
import func
from func import echo as local_echo

import text
from text.func import echo as text_echo

def echo_special():
    func.echo()
    local_echo()

    text.echo()
    text_echo()

if __name__ == "__main__":
    echo_special()

# path0\server.py 导入 echo_special 会报错，即便有 text.__init__.py
from path2.path2_1.path2_1_1.special import echo_special
echo_special()

Traceback (most recent call last):
  File "server.py", line 27, in <module>
    from path2.path2_1.path2_1_1.special import echo_special
  File "C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1\__init__.py", line 2, in <module>
    from .special import *
  File "C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1\special.py", line 5, in <module>
    from text.func import echo as text_echo
ModuleNotFoundError: No module named 'text'
```
但直接在 `path2_1_1` 目录下执行 `python special.py` 是正常运行的。
```python
cd C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1
python special.py
>>> echo from: C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1
>>> echo from: C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1
>>> echo from: C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1\text
>>> echo from: C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1\text
```

### 错误示范
```python
# 多了一个 `.` 能让 `server.py` 跑起来
from .text.func import echo as text_echo

# 但在 path2_1_1 目录下运行则会报错
cd C:\Users\Evilmass\Desktop\path0\path2\path2_1\path2_1_1
python special.py
>>> Traceback (most recent call last):
>>>   File "special.py", line 5, in <module>
>>>     from .text.func import echo as text_echo
>>> ImportError: attempted relative import with no known parent package
```

## sys.path
**绝大部分问题只要检查一下 `sys.path` 就能解决**
```python
import sys
print(sys.path)
>>>['C:\\Users\\Evilmass\\AppData\\Local\\Programs\\Python\\Python37\\DLLs',
    'C:\\Users\\Evilmass\\AppData\\Local\\Programs\\Python\\Python37\\lib',
    'C:\\Users\\Evilmass\\AppData\\Local\\Programs\\Python\\Python37',
    'C:\\Users\\Evilmass\\AppData\\Local\\Programs\\Python\\Python37\\lib\\site-packages']
```

很明显没有 `text` 目录，那么 `server.py` 加临时引用试试。
```python
import sys
from os.path import abspath, join, dirname
# 添加临时引用目录
sys.path.append(join(abspath(dirname(__file__)), "path2/path2_1/path2_1_1/text"))
from path2.path2_1.path2_1_1.special import echo_special

echo_special()
>>>
```
问题解决。

## if __name__ == "__main__"
- 如果作为脚本直接运行，会执行 `__name__ == "__main__"` 下面的内容
- 如果是被其他 `py` 文件作为 `package` 引用则不执行

99% 的文章都会这么告诉你，少部分提一下 `___name__` 作用域，我的建议是：
**Talk Is Cheap, Show Me Code**
```python
# echo.py
def echo():
    print(__name__)

if __name__ == "__main__":
    echo()
    print("after echo, run this")

>>> "__main__"
>>> "after echo, run this"

# another.py
from echo import echo

print(echo.__name__)
>>> "echo"
```