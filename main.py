import base64
import datetime
import json
import random
import requests
import hashlib
import time

# -----------------------「公告」-----------------------
# 重庆工程职业技术学院自动请假，用于：培训，外出，事假连续请假，大于3天需要校长同意，只能3天连续请假，特做出此定时请假，填写后在linux
# 设置crontab 即可
# 目前仅支持不外出
# 需要环境：python3
# 需要模块: requests hashlib time base64 datetime json random
# -----------------------「公告结束」-----------------------
# -----------------------「配置区」-----------------------
username = ""  # 账号，学号
password = ""  # 密码,默认身份证后八位，大写
leaveReason = ""  # 请假理由
leaveTime = 3  # 请假天数
type = 4  # 请假类别
# 请假类别说明：
# 1：病假
# 2：事假
# 3：求职
# 4：培训
# 5：实习
# 6：实践
# 7：回家
# 8：其他
# 除了这八项，填入其他数字可能造成请假错误，导致旷课
guardianPhone = ""  # 监护人电话
nameGuardian = ""  # 监护人姓名
whetherToCancelThe = True  # 上一个请假存在时，是否撤销，不撤销不能请假
photo = ""  # 图片地址(本计算机)，只能一张，不上传则不填
# -----------------------「高级配置区」-----------------------
bark_url = ""  # 可通知到手机的bark地址，只支持ios


