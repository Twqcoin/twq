self.onmessage = function(event) {
    if (event.data === 'startMining') {
        console.log('Mining started...');
        // نفذ عملية التعدين هنا
        // على سبيل المثال، عملية محاكاة للتعدين
        let progress = 0;
        const miningInterval = setInterval(() => {
            progress += 10;
            console.log(`Mining progress: ${progress}%`);
            postMessage(progress);  // إرسال التقدم إلى الكونسول
            
            if (progress >= 100) {
                clearInterval(miningInterval);
                console.log('Mining complete');
                postMessage('MiningComplete');  // إرسال رسالة اكتمال التعدين
            }
        }, 1000);  // قم بتكرار كل ثانية لمحاكاة التقدم
    }
};
