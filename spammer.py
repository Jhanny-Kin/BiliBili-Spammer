import requests
import bs4
import re
import sys
import time


path = 'message.txt'
reply = 'https://api.bilibili.com/x/v2/reply/add'
headers = {
    'User-Agent': 'Elysia is my waifu',
    'Cookie': '',
}
data = {
    'oid': None,
    'message': None,
    'csrf': '',
    'code': 'Elysia',
    'type': 1
}


with open(path) as file:
    data['message'] = file.readline()
    print(f'\nMessage Loaded: {data["message"]}')


def search(keyword, amount, target=[]):
    for i in range(amount):
        search = f'https://search.bilibili.com/all?keyword={keyword}&page={i+1}'
        html = requests.get(url=search)
        soup = bs4.BeautifulSoup(html.text, 'html.parser')
        temp = soup.find_all('a')

        for each in temp:
            bvid = re.findall(r'href="//www.bilibili.com/video/(.+)from=search"', str(each))
            if len(bvid) == 1:
                target.append(bvid[0].strip('?'))

        print('\r', end='')
        print(f'Page: {i+1}/{amount}', end='')
        sys.stdout.flush()

    print()
    return list(set(target))


def match(bvids, amount, oids={}):
    count = 0
    missing = 0
    for bv in bvids:
        url = f'https://www.bilibili.com/video/{bv}'
        html = requests.get(url=url)
        soup = bs4.BeautifulSoup(html.text, 'html.parser')
        temp = soup.find_all('script')

        for each in temp:
            aid = re.findall(r'"aid":(\d+),"bvid"', str(each))
            if len(aid) > 0:
                oids[bv] = int(aid[0])
                break
        else:
            missing += 1

        count += 1
        print('\r', end='')
        print(f'Matching: {count}/{amount*20} [{round(count/(amount*20)*100, 1)}%]', end='')
        sys.stdout.flush()

    if missing != 0:
        print(f'\n\033[0;31mWarning: {missing} video(s) missing!\033[0m')
    else:
        print()
    return oids


def send(bullets):
    for bvid, oid in bullets.items():
        data['oid'] = oid
        result = requests.post(url=reply, headers=headers, data=data)
        if '"code":0' in result.text:
            print(f'Successfully send to {bvid}')
        else:
            print(f'Failed to send to {bvid}')
        
        for i in range(1, 6001):
            print('\r', end='')
            print(f'Sleeping: {int(i//100)}/60s [{round(i/60, 1)}%]', end='')
            sys.stdout.flush()
            time.sleep(0.01)
    print()

        
def main():
    try:
        keyword = input('>>> Keyword(one word only): ')
        pages = int(input('>>> Pages(20 attmeps per page): '))
    except ValueError:
        print('\033[0;31mInvalid Input\033[0m')
    else:
        if keyword == 'self' and pages == 0:
            print('\033[0;32mTest Mode Activated\033[0m')
            send({'MYSELF': 717473650})
        else:
            bvids = search(keyword, pages)
            oids = match(bvids, pages)

            see = input('>>> See targets? (y/n)')
            if see != 'n':
                print(oids)
            check = input('>>> Start sending? (y/n)')
            if check != 'n':
                send(oids)


if __name__ == '__main__':
    main()
