// 1. استيراد المكتبات
import { TonConnect } from '@tonconnect/sdk';
import { TonClient } from '@ton/ton';

// 2. تهيئة TON Connect للاتصال بالمحافظ
const connector = new TonConnect({
    manifestUrl: 'https://ton-connect.github.io/demo-dapp-with-react/tonconnect-manifest.json' // رابط مؤقت للتجربة
});

// 3. تهيئة عميل TON
const client = new TonClient({
    endpoint: 'https://toncenter.com/api/v2/jsonRPC' // شبكة TON الرئيسية
});

// 4. زر الاتصال بالمحفظة
document.getElementById('connectWallet').addEventListener('click', async () => {
    try {
        // فتح نافذة الاتصال بالمحفظة (مثل TonKeeper أو OpenMask)
        await connector.connect();
        
        // إذا نجح الاتصال
        const walletInfo = connector.account;
        document.getElementById('walletInfo').innerHTML = `
            <p>تم الاتصال بالمحفظة بنجاح!</p>
            <p>العنوان: ${walletInfo.address}</p>
        `;
        
        console.log("المحفظة المتصلة:", walletInfo);
    } catch (error) {
        console.error("خطأ في الاتصال:", error);
    }
});
