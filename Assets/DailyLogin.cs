using System;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class DailyLogin : MonoBehaviour
{
    [Header("UI Elements")]
    public Button[] loginButtons; // أزرار تسجيل الدخول
    public GameObject[] checkMarks; // علامات التأشير
    public TMP_Text pointsText; // نص النقاط

    [Header("Settings")]
    public Color activeButtonColor = Color.green; // لون الزر النشط
    public int[] dailyRewards = new int[30]; // المكافآت اليومية
    public int resetThresholdHours = 24; // فترة السماح لإعادة التعيين (بالساعات)

    private int loginDays = 0; // عدد أيام تسجيل الدخول
    private DateTime lastLoginDate; // تاريخ آخر تسجيل دخول

    void Start()
    {
        LoadData(); // تحميل البيانات المحفوظة
        AutoLogin(); // تسجيل الدخول التلقائي إذا مر يوم كامل
        UpdateUI(); // تحديث الواجهة
    }

    private void LoadData()
    {
        // تحميل عدد أيام تسجيل الدخول
        loginDays = PlayerPrefs.GetInt("LoginDays", 0);

        // تحميل تاريخ آخر تسجيل دخول
        string lastLoginDateString = PlayerPrefs.GetString("LastLoginDate", "");
        if (!string.IsNullOrEmpty(lastLoginDateString))
        {
            lastLoginDate = DateTime.Parse(lastLoginDateString);
        }
        else
        {
            lastLoginDate = DateTime.MinValue; // إذا لم يكن هناك تاريخ محفوظ
        }
    }

    private void AutoLogin()
    {
        DateTime currentDate = DateTime.Today;

        // التحقق من مرور يوم كامل منذ آخر تسجيل دخول
        if (currentDate > lastLoginDate)
        {
            TimeSpan difference = currentDate - lastLoginDate;

            // إذا كانت الفترة أكبر من فترة السماح، يتم إعادة تعيين الأيام
            if (difference.TotalHours > resetThresholdHours)
            {
                ResetData(); // إعادة تعيين الأيام
                Debug.Log("Reset days due to inactivity.");
            }
            else if (difference.Days >= 1)
            {
                // تسجيل الدخول التلقائي
                loginDays++;
                lastLoginDate = currentDate;

                // إضافة النقاط تلقائيًا
                int rewardIndex = (loginDays - 1) % dailyRewards.Length; // حساب المكافأة
                PointsManager.Instance.AddPoints(dailyRewards[rewardIndex]); // إضافة النقاط

                // حفظ البيانات
                PlayerPrefs.SetInt("LoginDays", loginDays);
                PlayerPrefs.SetString("LastLoginDate", lastLoginDate.ToString("yyyy-MM-dd"));
                PlayerPrefs.Save();

                Debug.Log($"Auto login for day {loginDays}, earned {dailyRewards[rewardIndex]} points.");
            }
        }
        else
        {
            Debug.Log("No new day since last login.");
        }
    }

    private void UpdateUI()
    {
        DateTime currentDate = DateTime.Today;

        for (int i = 0; i < loginButtons.Length; i++)
        {
            if (i < loginDays)
            {
                // تعطيل الزر وإظهار علامة التأشير إذا تم تسجيل الدخول في هذا اليوم
                loginButtons[i].interactable = false;
                checkMarks[i].SetActive(true);
                ResetButtonColor(loginButtons[i]);
            }
            else if (i == loginDays)
            {
                // تفعيل الزر إذا مر يوم كامل منذ آخر تسجيل دخول
                if (currentDate > lastLoginDate)
                {
                    loginButtons[i].interactable = true;
                    SetButtonColor(loginButtons[i], activeButtonColor);
                    checkMarks[i].SetActive(false);
                }
                else
                {
                    loginButtons[i].interactable = false;
                    checkMarks[i].SetActive(false);
                    ResetButtonColor(loginButtons[i]);
                }
            }
            else
            {
                // تعطيل الزر وإخفاء علامة التأشير للأيام المستقبلية
                loginButtons[i].interactable = false;
                checkMarks[i].SetActive(false);
                ResetButtonColor(loginButtons[i]);
            }
        }

        // تحديث نص النقاط عبر PointsManager
        if (pointsText != null && PointsManager.Instance != null)
        {
            pointsText.text = $"{PointsManager.Instance.GetTotalPoints():n0}";
        }
        else
        {
            Debug.LogError("PointsManager.Instance or pointsText is not assigned!");
        }
    }

    public void OnLoginButtonClicked(int buttonIndex)
    {
        if (buttonIndex >= 0 && buttonIndex < loginButtons.Length && buttonIndex == loginDays)
        {
            DateTime currentDate = DateTime.Today;

            // التأكد من عدم تسجيل الدخول مرتين في نفس اليوم
            if (currentDate <= lastLoginDate)
            {
                Debug.Log("Cannot login again today.");
                return;
            }

            // حساب المكافأة اليومية
            int rewardIndex = loginDays % dailyRewards.Length;
            PointsManager.Instance.AddPoints(dailyRewards[rewardIndex]); // إضافة النقاط

            checkMarks[buttonIndex].SetActive(true);
            loginButtons[buttonIndex].interactable = false;
            ResetButtonColor(loginButtons[buttonIndex]);

            // زيادة عدد أيام تسجيل الدخول
            loginDays++;
            lastLoginDate = currentDate;
            PlayerPrefs.SetInt("LoginDays", loginDays);
            PlayerPrefs.SetString("LastLoginDate", lastLoginDate.ToString("yyyy-MM-dd"));
            PlayerPrefs.Save(); // حفظ البيانات

            UpdateUI(); // تحديث الواجهة
            Debug.Log($"Logged in for day {loginDays}, earned {dailyRewards[rewardIndex]} points.");
        }
    }

    public void ResetData()
    {
        // إعادة تعيين البيانات المحفوظة
        PlayerPrefs.DeleteKey("LoginDays");
        PlayerPrefs.DeleteKey("LastLoginDate");
        loginDays = 0;
        lastLoginDate = DateTime.MinValue;
        UpdateUI(); // تحديث الواجهة
        Debug.Log("Data reset.");
    }

    private void SetButtonColor(Button button, Color color)
    {
        // تغيير لون الزر
        Image buttonImage = button.GetComponent<Image>();
        if (buttonImage != null)
        {
            buttonImage.color = color;
        }
    }

    private void ResetButtonColor(Button button)
    {
        // إعادة تعيين لون الزر إلى اللون الأبيض
        Image buttonImage = button.GetComponent<Image>();
        if (buttonImage != null)
        {
            buttonImage.color = Color.white;
        }
    }
}