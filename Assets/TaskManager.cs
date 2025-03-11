using System;
using UnityEngine;
using TMPro;

public class TaskManager : MonoBehaviour
{
    public TMP_Text referralCountText; // النص الذي يعرض عدد الإحالات
    private int referralCount = 0;

    // إعادة تعيين المهام
    public void ResetTasks()
    {
        referralCount = 0; // إعادة تعيين عدد الإحالات
        PlayerPrefs.SetInt("LoginDays", 0); // إعادة تعيين أيام تسجيل الدخول
        PlayerPrefs.SetString("LastLoginDate", DateTime.Now.ToString("yyyy-MM-dd")); // تعيين آخر تاريخ دخول لليوم الحالي

        referralCountText.text = $"{referralCount}"; // تحديث عدد الإحالات
        Debug.Log("Tasks have been reset.");
    }

    // تحديث عدد الإحالات
    public void UpdateReferralCount(int count)
    {
        referralCount += count;
        referralCountText.text = $"{referralCount}"; // تحديث النص
    }
}
