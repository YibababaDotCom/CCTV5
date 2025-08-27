import requests
import re
import sys
import os

def test_m3u8_url(url):
    """
    测试一个m3u8链接是否有效。
    """
    try:
        # 使用 HEAD 请求来快速验证链接，不下载整个文件
        response = requests.head(url, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"URL {url} is not valid: {e}")
        return False

def extract_urls(input_url):
    """
    从指定URL下载文件并提取CCTV5的m3u8链接。
    """
    try:
        response = requests.get(input_url, timeout=10)
        response.raise_for_status()
        content = response.text

        # 优化后的正则表达式，用于匹配所有 "频道名,链接" 的组合
        # 它会精确地从一长串字符串中识别出每一个独立的条目
        pattern = re.compile(r'(CCTV\d\+?),((?:http|https|rtsp|rtmp):\/\/[^\s,]+?\.m3u8)', re.IGNORECASE)
        found_matches = pattern.findall(content)

        cctv5_urls = []
        for match in found_matches:
            # match 现在是一个包含 (频道名, 链接) 的元组
            channel_name, url = match
            if "CCTV5" in channel_name.upper():
                cctv5_urls.append(url.strip()) # strip() 移除可能的空白

        return cctv5_urls
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file from {input_url}: {e}", file=sys.stderr)
        return []

def main(input_urls, output_file):
    """
    从多个URL提取CCTV5的m3u8链接，测试并保存到文件。
    """
    all_urls = []
    for url in input_urls:
        all_urls.extend(extract_urls(url))

    valid_urls = []
    # 使用 set 去重
    for url in set(all_urls):
        if test_m3u8_url(url):
            valid_urls.append(url)

    # 将有效的链接写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in valid_urls:
            f.write(f"CCTV5,{url}\n")
    
    print(f"Successfully saved {len(valid_urls)} valid CCTV5 URLs to {output_file}")
    
    if not valid_urls:
        # 如果没有找到任何有效链接，则不创建文件，并让工作流失败
        print("No valid CCTV5 links were found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_and_test.py <output_file> <input_url_1> <input_url_2> ...", file=sys.stderr)
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_urls = sys.argv[2:]
    main(input_urls, output_file)
