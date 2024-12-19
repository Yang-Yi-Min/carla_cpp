#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# 导入全局模块，用于文件路径的匹配，通过通配符等方式查找符合特定模式的文件路径列表
import glob
# 导入操作系统接口模块，用于获取操作系统类型（如 'nt' 表示 Windows，'posix' 表示 Linux 等）、操作文件和目录等与操作系统相关的功能
import os
# 导入系统特定的参数和功能模块，可用于获取 Python 解释器相关的信息，如版本号等
import sys

try:
    # 根据Python版本和操作系统类型构造CARLA库的文件名模式
    carla_lib_name = 'carla-*%d.%d-%s.egg' % (
        sys.version_info.major,  # Python主版本号，例如 3 表示 Python 3.x 版本
        sys.version_info.minor,  # Python次版本号，例如 8 表示 Python 3.8 版本
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'  # 根据操作系统选择平台标识，若操作系统是 Windows（os.name == 'nt'）则选择 'win-amd64'，否则选择 'linux-x86_64'，用于适配不同平台的库文件
    )
    # 将匹配到的CARLA库文件所在的目录添加到系统路径中，以便能够导入CARLA模块。
    # glob.glob 函数会查找符合给定模式的文件路径列表，这里取第一个匹配的路径添加到系统路径，使得后续可以通过 import 语句正确导入CARLA相关模块
    sys.path.append(glob.glob('../carla/dist/%s' % carla_lib_name)[0])
except IndexError:
    # 如果没有找到匹配的CARLA库文件，则打印错误信息
    print('\n  [ERROR] Could not find "%s"' % carla_lib_name)
    print('          Blueprint library docs will not be generated')
    print(" .---------------------------------------------------.")
    print("  |     Make sure the python client is compiled!      |")
    print("  '---------------------------------------------------'\n")
    # 为了避免Travis检查失败（可能是在持续集成环境中的特定要求），这里不抛出错误，而是正常退出程序
    sys.exit(0)

# 导入CARLA模块，由于前面已经将CARLA库文件目录添加到系统路径中，这里可以成功导入，CARLA模块用于与CARLA模拟器进行交互等操作
import carla

# 定义一个颜色常量，用于文本格式化，这里可能是用于在生成的文档中设置特定颜色的文本样式（比如 HTML 中的字体颜色），采用十六进制颜色码表示
COLOR_LIST = '#498efc'

# 定义一个函数，用于将元素列表用指定的分隔符连接成一个字符串，默认分隔符为空字符串，例如输入 ['a', 'b', 'c']，返回 'abc'；若指定分隔符为 ','，则返回 'a,b,c'
def join(elem, separator=''):
    return separator.join(elem)

# 定义一个函数，用于给文本添加颜色，通过将文本包裹在 HTML 的 <font> 标签中，并设置 color 属性为指定的颜色值来实现文本颜色的改变，返回添加颜色后的文本（以HTML格式表示）
def color(col, buf):
    return join(['<font color="', col, '">', buf, '</font>'])

# 定义一个函数，用于检查字典中是否包含指定的键和值，返回布尔值，表示是否满足条件
def valid_dic_val(dic, value):
    return value in dic and dic[value]

# 定义一个函数，用于将文本转换为斜体，通过在文本前后添加 HTML 中的 <i>（或 Markdown 中的 _）标签来实现斜体样式，返回斜体格式的文本（以HTML或类似格式表示）
def italic(buf):
    return join(['_', buf, '_'])

# 定义一个函数，用于将文本转换为粗体，通过在文本前后添加 HTML 中的 <b>（或 Markdown 中的 **）标签来实现粗体样式，返回粗体格式的文本（以HTML或类似格式表示）
def bold(buf):
    return join(['**', buf, '**'])

# 定义一个函数，用于将文本用括号括起来，返回添加括号后的文本
def parentheses(buf):
    return join(['(', buf, ')'])

