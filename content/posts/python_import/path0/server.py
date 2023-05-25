# # 常规引用
# from path1.func import echo as path1_echo
# from path2.func import echo as path2_echo
# from path2.path2_1.func import echo as path2_1_echo
# from path2.path2_1.path2_1_1 import echo as path_2_1_1_echo
# path1_echo()
# path2_echo()
# path2_1_echo()
# path_2_1_1_echo()

# # 临时引用
# import sys
# from os.path import abspath, join, dirname
# sys.path.append(join(abspath(dirname(__file__)), "path2/path2_1/path2_1_1"))
# from func import echo as path2_1_1_echo
# path2_1_1_echo()

# # 有 text.__init__.py 也报错
# from path2.path2_1.path2_1_1.special import echo_special
# echo_special()

# # 添加临时引用目录
import sys
from os.path import abspath, join, dirname

sys.path.append(join(abspath(dirname(__file__)), "path2/path2_1/path2_1_1/text"))
from path2.path2_1.path2_1_1.special import echo_special

print(sys.path)
echo_special()
