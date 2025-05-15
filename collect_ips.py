import requests
from bs4 import BeautifulSoup
import re

def fetch_top_ips(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return {}

    table = soup.find('table')
    if not table:
        print("未找到表格，请检查页面结构。")
        return {}

    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    try:
        isp_idx = headers.index('线路名称')
        ip_idx = headers.index('优选地址')
    except ValueError:
        print("未找到必要的表头，请检查页面结构。")
        return {}

    top_ips = {}
    for row in table.find_all('tr')[1:]:  # 跳过表头
        cells = row.find_all('td')
        if len(cells) < max(isp_idx, ip_idx) + 1:
            continue
        isp = cells[isp_idx].get_text(strip=True)
        ip = cells[ip_idx].get_text(strip=True)
        if isp not in top_ips and re.match(r'\d+\.\d+\.\d+\.\d+', ip):
            top_ips[isp] = ip
        if len(top_ips) == 3:
            break

    if not top_ips:
        print("未找到任何 IP，请检查页面内容。")
    return top_ips

if __name__ == '__main__':
    url = 'https://monitor.gacjie.cn/page/cloudflare/ipv4.html'
    result = fetch_top_ips(url)
    if result:
        with open('ip.txt', 'w') as f:
            ips = list(result.values())
            for i, ip in enumerate(ips):
                if i < len(ips) - 1:
                    f.write(ip + '\n')
                else:
                    f.write(ip)
        print("IP 地址已保存到 ip.txt 文件中。")
    else:
        print("未能提取到 IP 地址。")
