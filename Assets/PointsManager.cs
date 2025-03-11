using UnityEngine;
using TMPro;

public class PointsManager : MonoBehaviour
{
    public static PointsManager Instance;

    private int totalPoints = 0;
    private const string TotalPointsKey = "TotalPoints";

    [SerializeField] private TMP_Text pointsText; // عنصر TextMeshPro لعرض النقاط

    private void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject); // استمرارية الكائن بين المشاهد
        }
        else
        {
            Destroy(gameObject);
        }
    }

    private void Start()
    {
        // تحميل النقاط المحفوظة مع التأكد من أنها غير سالبة
        totalPoints = Mathf.Max(0, PlayerPrefs.GetInt(TotalPointsKey, 0));
        UpdatePointsUI(); // تحديث واجهة المستخدم عند البدء
    }

    /// <summary>
    /// إضافة النقاط إلى المجموع الكلي.
    /// </summary>
    /// <param name="amount">عدد النقاط المضافة (يجب أن تكون قيمة غير سالبة).</param>
    public void AddPoints(int amount)
    {
        if (amount < 0) // السماح بإضافة صفر نقاط
        {
            Debug.LogWarning("Attempted to add negative points: " + amount);
            return;
        }

        totalPoints += amount;
        PlayerPrefs.SetInt(TotalPointsKey, totalPoints);
        PlayerPrefs.Save();
        UpdatePointsUI(); // تحديث واجهة المستخدم بعد إضافة النقاط
        Debug.Log("Points added! Current points: " + totalPoints);
    }

    /// <summary>
    /// الحصول على مجموع النقاط الكلي.
    /// </summary>
    /// <returns>عدد النقاط الكلي.</returns>
    public int GetTotalPoints()
    {
        Debug.Log("Current points: " + totalPoints);
        return totalPoints;
    }

    /// <summary>
    /// تعيين النقاط يدويًا.
    /// </summary>
    /// <param name="points">عدد النقاط الجديدة.</param>
    public void SetTotalPoints(int points)
    {
        if (points < 0)
        {
            Debug.LogWarning("Attempted to set negative points: " + points);
            return;
        }

        totalPoints = points;
        PlayerPrefs.SetInt(TotalPointsKey, totalPoints);
        PlayerPrefs.Save();
        UpdatePointsUI(); // تحديث واجهة المستخدم بعد تعيين النقاط
        Debug.Log("Points set to: " + totalPoints);
    }

    /// <summary>
    /// تصفير النقاط.
    /// </summary>
    /// <param name="resetSavedPoints">إذا كان true، يتم تصفير النقاط المحفوظة أيضًا.</param>
    public void ResetPoints(bool resetSavedPoints = false)
    {
        totalPoints = 0;

        if (resetSavedPoints)
        {
            PlayerPrefs.SetInt(TotalPointsKey, totalPoints);
            PlayerPrefs.Save();
        }

        UpdatePointsUI(); // تحديث واجهة المستخدم بعد تصفير النقاط
        Debug.Log("Points reset! Current points: " + totalPoints);
    }

    /// <summary>
    /// تحديث واجهة المستخدم لعرض النقاط.
    /// </summary>
    private void UpdatePointsUI()
    {
        FindPointsText(); // البحث عن النص قبل التحديث
        if (pointsText != null)
        {
            pointsText.text = totalPoints.ToString();
        }
    }

    private void FindPointsText()
    {
        if (pointsText == null)
        {
            GameObject pointsTextObject = GameObject.FindGameObjectWithTag("PointsText"); // ابحث عن النص باستخدام Tag
            if (pointsTextObject != null)
            {
                pointsText = pointsTextObject.GetComponent<TMP_Text>();
            }
            else
            {
                Debug.LogWarning("No GameObject with tag 'PointsText' found!");
            }
        }
    }
}