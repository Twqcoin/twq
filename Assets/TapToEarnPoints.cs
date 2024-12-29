using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking; // إضافة لتفعيل الاتصال بـ Telegram Bot

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

    public string telegramInviteLink = "https://t.me/gulab_coin";
    public string twitterInviteLink = "https://x.com/Gulab_coin?t=kp0IHdtS8V6Hm1BnnK1mpg&s=35";
    public string youtubeInviteLink = "https://www.youtube.com/@Gulab_coin";

    public string sandLink = "https://example.com/sandlink?ref="; // رابط Sand مع إضافة معرّف الإحالة
    public string copiLink = "https://example.com/copilink?ref="; // رابط Copi مع إضافة معرّف الإحالة

    private DateTime firstLoginDate;
    private string walletAddress;

    private bool isTaskCompleted = false; // حالة إتمام المهمة


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

    // إضافة هيكل بيانات للاعبين المحالين مع الصورة
    private List<ReferralPlayer> referralPlayers = new List<ReferralPlayer>(); // قائمة اللاعبين المحالين
    [System.Serializable]
    public class ReferralPlayer
    {
        public string playerID;
        public string playerName;
        public Sprite playerAvatar;
    }

    public GameObject referralItemPrefab;  // قالب العنصر الذي سيتم تكراره في القائمة
    public Transform referralListContainer; // المكان الذي سيتم فيه عرض القائمة

    void Start()
    {
        playerID = PlayerPrefs.GetString("PlayerID", "");

        if (string.IsNullOrEmpty(playerID))
        {
            playerID = Guid.NewGuid().ToString();
            PlayerPrefs.SetString("PlayerID", playerID);
        }

        ShowPanel1();
        ApplyDailyReward();
        LoadWalletAddress();
        ShowLoginDays();

        taskCompletedIcon.SetActive(false);

        // استرجاع عدد المدعوين من PlayerPrefs
        referralCount = PlayerPrefs.GetInt("ReferralCount", 0); 
        UpdateReferralCountText(); 

        // تحديث بيانات اللاعب
        UpdatePlayerInfo();

        leaderboardPanel.SetActive(false);

        // استعادة حالة التعدين إذا كانت موجودة
        savedMiningStartTime = PlayerPrefs.GetFloat("MiningStartTime", 0);
        savedIsMining = PlayerPrefs.GetInt("IsMining", 0) == 1;

        if (savedIsMining)
        {
            miningStartTime = savedMiningStartTime;
            isMining = true;
            StartCoroutine(MiningCountdown());
        }
    }
    
    // دالة لتحديث بيانات اللاعب في واجهة اللعبة
    void UpdatePlayerInfo()
    {
        // استرجاع الصورة والاسم من PlayerPrefs
        string savedPlayerName = PlayerPrefs.GetString("PlayerName", "Player1");
        string savedPlayerImage = PlayerPrefs.GetString("PlayerImage", "DefaultAvatar");

        Sprite playerAvatar = Resources.Load<Sprite>(savedPlayerImage);

        // إذا كانت الصورة غير موجودة، استخدم الصورة الافتراضية
        if (playerAvatar == null)
        {
            playerAvatar = Resources.Load<Sprite>("DefaultAvatar");
        }

        playerImage.sprite = playerAvatar;
        playerNameText.text = savedPlayerName;
    }

    // دالة لتعيين الصورة والاسم عند الدخول لأول مرة
    public void SetPlayerInfo(Sprite avatar, string playerName)
    {
        // تخزين الصورة والاسم في PlayerPrefs
        PlayerPrefs.SetString("PlayerName", playerName);
        PlayerPrefs.SetString("PlayerImage", avatar.name); // الاسم الافتراضي للصورة في Resources

        // تحديث الواجهة
        playerImage.sprite = avatar;
        playerNameText.text = playerName;
    }

    // دالة لزيادة عدد المدعوين
    public void IncreaseReferralCount(string referredPlayerID, string playerName, Sprite playerAvatar)
    {
        referralPlayers.Add(new ReferralPlayer { playerID = referredPlayerID, playerName = playerName, playerAvatar = playerAvatar });
        PlayerPrefs.SetInt("ReferralCount", referralPlayers.Count); // تخزين عدد المدعوين في PlayerPrefs
        ShowReferralList(); // تحديث عرض المحالين
    }

    // دالة لعرض قائمة المحالين في واجهة المستخدم
    public void ShowReferralList()
    {
        // مسح العناصر القديمة من القائمة
        foreach (Transform child in referralListContainer)
        {
            Destroy(child.gameObject);
        }

        // إضافة العناصر الجديدة إلى القائمة
        foreach (ReferralPlayer referral in referralPlayers)
        {
            GameObject referralItem = Instantiate(referralItemPrefab, referralListContainer);
            TMP_Text playerNameText = referralItem.GetComponentInChildren<TMP_Text>();
            Image playerAvatarImage = referralItem.GetComponentInChildren<Image>();

            // تحديث النص والصورة في العنصر
            playerNameText.text = referral.playerName;
            playerAvatarImage.sprite = referral.playerAvatar;
        }
    }

    // دالة لتحديث النص الذي يعرض عدد المدعوين
    void UpdateReferralCountText()
    {
        referralCountText.text = $"Referrals: {referralCount}"; // عرض العدد
    }

    void ApplyDailyReward()
    {
        string todayDate = DateTime.Now.ToString("yyyy-MM-dd");

        // التحقق مما إذا كان اليوم هو أول دخول في هذا اليوم
        if (!PlayerPrefs.HasKey("LastLoginDate") && PlayerPrefs.GetString("LastLoginDate") != todayDate)
        {
            PlayerPrefs.SetString("LastLoginDate", todayDate);

            // تحقق من عدم عرض مكافأة الدخول بعد
            if (!PlayerPrefs.HasKey("DailyRewardClaimed") || PlayerPrefs.GetInt("DailyRewardClaimed") == 0)
            {
                AddPoints(miningPoints); // إضافة نقاط التعدين اليومية
                PlayerPrefs.SetInt("DailyRewardClaimed", 1); // تعيين أنه تم عرض المكافأة
            }
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
    }

    public void ShowWallet()
    {
        HideAllPanels();
        walletPanel.SetActive(true);
        walletText.text = string.IsNullOrEmpty(walletAddress) ? " Wallet" : $"Wallet: {walletAddress}";
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

    public void ShowEarn() 
    {
        HideAllPanels(); 
        earnPanel.SetActive(true);
    }

    public void ShowFrens() 
    {
        HideAllPanels(); 
        frensPanel.SetActive(true);
        ShowReferralList(); // تحديث قائمة المحالين عند عرضها
    }

    public void ShowIrdrop() 
    {
        HideAllPanels(); 
        irdropPanel.SetActive(true);
    }private void HideAllPanels()
    {
        panel1.SetActive(false);
        earnPanel.SetActive(false);
        frensPanel.SetActive(false);
        walletPanel.SetActive(false);
        irdropPanel.SetActive(false);
        panelInvite.SetActive(false);
    }

    public void OnBackButtonPressed() 
    { 
        ShowPanel1(); 
    }
    
    public void ShowInvitePanel()
    {
        panelInvite.SetActive(true);
    }

    public void HideInvitePanel()
    {
        panelInvite.SetActive(false);
    }

    public void InviteOnTelegram()
    {
        Application.OpenURL(telegramInviteLink);
    }

    public void InviteOnTwitter()
    {
        Application.OpenURL(twitterInviteLink);
    }

    public void InviteOnYoutube()
    {
        Application.OpenURL(youtubeInviteLink);
    }

    // دالة لإرسال البيانات إلى البوت
    // دالة لإرسال البيانات إلى البوت
public class TelegramBotSender : MonoBehaviour
{
    private string botToken; // تعريف المتغير لتخزين توكن البوت
    private string chatId = "@GULAB_COIN"; // ضع الـ chat ID هنا

    void Start()
    {
        // الحصول على التوكن من المتغير البيئي
        botToken = System.Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN");

        if (string.IsNullOrEmpty(botToken))
        {
            Debug.LogError("Telegram Bot Token is missing!");
        }
    }

    public void SendMessageToTelegram(string message)
    {
        StartCoroutine(SendMessageCoroutine(message));
    }

    private System.Collections.IEnumerator SendMessageCoroutine(string message)
    {
        string url = $"https://api.telegram.org/bot{botToken}/sendMessage?chat_id={chatId}&text={UnityWebRequest.EscapeURL(message)}";
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Debug.Log("Message sent to Telegram");
        }
        else
        {
            Debug.LogError("Failed to send message: " + request.error);
        }
    }
}


    // دالة لنسخ الرابط الخاص باللاعب عند الضغط على sandLink
    public void CopySandLink()
    {
        string sandUrl = sandLink + playerID; // إضافة معرّف اللاعب
        GUIUtility.systemCopyBuffer = sandUrl; // نسخ الرابط إلى الحافظة
        Debug.Log("Sand link copied: " + sandUrl);
    }

    // دالة لنسخ الرابط الخاص باللاعب عند الضغط على copiLink
    public void CopyCopiLink()
    {
        string copiUrl = copiLink + playerID; // إضافة معرّف اللاعب
        GUIUtility.systemCopyBuffer = copiUrl; // نسخ الرابط إلى الحافظة
        Debug.Log("Copi link copied: " + copiUrl);
    }
}