# -----------------------「配置结束」-----------------------
class Gc:
    def __init__(self):
        self.geturl = "http://xgn.cqvie.edu.cn:8200/userhall/smart/omniselector/geturl?serviceid="
        self.login_url = "http://xgn.cqvie.edu.cn:8200/XGPhoneApi/api/Account/stuLogin"
        self.list_url = "http://xgn.cqvie.edu.cn:8200/XGPhoneApi/api/Leave/AllLeaveManage?LoginStatus="
        self.upis_url = "http://xgn.cqvie.edu.cn:8200/service/uploadserver/fileupload/upis"
        self.profile = "http://xgn.cqvie.edu.cn:8200/XGPhoneApi/api/Student/GetStuPersonInfo?LoginStatus="
        self.qj_url = "http://xgn.cqvie.edu.cn:8200/XGPhoneApi/api/Leave/SaveAllLeaveManage"
        self.dell_url = "http://xgn.cqvie.edu.cn:8200/XGPhoneApi/api/Leave/DelAllLeaveManage"

        self.user_gent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400 QQBrowser/9.4.7658.400",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.3 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0"
        ]
        self.token = "VUovimSU63yS5oAs2VGmRRW64uvPAPvk5GJliIglR4NMpu/puD6c25InbFMHZOGMkpAdPnEyMT5%2B4rbhIWsfPvaK5QjdZmq5l5790rF3W2NWea2F4o2EAw=="

    def _rand_ip(self):
        ip3 = random.randint(30, 191)
        ip4 = random.randint(1, 254)
        return f"106.84.{ip3},{ip4}"

    def _main(self):
        bool1 = True
        if len(username) == 0 or len(password) == 0:
            bool1 = False
            return bool1

        return bool1

    def _requests(self, url, action="get", cookies=None, data=None):
        if cookies is None:
            cookies = {}
        if data is None:
            data = {}
        user_gent_number = random.randint(0, 5)
        user_gent = self.user_gent[user_gent_number]
        if not self._main():
            print("未配置用户名或密码")
            return False
        ip = self._rand_ip()
        headers = {"User-Agent": user_gent,
                   "X-Client-IP": ip,
                   "X-Remote-IP": ip,
                   "X-Remote-Addr": ip,
                   "X-Originating-IP": ip,
                   "X-Forwarded-For": ip
                   }
        if action == "get":
            res = requests.get(url, headers=headers, cookies=cookies)
        else:
            res = requests.post(url, headers=headers, cookies=cookies, data=data)
        return res

    def _upis(self):
        if not self._main():
            print("未配置用户名或密码")
            return {"flag": False, "msg": "未配置用户名或密码"}
        if not self._is_login():
            print("未登录")
            return {"flag": False, "msg": "未登录"}
        if len(photo) == 0:
            print("未配置图片，无需上传")
            return {"flag": False, "msg": "未配置图片，无需上传"}
        f = open(photo, 'rb')  # 二进制方式打开图文件
        image_base64 = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        f.close()
        res = self._requests(self.upis_url, action="post",
                             data={"t": "s", "cf": "App_DailyLeave/Images", "bytes": image_base64})

        resi = res.content.decode()
        try:
            resi_json = json.loads(resi)
        except Exception:
            print("上传图片失败")
            return {"flag": False, "msg": "上传图片失败"}
        if resi_json['msg'] != "成功":
            print("上传图片失败")
            return {"flag": False, "msg": "上传图片失败"}
        return {"flag": True, "msg": "上传图片成功", "data": resi_json['data'].split("|")[0]}

    def _login(self):
        if not self._main():
            print("未配置用户名或密码")
            return False
        pass_j = hashlib.md5(password.encode(encoding="UTF-8")).hexdigest()
        print(username, pass_j)
        res = self._requests(self.login_url, action="post", data={"UserId": username, "PassWord": pass_j})
        resi = res.content.decode()
        try:
            res_json = json.loads(resi)

        except Exception:
            print("登录失败")
            return {"flag": False, "msg": "登录失败"}
        if res_json['Msg'] != "OK":
            print("登录失败")
            return {"flag": False, "msg": "登录失败"}
        self.token = res_json['Token']
        print("登录成功")
        return {"flag": True, "msg": "登录成功", "cookies": res.cookies, "data": resi}

    def _bark(self, msg):
        if len(bark_url) != 0:
            requests.get(bark_url + "自动请假/{}".format(msg) + "?group=自动请假")

    def qj(self):
        now_time = time.localtime()
        now_year = now_time.tm_year
        now_month = now_time.tm_mon
        now_day = now_time.tm_mday
        now_hour = now_time.tm_hour
        if now_day <= 9:
            now_day = f"0{now_day}"
        if now_month <= 9:
            now_month = f"0{now_month}"
        now_t = f"{now_year}-{now_month}-{now_day}"
        later_time = datetime.datetime.now() + datetime.timedelta(days=+leaveTime)
        later_year = later_time.year
        later_month = later_time.month
        later_day = later_time.day
        later_hour = later_time.hour
        if later_day <= 9:
            later_day = f"0{later_day}"
        if later_month <= 9:
            later_month = f"0{later_month}"
        later_t = f"{later_year}-{later_month}-{later_day}"
        print("请求登录")
        if not self._login()['flag']:
            print("登录失败")
            self._bark("登录失败")
            return
        print("登录成功")
        is_qj_flag = self._is_qj()
        if not is_qj_flag['flag']:
            print(is_qj_flag['msg'])
            self._bark(is_qj_flag['msg'])
            return
        if len(photo) == 0:
            photo_upis = ""
        else:
            print("上传图片中")
            upis_flag = self._upis()
            if not upis_flag['flag']:
                print(upis_flag['msg'])
                self._bark(upis_flag['msg'])
                return
            print("上传成功")
            photo_upis = upis_flag['data']
        print("获取用户信息")
        profile_flag = self._get_classNo()
        if not profile_flag['flag']:
            print("获取用户信息失败")
            self._bark("获取用户信息失败")
            return
        print("获取用户信息成功")
        classNo = profile_flag['data']['ClassNo']
        name = profile_flag['data']['Name']
        phone = profile_flag['data']['MoveTel']
        j_flag = True  # 是否有假
        if is_qj_flag['msg'] == "没有假":
            j_flag = False
        if j_flag:
            if whetherToCancelThe:  # 有假存在时撤销请假
                print("查询到有假，撤销")
                undo_flag = self._undo(is_qj_flag['data']['List'][0]['Id'])
                if not undo_flag['flag']:
                    print(undo_flag['msg'])
                    self._bark(undo_flag['msg'])
                    return
                print("撤销成功")
            else:
                print("当前有假，不可请假，请撤销,请假失败")
                self._bark("当前有假，不可请假，请撤销,请假失败")
                return
        print("申请请假")
        data = {
            "LoginStatus": self.token,
            "LeaveInfo[Id]": "",
            "LeaveInfo[BeginYear]": now_year,
            "LeaveInfo[TermNo]": "2",
            "LeaveInfo[LeaveId]": "",
            "LeaveInfo[StudentId]": username,
            "LeaveInfo[Name]": name,
            "LeaveInfo[ClassNo]": classNo,
            "LeaveInfo[LeaveBeginTime]": now_t,
            "LeaveInfo[LeaveBeginTimeDay]": now_t,
            "LeaveInfo[LeaveBeginTimeHour]": now_hour,
            "LeaveInfo[LeaveBeginTimeMinute]": "",
            "LeaveInfo[LeaveEndTime]": now_t,
            "LeaveInfo[LeaveEndTimeDay]": later_t,
            "LeaveInfo[LeaveEndTimeHour]": later_hour,
            "LeaveInfo[LeaveEndTimeMinute]": "",
            "LeaveInfo[LeaveDays]": leaveTime,
            "LeaveInfo[LeaveHours]": 0,
            "LeaveInfo[LeaveMinutes]": "",
            "LeaveInfo[LeaveReason]": f"0402800{type}",
            "LeaveInfo[LeaveReasonDetail]": leaveReason,
            "LeaveInfo[StuMoveTel]": phone,
            "LeaveInfo[IsTellGuarder]": "1",
            "LeaveInfo[GuarderName]": nameGuardian,
            "LeaveInfo[GuarderTel]": guardianPhone,
            "LeaveInfo[IsOut]": "0",
            "LeaveInfo[OutAddress]": "",
            "LeaveInfo[OutAddressArea]": "",
            "LeaveInfo[Province1]": "",
            "LeaveInfo[City1]": "",
            "LeaveInfo[County1]": "",
            "LeaveInfo[OutAddressStreet]": "",
            "LeaveInfo[OutGoTime]": now_t,
            "LeaveInfo[OutGoTimeDay]": now_t,
            "LeaveInfo[OutGoTimeHour]": now_hour,
            "LeaveInfo[OutGoTimeMinute]": "",
            "LeaveInfo[OutBackTime]": now_t,
            "LeaveInfo[OutBackTimeDay]": now_t,
            "LeaveInfo[OutBackTimeHour]": now_hour,
            "LeaveInfo[OutBackTimeMinute]": "",
            "LeaveInfo[OutGoVehicle]": "",
            "LeaveInfo[OutBackVehicle]": "",
            "LeaveInfo[OutContacts]": "",
            "LeaveInfo[OutContactsRelationship]": "",
            "LeaveInfo[OutContactsTel]": "",
            "LeaveInfo[IsCompanion]": "",
            "LeaveInfo[Companion]": "",
            "LeaveInfo[CompanionRelationship]": "",
            "LeaveInfo[CompanionTel]": "",
            "LeaveInfo[SystemId]": "",
            "LeaveInfo[IsGuarderConfirm]": "",
            "LeaveInfo[GuarderConfirmTime]": "",
            "LeaveInfo[IsCancel]": "",
            "LeaveInfo[IsDisLeave]": "",
            "LeaveInfo[Status]": "",
            "LeaveInfo[DataSource]": "",
            "LeaveInfo[FileUrl][0][Id]": "00000000-0000-0000-0000-000000000000",
            "LeaveInfo[FileUrl][0][SystemId]": "00000000-0000-0000-0000-000000000000",
            "LeaveInfo[FileUrl][0][Address]": photo_upis,
            "LeaveInfo[FileUrl][0][AddressName]": "",
            "LeaveInfo[FileUrl][0][AddressThing]": "",
            "LeaveInfo[FileUrl][0][AppKey]": "",
            "LeaveInfo[FileUrl][1][Id]": "00000000-0000-0000-0000-000000000000",
            "LeaveInfo[FileUrl][1][SystemId]": "00000000-0000-0000-0000-000000000000",
            "LeaveInfo[FileUrl][1][Address]": "",
            "LeaveInfo[FileUrl][1][AddressName]": "",
            "LeaveInfo[FileUrl][1][AddressThing]": "",
            "LeaveInfo[FileUrl][1][AppKey]": "",
            "LeaveInfo[FileUrl][2][Id]": "00000000-0000-0000-0000 000000000000",
            "LeaveInfo[FileUrl][2][SystemId]": "00000000-0000-0000-0000-000000000000",
            "LeaveInfo[FileUrl][2][Address]": "",
            "LeaveInfo[FileUrl][2][AddressName]": "",
            "LeaveInfo[FileUrl][2][AddressThing]": "",
            "LeaveInfo[FileUrl][2][AppKey]": "",
            "LeaveInfo[ServiceUploadUrl]": "http://xgn.cqvie.edu.cn:8200/service/uploadserver/fileupload/upis",
            "LeaveInfo[nextStepMsgStr]": "",
            "LeaveInfo[WFId]": "",
            "LeaveInfo[WFType]": "",
            "LeaveInfo[WFTypeStatus]": "",
            "LeaveInfo[FlowStatus]": "",
            "LeaveInfo[NextStepMsg]": "",
            "LeaveInfo[NextWFType]": "",
            "LeaveInfo[Status1]": "false",
            "LeaveInfo[OldTime]": "",
            "LeaveInfo[LeaveTime]": "",
            "LeaveInfo[OutTime]": "",
            "LeaveInfo[LeaveNumNo]": "",
        }
        res = self._requests(self.qj_url, action="post", data=data)
        try:
            res_json = json.loads(res.content.decode())
        except Exception:
            print("请假失败，检查程序")
            self._bark("请假失败，检查程序")
            return
        self._bark(res_json['errmsg'])
        print(res_json['errmsg'])
        # print(res.content.decode())

    def _undo(self, id):
        if not self._main():
            print("未配置用户名或密码")
            return {"flag": False, "msg": "未配置用户名或密码"}
        if not self._is_login():
            print("未登录")
            return {"flag": False, "msg": "未登录"}
        res = self._requests(self.dell_url, action="post", data={"LoginStatus": self.token, "Id": id})
        try:
            res_json = json.loads(res.content.decode())
        except Exception:
            return {"flag": True, "msg": "撤销失败"}
        if res_json["errcode"] == 0:
            return {"flag": True, "msg": "撤销成功"}
        return {"flag": True, "msg": res_json['errmsg']}

    def _is_login(self):
        if self.token is None:
            return False
        res = self._requests(self.list_url + self.token).content.decode()
        if res.find("Sorry, Page Not Found") != -1:
            return False
        else:
            return True

    def _is_qj(self):  # 是否可以请假
        if not self._main():
            print("未配置用户名或密码")
            return {"flag": False, "msg": "未配置用户名或密码"}
        if not self._is_login():
            print("未登录")
            return {"flag": False, "msg": "未登录"}
        res = self._requests(self.list_url + self.token).content.decode()
        resi_json = json.loads(res)
        if len(resi_json['List']) != 0:
            return {"flag": True, "msg": "有请假未销毁", "data": resi_json}
        else:
            return {"flag": True, "msg": "没有假", "data": resi_json}

    def _get_classNo(self):
        if not self._main():
            print("未配置用户名或密码")
            return {"flag": False, "msg": "未配置用户名或密码"}
        if not self._is_login():
            print("未登录")
            return {"flag": False, "msg": "未登录"}
        res = self._requests(self.profile + self.token)
        try:
            res_json = json.loads(res.content.decode())
        except Exception:
            return {"flag": False, "msg": "未登录"}
        return {"flag": True, "data": res_json}
    # def is_login(self):
    #     res = self.requests(self.geturl, cookies=self.cookies).content.decode()
    #     try:
    #         res_json = json.loads(res)
    #         if res_json['State'] == -100:
    #             return False
    #         else:
    #             return True
    #     except Exception:
    #         return False
    #     # res = requests.get(self.geturl).content.decode()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    Gc = Gc()
    Gc.qj()
# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
