import aiohttp
import asyncio
import requests
from Cryptodome.Cipher import AES
import base64

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
cookie = 'xxx' #后来发现竟然不用cookie也能请求到数据?!大开眼界
headers = {'User-Agent': user_agent, 'cookie': cookie, }

book_id = '4357430382'
书名 = '改写神话，成为道祖！'


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
    url = r'https://novelapi.baidu.com/boxnovel/cors?action=novel&type=content&osname=wise&data={"book_id":"' + book_id + r'","chapter_id":"' + cid + r'"}'

    async with session.get(url) as resp:
        result = await resp.json()
        if result.get('errno') == 0:
            novel_url = result['data']['url']
            async with session.get(novel_url) as content_resp:
                content = await content_resp.read()
            content = decry(content)

            return {
                'cid': cid,
                'title': (result['data']['order'] or '') + ' ' + (result['data']['title'] or ''),# 防止出现None
                'content': content
            }
        return None


# i是字符串，表示第i个50章的爬取
async def _50danzhang(i):
    # 请求前50章
    list_url = 'https://boxnovel.baidu.com/boxnovel/wiseapi/chapterList?bookid=' + book_id + '&pageNum=' + i + '&order=asc&site='
    list_response = requests.get(list_url)
    data = list_response.json()
    cid_list = [item['chapter_id'] for item in data['data']['chapter']['chapterInfo']]
    print(cid_list)

    print("开始并发爬取 ")

    async with aiohttp.ClientSession() as session:
        tasks = [danzhang(session, book_id, cid) for cid in cid_list]
        results = await asyncio.gather(*tasks)

    results = [r for r in results if r is not None]

    # 按章节ID排序
    results.sort(key=lambda x: int(x['cid']))

    # 一次性写入
    with open(f'{书名}.txt', 'a', encoding='utf-8') as f:
        for chapter in results:
            f.write(f"{chapter['title']}\n\n　　")
            f.write(f"{chapter['content']}\n\n")

    print(f"完成第{i}个50章！")


async def main():
    list_url = r'https://boxnovel.baidu.com/boxnovel/wiseapi/chapterList?bookid=' + book_id + '&pageNum=1&order=asc&site='
    list_response = requests.get(list_url)
    data = list_response.json()
    count = data['data']['chapter']['chapterCount'] // 50 + 1  # count就是最后目录表单，50章1个表单
    for i in range(1, count + 1):
        await _50danzhang(str(i))


if __name__ == '__main__':
    asyncio.run(main())
