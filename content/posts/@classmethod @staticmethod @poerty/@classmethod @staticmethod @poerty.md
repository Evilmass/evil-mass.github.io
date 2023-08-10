---
title: 未命名
date: 2023-08-10T09:16:57+08:00
draft: false
tags: ["python"]
categories: ["python"]
---

## @classmethod
如果只是简单“调用类方法不用实例化”概括，那么这种描述（无论长短）和“为什么要在 Python3 头部添加 `#coding: utf-8`” 一样，没有意义。  

补充：Python3 默认文件编码为 `UTF-8` 但是读写文件的时候默认是按文件原来编码来的，所以读写文件的时候补上 `encoding` 参数比较规范，而二进制文件则不需要。
```python
with open(file, mode="r", encoding="utf-8") as f:
    content = f.read()
```

**一句话描述 @classmethod：创建新实例时需要 数据校验/格式化。**

推荐第一种写法，灵活度更高。
```python
class Shopping:
    """出门前检查要带的金额：20 <= money <= 100"""
    
    def __init__(self, money) -> None:
        self.money = money

    @classmethod
    def check(cls, money):
        if 20 <= money <= 100:
            return cls(money)
        else:
            raise "money not validate"

    # 创建实例化就校验
    def __new__(cls, money):
        if 20 <= money <= 100:
            obj = object.__new__(cls)
            obj.money = money
            return obj
        else:
            raise "money not validate"

shopping = Shopping.check(50)
shopping = Shopping(-1)
```

## @staticmethod 
实际工作的时候我更偏向于将公共函数放在 `utils.py`，比如 create_folder()、decrypt_base64()、download_file() 等。

**一句话概括 @staticmethod：只服务于当前类（其他外部类/函数用不到或关联性较小），放在类里面比较简洁。**
```python
class Shopping:
    # 汇率转换
    @staticmethod
    def rmb_to_usd(rate: float, rmb: int):
        usd = rmb / rage
        return usd
```

## @poerty
实际工作用的不多，直接抄 [Python中@property和@setter的用法](https://www.cnblogs.com/yeer-xuan/p/13488291.html)的。

**一句话概括：将类方法转为属性更合理的读取值、预处理数据、禁止修改对象值。**

### 将类方法转为属性更合理的读取值
```python
class User():
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def tag(self):
        return self.name + str(self.age)
        
    @poerty
    def tag2(self):
        return self.name + str(self.age)

user = User('xiao',5)
print(user.tag())
# tag 更像是属性对象，所以使用类属性 user.tag 的方式获取会比 user.tag() 更加的合理。
print(user.tag2)   
```

### 预处理数据
```python
class User():
    def __init__(self, name, age):
        self.name = name
        self._age = age  # 私有变量

    @property
    def age(self):
        return self._age
        
    @age.setter
    def age(self,n):
        self._age = n + 5

user = User('xiao',0)
# 当执行 user.age = 5 时，@age.setter装饰器下的age函数会将数据+5 后再存入类属性_age中，实现了存入前对数据的预处理。
user.age = 5
print(user.age)  # 结果：10
```

### 禁止修改对象
```python
class User():
    def __init__(self, name, age):
        self.name = name
        self._age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self,n):
        print('数据不能被修改')

user = User('xiao',0)
# 在为 age 赋值时会立即触发 @age.setter 装饰器下的 age 函数中的提示语句或者异常处理语句。
user.age = 5
```


## Refference:
[python装饰器@classmethod的深入理解以及它的使用场合
](https://blog.csdn.net/qq_34546589/article/details/102760817)
[# @classmethod和@staticmethod](https://cs.pynote.net/sf/python/202203151/)

[Python中@property和@setter的用法](https://www.cnblogs.com/yeer-xuan/p/13488291.html)