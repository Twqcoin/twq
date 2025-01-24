using UnityEngine;
using TMPro;

public class ReferralSystem : MonoBehaviour
{
    [Header("Referral Settings")]
    public string baseReferralURL = "https://yourgame.com/referral?playerID="; // رابط الإحالة الأساسي

    private string playerID; // معرف اللاعب

    void Start()
    {
        // استرجاع أو إنشاء معرف اللاعب
        playerID = PlayerPrefs.GetString("PlayerID", GeneratePlayerID());
        PlayerPrefs.SetString("PlayerID", playerID);
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

        // مشاركة الرابط (تحتاج إلى مكتبة إضافية مثل NativeShare إذا كنت تستهدف الأجهزة المحمولة)
        Debug.Log("Share referral link: " + referralLink);
        // يمكن إضافة مكتبات أو استخدام API خاص بالتطبيق هنا.
    }
}
