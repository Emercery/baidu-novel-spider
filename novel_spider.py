import asyncio
import aiohttp
import requests
import json
import os
import time
import random
from Cryptodome.Cipher import AES
import base64
import urllib3
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================== 配置 ==================
BOOK_ID = '4357434716'
BOOK_NAME = 'test'
COOKIE = "xxx" # 填你自己的cookie！
HEADERS = {
    "Host": "novelapi.baidu.com",
    "x-bd-traceid": "3374ce9ceeda47c685d794b3b4fa629f",
    "x-sid": "H4sIAAAAAAAAAD1WUbJsMQRc0a1CCFnN7H8Xr2nnfc1UjgitNaZ+4/38z07K0Z/iz73v/axPPM6chNTDn3gvfu+9+jMNOYmj8rYVl/orMZyURfaNOven0k5UnW7fveP22rM5ST+FP69dFj+JrXFJ8mlT+108qALj2yep/JQmvJWSOSlc1/UseCvGM95qG7WSn74/vJ6CkwoLBB5yJ0Zhoqk+qVtWdbDnnnA4wi1h8EjsdRhm6v2l48Ef41vvl5OGh4w/l7Bf/R0J/J42VvhN+AulxdXTGetRl8bY7EU+2jb8TEt4clgHfLqLE6BnrSLzbRTFE7+1EDpvWUXGhHzL3pb6rE0+X+SAbicO4L+sTuOljlpVvb5vhec7Mj9AviPzPMQHDjaxM+TRV17NK7XUhU7yyMJt87xlWjHnvFNTlNZ9I7OuKYA3W47kFktqq31QZO8iWaMMvPLOB8Q7bsEqpPcm89zMPX3JY4uXTMkBUx3lS6gSbWzZYFdZkZAN8yp5blFuywcklX9RokJIkEs/buG3uawvgCD5kT7sPhcIsAs1+hPgQ/5niJL0gp7rXPAkKoOHkJNNNJ0cqYjLMjCCFuTbyRvMN3C9/Vg+5uJum5wssO5CABykL9a+QVJz83Zc0kUplH36GVUMFo/0vFcWXDnjSUTsDO5+zxnf7ypxB8HuqsAlB4/6V5KPuYy+i0WaIXpwyacDQBT/qzdk6MowCXuDl3pUERToxukSIfgzwVNWhtWKPvdAtczADHIRYUxJn+tZFiV1xlpV5nZ4btdRMyXtEnloEVmUGTSGdKwxW90+nsLzq8FJSw9tXLcPowFj4cA9GOtLoLsEK5YbpPuxH8/SG6ViP17E3GlZGKHLFlJGaLk8B5jDlneMAqG0QcTLKD/GT1fAnybxk45QhqGXbymJcESVJxdjYYlQbBgHSwkC4P2AoroB8b1lIV9TJZvKWi4v27WDfi4MOYFm54c/PWj+FFPMKCpoPGGTZo2xvbI9KfYQYrBY8gnrFqJsQKAb9Oy20++dTy0/CSoUGcZyu4A1ffay4VHEs6KNbth4ouEpqRZQ4NjvYyI0ZPoADc0NDqa6Z+ZxN6wzel0w4003ANuckdvXTkPFgn+xdcWKFOc9hUoTYPhekUn7hkXseHyH8xoqJey5mcCnE6D2venyzn7V9RwqJ7KugcN7jtdg50p3IW915/uDztw/+fXV20hTy78i3AHBlTuJv0+kIKJkVKv/ZOUIfWhs/z+ZTgqq/xeEN/2BkXqXPy0Gg8XhDGotvivuStmHA5lhfXYO3IhcSXiyoQ9/en6yfBDcnd5RtbZh3y6y/LYe/jJ6tlyF5s6kgvaANsP4XrZu80DePr6EAosPe6nlmcJri2TWzlE044rFLknQUt0RC14nZfb7s8sWJkDMhAYdOGNuP0GivdiRb/SjOTqCsQywMYo4gFhSAwEoaObOBrssSkPmuxpCC9qVQvw852Ozy7/ljq2KMXPYD7NYKOerSYvuk8v1ofeRJMSsVNwVVGyCj3iqn099V8XRjLTRXQHi/9aJhY0cPbsveDdfS7X3AjjQdGMgsOilM6ZRo8WgrFcCqNFobGyBsSXOXFJDtru/oEX5bO9cHFXZBcXOultrtLTO4Kvv5Ok3G3sF/AeNB5DxwAsAAA==",
    "x-sid-type": "1",
    "user-agent": "okhttp/3.12.12 SP-engine/3.51.0 Dalvik/2.1.0 (Linux; U; Android 12; DCO-AL00 Build/501caac.1) baiduboxapp/15.26.0.10 (Baidu; P1 12)",
    "content-type": "application/x-www-form-urlencoded",
    "content-length": "370",
    "accept-encoding": "gzip",
    "cookie": COOKIE
}

