import { TonConnect } from "@tonconnect/sdk";

// إنشاء كائن TonConnect
const tonConnect = new TonConnect();

// استدعاء المحفظة
tonConnect.connect().then(wallet => {
    console.log("Connected to wallet:", wallet);
}).catch(error => {
    console.error("Connection failed:", error);
});
