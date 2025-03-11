using UnityEngine;
using TMPro;
using System.Collections;
using UnityEngine.UI;

public class UIManager : MonoBehaviour
{
    public GameObject playButton;
    public GameObject gamePanel;
    public GameObject replayButton;
    public GameObject backButton;
    public TMP_Text pointsText; // نص النقاط
    public TMP_Text timeText; // نص الوقت
    public GameObject endGamePanel;
    public TMP_Text finalPointsText; // نص النقاط النهائية

    [SerializeField] private FallingObjectSpawner spawner; // Reference to FallingObjectSpawner

    private float gameDuration = 30f; // 30 ثانية
    private float timeRemaining;
    private bool isSpawning = false;
    private int currentRoundPoints = 0; // النقاط التي تم جمعها في الجولة الحالية

    void Start()
    {
        InitializeUI();
        timeRemaining = gameDuration;

        // تحديث النص عند البدء
        UpdatePointsText();
    }

    void Update()
    {
        if (isSpawning)
        {
            timeRemaining -= Time.deltaTime;

            // تحديث نص الوقت فقط إذا تغيرت القيمة
            if (timeText != null && Mathf.FloorToInt(timeRemaining) != Mathf.FloorToInt(timeRemaining + Time.deltaTime))
            {
                timeText.text = FormatTime(timeRemaining); // إظهار الوقت فقط بدون "Time: "
            }

            // انتهاء الوقت
            if (timeRemaining <= 0)
            {
                EndGame();
            }
        }
    }

    private string FormatTime(float timeInSeconds)
    {
        int minutes = Mathf.FloorToInt(timeInSeconds / 60); // حساب الدقائق
        int seconds = Mathf.FloorToInt(timeInSeconds % 60); // حساب الثواني

        // إرجاع الوقت بالتنسيق MM:SS
        return string.Format("{0:00}:{1:00}", minutes, seconds);
    }

    private void InitializeUI()
    {
        SetActiveUIElement(gamePanel, false); // إخفاء الـ gamePanel في البداية
        SetActiveUIElement(playButton, true);
        SetActiveUIElement(replayButton, false);
        SetActiveUIElement(backButton, false);
        SetActiveUIElement(endGamePanel, false);
    }

    private void SetActiveUIElement(GameObject element, bool isActive)
    {
        if (element != null) element.SetActive(isActive);
    }

    public void OnPlayButtonClicked()
    {
        Debug.Log("Play button clicked.");
        StartGame();
    }

    public void StartGame()
    {
        Debug.Log("StartGame called.");

        if (playButton == null || gamePanel == null)
        {
            Debug.LogError("UI elements are not assigned!");
            return;
        }

        if (spawner == null)
        {
            Debug.LogError("FallingObjectSpawner is not assigned!");
            return;
        }

        spawner.CancelSpawning();
        spawner.ClearObjects();

        // إخفاء زر "Play" وإظهار الـ gamePanel
        SetActiveUIElement(playButton, false);
        SetActiveUIElement(gamePanel, true); // تأكد من تفعيل gamePanel
        SetActiveUIElement(endGamePanel, false);

        // تأكد من إبقاء النصوص مرئية داخل gamePanel
        if (pointsText != null) pointsText.gameObject.SetActive(true);
        if (timeText != null) timeText.gameObject.SetActive(true);

        isSpawning = true; // بدء المؤقت
        timeRemaining = gameDuration; // إعادة تعيين الوقت
        ResetPoints(); // إعادة تعيين النقاط إلى الصفر

        spawner.StartSpawning(); // بدء توليد العناصر الساقطة
        Debug.Log("Game started successfully.");
    }

    private void UpdatePointsText()
    {
        if (pointsText != null)
        {
            pointsText.text = currentRoundPoints.ToString(); // عرض الرقم فقط
            Debug.Log("Updated pointsText: " + pointsText.text); // تأكيد التحديث
        }
        else
        {
            Debug.LogError("pointsText غير معين!");
        }
    }