JSON_FILE = f"{BOOK_ID}.json"
TXT_FILE = f"{BOOK_NAME}.txt"

# 并发控制
CONCURRENT_LIMIT = 5  # 每批并发数
BATCH_SIZE = 20  # 每批处理章节数
FAIL_LIMIT = 10  # 连续失败触发等待的阈值
SLEEP_SECONDS = 15  # 触发后等待秒数
REQUEST_DELAY = (0.3,0.8)  # 每个请求前随机延迟


# ================== 工具函数 ==================
def decrypt_content(binary_data):
    base64_str = base64.b64encode(binary_data).decode('utf-8')
    key = b'D0CD8B760CE07BC3'
    iv = b'2011121211143000'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(base64_str))
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    return decrypted.decode('utf-8', errors='ignore')


# ================== 获取所有章节列表 ==================
def fetch_all_chapters(book_id):
    chapters = []
    page = 1
    while True:
        url = f'https://boxnovel.baidu.com/boxnovel/wiseapi/chapterList?bookid={book_id}&pageNum={page}&order=asc&site='
        try:
            resp = requests.get(url, verify=False, timeout=10)
            data = resp.json()
        except Exception as e:
            print(f"获取第{page}页失败: {e}")
            break
        if 'data' not in data or 'chapter' not in data['data'] or 'chapterInfo' not in data['data']['chapter']:
            break
        chapter_list = data['data']['chapter']['chapterInfo']
        if not chapter_list:
            break
        for item in chapter_list:
            chapters.append({
                'cid': str(item['chapter_id']),
                'title': item['chapter_title']
            })
        print(f"获取第{page}页，共{len(chapter_list)}章，累计{len(chapters)}章")
        page += 1
        if len(chapter_list) < 50:
            break
        time.sleep(random.uniform(0.2,0.4))
    return chapters


# ================== 数据持久化 ==================
def load_or_init_data(book_id):
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"加载状态文件 {JSON_FILE}，共 {len(data)} 章")
        for item in data:
            item.setdefault('content', '')
            item.setdefault('is_success', False)
        return data
    else:
        print("未找到状态文件，开始获取章节列表...")
        raw = fetch_all_chapters(book_id)
        data = [{'cid': ch['cid'], 'title': ch['title'], 'content': '', 'is_success': False} for ch in raw]
        save_json(data)
        print(f"初始化完成，共 {len(data)} 章")
        return data


