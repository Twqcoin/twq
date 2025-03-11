using UnityEngine;
using TMPro;
using UnityEngine.UI;
using System.Collections;

public class TapToEarnPoints : MonoBehaviour
{
    public Image[] checkMarkImages; // تأكد من تعيين هذه الصور في الـ Inspector
    private float waitTime = 15f;

    public string[] inviteLinks = {
        "https://t.me/glqt_coin",
        "https://x.com/MinQX_Official?t=xQGqqJLnypq5TKP4jmDm2A&s=09",
        "https://www.youtube.com/@MinQX_Official",
        "https://www.instagram.com/minqx2025?igsh=MTRhNmJtNm1wYWxqYw==",
        "https://www.tiktok.com/@minqx2?_t=ZS-8u9g1d9GPLe&_r=1",
        "https://www.facebook.com/share/1BjH4qcGXb/"
    };

    public bool[] checkMarks = new bool[6];
    public Button[] buttons;

    private void Start()
    {
        SetupButtons();
        HideAllCheckMarks();
    }

    private void HideAllCheckMarks()
    {
        for (int i = 0; i < checkMarkImages.Length; i++)
        {
            if (checkMarkImages[i] != null)
            {
                checkMarkImages[i].gameObject.SetActive(false); // تأكد من إخفاء الكائن بالكامل
            }
        }
    }

    public void OpenLink(int index)
    {
        if (index < 0 || index >= inviteLinks.Length) return;

        Application.OpenURL(inviteLinks[index]);
        Debug.Log($"Link {index + 1} opened: {inviteLinks[index]}");

        StartCoroutine(StartTask(index));
    }

    private IEnumerator StartTask(int index)
    {
        Debug.Log($"StartTask called for index: {index}");
        yield return new WaitForSeconds(waitTime);

        if (buttons[index] != null)
        {
            TMP_Text buttonText = buttons[index].GetComponentInChildren<TMP_Text>();
            if (buttonText != null)
            {
                buttonText.text = "Claim"; // تغيير النص إلى "Claim"
                buttonText.color = Color.black; // تغيير النص إلى اللون الأسود
            }

            // تغيير لون الزر نفسه
            Image buttonImage = buttons[index].GetComponent<Image>();
            if (buttonImage != null)
            {
                buttonImage.color = Color.green; // تغيير لون الزر إلى الأخضر
            }

            buttons[index].interactable = true;
            buttons[index].onClick.RemoveAllListeners();
            buttons[index].onClick.AddListener(() => ClaimPoints(index));
        }
    }

    public void ClaimPoints(int index)
    {
        Debug.Log($"ClaimPoints called for index: {index}");

        // التأكد من أن PointsManager موجود
        if (PointsManager.Instance == null)
        {
            Debug.LogError("PointsManager instance is null!");
            return;
        }

        // إضافة النقاط
        PointsManager.Instance.AddPoints(20000);

        // التأكد من إضافة النقاط
        Debug.Log("Points Added: 20000");

        // إخفاء الزر بعد المطالبة
        if (buttons[index] != null)
        {
            buttons[index].gameObject.SetActive(false);
        }

        // عرض علامة الاختيار
        if (index >= 0 && index < checkMarkImages.Length && checkMarkImages[index] != null)
        {
            checkMarks[index] = true;
            checkMarkImages[index].gameObject.SetActive(true);
            checkMarkImages[index].enabled = true;
            checkMarkImages[index].color = Color.white;
            checkMarkImages[index].transform.SetAsLastSibling();
            Canvas.ForceUpdateCanvases();
            Debug.Log($"✅ Checkmark {index} should now be visible!");
        }
        else
        {
            Debug.LogError($"⚠ Checkmark image at index {index} is not assigned!");
        }
    }

    private void SetupButtons()
    {
        for (int i = 0; i < buttons.Length; i++)
        {
            int index = i;
            buttons[i].onClick.RemoveAllListeners();
            buttons[i].onClick.AddListener(() => OpenLink(index));
        }
    }
}