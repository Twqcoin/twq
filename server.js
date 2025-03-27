const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();

// اسمح لتطبيقك بالاتصال بهذا الخادم
app.use(cors({ 
  origin: ['https://minqx.onrender.com'] 
}));

// اتصل بقاعدة البيانات
mongoose.connect('mongodb://username:password@dpg-xxxxx-a.oregon-postgres.render.com:5432/dbname', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('تم الاتصال بقاعدة البيانات بنجاح'))
.catch(err => console.error('خطأ في الاتصال:', err));

// مسار بسيط لاختبار الخادم
app.get('/api/test', (req, res) => {
  res.json({ message: 'الخادم يعمل!' });
});

const PORT = 5000;
app.listen(PORT, () => {
  console.log(`الخادم يعمل على الرابط http://localhost:${PORT}`);
});
