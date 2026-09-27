import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import joblib

# 1. إنشاء بيانات افتراضية محاكية لمصنع البلوك (في حال لم يجهز ملف صديقتكِ بعد)
np.random.seed(42)
n_samples = 500

pH = np.random.uniform(6.0, 11.0, n_samples)          # درجة الحموضة (المياه الكلسية عالية الـ pH)
turbidity = np.random.uniform(10.0, 300.0, n_samples)  # العكارة NTU
ec = np.random.uniform(200.0, 2500.0, n_samples)       # التوصيل الكهربائي uS/cm

# معادلة تحاك التلوث الكيميائي المعقد (COD) من المدخلات الفيزيائية السريعة
cod = (pH * 12.5) + (turbidity * 0.45) + (ec * 0.08) + np.random.normal(0, 10, n_samples)

data = pd.DataFrame({'pH': pH, 'Turbidity': turbidity, 'EC': ec, 'COD': cod})

# 2. تقسيم البيانات إلى ميزات (Features) وهدف (Target)
X = data[['pH', 'Turbidity', 'EC']]
y = data['COD']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. تدريب نموذج الذكاء الاصطناعي (Random Forest)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 4. تقييم دقة النموذج (R^2 Score)
predictions = model.predict(X_test)
score = r2_score(y_test, predictions)

print(f"--- تم تدريب النموذج بنجاح ---")
print(f"دقة التنبؤ بالـ COD هي: {score * 100:.2f}%")

# 5. حفظ العقل المتعلم في ملف خارجي
joblib.dump(model, 'model.pkl')
print("تم حفظ النموذج باسم: model.pkl")