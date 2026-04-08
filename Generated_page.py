from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from typing import Literal
from time import sleep

class Generated_page:

    #[定义属性] 生成安全的上下文实例
    def __init__(self,
                 #[参数] 是否从文件获取登录态
                 LogIn_state_FilePath :None|str = None,
                 #[参数] 是否显示浏览器窗口
                 look_window=False,
                 #[参数]指定浏览器路径
                 browser_path=r"D:\Quark\quark.exe"):

        #启动 Playwright
        p = sync_playwright()
        #启动浏览器内核
        self.playwright = p.start()
        #创建浏览器实例
        self.browser = self.playwright.chromium.launch(
            executable_path=browser_path,
            headless= not look_window,
            slow_mo=1000,
        )

        context = None
        #创建上下文实例
        if type(LogIn_state_FilePath) == str:
            #参数 LogIn_from_file == True 时，从文件获取登录态
            context = self.browser.new_context(storage_state=LogIn_state_FilePath)
        else:
            context = self.browser.new_context()

        #创建 Stealth 实例
        stealth = Stealth(
            #设置语言偏好
            navigator_languages_override=("zh-CN", "zh"),
            #是否(仅通过初始化脚本注入 stealth 代码，而不使用其他注入方式)
            init_scripts_only=False
        )

        #手动装饰上下文实例
        stealth.apply_stealth_sync(context)

        #创建页面实例
        self.page = context.new_page()

    #[定义方法] 跳转页面
    def goto(self, url, timeout=30):
        self.page.goto(url, wait_until="domcontentloaded",timeout=timeout*1000)

    #[定义方法] 利用CSS选择器获取DOM元素或元素的属性值
    def get_DOM(self, css_selector, get_attribute_name:None|str=None):

        #已知属性名时返回属性值
        if type(get_attribute_name) == str:
            list_ = self.page.locator(css_selector).all()
            return [i.get_attribute(get_attribute_name) for i in list_]

        #否则返回元素本身
        else:
            return self.page.locator(css_selector).all()

    #[定义方法] 执行JS代码
    def eval_js(self, js_code):
        return self.page.evaluate(js_code)

    #[定义方法] 点击元素
    def click(self, css_selector, text:None|str=None, index:None|int=None,
                    key:Literal['left','right','middle']='left'):

        DOM = None

        if type(text) == str:
            if index != None:
                DOM = self.page.locator(css_selector, has_text=text).nth(index)
            else:
                DOM = self.page.locator(css_selector, has_text=text)
        else:
            if index != None:
                DOM = self.page.locator(css_selector).nth(index)
            else:
                DOM = self.page.locator(css_selector)

        #手动移动到元素中心点击，防止出现遮罩阻挡点击事件
        DOM.hover()
        self.page.mouse.down(button=key)
        sleep(0.1)
        self.page.mouse.up(button=key)

    #[定义方法] 获取元素坐标
    def get_element_coordinate(self, css_selector, text:None|str=None):
        DOM = None
        if type(text) == str:
            DOM = self.page.locator(css_selector, has_text=text)
        else:
            DOM = self.page.locator(css_selector)
        box = DOM.bounding_box()
        x = box['x'] + box['width'] / 2
        y = box['y'] + box['height'] / 2
        return (x,y)
    #[定义方法] 按下单个鼠标按键
    def mouse_key_down(self, key:Literal['left','right','middle']='left'):
        self.page.mouse.down(key)
    #[定义方法] 抬起单个鼠标按键
    def mouse_key_up(self, key:Literal['left','right','middle']='left'):
        self.page.mouse.up(key)
    #[定义方法] 鼠标平面移动
    def mouse_move(self, x, y):
        self.page.mouse.move(x, y)
    #[定义方法] 模拟鼠标滚轮上下滚动
    def mose_wheel(self, delta_x=0, delta_y=500, Declaration='正数默认向[右,下]方移动，负数为相反方向'):
        self.page.mouse.wheel(delta_x, delta_y)

    #[定义方法] 按下单个键盘按键
    def key_press(self, key):
        self.page.keyboard.press(key)
    #[定义方法] 抬起单个键盘按键
    def key_up(self, key):
        self.page.keyboard.up(key)

    #[定义方法] 保存登录态为 JSON 文件
    def save_LogIn_state(self, FilePath):
        self.page.context.storage_state(path=FilePath)

    #[定义方法] 返回页面HTML源代码
    def html(self):
        return self.page.content()

    #[定义方法] 关闭实例
    def close(self):
        self.browser.close()
        self.playwright.stop()