using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class CodeVerification : MonoBehaviour
{
    [Header("UI Elements")]
    public Button mainButton;
    public TMP_Text buttonText;
    public GameObject panel;
    public TMP_Text errorText;
    public TMP_InputField codeInput;
    public Button verifyButton;
    public TMP_Text tonBalanceText;
    public TMP_Text earnedBalanceText; // النص الجديد لعرض الرصيد المكتسب
    public Image checkMark;
    public Button withdrawButton;
    public Button closeButton;
    public Button openLinkButton;

    [Header("Settings")]
    public string correctCode = "1234";
    public decimal tonReward = 0.0299m;
    public decimal tonWithdrawalThreshold = 1.0m;
    public int maxPlayers = 100;

    private string status = "start";
    private decimal tonBalance = 0;
    private decimal claimAmount = 0; // تخزين قيمة المطالبة
    private int playersClaimed = 0;

    void Start()
    {
        if (mainButton != null)
            mainButton.onClick.AddListener(OnMainButtonClick);
        if (verifyButton != null)
            verifyButton.onClick.AddListener(OnVerifyButtonClick);
        if (withdrawButton != null)
            withdrawButton.onClick.AddListener(WithdrawTon);
        if (closeButton != null)
            closeButton.onClick.AddListener(OnCloseButtonClick);
        if (openLinkButton != null)
            openLinkButton.onClick.AddListener(OnOpenLinkButtonClick);

        if (buttonText != null)
            buttonText.text = "Start";
        if (errorText != null)
            errorText.text = "";
        if (panel != null)
            panel.SetActive(false);
        if (checkMark != null)
            checkMark.gameObject.SetActive(false);
        if (withdrawButton != null)
            withdrawButton.interactable = false;
        if (earnedBalanceText != null)
            earnedBalanceText.text = "0.0000"; // تهيئة النص الجديد بدون "Earned"

        playersClaimed = PlayerPrefs.GetInt("PlayersClaimed", 0);

        UpdateUI();
    }

    void OnMainButtonClick()
    {
        if (status == "start")
        {
            OpenURL("https://youtu.be/bi2ZwUpwANA?si=AZgiGs80EQqbGFx8");
            status = "verify";
            buttonText.text = "Verify";
            ResetButtonColor(mainButton); // إعادة تعيين لون الزر إلى الأصلي
        }
        else if (status == "verify")
        {
            panel.SetActive(true);
            errorText.text = "";
            codeInput.text = "";
        }
        else if (status == "claim")
        {
            tonBalance += claimAmount; // إضافة المبلغ المطالب به إلى الرصيد
            claimAmount = 0; // تصفير المبلغ المطالب به
            
            playersClaimed++;
            PlayerPrefs.SetInt("PlayersClaimed", playersClaimed);
            panel.SetActive(false);
            status = "start";

            // تغيير لون الزر إلى الأخند
            ChangeButtonColor(mainButton, Color.green);

            buttonText.text = "✔️";
            checkMark.gameObject.SetActive(true);
            mainButton.gameObject.SetActive(false);

            // تصفير القيمة المكتسبة
            if (earnedBalanceText != null)
                earnedBalanceText.text = "0.0000";

            UpdateUI();
        }
    }

    void OnVerifyButtonClick()
    {
        errorText.text = "";

        if (codeInput != null && codeInput.text == correctCode)
        {
            if (playersClaimed < maxPlayers)
            {
                claimAmount = tonReward; // تخزين قيمة الجائزة بدون إضافتها إلى الرصيد بعد
                playersClaimed++;
                PlayerPrefs.SetInt("PlayersClaimed", playersClaimed);
                panel.SetActive(false);
                status = "claim";
                buttonText.text = "Claim";

                // تغيير لون الزر إلى الأخند
                ChangeButtonColor(mainButton, Color.green);

                // تحديث النص الجديد لعرض الرصيد المكتسب
                if (earnedBalanceText != null)
                    earnedBalanceText.text = $"{tonReward.ToString("0.0000")}";

                UpdateUI();
            }
            else
            {
                errorText.text = "The maximum number of players has been reached!";
                errorText.color = Color.red; // تغيير لون النص إلى الأحمر
            }
        }
        else
        {
            errorText.text = "Incorrect code!";
            errorText.color = Color.red; // تغيير لون النص إلى الأحمر
            codeInput.text = "";
        }
    }

    private void UpdateUI()
    {
        if (tonBalanceText != null)
            tonBalanceText.text = $"{tonBalance.ToString("0.0000")}";

        if (withdrawButton != null)
            withdrawButton.interactable = tonBalance >= tonWithdrawalThreshold;
    }

    public void WithdrawTon()
    {
        if (tonBalance >= tonWithdrawalThreshold)
        {
            Debug.Log($"Withdrawing {tonBalance.ToString("0.0000")} TON...");
            tonBalance = 0;
            PlayerPrefs.SetFloat("TonBalance", (float)tonBalance);
            UpdateUI();
            errorText.text = $"تم سحب {tonWithdrawalThreshold} TON بنجاح!";
            errorText.color = Color.green; // تغيير لون النص إلى الأخند
        }
        else
        {
            errorText.text = $"أنت بحاجة إلى {tonWithdrawalThreshold} TON على الأقل للسحب.";
            errorText.color = Color.red; // تغيير لون النص إلى الأحمر
        }
    }

    void OnCloseButtonClick()
    {
        panel.SetActive(false);
    }

    void OnOpenLinkButtonClick()
    {
        OpenURL("https://youtu.be/bi2ZwUpwANA?si=AZgiGs80EQqbGFx8");
    }

    private void OpenURL(string url)
    {
        Application.OpenURL(url);
    }

    // وظيفة لتغيير لون الزر
    private void ChangeButtonColor(Button button, Color color)
    {
        if (button != null)
        {
            var colors = button.colors;
            colors.normalColor = color;
            colors.highlightedColor = color;
            colors.pressedColor = color;
            colors.selectedColor = color;
            button.colors = colors;
        }
    }

    // وظيفة لإعادة تعيين لون الزر إلى الأصلي
    private void ResetButtonColor(Button button)
    {
        if (button != null)
        {
            var colors = button.colors;
            colors.normalColor = Color.white; // أو أي لون آخر تريده
            colors.highlightedColor = Color.white;
            colors.pressedColor = Color.white;
            colors.selectedColor = Color.white;
            button.colors = colors;
        }
    }
}