# 定义一个函数，用于将文本转换为下标，通过将文本包裹在 HTML 的 <sub> 标签中来实现下标样式，返回下标格式的文本（以HTML格式表示）
def sub(buf):
    return join(['<sub>', buf, '</sub>'])

# 定义一个函数，用于将文本转换为代码格式，通过在文本前后添加 HTML 中的 <code>（或 Markdown 中的 `）标签来实现代码样式，返回代码格式的文本（以HTML或类似格式表示）
def code(buf):
    return join(['`', buf, '`'])

# 定义一个MarkdownFile类，用于处理Markdown文档的生成，内部通过维护一个字符串来逐步构建文档内容，并管理列表相关的格式（如列表深度等）
class MarkdownFile:
    def __init__(self):
        self._data = ""  # 用于存储Markdown文档内容的字符串，初始为空
        self._list_depth = 0  # 用于记录当前列表的深度，初始为 0，表示没有处于列表层级中
        self.endl = '  \n'  # 定义一个换行符，用于在Markdown文档中添加换行，采用两个空格加换行的格式，符合Markdown语法要求

    # 一个方法，返回Markdown文件的内容，即当前存储在 _data 属性中的文档内容字符串
    def data(self):
        return self._data

    def list_push(self, buf=''):
        """
        用于向文档中添加列表项。

        如果传入的字符串buf不为空，则根据当前列表深度添加相应的缩进（如果深度不为 0），并添加列表项标记（'-'）和传入的文本内容。
        然后增加列表深度，表示进入下一层列表层级。
        """
        if buf:
            self.text(join([
                '    ' * self._list_depth if self._list_depth!= 0 else '', '- ', buf]))
        self._list_depth = (self._list_depth + 1)

    def list_pushn(self, buf):
        """
        类似于 list_push 方法，但会在传入的文本内容后自动添加换行符（通过调用 list_push 并传入添加换行后的文本内容实现），
        方便一次性添加带有换行的列表项内容。
        """
        self.list_push(join([buf, self.endl]))

    def list_pop(self):
        """
        用于减少列表深度，模拟从当前列表层级退出一层的操作，但保证列表深度不小于 0，避免出现不合理的列表格式。
        """
        self._list_depth = max(self._list_depth - 1, 0)

    def list_popn(self):
        """
        先执行 list_pop 操作减少列表深度，然后在文档内容字符串中添加换行符，用于在文档中体现列表层级的结束并换行。
        """
        self.list_pop()
        self._data = join([self._data, '\n'])

    def list_depth(self):
        """
        根据当前列表深度返回相应的缩进字符串，如果文档内容字符串的最后一个字符不是换行符或者列表深度为 0，则返回空字符串，
        否则返回根据列表深度生成的缩进字符串（由多个空格组成，用于在文档中体现列表的层级缩进格式）。
        """
        if self._data.strip()[-1:]!= '\n' or self._list_depth == 0:
            return ''
        return join(['    ' * self._list_depth])

    def text(self, buf):
        """
        将传入的文本内容添加到文档内容字符串中，用于向文档中添加普通文本内容（非列表、标题等特定格式的文本）。
        """
        self._data = join([self._data, buf])

    def textn(self, buf):
        """
        将传入的文本内容添加到文档内容字符串中，并根据当前列表深度添加相应的缩进，然后添加换行符，方便添加带有换行且遵循列表缩进格式的文本内容。
        """
        self._data = join([self._data, self.list_depth(), buf, self.endl])

    def not_title(self, buf):
        """
        在文档内容字符串中添加非标题文本，先添加换行符，再根据当前列表深度添加相应的缩进，然后添加以 '#' 开头的文本内容（表示普通段落文本，非标题格式），最后再添加换行符。
        """
        self._data = join([
            self._data, '\n', self.list_depth(), '#', buf, '\n'])

    def title(self, strongness, buf):
        """
        在文档内容字符串中添加标题文本，标题的级别由 strongness 参数决定（'#' 的数量表示标题级别，例如 3 个 '#' 表示三级标题）。
        先添加换行符，再根据当前列表深度添加相应的缩进，然后添加对应数量的 '#' 符号、空格以及标题文本内容，最后再添加换行符。
        """
        self._data = join([
            self._data, '\n', self.list_depth(), '#' * strongness, ' ', buf, '\n'])

    def new_line(self):
        """
        在文档内容字符串中添加新行，通过添加预定义的换行符（self.endl）来实现。
        """
        self._data = join([self._data, self.endl])

    def code_block(self, buf, language=''):
        """
        在文档中添加代码块。

        返回一个包含代码块格式的字符串，由三个反引号（```）开头，后面可选地跟上编程语言名称（用于语法高亮等，若不指定则为空），
        接着换行添加根据当前列表深度生成的缩进、代码内容、同样缩进的换行以及三个反引号结尾并换行，形成符合Markdown语法的代码块格式。
        """
        return join(['```', language, '\n', self.list_depth(), buf, '\n', self.list_depth(), '```\n'])


