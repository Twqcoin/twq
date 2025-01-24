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

    private string walletAddress = ""; // عنوان المحفظة
    private bool isConnecting = false; // حالة الاتصال

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
        if (string.IsNullOrEmpty(walletAddress))
        {
            // إذا لم يكن هناك اتصال
            connectButtonText.text = "Connect Wallet"; // النص الافتراضي
            statusText.text = "Inactive"; // حالة غير متصلة
            disconnectButton.gameObject.SetActive(false); // إخفاء زر قطع الاتصال
        }
        else
        {
            // إذا كان هناك اتصال
            connectButtonText.text = walletAddress; // عرض عنوان المحفظة
            statusText.text = "Active"; // حالة متصلة
            disconnectButton.gameObject.SetActive(true); // إظهار زر قطع الاتصال
        }
    }

    private async void OnConnectButtonClicked()
    {
        if (isConnecting)
            return; // إذا كان الاتصال جارياً بالفعل، لا تفعل شيئاً

        isConnecting = true; // تعيين حالة الاتصال إلى قيد التنفيذ

        // عرض "Connecting..." أثناء محاولة الاتصال
        connectButtonText.text = "Connecting...";

        // الاتصال الفعلي بمحفظة Telegram باستخدام TonConnect
        bool isConnected = await ConnectToTelegramWallet();

        if (isConnected)
        {
            // إذا تم الاتصال بنجاح
            PlayerPrefs.SetString("WalletAddress", walletAddress); // حفظ العنوان
        }
        else
        {
            // إذا فشل الاتصال
            walletAddress = ""; // مسح العنوان
            Debug.LogWarning("Failed to connect to wallet.");
        }

        // تحديث واجهة المستخدم
        isConnecting = false;
        UpdateUI();
    }

    private void OnDisconnectButtonClicked()
    {
        // فصل الاتصال
        walletAddress = "";
        PlayerPrefs.DeleteKey("WalletAddress"); // حذف العنوان من التخزين

        // تسجيل العملية في الـ Console
        Debug.Log("Wallet disconnected.");

        // تحديث واجهة المستخدم
        UpdateUI();
    }

    private async Task<bool> ConnectToTelegramWallet()
    {
        try
        {
            // **المنطق الفعلي للاتصال بمحفظة Telegram عبر TonConnect**
            // استخدام API مكتبة TonConnect لفتح واجهة المحفظة داخل Telegram

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
}
