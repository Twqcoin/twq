using UnityEngine;
using UnityEngine.UI;

public class PanelManager : MonoBehaviour
{
    [Header("UI Panels")]
    public GameObject homePanel;    // شاشة الصفحة الرئيسية
    public GameObject earnPanel;    // شاشة الكسب
    public GameObject frensPanel;   // شاشة الأصدقاء (فريندز)
    public GameObject walletPanel;  // شاشة المحفظة
    public GameObject irdropPanel;  // شاشة الأيردروب

    [Header("UI Buttons")]
    public Button homeButton;       // زر الصفحة الرئيسية
    public Button earnButton;       // زر الكسب
    public Button frensButton;      // زر الأصدقاء
    public Button walletButton;     // زر المحفظة
    public Button airdropButton;    // زر الأيردروب

    [Header("Highlight Frame")]
    public RectTransform highlightFrame; // الإطار الذي سيتحرك حول الزر النشط

    void Start()
    {
        // ربط الأزرار بدوال التبديل بين الصفحات
        homeButton.onClick.AddListener(ShowHomePanel);
        earnButton.onClick.AddListener(ShowEarnPanel);
        frensButton.onClick.AddListener(ShowFrensPanel);
        walletButton.onClick.AddListener(ShowWallet);
        airdropButton.onClick.AddListener(ShowAirdropPanel);

        ShowHomePanel(); // عرض الشاشة الرئيسية عند بدء اللعبة
    }

    // إخفاء جميع الشاشات
    private void HideAllPanels()
    {
        homePanel.SetActive(false);
        earnPanel.SetActive(false);
        frensPanel.SetActive(false);
        walletPanel.SetActive(false);
        irdropPanel.SetActive(false);
    }

    // تحريك الإطار إلى الزر النشط
    private void MoveHighlightToButton(Button button)
    {
        if (highlightFrame != null && button != null)
        {
            RectTransform buttonRect = button.GetComponent<RectTransform>();
            highlightFrame.position = buttonRect.position; // نقل الإطار إلى موضع الزر
        }
        else
        {
            Debug.LogWarning("Highlight frame or button is missing!");
        }
    }

    // عرض شاشة الصفحة الرئيسية
    public void ShowHomePanel()
    {
        HideAllPanels();
        homePanel.SetActive(true);
        MoveHighlightToButton(homeButton); // نقل الإطار إلى زر الصفحة الرئيسية
    }

    // عرض شاشة المحفظة
    public void ShowWallet()
    {
        HideAllPanels();
        walletPanel.SetActive(true);
        MoveHighlightToButton(walletButton); // نقل الإطار إلى زر المحفظة
    }

    // عرض شاشة الكسب
    public void ShowEarnPanel()
    {
        HideAllPanels();
        earnPanel.SetActive(true);
        MoveHighlightToButton(earnButton); // نقل الإطار إلى زر الكسب
    }

    // عرض شاشة الأصدقاء
    public void ShowFrensPanel()
    {
        HideAllPanels();
        frensPanel.SetActive(true);
        MoveHighlightToButton(frensButton); // نقل الإطار إلى زر الأصدقاء
    }

    // عرض شاشة الأيردروب
    public void ShowAirdropPanel()
    {
        HideAllPanels();
        irdropPanel.SetActive(true);
        MoveHighlightToButton(airdropButton); // نقل الإطار إلى زر الأيردروب
    }
}
