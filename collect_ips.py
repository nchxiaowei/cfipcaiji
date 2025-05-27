import requests
from bs4 import BeautifulSoup
import re

# 获取 GitHub IP 列表
def fetch_github_ips():
    url = "https://raw.githubusercontent.com/ZhiXuanWang/cf-speed-dns/main/ipTop.html"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except requests.RequestException as e:
        print(f"[GitHub] 请求错误: {e}")
        return []

    match = re.search(r'((\d{1,3}\.){3}\d{1,3}(,\s*(\d{1,3}\.){3}\d{1,3})+)', html_content)
    if not match:
        print("[GitHub] 未找到 IP 列表")
        return []

    ip_block = match.group(1)
    ip_list = [ip.strip() for ip in ip_block.split(",")]
    return sorted(set(ip_list))  # 去重并排序

# 获取页面中的优选 IP
def fetch_top_ips(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"[页面] 请求错误: {e}")
        return []

    table = soup.find('table')
    if not table:
        print("[页面] 未找到表格")
        return []

    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    try:
        isp_idx = headers.index('线路名称')
        ip_idx = headers.index('优选地址')
    except ValueError:
        print("[页面] 表头错误")
        return []

    top_ips = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) <= max(isp_idx, ip_idx):
            continue
        ip = cells[ip_idx].get_text(strip=True)
        if re.match(r'\d+\.\d+\.\d+\.\d+', ip) and ip not in top_ips:
            top_ips.append(ip)
        if len(top_ips) == 3:
            break
    return top_ips

# 主函数
if __name__ == '__main__':
    github_ips = fetch_github_ips()
    page_ips = fetch_top_ips('https://monitor.gacjie.cn/page/cloudflare/ipv4.html')

    all_ips = github_ips + page_ips
    total_lines = ['mci.ircf.space'] + all_ips

    with open('ip.txt', 'w', encoding='utf-8') as f:
        for i, line in enumerate(total_lines):
            if i < len(total_lines) - 1:
                f.write(line + '\n')
            else:
                f.write(line)  # 最后一行不加换行

    print(f"✅ 写入完成，共 {len(total_lines)} 行，已无多余空行。")