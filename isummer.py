# coding: utf-8

import json
from random import random

import requests
import urllib3
import time

# 授权信息，该值首先直接固定
Authorization = ''
# 经度
lat = ''
# 维度
lng = ''


# 通用GET/POST请求
def request_isummer(url, type, submit):
    headers = {
        'Summerversion': '3.5.5',
        'Summerplatform': 'Android',
        'Summerchannel': 'official',
        'Devicebrand': 'Xiaomi',
        'Systemmodel': 'Mi',
        'Systemlanguage': 'zh_CN',
        'Systemversion': '8.0.0',
        'lat': lat,
        'lng': lng,
        'Authorization': Authorization,
        'User-Agent': 'okhttp / 3.8',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    if type == 'GET':
        r = requests.get(url, params=submit, headers=headers, verify=False)
    else:
        r = requests.post(url, data=submit.encode('UTF-8'), headers=headers, verify=False)
    
    r.encoding = 'utf-8'
    if r.text == "[]":
        return 0
    # print(r.text)
    return json.loads(r.text)


# 获取指定城市/指定学校/附近人的学生
def nearbies(city_id_eq, school_id_eq, limit, offset):
    data = "scope=&view_mode=normal&q[gender_eq]=2"

    if city_id_eq != "":
        data = data + "&q[city_id_eq]=" + city_id_eq

    if school_id_eq != "":
        data = data + "&q[school_id_eq]=" + school_id_eq

    data = data + "&lat=" + lat
    data = data + "&lng=" + lng
    data = data + "&limit=" + limit
    data = data + "&offset=" + offset

    url = "https://imsummer.cn/api/v6/user/nearbies?" + data

    return request_isummer(url, 'GET', {})


# 获取试卷题目
def getPapers(paper_id):
    url = 'https://imsummer.cn/api/v6/papers/' + paper_id + '?tips_type=2'
    return request_isummer(url, 'GET', {})


# 获取题目小抄
def getComment(question_id):
    url = "https://imsummer.cn/api/v6/questions/" + question_id + "/answers?offset=0&limit=20&sort=top&comment_filter" \
                                                                  "=all "
    return request_isummer(url, 'GET', {})


# 发送验证码
def sendCode():
    return


# 登录
def login():
    return


def submitPaper(paper_id, answer_str):
    url = 'https://imsummer.cn/api/v6/papers/' + paper_id + '/quizzes'
    return request_isummer(url, 'POST', answer_str)


if __name__ == '__main__':

    # 禁用安全请求警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    all_content = {'这道题太难了，我不知道啊~', '求求你饶了我吧，我太难了~', '小姐姐偷偷地告诉你，如果有五个问题我都回答不上来的话，到后面会有surprise', '还来？哎呀，我的天我错了',
                   '妈呀，救救我吧，小姐姐，其实我是一个技术宅，我是一个学计算机的哦，这个问题是我答的也不是我答的，一定要通过哦，告诉你秘密'}
    content_i = 0

    for page in range(0, 1):

        nearby_people = nearbies("", "", '20', str(page * 20))  # 每次步进20个人

        if nearby_people != 0:
            for item in nearby_people:  # 遍历获取到的学生
                nickname = item['nickname']
                gender = item['gender']  # 1是男，2是女
                birthday = item['birthday']
                id = item['id']
                if 'paper_id' in item:
                    paper_id = item['paper_id']
                else:
                    paper_id = ''

                # 如果试卷不存在，检查下一个人
                if paper_id == '':
                    print(nickname + '\t' + 'paper is not exist')
                    continue

                log_info = nickname + '\t' + str(gender) + '\t' + birthday + '\t' + str(id) + '\t' + str(paper_id)
                print(log_info)

                # 如果试卷存在，获取试卷
                papers = getPapers(paper_id)
                if papers == 0:
                    print('Failure to get the paper')
                    continue

                # 获取试卷成功,获取试卷描述以及小提示
                if 'description' in papers:
                    description = papers['description']
                    print('description:' + description)
                if 'tips' in papers:
                    tips = papers['tips']
                    print('tips:' + tips)

                answer = dict()

                # answer['answer'] = {}
                i = 0
                question_answers = []
                for question in papers['questions']:  # 遍历问题

                    question_content = question['content']
                    question_id = question['id']
                    content_type = question['content_type']
                    question_type = question['question_type']
                    options = question['options']

                    # 如果是语音问题，那直接把问题复述一遍吧
                    if question_type == 3:
                        content_url = question['content_url']
                        temp = dict()
                        temp['public'] = False
                        temp['anonymous'] = False
                        temp['answer_type'] = question_type
                        temp['content'] = False
                        temp['content_type'] = content_type
                        temp['content_url'] = content_url
                        temp['option_index'] = -1
                        question_answers.append(temp)
                        print('content_url:' + content_url)
                        continue

                    if question_content != '':
                        print('question:' + question_content)
                    if options:
                        print(options)

                    # 不是语音的话，获取小抄
                    comments = getComment(question_id)
                    if comments == 0:  # 获取不到小抄
                        content = all_content[content_i]
                        option_index = 1  # 固定选第一个答案吧
                    else:  # 获取到小抄
                        for comment in comments:
                            content = ''
                            if 'content' in comment:
                                content = comment['content']
                            option_index = -1
                            if 'option_index' in comment:
                                option_index = comment['option_index']

                    if '身高' in question_content:
                        content = '175'
                    if '体重' in question_content:
                        content = '140'

                    # 构建答案
                    temp = dict()
                    temp['public'] = False
                    temp['anonymous'] = False
                    temp['answer_type'] = question_type
                    temp['content'] = content
                    temp['content_type'] = content_type
                    temp['option_index'] = option_index
                    question_answers.append(temp)

                    if content != '':
                        print('answer:' + content)
                    if option_index != -1:
                        print('answer:' + str(option_index))

                # 提交答案

                answer['answers'] = question_answers
                answer['paper_id'] = paper_id
                answer['rate'] = 5
                answer_str = json.dumps(answer, ensure_ascii=False)
                # print(answer_str)
                result = submitPaper(paper_id, answer_str)
                print('submit success! start next')
                print('\n')
                time.sleep(1)

    print("Done")
