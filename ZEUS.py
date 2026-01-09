import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

# --- الإعدادات (نفس منطق الكود البسيط الذي أرسلته) ---
BASE_URL = "https://rewayat.club/novel/you-are-running-30000-simulations-a-day-trying-to-stay-healthy-or-what/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_extraction(num):
    """وظيفة لاختبار هل يستطيع الكود قراءة الفصل أم لا"""
    url = f"{BASE_URL}{num}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # محاولة استخراج العنوان
            subtitle_tag = soup.find("div", class_="v-card__subtitle") or soup.find("h1")
            title = subtitle_tag.get_text(strip=True) if subtitle_tag else "لم يتم العثور على عنوان"
            
            # محاولة استخراج النصوص (الوسوم العامة p)
            paragraphs = soup.find_all('p')
            clean_text = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 25]
            
            if clean_text:
                return {
                    'status': 'نجاح ✅',
                    'chapter': num,
                    'title': title,
                    'content_preview': clean_text[0][:100] + "...", # عرض أول 100 حرف فقط للتأكد
                    'paragraphs_count': len(clean_text)
                }
            else:
                return {'status': 'فشل ❌', 'chapter': num, 'reason': 'لم يجد أي نصوص داخل وسوم p'}
        else:
            return {'status': 'فشل ❌', 'chapter': num, 'reason': f'HTTP Error {response.status_code}'}
    except Exception as e:
        return {'status': 'فشل ❌', 'chapter': num, 'reason': str(e)}

@app.route('/')
def home():
    return "<h1>مرحباً بك في أداة فحص السحب</h1><p>أضف <b>/test</b> لنهاية الرابط لبدء فحص أول 5 فصول.</p>"

@app.route('/test')
def run_test():
    # سنقوم باختبار أول 5 فصول فقط للتأكد من أن السحب يعمل
    results = []
    for i in range(1, 6):
        print(f"جاري فحص الفصل {i}...")
        res = check_extraction(i)
        results.append(res)
        time.sleep(1) # تأخير لتجنب الحظر
        
    return jsonify({
        'description': 'نتائج اختبار سحب أول 5 فصول',
        'results': results
    })

if __name__ == "__main__":
    # تشغيل التطبيق على المنفذ الذي يطلبه Railway
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
