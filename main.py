import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

# --- الإعدادات ---
BASE_URL = "https://rewayat.club/novel/you-are-running-30000-simulations-a-day-trying-to-stay-healthy-or-what/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_extraction(num):
    """وظيفة لاختبار هل يستطيع الكود قراءة الفصل أم لا"""
    url = f"{BASE_URL}{num}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # محاولة استخراج العنوان
            subtitle_tag = soup.find("div", class_="v-card__subtitle") or soup.find("h1")
            title = subtitle_tag.get_text(strip=True) if subtitle_tag else "لم يتم العثور على عنوان"
            
            # محاولة استخراج النصوص
            paragraphs = soup.find_all('p')
            clean_text = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 25]
            
            if clean_text:
                return {
                    'status': 'نجاح ✅',
                    'chapter': num,
                    'title': title,
                    'content_preview': clean_text[0][:100] + "...", 
                    'paragraphs_found': len(clean_text)
                }
            else:
                return {'status': 'فشل ❌', 'chapter': num, 'reason': 'لم يجد نصوص داخل وسوم p'}
        else:
            return {'status': 'فشل ❌', 'chapter': num, 'reason': f'HTTP Error {response.status_code}'}
    except Exception as e:
        return {'status': 'فشل ❌', 'chapter': num, 'reason': str(e)}

@app.route('/')
def home():
    return """
    <h1>أداة فحص سحب الروايات ⚡</h1>
    <p>اضغط على الزر أدناه لفحص أول 3 فصول والتأكد من أن السيرفر يستطيع القراءة من الموقع.</p>
    <a href="/test"><button style="padding:10px 20px; font-size:16px; cursor:pointer;">ابدأ الفحص الآن</button></a>
    """

@app.route('/test')
def run_test():
    results = []
    # فحص 3 فصول فقط للتجربة السريعة
    for i in range(1, 4):
        res = check_extraction(i)
        results.append(res)
        time.sleep(1)
        
    return jsonify({
        'info': 'نتائج اختبار السحب المباشر',
        'results': results
    })

if __name__ == "__main__":
    # هذا السطر مهم جداً لـ Railway
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
