const express = require('express');
const path = require('path');
const app = express();

// تحديد المسار لخدمة ملفات Build
app.use(express.static(path.join(__dirname, 'build')));

// صفحة البداية
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// التعامل مع باقي الملفات (مثل JavaScript, CSS, images)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'build', req.url));
});

// تشغيل الخادم على المنفذ 5000
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(Server is running on port ${PORT});
});