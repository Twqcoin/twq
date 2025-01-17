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

    // بداية اللعبة
    void Start()
    {
        // الحصول على البيانات من الرابط
        string urlParams = GetUrlParams();
        if (!string.IsNullOrEmpty(urlParams))
        {
            ProcessUrlData(urlParams);
        }
    }

    // الحصول على البيانات من رابط URL
    string GetUrlParams()
    {
        string query = Application.absoluteURL;
        if (query.Contains("data="))
        {
            string data = query.Split(new string[] { "data=" }, System.StringSplitOptions.None)[1];
            return data;
        }
        return string.Empty;
    }

    // معالجة البيانات القادمة من الرابط
    void ProcessUrlData(string data)
    {
        var jsonData = JsonUtility.FromJson<PlayerData>(data);

        // التحقق من البيانات
        Debug.Log("Player Name: " + jsonData.name);
        Debug.Log("Player Profile Pic: " + jsonData.profile_pic);

        // تحديث اسم وصورة اللاعب
        playerName = jsonData.name;
        playerProfilePic = jsonData.profile_pic;

        playerNameText.text = playerName;
        StartCoroutine(LoadPlayerImage(playerProfilePic));
    }

    // تحميل صورة اللاعب
    IEnumerator LoadPlayerImage(string url)
    {
        UnityWebRequest request = UnityWebRequestTexture.GetTexture(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            Texture2D texture = ((DownloadHandlerTexture)request.downloadHandler).texture;
            playerImage.sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
            playerImage.type = Image.Type.Simple;
            playerImage.preserveAspect = true;
        }
        else
        {
            Debug.LogError("Error: " + request.error);
        }
    }
}

// كلاس البيانات الخاصة باللاعب
[System.Serializable]
public class PlayerData
{
    public string name;
    public string profile_pic;
}
