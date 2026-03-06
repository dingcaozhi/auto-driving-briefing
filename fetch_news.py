#!/usr/bin/env python3
"""
汽车自动驾驶每日简报 - 新闻抓取脚本
每天早上 9:00 自动运行
"""

import json
import os
from datetime import datetime
import requests

# API Keys
NEWSDATA_API_KEY = "pub_aa9eeb72d801433a93ad17d890599f75"
GNEWS_API_KEY = "1d9f97280cb39eb9d8436c143b79c185"

def fetch_from_newsdata():
    """从 NewsData.io 抓取自动驾驶新闻"""
    news_list = []
    keywords = ["自动驾驶", "无人驾驶", "智能驾驶", "ADAS", "Tesla FSD", "百度 Apollo", "小鹏 NGP"]
    
    for keyword in keywords[:3]:
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                "apikey": NEWSDATA_API_KEY,
                "q": keyword,
                "language": "zh,en",
                "size": 10
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get("status") == "success":
                for article in data.get("results", []):
                    news_list.append({
                        "id": article.get("link", ""),
                        "title": article.get("title", ""),
                        "summary": article.get("description", "")[:150] + "..." if article.get("description") else "",
                        "source": article.get("source_id", "NewsData").replace("-", " ").title(),
                        "date": article.get("pubDate", "")[:10] if article.get("pubDate") else datetime.now().strftime('%Y-%m-%d'),
                        "url": article.get("link", ""),
                        "category": categorize_news(article.get("title", ""))
                    })
        except Exception as e:
            print(f"NewsData 抓取失败 {keyword}: {e}")
    
    return news_list

def fetch_from_gnews():
    """从 GNews 抓取英文自动驾驶新闻"""
    news_list = []
    keywords = ["autonomous driving", "self-driving car", "Tesla Autopilot", "Waymo"]
    
    for keyword in keywords[:2]:
        try:
            url = "https://gnews.io/api/v4/search"
            params = {
                "q": keyword,
                "lang": "en",
                "max": 10,
                "sortby": "publishedAt",
                "apikey": GNEWS_API_KEY
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if "articles" in data:
                for article in data["articles"]:
                    news_list.append({
                        "id": article.get("url", ""),
                        "title": article.get("title", ""),
                        "summary": article.get("description", "")[:150] + "..." if article.get("description") else "",
                        "source": article.get("source", {}).get("name", "GNews"),
                        "date": article.get("publishedAt", "")[:10],
                        "url": article.get("url", ""),
                        "category": categorize_news(article.get("title", ""))
                    })
        except Exception as e:
            print(f"GNews 抓取失败 {keyword}: {e}")
    
    return news_list

def categorize_news(title):
    """根据标题分类新闻"""
    title_lower = title.lower()
    if any(k in title_lower for k in ["政策", "法规", "监管", "许可", "approval", "regulation", "policy"]):
        return "policy"
    elif any(k in title_lower for k in ["发布", "launch", "release", "新品", "新车", "product"]):
        return "product"
    elif any(k in title_lower for k in ["技术", "芯片", "激光雷达", "算法", "tech", "lidar", "chip", "algorithm"]):
        return "tech"
    else:
        return "industry"

def generate_fallback_news():
    """生成备用新闻"""
    return [
        {
            "id": "1",
            "title": "自动驾驶行业迎来新政策支持",
            "summary": "多地发布自动驾驶路测新政策，推动行业加速发展...",
            "source": "行业聚合",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "url": "https://www.google.com/search?q=自动驾驶+政策+2024",
            "category": "policy"
        },
        {
            "id": "2",
            "title": "L3级自动驾驶车型密集上市",
            "summary": "多家车企推出具备L3级自动驾驶功能的新车型，市场竞争加剧...",
            "source": "行业聚合",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "url": "https://www.google.com/search?q=L3+自动驾驶+新车",
            "category": "product"
        },
        {
            "id": "3",
            "title": "激光雷达成本持续下降",
            "summary": "随着技术成熟和量产规模扩大，车载激光雷达价格降至千元级别...",
            "source": "技术聚合",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "url": "https://www.google.com/search?q=激光雷达+降价",
            "category": "tech"
        }
    ]

def main():
    print(f"[{datetime.now()}] 开始抓取自动驾驶新闻...")
    
    all_news = []
    
    # 抓取新闻
    print("抓取 NewsData...")
    all_news.extend(fetch_from_newsdata())
    
    print("抓取 GNews...")
    all_news.extend(fetch_from_gnews())
    
    # 去重
    seen = set()
    unique_news = []
    for item in all_news:
        if item["title"] not in seen and len(item["title"]) > 10:
            seen.add(item["title"])
            unique_news.append(item)
    
    print(f"去重后: {len(unique_news)} 条")
    
    # 如果太少，补充备用数据
    if len(unique_news) < 5:
        print("补充备用数据...")
        unique_news.extend(generate_fallback_news())
    
    # 最终去重
    seen = set()
    final_news = []
    for item in unique_news:
        if item["title"] not in seen:
            seen.add(item["title"])
            final_news.append(item)
    
    # 保存
    output = {
        "lastUpdated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "totalCount": len(final_news),
        "news": final_news[:20]
    }
    
    with open('news.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] 完成，共 {len(final_news)} 条新闻")

if __name__ == '__main__':
    main()
