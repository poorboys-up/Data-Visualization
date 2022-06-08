#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
import time
import re
import pandas as pd
import os

def close_windows():
    #如果有登录弹窗，就关闭
    try:
        time.sleep(0.5)
        if dr.find_element_by_class_name("jconfirm").find_element_by_class_name("closeIcon"):
            dr.find_element_by_class_name("jconfirm").find_element_by_class_name("closeIcon").click()
    except BaseException as e:
        print('close_windows,没有弹窗',e)


def get_current_region_job(k_index):
    flag = 0
    # page_num_set=0#每区获取多少条数据，对30取整

    df_empty = pd.DataFrame(columns=['岗位', '地点', '薪资', '工作经验', '学历', '公司名称', '技能', '工作福利', '工作类型', '融资情况', '公司规模'])
    while (flag == 0):
        # while (page_num_set<151)&(flag == 0):#每次只能获取150条信息
        time.sleep(0.5)
        close_windows()
        job_list = dr.find_elements_by_class_name("job-primary")
        for job in job_list:  # 获取当前页的职位30条
            job_name = job.find_element_by_class_name("job-name").text
            # print(job_name)
            job_area = job.find_element_by_class_name("job-area").text
            # salary = job.find_element_by_class_name("red").get_attribute("textContent")  # 获取薪资
            salary_raw = job.find_element_by_class_name("red").get_attribute("textContent")  # 获取薪资
            salary_split = salary_raw.split('·')  # 根据·分割
            salary = salary_split[0]  # 只取薪资，去掉多少薪

            # if re.search(r'天', salary):
            #     continue

            experience_education = job.find_element_by_class_name("job-limit").find_element_by_tag_name(
                "p").get_attribute("innerHTML")

            # experience_education_raw = '1-3年<em class="vline"></em>本科'
            experience_education_raw = experience_education
            split_str = re.search(r'[a-zA-Z =<>/"]{23}', experience_education_raw)  # 搜索分割字符串<em class="vline"></em>
            # print(split_str)

            experience_education_replace = re.sub(r'[a-zA-Z =<>/"]{23}', ",", experience_education_raw)  # 分割字符串替换为逗号
            # print(experience_education_replace)

            experience_education_list = experience_education_replace.split(',')  # 根据逗号分割
            # print('experience_education_list:',experience_education_list)

            if len(experience_education_list) != 2:
                print('experience_education_list不是2个，跳过该数据', experience_education_list)
                break
            experience = experience_education_list[0]
            education = experience_education_list[1]
            # print(experience)
            # print(education)

            company_type = job.find_element_by_class_name("company-text").find_element_by_tag_name(
                "p").get_attribute("innerHTML")
            company_type_size_row = company_type
            split_str_2 = re.search(r'[a-zA-Z =<>/"]{23}', company_type_size_row)
            # print(split_str_2)
            # print("split2------------------------------------------------------")
            company_size_replace = re.sub(r'[a-zA-Z =<>/"]{23}', ",", company_type_size_row)
            # print(company_size_replace)

            company_size_list = company_size_replace.split(',')
            # print(company_size_list)

            if len(company_size_list) != 3:
                print('company_size_list不是3个，跳过该数据', company_size_list)
                break
            company_direct_info = company_size_list[0].split(">")[1]
            company_salary_info = company_size_list[1].split(">")[1]
            company_size_info = company_size_list[2]

            company = job.find_element_by_class_name("company-text").find_element_by_class_name("name").text

            skill_list = job.find_element_by_class_name("tags").find_elements_by_class_name("tag-item")
            skill = []
            job_advantage = job.find_element_by_class_name("info-desc").text
            for skill_i in skill_list:
                skill_i_text = skill_i.text
                if len(skill_i_text) == 0:
                    continue
                skill.append(skill_i_text)
            # print(job_name)
            # print(skill)

            df_empty.loc[k_index, :] = [job_name, job_area, salary, experience, education, company, skill,
                                        job_advantage, company_direct_info, company_salary_info, company_size_info]
            print(df_empty.loc[k_index, :])
            k_index = k_index + 1
            # page_num_set=page_num_set+1
            print("已经读取数据{}条".format(k_index))

        close_windows()
        try:  # 点击下一页
            cur_page_num = dr.find_element_by_class_name("page").find_element_by_class_name("cur").text
            # print('cur_page_num',cur_page_num)

            # 点击下一页
            element = dr.find_element_by_class_name("page").find_element_by_class_name("next")
            dr.execute_script("arguments[0].click();", element)
            time.sleep(1)
            # print('点击下一页')

            new_page_num = dr.find_element_by_class_name("page").find_element_by_class_name("cur").text
            # print('new_page_num',new_page_num)

            if cur_page_num == new_page_num:
                flag = 1
                break

        except BaseException as e:
            print('点击下一页错误', e)
            break

    print(df_empty)
    if os.path.exists("ai数据.csv"):  # 存在追加，不存在创建
        df_empty.to_csv('ai数据.csv', mode='a', header=False, index=None, encoding='gb18030')
    else:
        df_empty.to_csv("ai数据.csv", index=False, encoding='gb18030')

    return k_index