def save_json(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存状态到 {JSON_FILE}")


# ================== 异步单章爬取 ==================
async def fetch_chapter(session, book_id, cid, semaphore):
    """返回 (cid, content, is_success)"""
    async with semaphore:
        url = "https://novelapi.baidu.com/searchbox?action=novel&type=content&is_close_individual_novel=0&nfonttype=0&service=bdbox&uid=gi20f_uS-u_daHudg825ilaWvalPuHaR_a2xi0uW2a8y9Hanpu2ER8WaA&from=1026250u&ua=YavjC_al2i4qywoUfpw1z4u32N_-aX8WoavjhxGHNqqqB&osname=baiduboxapp&osbranch=a0&branchname=baiduboxapp&pkgname=com.baidu.searchbox&p_sv=32&mps=1597730474&mpv=1&network=1_-1&cfrom=1026250u&ctv=2&cen=ua_uid&typeid=0&puid=gav4igaa28L6dqqqB&c3_aid=A00-WEBWGX3FXDDDYPGLGD3CAZMIZD4X3PBO-EYLAWMVQ&zid=975E42D44FDA5B9F2642937297834CE9DC39F62463A1&matrixstyle=0&ds_stc=0.4813&ds_lv=1&dt=0&andrst=0&cp_isbg=0&needmap=1&isnewtab_novel=0&istabbar_novel=0&newtab_version=2"
        post_data = {
            "data": f'{{"gid":{book_id},"read_status":0,"ctsrc":"","cid":"{book_id}|{cid}","dir":"0","fromaction":"viewcontent","tts_tf_fr":"ads_tingshu","autobuy":"0","need_buy_info":0,"nid":"","openreadertime":"1784565241","lastvisittime":"0"}}'
        }
        try:
            async with session.post(url, headers=HEADERS, data=post_data, timeout=15) as resp:
                result = await resp.json()
        except Exception as e:
            print(f"[{cid}] 请求异常: {e}")
            return (cid, '', False)

        try:
            dataset = result['data']['novel']['content']['dataset']
        except (KeyError, TypeError):
            print(f"[{cid}] 数据结构异常")
            return (cid, '', False)

        # 特殊状态：国家法规屏蔽
        if dataset.get('public_status') != 1:
            return (
            cid, '因部分内容不符合国家相关法律法规要求，本章节内容暂时无法阅读；小编正在努力修复，请耐心等待。', True)

        # 其他不可读状态（如付费、权限等）
        if dataset.get('status_code') == 501:
            print(f"[{cid}] 状态码501，爬取失败")
            return (cid, '', False)

        try:
            novel_url = dataset['content_url']
        except KeyError:
            print(f"[{cid}] 缺少content_url")
            return (cid, '', False)

        try:
            async with session.get(novel_url, timeout=15) as content_resp:
                encrypted = await content_resp.read()
                content = decrypt_content(encrypted)
                return (cid, content, True)
        except Exception as e:
            print(f"[{cid}] 正文获取失败: {e}")
            return (cid, '', False)


# ================== 主流程 ==================
async def main():
    # 加载或初始化数据
    data = load_or_init_data(BOOK_ID)
    pending = [item for item in data if not item['is_success']]

    if not pending:
        if all(item['is_success'] for item in data):
            generate_txt(data)
        print("所有章节已成功，无需爬取。")
        return

    total_pending = len(pending)
    print(f"需要爬取 {total_pending} 章，开始分批处理...")

    # 分批
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    consecutive_failures = 0
    success_count = sum(1 for item in data if item['is_success'])

    for batch_idx, batch in enumerate(batches, 1):
        print(f"\n===== 批次 {batch_idx}/{len(batches)}，共 {len(batch)} 章 =====")

        # 每批次创建独立的 Session
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
            tasks = [fetch_chapter(session, BOOK_ID, item['cid'], semaphore) for item in batch]

            # 使用 as_completed 实时处理结果
            for coro in asyncio.as_completed(tasks):
                time.sleep(random.uniform(*REQUEST_DELAY))
                try:
                    cid, content, is_ok = await coro
                except Exception as e:
                    print(f"任务异常: {e}")
                    consecutive_failures += 1
                    # 异常视为失败，但无法更新特定章节，留待下次处理
                    if consecutive_failures >= FAIL_LIMIT:
                        print(f"连续失败达到 {FAIL_LIMIT} 次，将在此批次结束后等待 {SLEEP_SECONDS} 秒")
                    continue

                # 更新数据
                for item in data:
                    if item['cid'] == cid:
                        item['content'] = content
                        item['is_success'] = is_ok
                        break

                if is_ok:
                    consecutive_failures = 0
                    success_count += 1
                    print(f"✓ 章节 {cid} 成功 (当前成功 {success_count}/{len(data)})")
                else:
                    consecutive_failures += 1
                    print(f"✗ 章节 {cid} 失败 (连续失败 {consecutive_failures})")
                    if consecutive_failures >= FAIL_LIMIT:
                        print(f"连续失败达到 {FAIL_LIMIT} 次，此批次结束后将等待 {SLEEP_SECONDS} 秒")
                        # 注意：我们不能立即中断其他任务，但可以在批次结束后等待
                        # 这里只做标记，批次结束统一处理

        # 批次结束，检查是否触发等待
        if consecutive_failures >= FAIL_LIMIT:
            print(f"连续失败达到阈值，静默 {SLEEP_SECONDS} 秒后继续...")
            await asyncio.sleep(SLEEP_SECONDS)
            consecutive_failures = 0  # 重置计数

        # 每批次结束后保存进度
        save_json(data)

    # 所有批次完成
    final_success = sum(1 for item in data if item['is_success'])
    final_fail = len(data) - final_success
    print(f"\n========== 爬取结束 ==========")
    print(f"成功: {final_success} 章")
    print(f"未成功: {final_fail} 章")

    if final_fail == 0:
        generate_txt(data)
        print("所有章节全部成功，TXT 文件已生成。")
    else:
        print(f"仍有 {final_fail} 章未成功，可再次运行程序继续爬取。")


def generate_txt(data):
    """按 cid 排序生成 TXT 小说"""
    sorted_data = sorted(data, key=lambda x: int(x['cid']))
    with open(TXT_FILE, 'w', encoding='utf-8') as f:
        for item in sorted_data:
            f.write(f"{item['title']}\n\n　　")
            f.write(f"{item['content']}\n\n")
    print(f"TXT文件已生成: {TXT_FILE}")
    os.remove(JSON_FILE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='百度小说爬虫（支持断点续爬）')
    parser.add_argument('--concurrent', type=int, default=10, help='每批并发数')
    parser.add_argument('--batch', type=int, default=20, help='每批处理章节数')
    parser.add_argument('--fail-limit', type=int, default=10, help='连续失败触发等待的阈值')
    parser.add_argument('--sleep-seconds', type=int, default=15, help='触发后等待秒数')
    parser.add_argument('--delay-min', type=float, default=0.1, help='请求延迟最小值')
    parser.add_argument('--delay-max', type=float, default=0.3, help='请求延迟最大值')
    # parser.add_argument('--BOOK_ID', type=str, default='4357297202', help='请求延迟最大值')
    # parser.add_argument('--BOOK_NAME', type=str, default='仙子，一日得道了解一下', help='请求延迟最大值')
    args = parser.parse_args()

    # 并发控制
    CONCURRENT_LIMIT = args.concurrent  # 每批并发数
    BATCH_SIZE = args.batch  # 每批处理章节数
    FAIL_LIMIT = args.fail_limit  # 连续失败触发等待的阈值
    SLEEP_SECONDS = args.sleep_seconds  # 触发后等待秒数
    REQUEST_DELAY = (args.delay_min, args.delay_max)  # 每个请求前随机延迟
    # BOOK_ID = args.BOOK_ID
    # BOOK_NAME = args.BOOK_NAME

    JSON_FILE = f"{BOOK_ID}.json"
    TXT_FILE = f"{BOOK_NAME}.txt"

    success = asyncio.run(main())
    exit(0 if success else 1)
