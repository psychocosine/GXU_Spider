class OutOfLimitedTimeException(Exception):
    def __init__(self):
        print('当前无可选课程')


class LoginException(Exception):
    def __init__(self):
        print('登录异常')