    private void EndGame()
    {
        isSpawning = false; // إيقاف المؤقت
        spawner.CancelSpawning(); // إيقاف توليد الكائنات
        spawner.ClearObjects(); // تنظيف الكائنات الموجودة

        // عرض النقاط النهائية في finalPointsText
        if (finalPointsText != null)
        {
            finalPointsText.text = currentRoundPoints.ToString(); // عرض الرقم فقط
            Debug.Log("Updated finalPointsText: " + finalPointsText.text); // تأكيد التحديث
        }
        else
        {
            Debug.LogError("finalPointsText غير معين!");
        }

        // إرسال النقاط إلى PointsManager
        if (PointsManager.Instance != null)
        {
            PointsManager.Instance.AddPoints(currentRoundPoints); // إضافة نقاط الجولة الحالية إلى المجموع الكلي
        }
        else
        {
            Debug.LogError("PointsManager.Instance is null!");
        }

        SetActiveUIElement(replayButton, true);
        SetActiveUIElement(backButton, true);
        SetActiveUIElement(gamePanel, false); // إخفاء اللوحة الرئيسية
        ShowEndGamePanel(); // إظهار اللوحة الأخيرة
    }

    private void ShowEndGamePanel()
    {
        if (endGamePanel != null)
        {
            endGamePanel.SetActive(true);
        }
        else
        {
            Debug.LogError("endGamePanel is not assigned!");
        }
    }

    public void AddPoints(int amount)
    {
        if (amount < 0) // تأكد من أن القيمة غير سالبة
        {
            Debug.LogWarning("Attempted to add negative points: " + amount);
            return;
        }

        currentRoundPoints += amount; // إضافة النقاط
        UpdatePointsText(); // تحديث نص النقاط
        Debug.Log("Points added in UIManager. Current Round Points: " + currentRoundPoints); // طباعة القيمة
    }

    public void ResetPoints()
    {
        currentRoundPoints = 0; // إعادة تعيين النقاط إلى الصفر
        UpdatePointsText(); // تحديث نص النقاط
        Debug.Log("Points have been reset to 0.");
    }

    public void OnPointsIconClicked()
    {
        AddPoints(10); // إضافة 10 نقاط
        Debug.Log("تم النقر على الأيقونة وإضافة 10 نقاط!");
    }

    public void OnReplayButtonClicked()
    {
        Debug.Log("Replay button clicked.");
        ReplayGame();
    }

    public void ReplayGame()
    {
        Debug.Log("ReplayGame called.");

        if (endGamePanel == null || gamePanel == null)
        {
            Debug.LogError("UI elements are not assigned!");
            return;
        }

        endGamePanel.SetActive(false);
        timeRemaining = gameDuration; // إعادة تعيين الوقت
        isSpawning = true; // بدء المؤقت
        ResetPoints(); // إعادة تعيين النقاط إلى الصفر

        spawner.ClearObjects();
        SetActiveUIElement(replayButton, false);
        SetActiveUIElement(backButton, false);

        gamePanel.SetActive(true);
        StartGame();

        Debug.Log("Game replayed successfully.");
    }

    public void OnBackButtonClicked()
    {
        Debug.Log("Back button clicked.");
        GoBack();
    }

    public void GoBack()
    {
        Debug.Log("GoBack called.");

        if (spawner == null)
        {
            Debug.LogError("FallingObjectSpawner is not assigned!");
            return;
        }

        spawner.CancelSpawning();
        spawner.ClearObjects();

        SetActiveUIElement(gamePanel, false);
        SetActiveUIElement(endGamePanel, false);
        SetActiveUIElement(playButton, true);
        SetActiveUIElement(replayButton, false);
        SetActiveUIElement(backButton, false);

        timeRemaining = gameDuration;
        if (timeText != null) timeText.text = FormatTime(timeRemaining); // عرض الوقت فقط بدون "Time: "

        Debug.Log("Returned to main menu successfully.");
    }
}