def generate_pb_docs():
    """生成API蓝图文档"""

    print('Generating API blueprint documentation...')
    client = carla.Client('127.0.0.1', 2000)  # 创建CARLA客户端连接，指定连接的主机地址为本地（127.0.0.1）和端口号为 2000，用于与CARLA模拟器进行通信
    client.set_timeout(2.0)  # 设置客户端超时时间为 2 秒，即如果在 2 秒内没有收到服务器响应，则认为操作超时
    world = client.get_world()  # 获取CARLA世界对象，代表模拟器中的整个虚拟世界场景，通过该对象可以进一步获取世界中的各种实体、资源等信息

    bp_dict = {}  # 初始化一个字典，用于存储蓝图信息，字典的键将是蓝图类型，值是对应的蓝图相关信息列表
    blueprints = [bp for bp in world.get_blueprint_library().filter('*')]  # Returns list of all blueprints
    # 获取世界中所有的蓝图对象列表，通过调用世界对象的 get_blueprint_library 方法获取蓝图库，再使用 filter 方法筛选出所有符合 '*'（表示全部）条件的蓝图
    blueprint_ids = [bp.id for bp in world.get_blueprint_library().filter('*')]  # Returns list of all blueprint ids
    # 获取所有蓝图的唯一标识符（ID）列表，通过遍历前面获取的所有蓝图对象，提取它们的 id 属性来得到

    # 根据蓝图类型分类蓝图，Creates a dict key = walker, static, prop, vehicle, sensor, controller; value = [bp_id, blueprint]
    for bp_id in sorted(blueprint_ids):
        bp_type = bp_id.split('.')[0]
        value = []
        for bp in blueprints:
            if bp.id == bp_id:
                value = [bp_id, bp]
        if bp_type in bp_dict:
            bp_dict[bp_type].append(value)
        else:
            bp_dict[bp_type] = [value]

    # 生成Markdown文档
    md = MarkdownFile()
    md.not_title('Blueprint Library')  # 添加非标题文本，作为文档中关于蓝图库的说明部分开头
    md.textn(
        "The Blueprint Library ([`carla.BlueprintLibrary`](../python_api/#carlablueprintlibrary-class)) " +
        "is a summary of all [`carla.ActorBlueprint`](../python_api/#carla.ActorBlueprint) " +
        "and its attributes ([`carla.ActorAttribute`](../python_api/#carla.ActorAttribute)) " +
        "available to the user in CARLA.")
    # 添加一段关于蓝图库的详细描述文本，包含对相关类的链接引用（可能用于指向文档中其他部分或者外部文档中的对应类说明），介绍蓝图库是包含各种蓝图及其属性的汇总，可供用户在CARLA中使用

    md.textn("\nHere is an example code for printing all actor blueprints and their attributes:")
    # 添加提示文本，说明接下来要展示用于打印所有演员蓝图及其属性的示例代码
    md.textn(md.code_block("blueprints = [bp for bp in world.get_blueprint_library().filter('*')]\n"
                           "for blueprint in blueprints:\n"
                           "   print(blueprint.id)\n"
                           "   for attr in blueprint:\n"
                           "       print('  - {}'.format(attr))", "py"))
    # 添加示例代码块，代码内容是通过循环遍历获取到的所有蓝图并打印它们的 ID 以及每个蓝图的属性，指定代码块的语言为 Python（用于语法高亮等展示效果）
    md.textn("Check out the [introduction to blueprints](core_actors.md).")
    # 添加提示文本，引导查看关于蓝图的介绍文档（可能是另一个 Markdown 文件 core_actors.md）

    for key, value in bp_dict.items():  # bp types, bp's
        md.title(3, key)  # 添加三级标题，标题文本为当前蓝图类型（如 'walker'、'vehicle' 等），用于对不同类型的蓝图进行分组展示
        for bp in sorted(value):  # Value = bp[0]= name bp[1]= blueprint
            md.list_pushn(bold(color(COLOR_LIST, bp[0])))  # 添加列表项，将蓝图名称设置为加粗且带有指定颜色的样式，突出显示蓝图名称，并添加换行
            md.list_push(bold('Attributes:') + '\n')  # 添加列表项，文本为加粗的 'Attributes:'，并添加换行，用于引出蓝图属性的展示
            for attr in sorted(bp[1], key=lambda x: x.id):  # 遍历蓝图属性，按照属性的 ID 进行排序
                md.list_push(code(attr.id))  # 将属性 ID 以代码格式添加为列表项，突出显示属性的标识符
                md.text(' ' + parentheses(italic(str(attr.type))))  # 在属性 ID 后添加属性类型信息，设置为斜体并加上括号，用于展示属性类型详情
                if attr.is_modifiable:
                    md.text(' ' + sub(italic('- Modifiable')))  # 如果属性是可修改的，则添加一个下标格式的 '- Modifiable' 文本，用于标识该属性可被修改
                md.list_popn()  # 结束当前属性的列表项展示，添加换行
            md.list_pop()  # 结束属性列表的展示，回到上一层列表层级
            md.list_pop()  # 再结束蓝图名称这一层列表的展示，回到更上一层列表层级
        md.list_pop()  # 结束当前蓝图类型下所有蓝图相关内容的展示，回到再上一层列表层级
    return md.data()  # 返回生成好的Markdown文档内容

