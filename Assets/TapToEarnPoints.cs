using System;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public class Player
{
    public string playerName;
    public int playerPoints;
    public int totalReferralPoints;
}

public class TapToEarnPoints : MonoBehaviour
{
    public int points = 0;
    public int referralPoints = 10;
    public int referralBonusPercentage = 2;
    public int referralRewardPercentage = 20;

    public TMP_Text pointsText, timerText;
    public TMP_Text referralCountText;

    public Button[] loginButtons;
    public GameObject[] checkMarks;
    public Image[] buttonImages; // إضافة صورة الأزرار

    private Color normalColor = new Color(0, 1, 0);
    private Color highlightedColor = new Color(0, 1, 1);

    private int referralCount = 0;

    public PanelManager panelManager;

    public const string telegramInviteLink = "https://t.me/gulab_coin";
    public const string twitterInviteLink = "https://x.com/Gulab_coin?t=kp0IHdtS8V6Hm1BnnK1mpg&s=35";
    public const string youtubeInviteLink = "https://www.youtube.com/@Gulab_coin";

    public List<Player> players;

    // مصفوفة المكافآت اليومية
    private int[] dailyRewards = new int[30]
    {
        100, 100, 100, 100, 100, 200, 200, 200, 200, 200,
        300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
        500, 500, 500, 500, 500, 1000, 1000, 1000, 5000, 10000
    };

    private int loginDays;

    private void Start()
    {
        // ربط الأزرار بالدالة
        AssignButtonEvents();

        // إخفاء جميع checkMarks عند البداية
        foreach (var checkMark in checkMarks)
        {
            checkMark.SetActive(false); // إخفاء جميع العلامات
        }

        DateTime currentDate = DateTime.Now.Date;
        string lastLoginDateString = PlayerPrefs.GetString("LastLoginDate", "2000-01-01");

        DateTime lastLoginDate;
        if (!DateTime.TryParse(lastLoginDateString, out lastLoginDate))
        {
            lastLoginDate = DateTime.Parse("2000-01-01");
            Debug.LogWarning("Invalid or missing date in PlayerPrefs. Setting default value.");
        }

        loginDays = PlayerPrefs.GetInt("LoginDays", 0);

        // إذا كان التاريخ الحالي بعد آخر تسجيل دخول بيوم واحد أو أكثر
        if ((currentDate - lastLoginDate).TotalDays >= 1)
        {
            loginDays++;
            PlayerPrefs.SetInt("LoginDays", loginDays);
            PlayerPrefs.SetString("LastLoginDate", currentDate.ToString("yyyy-MM-dd"));
        }
        // إذا كان التاريخ المسجل هو اليوم الحالي، إعادة تعيين الأيام إلى اليوم الأول
        else if (lastLoginDate.Date == currentDate)
        {
            loginDays = 0; // إعادة تعيين الأيام إلى اليوم الأول
            PlayerPrefs.SetInt("LoginDays", loginDays);
            PlayerPrefs.SetString("LastLoginDate", currentDate.ToString("yyyy-MM-dd"));
        }

        // إعداد الأزرار والعلامات بناءً على عدد الأيام
        SetupLoginButtons(loginDays);
    }

    private void SetupLoginButtons(int loginDays)
    {
        for (int i = 0; i < loginButtons.Length; i++)
        {
            if (i < loginDays)
            {
                loginButtons[i].interactable = false;
                SetButtonColor(loginButtons[i], highlightedColor);
                checkMarks[i].SetActive(true); // إظهار العلامة للأيام السابقة
            }
            else if (i == loginDays)
            {
                loginButtons[i].interactable = true; // تمكين الزر الحالي فقط
                SetButtonColor(loginButtons[i], highlightedColor);
                checkMarks[i].SetActive(false); // إخفاء العلامة الحالية حتى يتم الضغط
            }
            else
            {
                loginButtons[i].interactable = false; // تعطيل الأزرار المستقبلية
                SetButtonColor(loginButtons[i], normalColor);
                checkMarks[i].SetActive(false); // إخفاء العلامات المستقبلية
            }
        }
    }

    public void OnLoginButtonClicked(int buttonIndex)
    {
        // تحقق من حدود المصفوفات
        if (buttonIndex >= 0 && buttonIndex < dailyRewards.Length && buttonIndex < checkMarks.Length && buttonIndex < loginButtons.Length)
        {
            int reward = dailyRewards[buttonIndex];
            points += reward;
            UpdatePointsText();
            Debug.Log($"Login Day {buttonIndex + 1}: Earned {reward} points.");

            // إضافة المكافأة لليوم الأول فقط إذا لم تكن قد أُضيفت
            if (buttonIndex == 0)
            {
                if (PlayerPrefs.GetInt("Day1RewardAdded", 0) == 0)
                {
                    PlayerPrefs.SetInt("Day1RewardAdded", 1); // حفظ أن المكافأة لليوم الأول قد أُضيفت
                    Debug.Log("Added reward for Day 1.");
                }
                else
                {
                    Debug.Log("Reward for Day 1 already added.");
                }
            }
            // إضافة المكافأة لليوم الثاني فقط إذا لم تكن قد أُضيفت
            else if (buttonIndex == 1 && loginDays > 1) // تأكد من مرور يومين
            {
                if (PlayerPrefs.GetInt("Day2RewardAdded", 0) == 0)
                {
                    points += dailyRewards[1]; // إضافة المكافأة لليوم الثاني
                    UpdatePointsText();
                    PlayerPrefs.SetInt("Day2RewardAdded", 1); // حفظ أن المكافأة لليوم الثاني قد أُضيفت
                    Debug.Log("Added reward for Day 2.");
                }
                else
                {
                    Debug.Log("Reward for Day 2 already added.");
                }
            }

            // إظهار العلامة عند تسجيل الدخول
            checkMarks[buttonIndex].SetActive(true);

            // تعطيل الزر الحالي
            loginButtons[buttonIndex].interactable = false;

            // إذا كان هذا الزر هو اليوم الحالي (تم الضغط عليه)، نغير لونه
            if (buttonIndex == loginDays)
            {
                SetButtonColor(loginButtons[buttonIndex], normalColor); // العودة للون الطبيعي
                buttonImages[buttonIndex].color = new Color(9, 9, 9, 1f); // تأثير الشفافية
                checkMarks[buttonIndex].SetActive(true); // إظهار العلامة
            }
        }
        else
        {
            Debug.LogError($"Invalid button index: {buttonIndex}. It is out of bounds.");
        }
    }

    private void SetButtonColor(Button button, Color color)
    {
        ColorBlock colorBlock = button.colors;
        colorBlock.normalColor = color;
        colorBlock.highlightedColor = color;
        colorBlock.pressedColor = color; // تأكد من أن اللون عند الضغط هو نفس اللون العادي
        button.colors = colorBlock;
    }

    private void UpdatePointsText()
    {
        if (pointsText != null)
        {
            pointsText.text = $"{points:n0}"; // عرض النقاط مع تنسيق العدد
        }
    }

    // ربط الأزرار بالدالة
    private void AssignButtonEvents()
    {
        for (int i = 0; i < loginButtons.Length; i++)
        {
            int index = i; // ضمان التمرير الصحيح للـ index
            loginButtons[i].onClick.AddListener(() => OnLoginButtonClicked(index));
        }
    }

    public void OpenTelegramLink() => Application.OpenURL(telegramInviteLink);

    public void OpenTwitterLink() => Application.OpenURL(twitterInviteLink);

    public void OpenYoutubeLink() => Application.OpenURL(youtubeInviteLink);
}
