import time

import aiohttp
import asyncio
import requests
from Cryptodome.Cipher import AES
import base64

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
# cookie换成自己的
cookie = ""
headers = {
    "Host": "novelapi.baidu.com",
    "x-bd-traceid": "3374ce9ceeda47c685d794b3b4fa629f",
    "x-sid": "H4sIAAAAAAAAAD1WUbJsMQRc0a1CCFnN7H8Xr2nnfc1UjgitNaZ+4/38z07K0Z/iz73v/axPPM6chNTDn3gvfu+9+jMNOYmj8rYVl/orMZyURfaNOven0k5UnW7fveP22rM5ST+FP69dFj+JrXFJ8mlT+108qALj2yep/JQmvJWSOSlc1/UseCvGM95qG7WSn74/vJ6CkwoLBB5yJ0Zhoqk+qVtWdbDnnnA4wi1h8EjsdRhm6v2l48Ef41vvl5OGh4w/l7Bf/R0J/J42VvhN+AulxdXTGetRl8bY7EU+2jb8TEt4clgHfLqLE6BnrSLzbRTFE7+1EDpvWUXGhHzL3pb6rE0+X+SAbicO4L+sTuOljlpVvb5vhec7Mj9AviPzPMQHDjaxM+TRV17NK7XUhU7yyMJt87xlWjHnvFNTlNZ9I7OuKYA3W47kFktqq31QZO8iWaMMvPLOB8Q7bsEqpPcm89zMPX3JY4uXTMkBUx3lS6gSbWzZYFdZkZAN8yp5blFuywcklX9RokJIkEs/buG3uawvgCD5kT7sPhcIsAs1+hPgQ/5niJL0gp7rXPAkKoOHkJNNNJ0cqYjLMjCCFuTbyRvMN3C9/Vg+5uJum5wssO5CABykL9a+QVJz83Zc0kUplH36GVUMFo/0vFcWXDnjSUTsDO5+zxnf7ypxB8HuqsAlB4/6V5KPuYy+i0WaIXpwyacDQBT/qzdk6MowCXuDl3pUERToxukSIfgzwVNWhtWKPvdAtczADHIRYUxJn+tZFiV1xlpV5nZ4btdRMyXtEnloEVmUGTSGdKwxW90+nsLzq8FJSw9tXLcPowFj4cA9GOtLoLsEK5YbpPuxH8/SG6ViP17E3GlZGKHLFlJGaLk8B5jDlneMAqG0QcTLKD/GT1fAnybxk45QhqGXbymJcESVJxdjYYlQbBgHSwkC4P2AoroB8b1lIV9TJZvKWi4v27WDfi4MOYFm54c/PWj+FFPMKCpoPGGTZo2xvbI9KfYQYrBY8gnrFqJsQKAb9Oy20++dTy0/CSoUGcZyu4A1ffay4VHEs6KNbth4ouEpqRZQ4NjvYyI0ZPoADc0NDqa6Z+ZxN6wzel0w4003ANuckdvXTkPFgn+xdcWKFOc9hUoTYPhekUn7hkXseHyH8xoqJey5mcCnE6D2venyzn7V9RwqJ7KugcN7jtdg50p3IW915/uDztw/+fXV20hTy78i3AHBlTuJv0+kIKJkVKv/ZOUIfWhs/z+ZTgqq/xeEN/2BkXqXPy0Gg8XhDGotvivuStmHA5lhfXYO3IhcSXiyoQ9/en6yfBDcnd5RtbZh3y6y/LYe/jJ6tlyF5s6kgvaANsP4XrZu80DePr6EAosPe6nlmcJri2TWzlE044rFLknQUt0RC14nZfb7s8sWJkDMhAYdOGNuP0GivdiRb/SjOTqCsQywMYo4gFhSAwEoaObOBrssSkPmuxpCC9qVQvw852Ozy7/ljq2KMXPYD7NYKOerSYvuk8v1ofeRJMSsVNwVVGyCj3iqn099V8XRjLTRXQHi/9aJhY0cPbsveDdfS7X3AjjQdGMgsOilM6ZRo8WgrFcCqNFobGyBsSXOXFJDtru/oEX5bO9cHFXZBcXOultrtLTO4Kvv5Ok3G3sF/AeNB5DxwAsAAA==",
    "x-sid-type": "1",
    "user-agent": "okhttp/3.12.12 SP-engine/3.51.0 Dalvik/2.1.0 (Linux; U; Android 12; DCO-AL00 Build/501caac.1) baiduboxapp/15.26.0.10 (Baidu; P1 12)",
    "content-type": "application/x-www-form-urlencoded",
    "content-length": "370",
    "accept-encoding": "gzip",
    "cookie": cookie}

book_id = '4357434201'
书名 = '龙族：归来的他，反抗天命'