def main():

    script_path = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在的目录路径，通过获取当前脚本文件的绝对路径，再取其所在的目录部分得到
    try:
        docs = generate_pb_docs()  # 调用 generate_pb_docs 函数生成API蓝图文档内容
    except RuntimeError:
        print("\n  [ERROR] Can't establish connection with the simulator")  # 无法连接到模拟器时的错误信息，可能是CARLA客户端连接失败等原因导致
        print(" .---------------------------------------------------.")
        print("  |       Make sure the simulator is connected!       |")
        print("  '---------------------------------------------------'\n")
        # We don't provide an error to prvent Travis checks failing
        sys.exit(0)  # 为了避免Travis检查失败（可能是在持续集成环境中的特定要求），遇到运行时错误则直接退出程序

    with open(os.path.join(script_path, '../../Docs/bp_library.md'), 'w') as md_file:  # 保存Markdown文档，打开指定路径下的文件（相对于脚本所在目录的上级目录的 Docs 文件夹中的 bp_library.md 文件），以写入模式打开
        md_file.write(docs)  # 将生成的文档内容写入到打开的文件中
    print("Done!")  # 完成提示，表示文档生成并保存成功

if __name__ == '__main__':
    main()  # 执行主函数，启动整个文档生成流程，包括连接CARLA、生成文档内容以及保存文档等操作
