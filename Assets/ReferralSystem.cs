using UnityEngine;
using TMPro;
using UnityEngine.UI;

public class ReferralSystem : MonoBehaviour
{
    [Header("Referral Settings")]
    public string baseReferralURL = "https://yourgame.com/referral?playerID="; // رابط الإحالة الأساسي
    public decimal tonRewardPerReferral = 0.0001m; // مكافأة TON لكل إحالة ناجحة
    public decimal tonWithdrawalThreshold = 5.0m; // حد السحب (5 TON)

    [Header("UI Elements")]
    public Button copyButton; // زر نسخ الرابط
    public Button shareButton; // زر مشاركة الرابط
    public TMP_Text tonBalanceText; // نص لعرض رصيد TON
    public Button withdrawButton; // زر سحب الرصيد

    private string playerID; // معرف اللاعب
    private decimal tonBalance = 0; // رصيد TON الحالي

    void Start()
    {
        // استرجاع أو إنشاء معرف اللاعب
        playerID = PlayerPrefs.GetString("PlayerID", GeneratePlayerID());
        PlayerPrefs.SetString("PlayerID", playerID);

        // استرجاع رصيد TON من PlayerPrefs
        tonBalance = decimal.Parse(PlayerPrefs.GetString("TonBalance", "0"));

        // تحديث الواجهة
        UpdateUI();

        // ربط الأزرار بالوظائف
        if (copyButton != null)
            copyButton.onClick.AddListener(CopyReferralLink);
        if (shareButton != null)
            shareButton.onClick.AddListener(ShareReferralLink);
        if (withdrawButton != null)
            withdrawButton.onClick.AddListener(WithdrawTon);
    }

    /// <summary>
    /// توليد معرف فريد للاعب (UUID).
    /// </summary>
    private string GeneratePlayerID()
    {
        return System.Guid.NewGuid().ToString();
    }

    /// <summary>
    /// نسخ الرابط إلى الحافظة.
    /// </summary>
    public void CopyReferralLink()
    {
        string referralLink = baseReferralURL + playerID;
        GUIUtility.systemCopyBuffer = referralLink;
        Debug.Log("Referral link copied to clipboard: " + referralLink);
    }

    /// <summary>
    /// مشاركة الرابط عبر وسائل التواصل.
    /// </summary>
    public void ShareReferralLink()
    {
        string referralLink = baseReferralURL + playerID;

#if UNITY_ANDROID || UNITY_IOS
        new NativeShare()
            .SetText("Check out this game! Use my referral link: " + referralLink)
            .SetSubject("Join me in this awesome game!")
            .Share();
#endif

        Debug.Log("Share referral link: " + referralLink);
    }

    /// <summary>
    /// تحديث الواجهة.
    /// </summary>
    private void UpdateUI()
    {
        if (tonBalanceText != null)
            tonBalanceText.text = $"{tonBalance.ToString("0.0000")}"; // عرض الرصيد فقط

        // تفعيل أو تعطيل زر السحب بناءً على الرصيد
        if (withdrawButton != null)
            withdrawButton.interactable = tonBalance >= tonWithdrawalThreshold;
    }

    /// <summary>
    /// إضافة إحالة ناجحة إلى الرصيد.
    /// </summary>
    public void AddSuccessfulReferral()
    {
        // إضافة المكافأة إلى الرصيد الحالي
        tonBalance += tonRewardPerReferral;

        // حفظ الرصيد الجديد
        PlayerPrefs.SetString("TonBalance", tonBalance.ToString());

        Debug.Log($"TON reward granted: {tonRewardPerReferral.ToString("0.0000")} TON | New Balance: {tonBalance.ToString("0.0000")} TON");

        // تحديث الواجهة
        UpdateUI();
    }

    /// <summary>
    /// سحب الرصيد عند الوصول إلى الحد المطلوب.
    /// </summary>
    private void WithdrawTon()
    {
        if (tonBalance >= tonWithdrawalThreshold)
        {
            // هنا يمكنك إضافة الكود الخاص بسحب TON إلى محفظة اللاعب
            Debug.Log($"Withdrawing {tonBalance.ToString("0.0000")} TON...");

            // إعادة تعيين الرصيد بعد السحب
            tonBalance = 0;
            PlayerPrefs.SetString("TonBalance", tonBalance.ToString());

            // تحديث الواجهة
            UpdateUI();
        }
        else
        {
            Debug.Log($"You need at least {tonWithdrawalThreshold} TON to withdraw.");
        }
    }

    private void OnDestroy()
    {
        if (copyButton != null)
            copyButton.onClick.RemoveListener(CopyReferralLink);
        if (shareButton != null)
            shareButton.onClick.RemoveListener(ShareReferralLink);
        if (withdrawButton != null)
            withdrawButton.onClick.RemoveListener(WithdrawTon);
    }
}
