// تحميل الـ Web Worker
var miningWorker = new Worker('{{ url_for('static', filename='worker.js') }}'); // تأكد من المسار الصحيح

// التعامل مع الرسائل الواردة من الـ Web Worker
miningWorker.onmessage = function(event) {
    console.log("Received message from worker:", event.data);
    
    // هنا يمكنك إضافة المزيد من العمليات حسب الحاجة، مثل:
    // إذا كانت الرسالة 'MiningComplete'، يمكن إظهار إشعار في اللعبة
    if (event.data === 'MiningComplete') {
        unityInstance.SendMessage('GameController', 'OnMiningComplete');
    } else {
        unityInstance.SendMessage('GameController', 'OnMiningProgressUpdated', event.data);
    }
};

// التعامل مع الأخطاء في الـ Web Worker
miningWorker.onerror = function(error) {
    console.error("Error in worker:", error.message);
    // يمكنك إضافة مزيد من التعامل مع الأخطاء مثل إظهار إشعار للمستخدم
};

// إرسال رسالة إلى الـ Worker لبدء التعدين
miningWorker.postMessage('startMining');

// تتبع عمل الـ Web Worker عبر الكونسول
console.log("Web Worker initialized and message sent to start mining.");

// عند الخروج أو تحديث الصفحة، تأكد من إنهاء الـ Worker
window.onbeforeunload = function() {
    localStorage.setItem('isMining', 'false');
    if (miningWorker) {
        miningWorker.terminate();
        console.log("Web Worker terminated due to page unload.");
    }
};
