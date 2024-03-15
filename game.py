import random

cards_list = ['A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2']
print(f'您的原始卡片顺序为：{cards_list}')
# Name
name_length = len(input('请输入您的名字：').strip('·'))
cards_list = cards_list[name_length:] + cards_list[:name_length]
print(f'名字字数：{name_length}，现在的卡片顺序：{cards_list}')
# Move and hide
insert_index = random.sample(range(1, len(cards_list)-3-1), 1)[0]
cards_list = cards_list[3:][:insert_index] + cards_list[:3] + cards_list[3:][insert_index:]
print(f'移动三张之后，卡片顺序为：{cards_list}')
card_hidden = cards_list[0]
cards_list = cards_list[1:]
print(f'藏起的卡片为：{card_hidden}，现在的卡片顺序为：{cards_list}')
# Hometown
location = input('请输入您的家乡（南方/北方/未知）：')
location_num = 1 if location == '北方' else (2 if location == '南方' else 3)
insert_index = random.sample(range(1, len(cards_list)-location_num-1), 1)[0]
cards_list = cards_list[location_num:][:insert_index] + cards_list[:location_num] + cards_list[location_num:][insert_index:]
print(f'您的家乡在：{location}，现在的卡片顺序为：{cards_list}')
# Gender
gender = input('请输入您的性别：')
gender_num = 1 if gender == '男' else 2
cards_list = cards_list[gender_num:]
print(f'您的性别：{gender}，现在的卡片顺序为：{cards_list}')
# ?
curse = '见证奇迹的时刻'
for one in list(curse):
    cards_list = cards_list[1:] + [cards_list[0]]
    print(f'{one}!{cards_list}')
while len(cards_list) != 1:
    cards_list = cards_list[1:] + [cards_list[0]]
    cards_list = cards_list[1:]
    print(f'扔掉一张！还剩{cards_list}')
card_result = cards_list[0]
result = '成功了！' if card_result[0] == card_hidden[0] else '失败了！'
print(f'您藏的牌是{card_hidden}，最后留下的牌是{card_result}，{result}')
