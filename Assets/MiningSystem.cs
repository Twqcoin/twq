using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections;

public class MiningSystem : MonoBehaviour
{
    private bool isMining = false;
    private float miningStartTime;
    private float miningProgress = 0.0000001f;  // بداية التعدين
    private float miningDurationInSeconds = 21600f; // 6 ساعات (21600 ثانية)

    [Header("UI Elements")]
    public Button miningButton; // زر التعدين
    public TMP_Text buttonText; // النص داخل الزر
    public TMP_Text timerText;  // النص لعرض الوقت المتبقي
    public TMP_Text pointsText; // لعرض النقاط

    private int miningEarnings = 5; // النقاط المكتسبة من التعدين
    private int points = 0;  // إجمالي النقاط

    void Start()
    {
        // تأكد من أن النص الأولي للزر هو "Start Mining"
        buttonText.text = "Start Mining";
        miningButton.onClick.AddListener(OnButtonClick);
        timerText.text = ""; // تأكد من أن نص الوقت فارغ عند البداية
    }

    void OnButtonClick()
    {
        if (!isMining && buttonText.text == "Start Mining")
        {
            StartMining();
        }
        else if (!isMining && buttonText.text == "Claim")
        {
            ClaimPoints();
        }
    }

    private void StartMining()
    {
        isMining = true;
        miningStartTime = Time.time;
        StartCoroutine(MiningCountdown());
    }

    private IEnumerator MiningCountdown()
    {
        while (isMining)
        {
            float elapsedTime = Time.time - miningStartTime;
            miningProgress = Mathf.Min(elapsedTime / miningDurationInSeconds, 1f);

            // تحديث نص الزر ليعرض التعدين
            buttonText.text = $"{miningProgress:F7}";

            // حساب الوقت المتبقي
            float timeRemaining = miningDurationInSeconds - elapsedTime;
            System.TimeSpan timeSpan = System.TimeSpan.FromSeconds(timeRemaining);
            timerText.text = $"{timeSpan.Hours:D2}:{timeSpan.Minutes:D2}:{timeSpan.Seconds:D2}";

            if (elapsedTime >= miningDurationInSeconds)
            {
                isMining = false;
                buttonText.text = "Claim"; // عند الانتهاء يظهر "Claim"
                timerText.text = "00:00:00"; // عند انتهاء التعدين يتم ضبط الوقت إلى الصفر
            }

            yield return null;
        }
    }

    private void ClaimPoints()
    {
        points += miningEarnings;
        pointsText.text = $"Points: {points}";

        // إعادة تعيين الزر إلى "Start Mining"
        buttonText.text = "Start Mining";
        timerText.text = ""; // إخفاء العداد بعد المطالبة بالنقاط
        miningProgress = 0.0000001f;
    }
}
