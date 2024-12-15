using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class TapToEarnPoints : MonoBehaviour
{
    public int points = 0; // النقاط الإجمالية للاعب
    public int miningPoints = 5; // النقاط المكتسبة من التعدين
    public int taskCompletionReward = 10; // النقاط المكتسبة من إتمام المهام
    public int referralPoints = 1; // النقاط المكتسبة من الإحالة
    public int referralBonusPercentage = 2; // 2% من نقاط المحال
    public TMP_Text pointsText, startButtonText, loginDaysText, walletText, timerText, miningProgressText;
    public TMP_Text referralCountText; // النص لعدد المدعوين
    public GameObject startButton;
    public GameObject taskCompletedIcon;

    private bool isMining = false;
    private float miningStartTime;
    private float miningProgress = 0.0000001f;
    private float miningDurationInSeconds = 21600f;

    private int loginDays = 0;

    public GameObject panel1;
    public GameObject earnPanel;
    public GameObject frensPanel;
    public GameObject walletPanel;
    public GameObject irdropPanel;
    public GameObject panelInvite;
    public GameObject backButton;

    public string telegramInviteLink = "https://t.me/twq_coin";
    public string twitterInviteLink = "https://x.com/Twq_coin?t=GCEYsN0o6ymexvRu9hUD6A&s=09";
    public string youtubeInviteLink = "https://www.youtube.com/@Twq_coinz";

    private DateTime firstLoginDate;
    private string walletAddress;

    private bool isTaskCompleted = false; // حالة إتمام المهمة

    public Slider pointsSlider;
    public Image sliderFillImage;

    public Image playerImage;
    public TMP_Text playerNameText;

    private string playerID; // معرّف فريد للاعب
    private string referralID; // معرّف اللاعب المحال

    private int totalPoints = 0; // النقاط الإجمالية المكتسبة من كل الأنشطة

    // لوحة ترتيب اللاعبين
    public GameObject leaderboardPanel; // اللوحة الخاصة بالترتيب
    public TMP_Text leaderboardText; // النص لعرض ترتيب اللاعبين

    private List<Player> players = new List<Player>(); // قائمة اللاعبين (اسم + نقاط)

    // هذا هيكل بيانات للاعبين
    [System.Serializable]
    public class Player
    {
        public string playerName;
        public int playerPoints;
    }

    // متغيرات الإحالات
    private int referralCount = 0; // عدد المدعوين

    // متغيرات لحفظ تقدم التعدين
    private float savedMiningStartTime;
    private bool savedIsMining;

    void Start()
    {
        playerID = PlayerPrefs.GetString("PlayerID", "");

        if (string.IsNullOrEmpty(playerID))
        {
            playerID = Guid.NewGuid().ToString();
            PlayerPrefs.SetString("PlayerID", playerID);
        }

        pointsSlider.value = 0f;  
        sliderFillImage.fillAmount = pointsSlider.value / 100f;

        ShowPanel1();
        ApplyDailyReward();
        LoadWalletAddress();
        ShowLoginDays();

        taskCompletedIcon.SetActive(false);

        // استرجاع عدد المدعوين من PlayerPrefs
        referralCount = PlayerPrefs.GetInt("ReferralCount", 0); 
        UpdateReferralCountText(); 

        UpdatePlayerInfo(Resources.Load<Sprite>("DefaultAvatar"), "Player1");

        leaderboardPanel.SetActive(false);

        // استعادة حالة التعدين إذا كانت موجودة
        savedMiningStartTime = PlayerPrefs.GetFloat("MiningStartTime", 0);
        savedIsMining = PlayerPrefs.GetInt("IsMining", 0) == 1; // تعديل هنا لاسترجاع الحالة كـ bool

        if (savedIsMining)
        {
            miningStartTime = savedMiningStartTime;
            isMining = true;
            StartCoroutine(MiningCountdown());
        }
    }

    // دالة لزيادة عدد المدعوين
    public void IncreaseReferralCount()
    {
        referralCount++;
        PlayerPrefs.SetInt("ReferralCount", referralCount); // تخزين العدد في PlayerPrefs
        UpdateReferralCountText(); // تحديث النص لعرض العدد الجديد
    }

    // دالة لتحديث النص الذي يعرض عدد المدعوين
    void UpdateReferralCountText()
    {
        referralCountText.text = $"Referrals: {referralCount}"; // عرض العدد
    }

    void ApplyDailyReward()
    {
        string todayDate = DateTime.Now.ToString("yyyy-MM-dd");

        if (!PlayerPrefs.HasKey("LastLoginDate") || PlayerPrefs.GetString("LastLoginDate") != todayDate)
        {
            PlayerPrefs.SetString("LastLoginDate", todayDate);
            AddPoints(miningPoints); // إضافة نقاط التعدين اليومية
        }

        if (!PlayerPrefs.HasKey("FirstLoginDate"))
        {
            firstLoginDate = DateTime.Now;
            PlayerPrefs.SetString("FirstLoginDate", firstLoginDate.ToString("yyyy-MM-dd"));
        }
        else
        {
            firstLoginDate = DateTime.Parse(PlayerPrefs.GetString("FirstLoginDate"));
        }

        loginDays = (DateTime.Now - firstLoginDate).Days + 1;
    }

    void ShowLoginDays()
    {
        loginDaysText.text = $"Daily {loginDays}";
        loginDaysText.gameObject.SetActive(true);
        pointsText.gameObject.SetActive(false);
        Invoke(nameof(HideLoginDaysAndShowPoints), 3f);
    }

    void HideLoginDaysAndShowPoints()
    {
        loginDaysText.gameObject.SetActive(false);
        pointsText.gameObject.SetActive(true);
        UpdatePointsText();
    }

    public void StartMining()
    {
        if (!isMining)
        {
            isMining = true;
            miningStartTime = Time.time; // تحديد الوقت الذي بدأ فيه التعدين
            StartCoroutine(MiningCountdown());
        }
    }

    private System.Collections.IEnumerator MiningCountdown()
    {
        while (isMining)
        {
            float miningElapsedTime = Time.time - miningStartTime;

            miningProgress = Mathf.Min(miningElapsedTime / miningDurationInSeconds, 1f);

            pointsSlider.value = miningProgress * 100f;

            miningProgressText.text = $"Mining: {miningProgress:0.000000}";

            float timeRemaining = miningDurationInSeconds - miningElapsedTime;
            TimeSpan timeSpan = TimeSpan.FromSeconds(timeRemaining);
            timerText.text = $"{timeSpan.Hours:D2}:{timeSpan.Minutes:D2}:{timeSpan.Seconds:D2}";

            if (miningElapsedTime >= miningDurationInSeconds)
            {
                isMining = false;
                startButtonText.text = "Claim";
            }

            yield return null;
        }
    }

    public void ClaimPoints()
    {
        if (startButtonText.text == "Claim")
        {
            // إضافة النقاط من التعدين
            totalPoints += miningPoints;

            // إضافة النقاط المكتسبة من المهام
            if (isTaskCompleted)
            {
                totalPoints += taskCompletionReward;
            }

            // إضافة النقاط المكتسبة من الإحالات
            if (!string.IsNullOrEmpty(referralID))
            {
                totalPoints += referralPoints; // النقاط الخاصة بالإحالة
            }

            // إضافة 2% من النقاط المكتسبة من المحال
            if (!string.IsNullOrEmpty(referralID))
            {
                totalPoints += Mathf.FloorToInt(referralPoints * referralBonusPercentage / 100f); // إضافة 2% من نقاط المحال
            }

            // تحديث النقاط الإجمالية
            points += totalPoints;

            // تحديث النصوص
            startButtonText.text = "Start"; // إعادة تعيين النص بعد استلام النقاط
            UpdatePointsText();

            // إضافة اللاعب الحالي إلى الترتيب
            AddPlayerToLeaderboard("Player" + playerID, points);

            // إعادة تعيين النقاط المكتسبة من الأنشطة
            totalPoints = 0;
        }
    }

    public void AddPoints(int amount)
    {
        points += amount;
        UpdatePointsText();
    }

    void UpdatePointsText()
    {
        pointsText.text = $"{points}";
    }

    public void CompleteTask()
    {
        // عند إتمام المهمة بنجاح، إضافة النقاط مباشرة إلى الـ points
        AddPoints(taskCompletionReward);
        taskCompletedIcon.SetActive(true); // إظهار علامة إتمام المهمة
    }

    public void ShowPanel1()
    {
        HideAllPanels();
        panel1.SetActive(true);
        backButton.SetActive(false);
    }

    public void ShowWallet()
    {
        HideAllPanels();
        walletPanel.SetActive(true);
        backButton.SetActive(true);
        walletText.text = string.IsNullOrEmpty(walletAddress) ? "Connect Wallet" : $"Wallet: {walletAddress}";
    }

    public void LinkWallet(string walletInput)
    {
        if (string.IsNullOrEmpty(walletInput))
        {
            Debug.Log("Wallet Address cannot be empty!");
            return;
        }

        walletAddress = walletInput;
        PlayerPrefs.SetString("WalletAddress", walletAddress);
        Debug.Log("Wallet Linked: " + walletAddress);
        ShowWallet();
    }

    void LoadWalletAddress()
    {
        walletAddress = PlayerPrefs.GetString("WalletAddress", "");
    }

    public void ShowEarn() { HideAllPanels(); earnPanel.SetActive(true); backButton.SetActive(true); }
    public void ShowFrens() { HideAllPanels(); frensPanel.SetActive(true); backButton.SetActive(true); }
    public void ShowIrdrop() { HideAllPanels(); irdropPanel.SetActive(true); backButton.SetActive(true); }

    private void HideAllPanels()
    {
        panel1.SetActive(false);
        earnPanel.SetActive(false);
        frensPanel.SetActive(false);
        walletPanel.SetActive(false);
        irdropPanel.SetActive(false);
        leaderboardPanel.SetActive(false);
    }

    public void OnBackButtonPressed() { ShowPanel1(); }

    public void ShowInvitePanel()
    {
        panelInvite.SetActive(true);
    }

    public void HideInvitePanel()
    {
        panelInvite.SetActive(false);
    }

    public void CopyInviteLink()
    {
        string inviteLinkWithID = telegramInviteLink + "?ref=" + playerID;
        GUIUtility.systemCopyBuffer = inviteLinkWithID;
        Debug.Log("تم نسخ الرابط: " + inviteLinkWithID);
    }

    public void ShareInviteLink()
    {
        string inviteLinkWithID = telegramInviteLink + "?ref=" + playerID;
        string message = "Join me in this awesome game! " + inviteLinkWithID;

        Debug.Log("Invite Link Shared: " + message);
    }

    public void OpenTelegram() { OpenSocialMediaLinks("telegram"); }
    public void OpenTwitter() { OpenSocialMediaLinks("twitter"); }
    public void OpenYouTube() { OpenSocialMediaLinks("youtube"); }

    void OpenSocialMediaLinks(string platform)
    {
        switch (platform)
        {
            case "telegram":
                Application.OpenURL(telegramInviteLink);
                break;
            case "twitter":
                Application.OpenURL(twitterInviteLink);
                break;
            case "youtube":
                Application.OpenURL(youtubeInviteLink);
                break;
        }
    }

    // دالة لعرض الترتيب
    public void ShowLeaderboard()
    {
        leaderboardPanel.SetActive(true); // عرض لوحة الترتيب
        UpdateLeaderboard(); // تحديث ترتيب اللاعبين
    }

    // دالة لإخفاء الترتيب
    public void HideLeaderboard()
    {
        leaderboardPanel.SetActive(false); // إخفاء لوحة الترتيب
    }

    // دالة لتحديث ترتيب اللاعبين
    void UpdateLeaderboard()
    {
        players.Sort((x, y) => y.playerPoints.CompareTo(x.playerPoints)); // ترتيب اللاعبين بناءً على النقاط بترتيب تنازلي

        leaderboardText.text = "Leaderboard:\n";
        for (int i = 0; i < players.Count; i++)
        {
            leaderboardText.text += $"{i + 1}. {players[i].playerName} - {players[i].playerPoints} Points\n";
        }

        // هذا هو المكان الصحيح لـ foreach
        foreach (Player player in players)
        {
            leaderboardText.text += $"{player.playerName}: {player.playerPoints}\n";
        }

        leaderboardPanel.SetActive(true); // عرض لوحة الترتيب
    }

    // دالة لإضافة لاعب جديد إلى الترتيب
    public void AddPlayerToLeaderboard(string playerName, int points)
    {
        Player newPlayer = new Player
        {
            playerName = playerName,
            playerPoints = points
        };

        players.Add(newPlayer); // إضافة اللاعب إلى قائمة اللاعبين
    }

    // دالة لتحديث بيانات اللاعب في واجهة اللعبة
    void UpdatePlayerInfo(Sprite avatar, string playerName)
    {
        playerImage.sprite = avatar;
        playerNameText.text = playerName;
    }
} // قوس إغلاق الكل
