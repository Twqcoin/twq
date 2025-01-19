self.onmessage = function(event) {
    if (event.data === 'startMining') {
        console.log('Mining started...');
        // محاكاة لعملية التعدين (يمكنك استبدالها بكود تعدين حقيقي)
        let progress = 0;
        const miningInterval = setInterval(() => {
            progress += 10;
            console.log(`Mining progress: ${progress}%`);
            postMessage(progress);  // إرسال التقدم إلى الصفحة الرئيسية
            if (progress >= 100) {
                clearInterval(miningInterval);
                console.log('Mining complete');
                postMessage('MiningComplete');  // إرسال رسالة اكتمال التعدين
            }
        }, 1000);  // نفذ كل ثانية لمحاكاة التقدم
    }
};
