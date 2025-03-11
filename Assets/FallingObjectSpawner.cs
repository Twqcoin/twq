using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;

public class FallingObjectSpawner : MonoBehaviour
{
    public GameObject[] fallingObjects;
    public float spawnInterval = 0.0f;
    public GameObject gamePanel; // الـ Panel الرئيسي
    public GameObject explosionIcon, stopIcon, pointsIcon;
    public GameObject stopTimeIcon;
    public GameObject backgroundPanel; // الـ Panel الجديد لتغيير اللون

    private float stopTimeSpawnChance = 0.05f; // فرصة ظهور أيقونة التجمد
    private float explosionChance = 0.1f; // فرصة ظهور أيقونة الانفجار
    private float pointsChance = 1.0f; // فرصة ظهور أيقونة النقاط

    private float gravityScaleIncrease = 1f;
    private float maxGravityScale = 5f;

    private List<Rigidbody2D> rigidbodyList = new List<Rigidbody2D>();
    private float[] originalGravityScales;

    void Start()
    {
        if (gamePanel == null || backgroundPanel == null)
        {
            Debug.LogError("gamePanel or backgroundPanel is not assigned!");
        }
    }

    public void StartSpawning()
    {
        if (gamePanel == null)
        {
            Debug.LogError("gamePanel is not assigned!");
            return;
        }

        InvokeRepeating("SpawnObjects", 0f, spawnInterval);
    }

    public void CancelSpawning()
    {
        CancelInvoke("SpawnObjects");
    }

    public void ClearObjects()
    {
        if (gamePanel == null) return;

        foreach (Transform child in gamePanel.transform)
        {
            if (child != null)
            {
                Destroy(child.gameObject);
            }
        }
        rigidbodyList.Clear();
    }

    private void SpawnObjects()
    {
        if (gamePanel == null || !gamePanel.activeSelf)
        {
            return;
        }

        int objectsToSpawn = Random.Range(1, 5);
        for (int i = 0; i < objectsToSpawn; i++)
        {
            GameObject objectToSpawn = GetRandomObjectToSpawn();
            if (objectToSpawn != null)
            {
                SpawnObject(objectToSpawn);
            }
        }
    }

    private GameObject GetRandomObjectToSpawn()
    {
        float randomChance = Random.value;

        // تحديد أيقونة التجمد أو الانفجار أو النقاط بناءً على الفرص
        if (randomChance < stopTimeSpawnChance)
        {
            return stopTimeIcon; // أيقونة التجمد
        }
        else if (randomChance < stopTimeSpawnChance + explosionChance)
        {
            return explosionIcon; // أيقونة الانفجار
        }
        else if (randomChance < stopTimeSpawnChance + explosionChance + pointsChance)
        {
            return pointsIcon; // أيقونة النقاط
        }

        return null; // لا شيء
    }

    private void SpawnObject(GameObject objectToSpawn)
    {
        if (objectToSpawn == null || gamePanel == null) return;

        // الحصول على RectTransform الخاص بالـ panel
        RectTransform panelRect = gamePanel.GetComponent<RectTransform>();

        // حساب عرض وارتفاع الـ panel
        float panelWidth = panelRect.rect.width;
        float panelHeight = panelRect.rect.height;

        // الحصول على حجم الأيقونة
        RectTransform iconRect = objectToSpawn.GetComponent<RectTransform>();
        float iconWidth = iconRect.rect.width;
        float iconHeight = iconRect.rect.height;

        // تحديد الموضع العشوائي فوق الـ panel مع مراعاة حجم الأيقونة
        float minX = (-panelWidth / 2f) + (iconWidth / 2f); // الحد الأدنى للموقع الأفقي
        float maxX = (panelWidth / 2f) - (iconWidth / 2f); // الحد الأقصى للموقع الأفقي
        float randomX = Random.Range(minX, maxX); // موقع أفقي عشوائي

        float spawnY = (panelHeight / 2f) + (iconHeight / 2f); // موقع رأسي فوق الـ panel

        // تحويل الإحداثيات المحلية إلى العالمية
        Vector3 spawnPosition = panelRect.TransformPoint(new Vector3(randomX, spawnY, 0f));

        // إنشاء الأيقونة عند الموقع المحدد
        GameObject newObject = Instantiate(objectToSpawn, spawnPosition, Quaternion.identity, gamePanel.transform);

        // إضافة Rigidbody2D في حالة عدم وجوده
        Rigidbody2D rb = newObject.GetComponent<Rigidbody2D>() ?? newObject.AddComponent<Rigidbody2D>();

        // إيقاف دوران الأيقونة
        rb.constraints = RigidbodyConstraints2D.FreezeRotation;

        // تعديل الجاذبية
        rb.gravityScale = Mathf.Min(rb.gravityScale + gravityScaleIncrease, maxGravityScale);

        // الحركة للأسفل مع سرعة محددة
        rb.linearVelocity = new Vector2(0, -500); // ضبط السرعة للأسفل إلى 200

        rigidbodyList.Add(rb);
        AddClickEvent(newObject);
    }