def main():
    # 打开浏览器
    # dr = webdriver.Firefox()
    global dr
    dr = webdriver.Chrome()
    # dr = webdriver.Ie()

    # # 后台打开浏览器
    # option=webdriver.ChromeOptions()
    # option.add_argument('headless')
    # dr = webdriver.Chrome(chrome_options=option)
    # print("打开浏览器")

    # 将浏览器最大化显示
    dr.maximize_window()

    # 转到目标网址
    dr.get("https://www.zhipin.com/job_detail/?query=数据分析师&city=101280600&industry=&position=")  # 全国
    # dr.get("https://www.zhipin.com/c101010100/?query=人工智能&ka=sel-city-101010100")#北京
    print("打开网址")
    time.sleep(5)

    k_index = 0  # 数据条数、DataFrame索引

    flag_hot_city = 0

    for i in range(3, 19, 1):
        # print('第',i-2,'页')

        # try:

        # 获取城市
        close_windows()
        hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
        close_windows()
        # hot_city_list[i].click()#防止弹窗，改为下面两句
        # element_hot_city_list_first = hot_city_list[i]
        dr.execute_script("arguments[0].click();", hot_city_list[i])

        # 输出城市名
        close_windows()
        hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
        print('城市：{}'.format(i - 2), hot_city_list[i].text)
        time.sleep(0.5)

        # 获取区县
        for j in range(3, 50, 1):
            # print('第', j , '个区域')
            # try:

            # close_windows()
            # hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")

            # 在这个for循环点一下城市，不然识别不到当前页面已经更新了
            close_windows()
            hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
            close_windows()
            # hot_city_list[i].click()#防止弹窗，改为下面
            dr.execute_script("arguments[0].click();", hot_city_list[i])

            # 输出区县名称
            close_windows()
            city_district = dr.find_element_by_class_name("condition-district").find_elements_by_tag_name("a")
            if len(city_district) == j:
                print('遍历完所有区县，没有不可点击的，跳转下一个城市')
                break
            print('区县：', j, city_district[j].text)
            # city_district_value=city_district[j].text#当前页面的区县值

            # 点击区县
            close_windows()
            city_district = dr.find_element_by_class_name("condition-district").find_elements_by_tag_name("a")
            close_windows()
            # city_district[j].click()]#防止弹窗，改为下面两句
            # element_city_district = city_district[j]
            dr.execute_script("arguments[0].click();", city_district[j])

            # 判断区县是不是点完了
            close_windows()
            hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
            print('点击后这里应该是区县', hot_city_list[1].text)  # 如果是不限，说明点完了，跳出

            hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
            print('如果点完了，这里应该是不限：', hot_city_list[1].text)

            hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
            if hot_city_list[1].text == '不限':
                print('当前区县已经点完了，点击下一个城市')
                flag_hot_city = 1
                break

            close_windows()
            k_index = get_current_region_job(k_index)  # 获取职位，爬取数据

            # 重新点回城市页面，再次获取区县。但此时多了区县，所以i+1
            close_windows()
            hot_city_list = dr.find_element_by_class_name("condition-city").find_elements_by_tag_name("a")
            close_windows()
            # hot_city_list[i+1].click()#防止弹窗，改为下面两句
            # element_hot_city_list_again = hot_city_list[i+1]
            dr.execute_script("arguments[0].click();", hot_city_list[i + 1])

            # except BaseException as e:
            #     print('main的j循环-获取区县发生错误:', e)
            #     close_windows()

            time.sleep(0.5)

        # except BaseException as e:
        #     print('main的i循环发生错误:',e)
        #     close_windows()

        time.sleep(0.5)

    # 退出浏览器
    dr.quit()
    # p1.close()

if __name__ == "__main__":
    main()


# In[ ]:




