using System.Collections;  // لإضافة IEnumerator
using UnityEngine;         // للعمل مع Unity
using UnityEngine.Networking;  // للوصول إلى API
using UnityEngine.UI;      // للتعامل مع العناصر في واجهة المستخدم (مثل النصوص والصور)

public class PlayerInfo : MonoBehaviour
{
    public Text playerNameText;
    public Image playerImage;

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(GetPlayerInfo());
    }

    IEnumerator GetPlayerInfo()
    {
        // استدعاء API للحصول على البيانات من Flask
        UnityWebRequest www = UnityWebRequest.Get("http://your-server-url/get_player_info");
        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            // تحليل البيانات المستلمة من الخادم
            string jsonResponse = www.downloadHandler.text;
            PlayerInfoData playerInfo = JsonUtility.FromJson<PlayerInfoData>(jsonResponse);

            // تحديث اسم وصورة اللاعب في واجهة Unity
            playerNameText.text = playerInfo.name;
            StartCoroutine(LoadImage(playerInfo.photo_url));
        }
    }

    IEnumerator LoadImage(string url)
    {
        UnityWebRequest www = UnityWebRequestTexture.GetTexture(url);
        yield return www.SendWebRequest();

        if (www.result == UnityWebRequest.Result.Success)
        {
            Texture2D texture = ((DownloadHandlerTexture)www.downloadHandler).texture;
            playerImage.sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
        }
    }

    [System.Serializable]
    public class PlayerInfoData
    {
        public string name;
        public string photo_url;
    }
}