    private void AddClickEvent(GameObject obj)
    {
        if (obj == null) return;

        EventTrigger trigger = obj.GetComponent<EventTrigger>() ?? obj.AddComponent<EventTrigger>();
        EventTrigger.Entry entry = new EventTrigger.Entry { eventID = EventTriggerType.PointerClick };
        entry.callback.AddListener((data) => OnObjectClicked(obj));
        trigger.triggers.Add(entry);
    }

    private void OnObjectClicked(GameObject obj)
    {
        if (obj == null) return;

        if (obj.CompareTag("StopTimeIcon")) StopGravityFor5Seconds(obj);
        else if (obj.CompareTag("ExplosionIcon")) StartCoroutine(ExplosionEffect(obj));
        else if (obj.CompareTag("PointsIcon")) FindObjectOfType<UIManager>()?.AddPoints(10);

        if (obj != null)
        {
            Destroy(obj);
        }
    }

    public void StopGravityFor5Seconds(GameObject stopTimeIconInstance)
    {
        if (stopTimeIconInstance == null) return;

        StartCoroutine(StopGravityCoroutine(stopTimeIconInstance));
    }

    private IEnumerator StopGravityCoroutine(GameObject stopTimeIconInstance)
    {
        if (stopTimeIconInstance == null || backgroundPanel == null) yield break;

        // إيقاف التوليد
        CancelSpawning();

        // تغيير لون الخلفية إلى الأزرق (لون التجمد)
        Image panelBackground = backgroundPanel.GetComponent<Image>();
        Color originalColor = panelBackground != null ? panelBackground.color : Color.white;

        if (panelBackground != null)
        {
            panelBackground.color = new Color(0, 0, 1, 0.5f); // أزرق مع شفافية 50%
        }

        // تكبير أيقونة التجمد
        stopTimeIconInstance.transform.localScale = Vector3.one * 1.5f;

        // تغيير لون أيقونة التجمد
        var iconImage = stopTimeIconInstance.GetComponent<Image>();
        if (iconImage != null)
        {
            iconImage.color = Color.cyan;
        }

        // إنشاء نسخة من القائمة لتجنب التعديلات أثناء التنفيذ
        List<Rigidbody2D> rigidbodyListCopy = new List<Rigidbody2D>(rigidbodyList);
        originalGravityScales = new float[rigidbodyListCopy.Count];

        // إيقاف الجاذبية لجميع الكائنات
        for (int i = 0; i < rigidbodyListCopy.Count; i++)
        {
            if (rigidbodyListCopy[i] != null)
            {
                originalGravityScales[i] = rigidbodyListCopy[i].gravityScale;
                rigidbodyListCopy[i].gravityScale = 0; // إيقاف الجاذبية
                rigidbodyListCopy[i].linearVelocity = Vector2.zero; // إيقاف الحركة
            }
        }

        // الانتظار لمدة 5 ثوانٍ
        yield return new WaitForSeconds(5f);

        // استعادة الجاذبية الأصلية
        for (int i = 0; i < rigidbodyListCopy.Count; i++)
        {
            if (rigidbodyListCopy[i] != null)
            {
                rigidbodyListCopy[i].gravityScale = originalGravityScales[i];
            }
        }

        // إعادة لون الخلفية إلى الأصلي
        if (panelBackground != null)
        {
            panelBackground.color = originalColor;
        }

        // إعادة أيقونة التجمد إلى الحجم واللون الأصلي
        if (stopTimeIconInstance != null)
        {
            stopTimeIconInstance.transform.localScale = Vector3.one;

            if (iconImage != null)
            {
                iconImage.color = Color.white;
            }
        }

        // استئناف التوليد
        StartSpawning();
    }

    private IEnumerator ExplosionEffect(GameObject obj)
    {
        if (obj == null || backgroundPanel == null) yield break;

        // الحصول على Image الخاص بالـ panel
        Image panelBackground = backgroundPanel.GetComponent<Image>();
        if (panelBackground == null)
        {
            Debug.LogError("Panel background Image is not assigned!");
            yield break;
        }

        // حفظ اللون الأصلي للخلفية
        Color originalColor = panelBackground.color;

        // تغيير لون الخلفية إلى الأحمر مع شفافية
        panelBackground.color = new Color(1, 0, 0, 0.5f); // أحمر مع شفافية 50%

        // الانتظار لفترة قصيرة (0.5 ثانية)
        yield return new WaitForSeconds(0.5f);

        // إعادة اللون إلى الأصلي
        panelBackground.color = originalColor;

        // تصفير نقاط اللاعب
        FindObjectOfType<UIManager>()?.ResetPoints();

        // إخفاء الأيقونة
        if (obj != null)
        {
            Destroy(obj);
        }
    }
}