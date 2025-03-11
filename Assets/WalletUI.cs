using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Threading.Tasks;

public class WalletUI : MonoBehaviour
{
    [Header("UI Elements")]
    public Button connectButton; // زر الاتصال بالمحفظة
    public TMP_Text connectButtonText; // النص داخل زر الاتصال
    public Button disconnectButton; // زر قطع الاتصال (أيقونة)
    public TMP_Text statusText; // النص الذي يعرض "Active" أو "Inactive"
    public TMP_Text balanceText; // النص الذي يعرض رصيد المحفظة

    private string walletAddress = ""; // عنوان المحفظة
    private bool isConnecting = false; // حالة الاتصال
    private decimal walletBalance = 0; // رصيد المحفظة

    void Start()
    {
        // تحميل عنوان المحفظة من PlayerPrefs (إذا كان موجودًا)
        walletAddress = PlayerPrefs.GetString("WalletAddress", "");

        // تحديث الواجهة بناءً على حالة الاتصال
        UpdateUI();

        // ربط الأزرار بالوظائف
        connectButton.onClick.AddListener(OnConnectButtonClicked);
        disconnectButton.onClick.AddListener(OnDisconnectButtonClicked);
    }

    void UpdateUI()
    {
        if (connectButtonText == null || statusText == null || disconnectButton == null || balanceText == null)
        {
            Debug.LogError("UI elements are not assigned in the Inspector.");
            return;
        }

        if (string.IsNullOrEmpty(walletAddress))
        {
            // إذا لم يكن هناك اتصال
            connectButtonText.text = "Connect Wallet"; // النص الافتراضي
            statusText.text = "Inactive"; // حالة غير متصلة
            disconnectButton.gameObject.SetActive(false); // إخفاء زر قطع الاتصال
            balanceText.text = "0.0000"; // عرض الرصيد الافتراضي
        }
        else
        {
            // إذا كان هناك اتصال
            connectButtonText.text = walletAddress; // عرض عنوان المحفظة
            statusText.text = "Active"; // حالة متصلة
            disconnectButton.gameObject.SetActive(true); // إظهار زر قطع الاتصال
            balanceText.text = $"{walletBalance.ToString("0.0000")}"; // عرض الرصيد الحالي
        }
    }

    private async void OnConnectButtonClicked()
    {
        if (isConnecting)
            return; // إذا كان الاتصال جارياً بالفعل، لا تفعل شيئاً

        isConnecting = true; // تعيين حالة الاتصال إلى قيد التنفيذ

        // عرض "Connecting..." أثناء محاولة الاتصال
        if (connectButtonText != null)
            connectButtonText.text = "Connecting...";

        // الاتصال الفعلي بمحفظة Telegram باستخدام TonConnect
        bool isConnected = await ConnectToTelegramWalletAsync();

        if (isConnected)
        {
            // إذا تم الاتصال بنجاح
            PlayerPrefs.SetString("WalletAddress", walletAddress); // حفظ العنوان

            // جلب رصيد المحفظة
            walletBalance = await GetWalletBalanceAsync();
        }
        else
        {
            // إذا فشل الاتصال
            walletAddress = ""; // مسح العنوان
            walletBalance = 0; // إعادة تعيين الرصيد
            Debug.LogWarning("Failed to connect to wallet.");
            if (connectButtonText != null)
                connectButtonText.text = "Connect Wallet"; // إعادة النص الافتراضي
        }

        // تحديث واجهة المستخدم
        isConnecting = false;
        UpdateUI();
    }

    private void OnDisconnectButtonClicked()
    {
        // فصل الاتصال
        walletAddress = "";
        walletBalance = 0; // إعادة تعيين الرصيد
        PlayerPrefs.DeleteKey("WalletAddress"); // حذف العنوان من التخزين

        // تسجيل العملية في الـ Console
        Debug.Log("Wallet disconnected.");

        // تحديث واجهة المستخدم
        UpdateUI();
    }

    private async Task<bool> ConnectToTelegramWalletAsync()
    {
        try
        {
            // **المنطق الفعلي للاتصال بمحفظة Telegram عبر TonConnect**
            // استخدام API مكتبة TonConnect لفتح واجهة المحفظة داخل Telegram

            // محاكاة اتصال غير متزامن (مثل انتظار رد من الخادم)
            await Task.Delay(1000); // انتظار لمدة ثانية واحدة (لأغراض الاختبار)

            // في هذه الخطوة سنقوم بمحاكاة الاتصال باستخدام API خاص بـ Telegram فقط

            // الاتصال الفعلي باستخدام TonConnect (يرجى استبدال هذا بالكود الفعلي)
            // هنا نعتبر أنه تم الاتصال بنجاح
            walletAddress = "UQC...Wyx"; // هذه هي المحفظة المتصلة (ضع العنوان الفعلي هنا)

            Debug.Log($"Wallet connected: {walletAddress}");
            return true; // تم الاتصال بنجاح
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Error while connecting to wallet: {ex.Message}");
            return false; // فشل الاتصال بسبب خطأ
        }
    }

    private async Task<decimal> GetWalletBalanceAsync()
    {
        try
        {
            // **المنطق الفعلي لجلب رصيد المحفظة**
            // استخدام API مكتبة TonConnect أو أي API آخر للحصول على الرصيد

            // محاكاة اتصال غير متزامن (مثل انتظار رد من الخادم)
            await Task.Delay(1000); // انتظار لمدة ثانية واحدة (لأغراض الاختبار)

            // هنا نعتبر أن الرصيد تم جلبها بنجاح
            decimal balance = 100.5m; // هذا هو الرصيد المحاكى (ضع الرصيد الفعلي هنا)

            Debug.Log($"Wallet balance: {balance} TON");
            return balance; // إرجاع الرصيد
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"Error while fetching wallet balance: {ex.Message}");
            return 0; // إرجاع 0 في حالة الخطأ
        }
    }

    private void OnDestroy()
    {
        // تنظيف الذاكرة وإلغاء أي عمليات غير متزامنة
        connectButton.onClick.RemoveListener(OnConnectButtonClicked);
        disconnectButton.onClick.RemoveListener(OnDisconnectButtonClicked);
    }
}