def decry(binary_data):
    # 对二进制数据进行 Base64 编码
    base64_str = base64.b64encode(binary_data).decode('utf-8')
    # AES 解密
    key = b'D0CD8B760CE07BC3'  # 16字节，128bits
    iv = b'2011121211143000'  # 16字节

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(base64.b64decode(base64_str))

    # 去除 PKCS7 填充
    pad_len = decrypted_data[-1]
    decrypted_data = decrypted_data[:-pad_len]

    return decrypted_data.decode('utf-8', errors='ignore')


async def danzhang(session, book_id, cid):
    """抓取单章"""
    data = {
        "book_id": book_id,
        "cid": f"{book_id}|{cid}",
        "need_bookinfo": 1
    }
    url = "https://novelapi.baidu.com/searchbox?action=novel&type=content&is_close_individual_novel=0&nfonttype=0&service=bdbox&uid=gi20f_uS-u_daHudg825ilaWvalPuHaR_a2xi0uW2a8y9Hanpu2ER8WaA&from=1026250u&ua=YavjC_al2i4qywoUfpw1z4u32N_-aX8WoavjhxGHNqqqB&osname=baiduboxapp&osbranch=a0&branchname=baiduboxapp&pkgname=com.baidu.searchbox&p_sv=32&mps=1597730474&mpv=1&network=1_-1&cfrom=1026250u&ctv=2&cen=ua_uid&typeid=0&puid=gav4igaa28L6dqqqB&c3_aid=A00-WEBWGX3FXDDDYPGLGD3CAZMIZD4X3PBO-EYLAWMVQ&zid=975E42D44FDA5B9F2642937297834CE9DC39F62463A1&matrixstyle=0&ds_stc=0.4813&ds_lv=1&dt=0&andrst=0&cp_isbg=0&needmap=1&isnewtab_novel=0&istabbar_novel=0&newtab_version=2"
    post_data = {
        "data": f'{{"gid":{book_id},"read_status":0,"ctsrc":"","cid":"{book_id}|{cid}","dir":"0","fromaction":"viewcontent","tts_tf_fr":"ads_tingshu","autobuy":"0","need_buy_info":0,"nid":"","openreadertime":"1784565241","lastvisittime":"0"}}'
    }

    async with session.post(
            url=url,
            headers=headers,
            data=post_data,
            timeout=15
    ) as resp:
        result = await resp.json()
        try:
            novel_url = result['data']['novel']['content']['dataset']['content_url']
        except (KeyError, TypeError) as e:
            print(f"章节 {cid} 数据结构异常: {e}")
            if result['data']['novel']['content']['dataset']['status_code'] == 501:
                time.sleep(1)
            response = requests.post(url=url,headers=headers,data=post_data,timeout=15,verify=False)
            novel_url = response.json()['data']['novel']['content']['dataset']['content_url']



        async with session.get(novel_url) as content_resp:
            content = await content_resp.read()
        content = decry(content)

        return {
            'cid': cid,
            'title': 'post_data',
            'content': content
        }


# i是字符串，表示第i个50章的爬取
async def _50danzhang(i):
    # 请求前50章
    list_url = 'https://boxnovel.baidu.com/boxnovel/wiseapi/chapterList?bookid=' + book_id + '&pageNum=' + i + '&order=asc&site='
    list_response = requests.get(list_url, verify=False)
    data = list_response.json()
    cid_list = [item['chapter_id'] for item in data['data']['chapter']['chapterInfo']]
    title_list = [item["chapter_title"] for item in data['data']['chapter']['chapterInfo']]
    title_map = dict(zip(cid_list, title_list))

    print("开始并发爬取 ")
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [danzhang(session, book_id, cid) for cid in cid_list]
        results = await asyncio.gather(*tasks)

    results = [r for r in results if r is not None]
    for chapter in results:
        cid = chapter['cid']
        if cid in title_map:
            chapter['title'] = title_map[cid]
    # 按章节ID排序
    results.sort(key=lambda x: int(x['cid']))

    # 一次性写入
    with open(f'{书名}.txt', 'a', encoding='utf-8') as f:
        for chapter in results:
            f.write(f"{chapter['title']}\n\n　　")
            f.write(f"{chapter['content']}\n\n")

    print(f"完成第{i}个50章！")
    time.sleep(10)


async def main():
    list_url = r'https://boxnovel.baidu.com/boxnovel/wiseapi/chapterList?bookid=' + book_id + '&pageNum=1&order=asc&site='
    list_response = requests.get(list_url, verify=False)
    data = list_response.json()
    count = data['data']['chapter']['chapterCount'] // 50 + 1  # count就是最后目录表单，50章1个表单
    for i in range(1, count + 1):
        await _50danzhang(str(i))


if __name__ == '__main__':
    asyncio.run(main())
