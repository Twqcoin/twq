using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Networking;

public class GameController : MonoBehaviour
{
    public TMP_Text playerNameText;   // لعرض اسم اللاعب
    public Image playerImage;         // لعرض صورة اللاعب
    private string playerName;
    private string playerProfilePic;

    void Start()
    {
        // تحقق من أن المتغيرات العامة معينة
        if (playerNameText == null)
        {
            Debug.LogError("لم يتم تعيين playerNameText في Inspector.");
        }
        if (playerImage == null)
        {
            Debug.LogError("لم يتم تعيين playerImage في Inspector.");
            return; // توقف إذا لم يتم تعيين playerImage
        }

        // معالجة بيانات URL
        string urlParams = GetUrlParams();
        if (!string.IsNullOrEmpty(urlParams))
        {
            ProcessUrlData(urlParams);
        }

        // جعل صورة اللاعب دائرية
        MakePlayerImageCircular();
    }

    string GetUrlParams()
    {
        string query = Application.absoluteURL;
        if (query.Contains("data="))
        {
            string data = query.Split(new string[] { "data=" }, System.StringSplitOptions.None)[1];
            return System.Uri.UnescapeDataString(data); // فك تشفير البيانات
        }
        return string.Empty;
    }

    void ProcessUrlData(string data)
    {
        Debug.Log("Received Data: " + data); // طباعة البيانات المستلمة
        var jsonData = JsonUtility.FromJson<PlayerData>(data);

        if (jsonData == null)
        {
            Debug.LogError("فشل في تحويل البيانات إلى JSON.");
            return;
        }

        Debug.Log("Player Name: " + jsonData.name);
        Debug.Log("Player Profile Pic: " + jsonData.profile_pic);

        playerName = jsonData.name;
        playerProfilePic = jsonData.profile_pic;

        if (playerNameText != null)
        {
            playerNameText.text = playerName;
        }
        else
        {
            Debug.LogError("لم يتم تعيين playerNameText في Inspector.");
        }

        StartCoroutine(LoadPlayerImage(playerProfilePic));
    }

    IEnumerator LoadPlayerImage(string url)
    {
        UnityWebRequest request = UnityWebRequestTexture.GetTexture(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Texture2D texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
            if (playerImage != null)
            {
                playerImage.sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                playerImage.type = Image.Type.Simple;
                playerImage.preserveAspect = true;
            }
            else
            {
                Debug.LogError("لم يتم تعيين playerImage في Inspector.");
            }
        }
        else
        {
            Debug.LogError("Error: " + request.error);
        }
    }

    void MakePlayerImageCircular()
    {
        if (playerImage == null)
        {
            Debug.LogError("لم يتم تعيين playerImage في Inspector.");
            return;
        }

        // إضافة Mask إذا لم يكن موجودًا
        Mask mask = playerImage.GetComponent<Mask>();
        if (mask == null)
        {
            mask = playerImage.gameObject.AddComponent<Mask>();
            mask.showMaskGraphic = false;
        }

        // إضافة Image إذا لم يكن موجودًا
        Image maskImage = playerImage.GetComponent<Image>();
        if (maskImage == null)
        {
            maskImage = playerImage.gameObject.AddComponent<Image>();
            maskImage.sprite = Resources.Load<Sprite>("CircleMask");
            maskImage.type = Image.Type.Simple;
            maskImage.preserveAspect = true;
        }
    }
}

[System.Serializable]
public class PlayerData
{
    public string name;
    public string profile_pic;
}